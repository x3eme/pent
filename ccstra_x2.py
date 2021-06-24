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

    def exec(self, sym, data5min, data1hour, ex1:Btexchange, ord_log=None, strat_log=None):


        # print(data5min)
        # print(data1hour)

        self.symbol = sym
        self.ex1 = ex1
        # print(data5min)
        self.ts = data5min.iloc[1]['timespan1']
        self.lasto = data5min.iloc[1]['open']
        self.lasth = data5min.iloc[1]['high']
        self.lastl = data5min.iloc[1]['low']
        self.lastc = data5min.iloc[1]['close']
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
        # self.datah = data1hour
        # self.datah = self.data.reindex(index=self.datah.index[::-1])
        self.cch = data1hour['trend_cci']
        self.cc5l = 0
        self.cc5n = data5min.iloc[1]['trend_cci']
        self.ccbb = data5min.iloc[0]['trend_cci']
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
        # self.ma1 = self.df.iloc
        try:
            self.avoid = False
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
            # self.df["trend_cci_low"] = CCIIndicator(
            #     high=self.df['high'],
            #     low=self.df['low'],
            #     close=self.df['close'],
            #     window=20,
            #     constant=0.015,
            #     fillna=False,
            # ).ccilow()
            # # normal
            # self.df["trend_cci"] = CCIIndicator(
            #     high=self.df['high'],
            #     low=self.df['low'],
            #     close=self.df['close'],
            #     window=20,
            #     constant=0.015,
            #     fillna=False,
            # ).cci()
            # # high
            # self.df["trend_cci_high"] = CCIIndicator(
            #     high=self.df['high'],
            #     low=self.df['low'],
            #     close=self.df['close'],
            #     window=20,
            #     constant=0.015,
            #     fillna=False,
            # ).ccihigh()
            # # normal 1h
            # self.datah["trend_cci"] = CCIIndicator(
            #     high=self.datah['high'],
            #     low=self.datah['low'],
            #     close=self.datah['close'],
            #     window=20,
            #     constant=0.015,
            #     fillna=False,
            # ).cci()
            # print(self.df)
            # self.letlong = float(self.df.iloc[21]["trend_cci"])>0 or float(self.df.iloc[20]["trend_cci"])>0
            # self.letshort = float(self.df.iloc[21]["trend_cci"]) < 0 or float(self.df.iloc[20]["trend_cci"]) < 0
        except:
            print("some errors here")
        try:
            # self.cc5l = float(self.df.iloc[299]["trend_cci_low"])
            # self.cc5n = float(self.df.iloc[299]["trend_cci"])
            # self.cc5h = float(self.df.iloc[299]["trend_cci_high"])
            # self.ccbb = float(self.df.iloc[298]["trend_cci"])
            self.close0 = float(self.df.iloc[1]["close"])
            self.close1 = float(self.df.iloc[0]["close"])
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
        # print(str(self.candle) + " cci5min: " + str(self.cc5n) + " cci1hour: " + str(self.cch))
        if (float(self.cc5n) < float(-200)) and float(self.cch) < float(-200):
            print("going long :")
            # print(str(self.candle) + " cci5min: " + str(self.cc5n) + " cci1hour: " + str(self.cch))
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
        if (float(self.cc5n) > float(200)) and float(self.cch) > float(200):
            print("going short :")
            # print(str(self.candle) + " cci5min: " + str(self.cc5n) + " cci1hour: " + str(self.cch))
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
        if (float(self.cc5n) < 0 and float(self.ccbb) > 0) or (float(self.cc5n) >0 and float(self.cc5n)>float(self.ccbb) and self.close0<self.close1):
            # print("{} cci5l {}".format(str(datetime.fromtimestamp(self.candle[0]/1000)),str(self.cc5l)))
            self.ex1.close(self.symbol, "buy", self.candle)
            # self.ex.close_long(self.symbol)
            # pass
            # print("close_long : " + self.symbol + " at " + str(self.lastc))
            self.retval += "-close_long"

        if (float(self.cc5n) > 0 and float(self.ccbb) < 0) or (float(self.cc5n) <0 and float(self.cc5n)<float(self.ccbb) and self.close0>self.close1):
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
