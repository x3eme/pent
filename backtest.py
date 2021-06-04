import sqlite3
from threading import Thread
import exchange
import pandas
import ccstra
import rsistochstra
from plot import Plot
import data
import binance
import psycopg2
from binance import Client
from binance.enums import HistoricalKlinesType
import datetime
from btexchange import Btexchange


class Backtest:
    def __init__(self):
        self.period = 1  # period in months
        self.start_date = datetime.datetime(2020, 12, 1)
        self.market_type = "FUTURES"  # FUTURES or SPOT

        self.initial_capital = 100  # in USDT
        self.portion_per_trade = 1  # 1 for all 0.2 for 20 percent
        self.candles_length = 20  # candles strategy needs to decide
        self.ccstra = rsistochstra.Strategy()

    def run(self, pair, pl):
        ex1 = Btexchange()
        print(datetime.datetime.now())
        print(str(self.start_date))
        self.start_timespan = int(datetime.datetime.timestamp(self.start_date) * 1000) - (
                    self.candles_length * 5 * 60000)
        self.finish_timespan = self.start_timespan + (self.period * 30 * 24 * 12 * 5 * 60000)
        print(self.start_timespan)
        self.conn = None
        if (self.market_type == "FUTURES"):
            self.db_file = "data-futures.db"
        else:
            self.db_file = "data-spot.db"
        try:
            self.conn = sqlite3.connect(self.db_file)
        except self.Error as e:
            print(e)
        print("loading data ...")
        self.cur = self.conn.cursor()
        self.cur.execute(
            "SELECT timespan1, CAST(open as float) as open ,CAST(high as float) as high ,CAST(low as float) as low ,CAST(close as float) as close,volume FROM " + pair + " where timespan1>" + str(
                self.start_timespan - 1) + " and timespan1<" + str(self.finish_timespan + 1) + "")

        self.rows = self.cur.fetchall()
        print("data loaded ...")
        print(str(len(self.rows)) + " rows loaded!")
        total_rows = len(self.rows)
        df = pandas.DataFrame(self.rows)
        df.columns = [desc[0] for desc in self.cur.description]
        self.go = True
        ind = 0
        while self.go:
            # call
            sub_df = df.iloc[ind:ind + 20, ]
            sub_df = sub_df.reindex(index=sub_df.index[::1])
            ccstra.Strategy().exec(sym=pair, data5min=sub_df, ex1=ex1)
            if ((ind + 22) > total_rows):
                self.go = False
            else:
                ind += 1
        # print(datetime.datetime.now())
        pl.plot(ex1.closed_positions, pair, self.start_date)

        # print(self.rows)
        # pair = input("Enter pair (ex:'btcusdt' or 'all' for all pairs): ")
        # start_date = input("Enter start date (ex:'2018-01-02' for Jan 2,2018): ")
        # period = input("Enter backtest period in months: ")
        # capital=10000
        #
        # print(pair)

def main():
    pl = Plot()
    threads = []
    pairs = ["ADAUSDT", "ETHUSDT", "XRPUSDT", "EOSUSDT"]
    for p in pairs:
        bt = Backtest()
        t = Thread(target=bt.run, args=(p,pl))
        # self.run(p)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    pl.export()


bt = Backtest()
main()
