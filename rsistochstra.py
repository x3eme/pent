from datetime import datetime

import hta
import pandas
import data
import time
from exchange import Exchange
import logging
from btexchange import Btexchange



from ta.momentum import (
    AwesomeOscillatorIndicator,
    KAMAIndicator,
    PercentagePriceOscillator,
    PercentageVolumeOscillator,
    ROCIndicator,
    RSIIndicator,
    StochasticOscillator,
    StochRSIIndicator,
    TSIIndicator,
    UltimateOscillator,
    WilliamsRIndicator,
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

    def exec(self, sym, data5min, ex1:Btexchange, ord_log=None, strat_log=None):
        self.symbol = sym
        self.ex1 = ex1
        # print(data5min)
        self.ts = data5min.iloc[19]['timespan1']
        self.lasto = data5min.iloc[19]['open']
        self.lasth = data5min.iloc[19]['high']
        self.lastl = data5min.iloc[19]['low']
        self.lastc = data5min.iloc[19]['close']
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
        # self.datah = datac.geth(self.data)
        self.cch = 0
        self.cc5l = 0
        self.cc5n = 0
        self.cc5h = 0
        # self.ex = exch

        self.ord_log = ord_log
        self.strat_log = strat_log
        self.ta()
        self.decide()
        # self.update_positions()

    def ta(self):
        self.df = self.data
        # print(self.df)
        # dfh = self.datah
        # CCI Indicator
        # low
        try:
            self.avoid = False
            difff = float(self.df.tail(1)["high"])-float(self.df.tail(1)["low"])
            iin = 1
            high1 = 0
            high2 = 0
            low1 = 1000000
            low2 = 1000000
            self.golong = False
            self.goshort = False
            # self.dfm2 = self.df.iloc[1:, ]
            # self.dfm1 = self.df.iloc[1:30, ]
            # column1 = self.dfm1["high"]
            # high1 = column1.max()
            #
            # column2 = self.dfm2["high"]
            # high2 = column2.max()
            #
            # column3 = self.dfm1["low"]
            # low1 = column3.min()
            #
            # column4 = self.dfm2["low"]
            # low2 = column4.min()


            # while iin<251:
            #     if(float(self.df.iloc[iin]["high"])>high2):
            #         high2=float(self.df.iloc[iin]["high"])
            #     if(float(self.df.iloc[iin]["low"])<low2):
            #         low2=float(self.df.iloc[iin]["low"])
            #
            #     if (float(self.df.iloc[iin]["high"]) > high1) and (iin>220):
            #         high1 = float(self.df.iloc[iin]["high"])
            #     if (float(self.df.iloc[iin]["low"]) < low1) and (iin>220):
            #         low1 = float(self.df.iloc[iin]["low"])
            #
            #     iin += 1
            #
            # if (float(self.df.iloc[0]["high"]) > high1) and (float(self.df.iloc[0]["high"]) < high2):
            #     self.goshort = True
            # if (float(self.df.iloc[0]["low"]) < low1) and (float(self.df.iloc[0]["low"]) > low2):
            #     self.golong = True

            # RSI
            self.df["rsi"] = RSIIndicator(
                close=self.df['close'],
                window=20,
                fillna=False,
            ).rsi()
            # Stoch
            self.df["stoch"] = StochasticOscillator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                fillna=False,
            ).stoch()
            # Stoch Signal
            self.df["stoch_signal"] = StochasticOscillator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                smooth_window=3,
                fillna=False,
            ).stoch_signal()
            # CCI
            self.df["trend_cci"] = CCIIndicator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=20,
                constant=0.015,
                fillna=False,
            ).cci()
            # normal 1h
            # dfh["trend_cci"] = CCIIndicator(
            #     high=dfh['high'],
            #     low=dfh['low'],
            #     close=dfh['close'],
            #     window=20,
            #     constant=0.015,
            #     fillna=False,
            # ).cci()
            # print(self.df["rsi"])
        except:
            print("some errors here")
        try:
            self.rsi = float(self.df.tail(1)["rsi"])
            self.stoch = float(self.df.tail(1)["stoch"])
            self.stoch_signal = float(self.df.tail(1)["stoch_signal"])
            self.cci = float(self.df.tail(1)["trend_cci"])
            # print(self.cc5l)
            # print(self.cc5n)
            # print(self.cc5h)
            # self.cch = float(self.datah.tail(1)["trend_cci"])
        except:
            print("some errors in convert...")

    def decide(self):
        # print("we are in decide")
        self.ex1.update(self.candle)

        self.retval = "-"
        self.ex1.update(self.candle)
        # try:
        # if float(self.cc5h) < float(-220):
        #     self.strat_log.info("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5h))
        #     print("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5l: " + str(self.cc5l))
        # if float(self.cch) > float(200):
        #     self.strat_log.info("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5l))
        #     print("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5h: " + str(self.cc5h))

        if float(self.rsi) < float(20) and float(self.stoch)<float(20) :#and float(self.stoch_signal)>float(self.stoch) :#and self.golong:  # and float(self.cch) < float(-200):
            # print("going long")
            # print("{} cci5l {}".format(str(datetime.fromtimestamp(self.candle[0]/1000)),str(self.cc5l)))
            self.ex1.entry(self.symbol,"buy",self.candle,self.lastc)
            # self.strat_log.info("long: " + self.symbol)
            # print("long: " + self.symbol)
            # self.ex.open_long(self.symbol)
            # print("open_long : " + self.symbol + " at " + str(self.lastc))
            # self.retval += "-open_long"
            # frequency = 2500  # Set Frequency To 2500 Hertz
            # duration = 1000  # Set Duration To 1000 ms == 1 second
            # winsound.Beep(frequency, duration)
        if float(self.rsi) > float(80) and float(self.stoch)>float(80):# and float(self.stoch_signal)<float(self.stoch):# and self.goshort:  # and float(self.cch) > float(200):
            # print("going short")
            # print("{} cci5h {}".format(str(datetime.fromtimestamp(self.candle[0]/1000)),str(self.cc5h)))
            self.ex1.entry(self.symbol, "sell", self.candle, self.lastc)
            # print("short: " + self.symbol)
            # self.strat_log.info("short: " + self.symbol)
            # self.ex.open_short(self.symbol)
            # #
            # print("open_short : " + self.symbol + " at " + str(self.lastc))
            # self.retval += "-open_short"
            # frequency = 2500  # Set Frequency To 2500 Hertz
            # duration = 1000  # Set Duration To 1000 ms == 1 second
            # winsound.Beep(frequency, duration)
        if float(self.cci) > float(0):
            # print("{} cci5l {}".format(str(datetime.fromtimestamp(self.candle[0]/1000)),str(self.cc5l)))
            self.ex1.close(self.symbol, "buy", self.candle)
            # self.ex.close_long(self.symbol)
            # pass
            # print("close_long : " + self.symbol + " at " + str(self.lastc))
            self.retval += "-close_long"

        if float(self.cci) < float(0):
            # print("{} cci5h {}".format(str(datetime.fromtimestamp(self.candle[0]/1000)),str(self.cc5h)))
            self.ex1.close(self.symbol, "sell", self.candle)
            # self.ex.close_short(self.symbol)
            # pass
            # print("close_short : " + self.symbol + " at " + str(self.lastc))
            # self.retval += "-close_short"
        if self.retval == "-":
            pass
            # self.retval += "-nothing"

        # except Exception as e:
        #
        #     print('Failed to : ' + str(e))
        # print (self.retval)

    def update_positions(self):
        pass
        # if float(self.cc5l) > float(0):
        #     self.ex.close_long(self.symbol)
        #     pass
        #
        # if float(self.cc5h) < float(0):
        #     self.ex.close_short(self.symbol)
        #     pass
