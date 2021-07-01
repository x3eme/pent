from datetime import datetime

import hta
import pandas
import data
import time
from exchange import Exchange
import logging
from btexchange import Btexchange


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
        datac = data.Data()
        self.data = data5min
        self.datah = datac.geth(self.data)
        # self.datah = self.datah.reindex(index=self.datah.index[::-1])

        # self.cch = data1hour['trend_cci']
        self.cc5l = 0
        self.cc5n = 0
        self.ccbb = 0
        self.cc5h = 0
        # self.ex = exch

        self.ord_log = ord_log
        self.strat_log = strat_log
        self.ta()
        self.decide()
        self.update_positions()

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
        # self.update_positions()
        try:
            if float(self.cch) < float(-200):
                self.strat_log.info("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5h))
                # print("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5l: " + str(self.cc5l))
            if float(self.cch) > float(200):
                self.strat_log.info("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5l))
                # print("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5h: " + str(self.cc5h))




            if float(self.cc5l) < float(-200) and float(self.cch) < float(-200) and float(self.canlenma) > 1.0:
                print("symbol : " + self.symbol + "---cci hourly : " + str(self.cch) + " ---cci5s : " + str(
                    self.cc5l) + "-" + str(self.cc5n) + "-" + str(self.cc5h) + " ---candle lengh ma : " + str(
                    self.canlenma))

                self.strat_log.info("long: " + self.symbol)
                print("long: " + self.symbol)
                self.ex1.open_long(self.symbol)

            if float(self.cc5h) > float(200) and float(self.cch) > float(200) and float(self.canlenma) > 1.0:
                print("symbol : " + self.symbol + "---cci hourly : " + str(self.cch) + " ---cci5s : " + str(
                    self.cc5l) + "-" + str(self.cc5n) + "-" + str(self.cc5h) + " ---candle lengh ma : " + str(
                    self.canlenma))

                print("short: " + self.symbol)
                self.strat_log.info("short: " + self.symbol)
                self.ex1.open_short(self.symbol)


        except:
            pass

    def update_positions(self):
        if (float(self.cc5n) < 0 and float(self.ccbb) > 0) or (float(self.cc5n) >0 and float(self.cc5n)>float(self.ccbb) and self.close0<self.close1):
            self.ex1.close_long(self.symbol)
            pass

        if (float(self.cc5n) > 0 and float(self.ccbb) < 0) or (float(self.cc5n) <0 and float(self.cc5n)<float(self.ccbb) and self.close0>self.close1):
            self.ex1.close_short(self.symbol)
            pass
