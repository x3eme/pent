import winsound
from datetime import datetime

import hta
import pandas
import n3data
import ta
import util

import time
from exchange import Exchange
import warnings
import logging
from btexchange import Btexchange


import ta.trend
from ta.trend import (
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

    def __init__(self, symbols):
        self.retval = "-"
        # create a pandas dataframe for limit orders
        self.ordersdf = pandas.DataFrame(columns=['symbol', 'shortprice', 'longprice', 'side', 'ts'])
        i=0
        while i < len(symbols):
            self.ordersdf.loc[i]  = [symbols[i], 0.0, 0.0, 0, 0.0]  # adding a row
            i = i+1

        # self.ordersdf.loc[self.ordersdf['symbol'] == 'AAVEUSDT', 'shortprice'] = 4.5
        # print(float(self.ordersdf.loc[self.ordersdf['symbol'] == 'AAVEUSDT', 'shortprice']))
        # print(self.ordersdf)

    def exec(self, sym, data5min, ex1:Exchange, ord_log=None, strat_log=None):


        # print(data5min)
        # print("-----")
        # print(data1hour)
        # print("-------------------------")

        self.symbol = sym
        self.ex1 = ex1
        # print(str((float(data5min.iloc[101]['t1']))))
        if (len(data5min)==252) and ((float(data5min.iloc[251]['t1'])-float(data5min.iloc[0]['t1']))==251*5*60*1000):
            last_ts = float(data5min.iloc[251]['t1'])
            tsorder = util.Util().get_5min_order(last_ts)
            # print(str(tsorder))
            # if tsorder == float(1):
            if False:
                print("not checking 1st hour candle in 1 hour timeframe")
            else:
                # print("data ok")
                datac = n3data.Data()
                self.data = data5min
                self.datah = datac.geth(self.data)


                self.currentts = float(data5min.iloc[251]['t1'])
            #     print(data5min)
            #     self.ts = data5min.iloc[100]['t1']
            #     self.lasto = data5min.iloc[100]['open']
            #     self.lasth = data5min.iloc[100]['high']
            #     self.lastl = data5min.iloc[100]['low']
                self.lastc = data5min.iloc[251]['close']
            # # self.candles = "["+str(self.ts)+","+str(self.lasto)+","+str(self.lasth)+","+str(self.lastl)+","+str(self.lastc)+"]"
            #     self.candle = []
            #     self.candle.append(self.ts)
            #     self.candle.append(self.lasto)
            #     self.candle.append(self.lasth)
            #     self.candle.append(self.lastl)
            #     self.candle.append(self.lastc)

                self.symbol = sym.upper()
                # datac = data.Data()
                self.data = data5min
                # self.datah = datac.geth(self.data)
                # self.datah = self.datah.reindex(index=self.datah.index[::-1])

                # self.cch = data1hour['trend_cci']
                # self.cc5l = 0
                # self.cc5n = 0
                # self.ccbb = 0
                # self.cc5h = 0
                # self.ex = exch

                self.ord_log = ord_log
                self.strat_log = strat_log
                self.ta()
                self.decide()
                self.update_positions()
        else:
            print("data corrupt ..." + self.symbol)
            # data.Data().fix(symbol=self.symbol,timeframe="5m")

    def ta(self):
        self.df = self.data

        try:
            pass
            # print(self.symbol)


        except :
            # print(e)
            print("some errors here")
        # self.bothside = False
        try:
            i=0
            self.ma20 = 0.0
            self.ma50 = 0.0
            self.ma100 = 0.0
            self.ma20old = 0.0
            self.ma50old = 0.0
            self.ma100old = 0.0

            while i < 100:
                if i<20:
                    self.ma20 += self.df.iloc[250-i]["close"]
                    self.ma50 += self.df.iloc[250-i]["close"]
                    self.ma100 += self.df.iloc[250-i]["close"]
                if i>19 and i<50:
                    self.ma50 += self.df.iloc[250 - i]["close"]
                    self.ma100 += self.df.iloc[250 - i]["close"]
                if i>49 and i<100:
                    self.ma100 += self.df.iloc[250 - i]["close"]
                i+=1
            self.ma20old = self.ma20 - self.df.iloc[250]["close"] + self.df.iloc[230]["close"]
            self.ma50old = self.ma50 - self.df.iloc[250]["close"] + self.df.iloc[200]["close"]
            self.ma100old = self.ma100 - self.df.iloc[250]["close"] + self.df.iloc[150]["close"]
            self.ma20old = self.ma20old / 20
            self.ma50old = self.ma50old / 50
            self.ma100old = self.ma100old / 100
            self.ma20 = self.ma20 / 20
            self.ma50 = self.ma50 / 50
            self.ma100 = self.ma100 / 100

            self.oldstat = 0
            self.stat = 0
            if self.ma20old > self.ma50old and self.ma50old>self.ma100old:
                self.oldstat = 1
            elif self.ma20old < self.ma50old and self.ma50old<self.ma100old:
                self.oldstat = 2
            else :
                self.oldstat = 0

            if self.ma20 > self.ma50 and self.ma50>self.ma100:
                self.stat = 1
            elif self.ma20 < self.ma50 and self.ma50<self.ma100:
                self.stat = 2
            else :
                self.stat = 0
            # print("close : ",self.df.iloc[250]["close"])
            # print("ma20 : ",str(self.ma20))
            # print("ma50 : " , str(self.ma50))
            # print("ma100 : " , str(self.ma100))


        except:
            print("some errors in convert...")
    def decide(self):
        # self.update_positions()
        try:
            if self.oldstat != 1 and self.stat ==1:
                self.strat_log.info("long: " + self.symbol)
                print("long: " + self.symbol)
                self.ex1.open_long(self.symbol)
                frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 1000  # Set Duration To 1000 ms == 1 second
                # winsound.Beep(frequency, duration)

            if self.oldstat !=2 and self.stat ==2:
                print("short: " + self.symbol)
                self.strat_log.info("short: " + self.symbol)
                self.ex1.open_short(self.symbol)
                frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 1000  # Set Duration To 1000 ms == 1 second
                # winsound.Beep(frequency, duration)



        except:
            pass

    def update_positions(self):
        # if float(self.cc5n) > float(0):
            # self.ex1.close_long(self.symbol)
            pass

        # if float(self.cc5n) < float(0):
            # self.ex1.close_short(self.symbol)
            pass



        # if self.closelongCondition:
        #     self.ex1.close_long(self.symbol)
        #     # print(self.symbol+ " closed long")
        #     self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'side'] = 2
        #     self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'ts'] = self.currentts
        #     pass
        #
        # if self.closeshortCondition:
        #     self.ex1.close_short(self.symbol)
        #     # print(self.symbol + " closed short")
        #     self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'side'] = 1
        #     self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'ts'] = self.currentts
        #     pass
