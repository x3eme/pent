import ta
import pandas
import data
import time
# import winsound
from exchange import Exchange
import logging

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

    def __init__(self,sym,data5min,exch:Exchange, ord_log, strat_log):
        self.symbol = sym
        self.symbol = self.symbol.upper()
        datac = data.Data()
        self.data = data5min
        self.datah = datac.geth(self.data)
        self.cch = 0
        self.cc5l = 0
        self.cc5n = 0
        self.cc5h = 0
        self.ex = exch

        self.ord_log = ord_log
        self.strat_log = strat_log

    def exec(self):
        self.ta()
        self.decide()
        self.update_positions()

    def ta(self):
        df = self.data
        dfh = self.datah
        # CCI Indicator
        # low
        df["trend_cci_low"] = CCIIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=20,
            constant=0.015,
            fillna=False,
        ).ccilow()
        # normal
        df["trend_cci"] = CCIIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=20,
            constant=0.015,
            fillna=False,
        ).cci()
        # high
        df["trend_cci_high"] = CCIIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=20,
            constant=0.015,
            fillna=False,
        ).ccihigh()
        # normal 1h
        dfh["trend_cci"] = CCIIndicator(
            high=dfh['high'],
            low=dfh['low'],
            close=dfh['close'],
            window=20,
            constant=0.015,
            fillna=False,
        ).cci()
        try:
            self.cc5l = float(self.data.tail(1)["trend_cci_low"])
            self.cc5n = float(self.data.tail(1)["trend_cci"])
            self.cc5h = float(self.data.tail(1)["trend_cci_high"])
            self.cch = float(self.datah.tail(1)["trend_cci"])
        except:
            print("some errors in convert...")

    def decide(self):
        try:
            if float(self.cch) < float(-200):
                self.strat_log.info("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5h))
                # print("possible long: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5l: " + str(self.cc5l))
            if float(self.cch) > float(200):
                self.strat_log.info("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5: " + str(self.cc5l))
                # print("possible short: " + str(self.symbol) + " cci60: " + str(self.cch) + " cci5h: " + str(self.cc5h))



            if float(self.cc5l) < float(-220):# and float(self.cch) < float(-200):
                self.strat_log.info("long: " + self.symbol)
                # print("long: " + self.symbol)
                self.ex.open_long(self.symbol)

                # frequency = 2500  # Set Frequency To 2500 Hertz
                # duration = 1000  # Set Duration To 1000 ms == 1 second
                # winsound.Beep(frequency, duration)
            if float(self.cc5h) > float(220):# and float(self.cch) > float(200):
                # print("short: " + self.symbol)
                self.strat_log.info("short: " + self.symbol)
                self.ex.open_short(self.symbol)


                # frequency = 2500  # Set Frequency To 2500 Hertz
                # duration = 1000  # Set Duration To 1000 ms == 1 second
                # winsound.Beep(frequency, duration)


        except:
            pass

    def update_positions(self):
        if float(self.cc5l) > float(0):
            self.ex.close_long(self.symbol)
            pass

        if float(self.cc5h) < float(0):
            self.ex.close_short(self.symbol)
            pass
