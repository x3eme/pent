from datetime import datetime

import hta
import pandas
import data
import time
from exchange import Exchange
import logging
from btexchange import Btexchange

from ta.volatility import (
    AverageTrueRange
)

from hta import (
    MACD,
    ADXIndicator,
    AroonIndicator,
    CCIIndicator,
    DPOIndicator,
    EMAIndicator,
    IchimokuIndicator,
    KSTIndicator,
    MassIndex,
    PSARIndicator,
    SMAIndicator,
    STCIndicator,
    TRIXIndicator,
    VortexIndicator,
)


class Strategy:

    def __init__(self):

        self.retval = "-"

    def exec(self, sym, data5min, ex1:Exchange, ord_log=None, strat_log=None):


        # print(data5min)
        # print("-----")
        # print(data1hour)
        # print("-------------------------")

        self.symbol = sym
        self.ex1 = ex1
        # print(data5min)
        self.ts = data5min.iloc[251]['t1']
        self.lasto = data5min.iloc[251]['open']
        self.lasth = data5min.iloc[251]['high']
        self.lastl = data5min.iloc[251]['low']
        self.lastc = data5min.iloc[251]['close']
        # self.candles = "["+str(self.ts)+","+str(self.lasto)+","+str(self.lasth)+","+str(self.lastl)+","+str(self.lastc)+"]"
        self.candle = []
        self.candle.append(self.ts)
        self.candle.append(self.lasto)
        self.candle.append(self.lasth)
        self.candle.append(self.lastl)
        self.candle.append(self.lastc)

        self.symbol = sym.upper()
        # datac = data.Data()
        self.data = data5min
        ########################################################################################
        # strategy variables :
        self.usr_risk = 3.0
        self.atr_mult = 0.5
        self.sma_slow = 99
        self.sma_med = 25
        self.sma_fast = 7

        # strategy conditions :
        # find pinbars in a candle
        self.bullishPinBar = (self.lastc > self.lasto and (self.lasto - self.lastl) > 0.66 * (
                self.lasth - self.lastl)) or (self.lastc < self.lasto and (self.lastc - self.lastl) > 0.66 * (
                self.lasth - self.lastl))
        self.bearishPinBar = (self.lastc > self.lasto and (self.lasth - self.lastc) > 0.66 * (
                    self.lasth - self.lastl)) or (self.lastc < self.lasto and (self.lasth - self.lasto) > 0.66 * (
                    self.lasth - self.lastl))

        # check if we are in an uptrend or downtrend
        sum1 = 0.0
        sum2 = 0.0
        sum3 = 0.0
        index = 0
        while index<99:
            if index<7:
               sum1 += data5min.iloc[251-index]['close']
               sum2 += data5min.iloc[251 - index]['close']
               sum3 += data5min.iloc[251 - index]['close']
            if index>=7 and index<25:
               sum2 += data5min.iloc[251 - index]['close']
               sum3 += data5min.iloc[251 - index]['close']
            if index>=25 and index<99:
               sum3 += data5min.iloc[251 - index]['close']
            index += 1
        self.ma7 = sum1 / 7
        self.ma25 = sum2 / 25
        self.ma99 = sum3 / 99
        self.upTrend = self.ma7 > self.ma25 and self.ma25 > self.ma99
        self.dnTrend = self.ma7 < self.ma25 and self.ma25 < self.ma99

        # now lets check some piercing a candle in a MA :
        self.bullPierce = (self.lastl < self.ma7 and self.lasto > self.ma7 and self.lastc > self.ma7) or (
                self.lastl < self.ma25 and self.lasto > self.ma25 and self.lastc > self.ma25) or (
                                self.lastl < self.ma99 and self.lasto > self.ma99 and self.lastc > self.ma99)
        self.bearPierce = (self.lasth > self.ma7 and self.lasto < self.ma7 and self.lastc < self.ma7) or (
                self.lasth > self.ma25 and self.lasto < self.ma25 and self.lastc < self.ma25) or (
                                  self.lasth > self.ma99 and self.lasto < self.ma99 and self.lastc < self.ma99)

        # Final long short condition :
        self.logCondition = self.bullishPinBar and self.upTrend and self.bullPierce
        self.shortCondition = self.bearishPinBar and self.dnTrend and self.bearPierce

        # now lets calculate ATR :
        self.df = self.data
        self.df["atr"] = AverageTrueRange(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=14,
            fillna=False,
        ).average_true_range()

        # Amount and Entry and Stoploss :
        risk = self.usr_risk * 0.01 * 10 # 10 is strategy equity
        self.sl = self.df.iloc[250]['low'] - (self.df.iloc[250]['atr'] * self.atr_mult)
        self.entry = self.df.iloc[250]['high']
        self.amount = risk / (self.entry - self.sl)




        self.ord_log = ord_log
        self.strat_log = strat_log
        # self.ta()
        self.decide()
        # self.update_positions()

    def ta(self):
        self.df = self.data
        # print(self.df)
        # dfh = self.datah
        # CCI Indicator
        # low
        # self.ma1 = self.df.iloc
        self.calenma = 0.0
        try:
            self.avoid = False

            self.canlenma = (abs(self.data.iloc[251]['close']-self.data.iloc[251]['open'])/self.data.iloc[251]['close']*100)+\
                (abs(self.data.iloc[250]['close'] - self.data.iloc[250]['open']) / self.data.iloc[250]['close'] * 100) + \
                (abs(self.data.iloc[249]['close'] - self.data.iloc[249]['open']) / self.data.iloc[249]['close'] * 100) + \
                (abs(self.data.iloc[248]['close'] - self.data.iloc[248]['open']) / self.data.iloc[248]['close'] * 100) + \
                (abs(self.data.iloc[247]['close'] - self.data.iloc[247]['open']) / self.data.iloc[247]['close'] * 100) + \
                (abs(self.data.iloc[246]['close'] - self.data.iloc[246]['open']) / self.data.iloc[246]['close'] * 100) + \
                (abs(self.data.iloc[245]['close'] - self.data.iloc[245]['open']) / self.data.iloc[245]['close'] * 100) + \
                (abs(self.data.iloc[244]['close'] - self.data.iloc[244]['open']) / self.data.iloc[244]['close'] * 100) + \
                (abs(self.data.iloc[243]['close'] - self.data.iloc[243]['open']) / self.data.iloc[243]['close'] * 100) + \
                (abs(self.data.iloc[242]['close'] - self.data.iloc[242]['open']) / self.data.iloc[242]['close'] * 100) + \
                (abs(self.data.iloc[241]['close'] - self.data.iloc[241]['open']) / self.data.iloc[241]['close'] * 100) + \
                (abs(self.data.iloc[240]['close'] - self.data.iloc[240]['open']) / self.data.iloc[240]['close'] * 100)
            self.canlenma = self.canlenma / 12
                # difff = float(self.df.tail(1)["high"])-float(self.df.tail(1)["low"])
            # iin = 0
            # summ = 0
            # while iin<20:
            #     summ += (float(self.df.iloc[iin]["close"]))
            #     iin += 1
            # avg = summ/20
            # iin2 = 1
            # summ2 = 0
            # while iin2 < 21:
            #     summ2 += (float(self.df.iloc[iin]["close"]))
            #     iin2 += 1
            # avg2 = summ2 / 20
            self.letlong = False
            self.letshort = False
            # self.letlong = (float(self.df.iloc[20]["close"]) > avg) or (float(self.df.iloc[21]["close"]) > avg2)
            # self.letshort = (float(self.df.iloc[20]["close"]) < avg) or (float(self.df.iloc[21]["close"]) < avg2)
            # if (difff>3*avg):
            #     self.avoid = True
            self.df["trend_cci_low"] = CCIIndicator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                constant=0.015,
                fillna=False,
            ).ccilow()
            # normal
            self.df["trend_cci"] = CCIIndicator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                constant=0.015,
                fillna=False,
            ).cci()
            # high
            self.df["trend_cci_high"] = CCIIndicator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                constant=0.015,
                fillna=False,
            ).ccihigh()
            # normal 1h
            self.datah["trend_cci"] = CCIIndicator(
                high=self.datah['high'],
                low=self.datah['low'],
                close=self.datah['close'],
                window=20,
                constant=0.015,
                fillna=False,
            ).cci()
            # print(self.df)
            # self.letlong = float(self.df.iloc[21]["trend_cci"])>0 or float(self.df.iloc[20]["trend_cci"])>0
            # self.letshort = float(self.df.iloc[21]["trend_cci"]) < 0 or float(self.df.iloc[20]["trend_cci"]) < 0
        except self.Error as e:
            print(e)
            print("some errors here")
        try:
            self.cc5l = float(self.df.iloc[251]["trend_cci_low"])
            self.cc5n = float(self.df.iloc[251]["trend_cci"])
            self.cc5h = float(self.df.iloc[251]["trend_cci_high"])
            self.ccbb = float(self.df.iloc[250]["trend_cci"])
            self.close0 = float(self.df.iloc[251]["close"])
            self.close1 = float(self.df.iloc[250]["close"])
            self.cch = float(self.datah.tail(1)["trend_cci"])
            # print("symbol : " + self.symbol + "---cci hourly : " + str(self.cch)+ " ---cci5s : " + str(self.cc5l)+"-"+str(self.cc5n)+"-"+str(self.cc5h)+" ---candle lengh ma : "+str(self.canlenma))
            # print (self.canlenma)
            # print(self.cc5l)
            # print(self.cc5n)
            # print(self.cc5h)
            # print(self.df)
            # print(self.cch)
            # self.cch = float(self.datah.tail(1)["trend_cci"])
        except:
            print("some errors in convert...")
    def decide(self):
        try:
            if self.logCondition:
                self.strat_log.info("long: " + self.symbol)
                print("long: " + self.symbol)
                # self.ex1.open_long(self.symbol)

            if self.shortCondition:
                print("short: " + self.symbol)
                self.strat_log.info("short: " + self.symbol)
                # self.ex1.open_short(self.symbol)
        except:
            pass

    def update_positions(self):
        if (not self.upTrend):
            self.ex1.close_long(self.symbol)
            pass

        if (not self.dnTrend):
            self.ex1.close_short(self.symbol)
            pass
