from datetime import datetime

import hta
import pandas
import data
import time
from exchange import Exchange
import warnings
import logging
from btexchange import Btexchange


import ta.trend


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
        if (len(data5min)==102) and ((float(data5min.iloc[101]['t1'])-float(data5min.iloc[0]['t1']))==101*5*60*1000):
            # print("data ok")
            self.currentts = float(data5min.iloc[101]['t1'])
        #     print(data5min)
        #     self.ts = data5min.iloc[100]['t1']
        #     self.lasto = data5min.iloc[100]['open']
        #     self.lasth = data5min.iloc[100]['high']
        #     self.lastl = data5min.iloc[100]['low']
            self.lastc = data5min.iloc[101]['close']
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
            data.Data().fix(symbol=self.symbol,timeframe="5m")

    def ta(self):
        self.df = self.data
        #find hh and ll
        indd = 92
        indd1 = 91
        indd2 = 90
        indd3 = 89
        self.ll = 10000000.0
        self.hh = 0.0
        self.ll1 = 10000000.0
        self.hh1 = 0.0
        self.ll2 = 10000000.0
        self.hh2 = 0.0
        self.ll3 = 10000000.0
        self.hh3 = 0.0
        self.hhindex = 0
        self.llindex = 0
        while indd<101:
            if self.data.iloc[indd]['high']>self.hh:
                self.hh = self.data.iloc[indd]['high']
                self.hhindex = 101-indd
            if self.data.iloc[indd]['low']<self.ll:
                self.ll = self.data.iloc[indd]['low']
                self.llindex = 101-indd
            indd+=1
        while indd1<100:
            if self.data.iloc[indd]['high']>self.hh1:
                self.hh1 = self.data.iloc[indd]['high']
            if self.data.iloc[indd]['low']<self.ll1:
                self.ll1 = self.data.iloc[indd]['low']
            indd1+=1
        while indd2<99:
            if self.data.iloc[indd]['high']>self.hh2:
                self.hh2 = self.data.iloc[indd]['high']
            if self.data.iloc[indd]['low']<self.ll2:
                self.ll2 = self.data.iloc[indd]['low']
            indd2+=1
        while indd3<98:
            if self.data.iloc[indd]['high']>self.hh3:
                self.hh3 = self.data.iloc[indd]['high']
            if self.data.iloc[indd]['low']<self.ll3:
                self.ll3 = self.data.iloc[indd]['low']
            indd3+=1
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.df["trend_adx"] = ta.trend.ADXIndicator(
                    high=self.df['high'],
                    low=self.df['low'],
                    close=self.df['close'],
                    window=14,
                    fillna=False,
                ).adx()
            # normal
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.df["trend_cci"] = ta.trend.CCIIndicator(
                    high=self.df['high'],
                    low=self.df['low'],
                    close=self.df['close'],
                    window=20,
                    constant=0.015,
                    fillna=False,
                ).cci()

        except :
            # print(e)
            print("some errors here")
        self.bothside = False
        try:
            if float(self.df.iloc[101]['high']) >= self.hh and float(self.df.iloc[101]['low']) <= self.ll:
                self.bothside = True
            # update pandas if adx below 15
            if float(self.df.iloc[100]["trend_adx"]) < float(15):
                self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'shortprice'] = self.ll
                self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'longprice'] = self.hh
            self.longCondition = float(self.df.iloc[101]['high']) >= self.hh and float(self.df.iloc[100]["trend_adx"])<float(15) and (
                self.hhindex != 1 or self.df.iloc[99]["trend_adx"]>float(15)) and self.lastc<self.hh*1.001
            self.shortCondition = float(self.df.iloc[101]['low']) <= self.ll and float(
                self.df.iloc[100]["trend_adx"]) < float(15) and (self.llindex != 1 or self.df.iloc[99]["trend_adx"]>float(15)) and self.lastc>self.ll*0.999

            self.longCondition1 = float(self.df.iloc[100]['high']) >= self.hh1 and float(
                self.df.iloc[99]["trend_adx"]) < float(15)
            self.shortCondition1 = float(self.df.iloc[100]['low']) <= self.ll1 and float(
                self.df.iloc[99]["trend_adx"]) < float(15)

            self.longCondition2 = float(self.df.iloc[99]['high']) >= self.hh2 and float(
                self.df.iloc[98]["trend_adx"]) < float(15)
            self.shortCondition2 = float(self.df.iloc[99]['low']) <= self.ll2 and float(
                self.df.iloc[98]["trend_adx"]) < float(15)

            self.longCondition3 = float(self.df.iloc[98]['high']) >= self.hh3 and float(
                self.df.iloc[97]["trend_adx"]) < float(15)
            self.shortCondition3 = float(self.df.iloc[98]['low']) <= self.ll3 and float(
                self.df.iloc[97]["trend_adx"]) < float(15)



            self.longCondition = self.longCondition and not (self.longCondition1 or self.longCondition2 or self.longCondition3)
            self.shortCondition = self.shortCondition and not (self.shortCondition1 or self.shortCondition2 or self.shortCondition3)

            self.pastll = float(self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'shortprice'])
            self.pasthh = float(self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'longprice'])

            self.longConditionnew = (self.pasthh != 0.0 and float(self.df.iloc[101]['high']) >= self.pasthh and float(self.df.iloc[100]['high']) < self.pasthh and float(self.df.iloc[99]['high']) < self.pasthh and float(self.df.iloc[98]['high']) < self.pasthh)
            self.shortConditionnew = (self.pastll != 0.0 and float(self.df.iloc[101]['low']) <= self.pastll and float(self.df.iloc[100]['low']) > self.pastll  and float(self.df.iloc[99]['low']) > self.pastll and float(self.df.iloc[98]['low']) > self.pastll)

            # clear limit short and long prices if we are not at exact cross of limit :
            if (self.pasthh != 0.0 and float(self.df.iloc[101]['high']) > self.pasthh) and (
                    float(self.df.iloc[100]['high']) > self.pasthh or float(
                self.df.iloc[99]['high']) > self.pasthh or float(self.df.iloc[98]['high']) > self.pasthh):
                self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'longprice'] = 0.0
            if (self.pastll != 0.0 and float(self.df.iloc[101]['low']) < self.pastll) and (
                    float(self.df.iloc[100]['low']) < self.pastll or float(
                    self.df.iloc[99]['low']) < self.pastll or float(self.df.iloc[98]['low']) < self.pastll):
                self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'shortprice'] = 0.0

            self.closelongCondition = float(self.df.iloc[99]['trend_cci']) > float(200) and float(
                self.df.iloc[100]['trend_cci']) < float(200)
            self.closeshortCondition = float(self.df.iloc[99]['trend_cci']) < float(-200) and float(
                self.df.iloc[100]['trend_cci']) > float(-200)

            #there was a bug so ...
            self.longisok = False
            self.shortisok = False
            self.last_side = float(self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'side'])
            self.last_ts = float(self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'ts'])
            self.longisok = (self.last_side!=float(2)) or (self.last_ts != self.currentts)
            self.shortisok = (self.last_side != float(1)) or (self.last_ts != self.currentts)

            # print(self.ordersdf)
            # print(self.symbol+ ": ADX: "+str(float(self.df.iloc[100]["trend_adx"]))+" price: "+str(self.lastc)+" hh: "+str(self.hh)+" ll: "+str(self.ll)+ " lastts: "+
            #       str(self.last_ts)+ " currentts: "+str(self.currentts)+" lastside: "+str(self.last_side) +" so islongok: "+
            #       str(self.longisok) + " so shortisok : "+str(self.shortisok))


            # print(self.df)
            # self.cc5l = float(self.df.iloc[251]["trend_cci_low"])
            # self.cc5n = float(self.df.iloc[251]["trend_cci"])
            # self.cc5h = float(self.df.iloc[251]["trend_cci_high"])
            # self.ccbb = float(self.df.iloc[250]["trend_cci"])
            # self.close0 = float(self.df.iloc[251]["close"])
            # self.close1 = float(self.df.iloc[250]["close"])
            # self.cch = float(self.datah.tail(1)["trend_cci"])
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
            # if float(self.cch) < float(-200):
            #     self.strat_log.info("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5h))
            #     # print("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5l: " + str(self.cc5l))
            # if float(self.cch) > float(200):
            #     self.strat_log.info("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5l))
            #     # print("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5h: " + str(self.cc5h))




            if self.bothside == False:
                if (self.longCondition or self.longConditionnew) and (self.longisok):
                    self.strat_log.info("long: " + self.symbol)
                    print("long: " + self.symbol)
                    self.ex1.open_long(self.symbol)
                    # set pandas limit price order to zero so that we won't get that direction next time
                    self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'longprice'] = 0.0

                if (self.shortCondition or self.shortConditionnew) and (self.shortisok):
                    print("short: " + self.symbol)
                    self.strat_log.info("short: " + self.symbol)
                    self.ex1.open_short(self.symbol)
                    # set pandad limit price order to zero so that we won't get that direction next time
                    self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'shortprice'] = 0.0


        except:
            pass

    def update_positions(self):
        if self.closelongCondition:
            self.ex1.close_long(self.symbol)
            # print(self.symbol+ " closed long")
            self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'side'] = 2
            self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'ts'] = self.currentts
            pass

        if self.closeshortCondition:
            self.ex1.close_short(self.symbol)
            # print(self.symbol + " closed short")
            self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'side'] = 1
            self.ordersdf.loc[self.ordersdf['symbol'] == self.symbol, 'ts'] = self.currentts
            pass
