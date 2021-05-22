import sqlite3
import data
import binance
import psycopg2
from binance import Client
from binance.enums import HistoricalKlinesType
import winsound

class Historical:
    def __init__(self):
        pass
    def get_klines(self,pair):
        client = binance.Client()
        # for y in ["apple", "banana", "cherry"]
        klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_5MINUTE, "1, 1, 2017","1, 1, 2022",klines_type=HistoricalKlinesType.SPOT)
        # print(klines[0][0])
        print(str(len(klines))+" candles saved!")# , " 5min candle for Jan")
        self.save_data(klines,pair)

    def save_data(self,rows,pair):
        # print(t)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        if pair=='1INCHUSDT':
            pair='A1INCHUSDT'
        c.execute("CREATE TABLE IF NOT EXISTS "+pair+" (timespan1, open, high, low, close, volume,timespan2,f1,f2,f3,f4,f5)")
        c.executemany('insert into '+ pair + ' values (?,?,?,?,?,?,?,?,?,?,?,?)', rows)
        conn.commit()
    def start(self):
        self.my_data = data.Data()
        self.symbol_records = self.my_data.get_symbols()
        cnt = len(self.symbol_records)
        # print(cnt)
        ii = 107
        while ii < cnt:
            ssyy = self.symbol_records[ii][0].upper()
            print("going for : "+ssyy)
            self.get_klines(ssyy)
            ii += 1
        pass

his = Historical()

his.start()