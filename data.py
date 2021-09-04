import sqlite3
import warnings

import pandas
import psycopg2
import util
import time,datetime
import ccxt



class Data:


    def __init__(self):
        #create a db connection
        with open('conf.txt', 'r') as file:
            data = file.read().split('\n')
            self.dbuser = data[0]
            self.dbpass = data[1]
            self.dbhost = data[2]
            self.dbport = data[3]
            self.dbdb = data[4]
            self.binance_api_key = data[5]
            self.binance_api_secret = data[6]


        self.binance = ccxt.binance({
            'apiKey': self.binance_api_key,
            'secret': self.binance_api_secret,
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
                "adjustForTimeDifference": True
            }
        })


        #init attribs and load data from db
        # self.symbol = symbol
        # self.interval = interval
        # self.data = self.load()
    def get_historical_data(self):
        pass
        #conn = sqlite3.connect(db_file)
    def dbconnect(self):
        return psycopg2.connect(user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost,
                                           port=self.dbport,
                                           database=self.dbdb)
    def get_5min_by_symbol(self,symbol) -> pandas.DataFrame:
        newdf = self.all_data.loc[self.all_data['s3'] == symbol]
        # print(str(len(newdf)))
        # print (newdf['t1'])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            newdf.drop(newdf.tail(len(newdf)-102).index, inplace=True)
        # print(str(len(newdf)))
        newdf = newdf.reindex(index=newdf.index[::-1])
        # newdf.columns = [desc[0] for desc in newdf.description]
        return newdf
    def data_is_live(self) -> bool:
        live = False
        ts1 = time.time()
        ts2 = int(ts1*1000)
        db_timespan = self.all_data.iloc[0]['t1']
        time_lag = int((ts2-int(db_timespan))/60000)
        if time_lag < 30:
            live = True
        else:
            print("we have backwardness : ", time_lag, " Minutes!")
            print("database is not updating or check if local system datetime is not set to UTC")
        return live


    def fix(self, symbol, timeframe="5m"):

        self.connection = psycopg2.connect(user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost,
                                           port=self.dbport,
                                           database=self.dbdb)

        try:
            bnc = self.binance
            symb = symbol.replace("/", "").replace("USDT", "/USDT")

            cans = bnc.fetch_ohlcv(symbol=symb, timeframe=timeframe,limit=250)
            cans.pop()
            conn = self.dbconnect()
            for ca in cans:
                t = ca[0]
                o = ca[1]
                h = ca[2]
                l = ca[3]
                c = ca[4]
                v = ca[5]
                s = symbol
                i = timeframe
                x = "true"

                dt = datetime.datetime.fromtimestamp(t / 1000)

                print("t={} o={} h={} l={} c={} v={}".format(dt, o, h, l, c, v))

                cursor = self.connection.cursor()
                sql_insert_query = """ INSERT INTO \"""" + "klines" + """\" ("t1","s3","i4","o7","c8","h9",
                                            "l10","v11","x13")
                                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                            ON CONFLICT ("t1","s3","i4") DO UPDATE SET
                                            ("o7","c8","h9","l10","v11") = 
                                            (EXCLUDED.o7,EXCLUDED.c8,EXCLUDED.h9,EXCLUDED.l10,
                                            EXCLUDED.v11)"""

                cursor.execute(sql_insert_query, (t, s, i, o, c, h, l, v, x))
                self.connection.commit()


        except (Exception, psycopg2.Error) as error:
            print("DB Error: ", error)
            pass

        finally:
            # closing database connection.
            if (conn):
                cursor.close()
                conn.close()



    def load(self) -> pandas.DataFrame:
        #load data from database into dataframe using self.symbol and self.interval
        self.connection = psycopg2.connect(user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost,
                                           port=self.dbport,
                                           database=self.dbdb)
        try:
            conn = self.dbconnect()
            cursor = conn.cursor()
            postgreSQL_select_Query = "SELECT t1, o7 as Open,h9 as High,l10 as Low,c8 as Close,v11 as Volume FROM klines WHERE s3 = '{}' and x13='true' order by t1 desc LIMIT 252 ".format(self.symbol)#and x13='true'
            cursor.execute(postgreSQL_select_Query)
            kline_records = cursor.fetchall()
            df = pandas.DataFrame(kline_records)
            df= df.reindex(index=df.index[::-1])
            df.columns = [desc[0] for desc in cursor.description]
            if (self.interval == '1h'):
                df = self.geth(df)
            # print(df)
            return df

        except (Exception, psycopg2.Error) as error:
            print("DB Error: ",error)
            pass

        finally:
            # closing database connection.
            if (conn):
                cursor.close()
                conn.close()


        # print(df.loc[1])
        # reverse rows
        # df = df.iloc[::-1]

        return df

    def update(self) -> pandas.DataFrame:
        #update dataframe
        self.connection = psycopg2.connect(user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost,
                                           port=self.dbport,
                                           database=self.dbdb)
        try:
            conn = self.dbconnect()
            cursor = conn.cursor()
            postgreSQL_select_Query = "SELECT t1,s3, o7 as Open,h9 as High,l10 as Low,c8 as Close,v11 as Volume FROM klines order by t1 desc LIMIT 11934 " #WHERE x13='true'
            cursor.execute(postgreSQL_select_Query)
            kline_records = cursor.fetchall()
            df = pandas.DataFrame(kline_records)
            # df= df.reindex(index=df.index[::-1])
            df.columns = [desc[0] for desc in cursor.description]
            self.all_data = df
            # print(df)
            return df

        except (Exception, psycopg2.Error) as error:
            print("DB Error: ",error)
            pass

        finally:
            # closing database connection.
            if (conn):
                cursor.close()
                conn.close()

        pass
    def get_symbols(self):
        self.connection = psycopg2.connect(user=self.dbuser,
                                           password=self.dbpass,
                                           host=self.dbhost,
                                           port=self.dbport,
                                           database=self.dbdb)
        try:
            cursor = self.connection.cursor()
            postgreSQL_select_Query = "select sname from symbols"
            cursor.execute(postgreSQL_select_Query)
            self.symbol_records = cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

        finally:
            # closing database connection.
            return self.symbol_records
            if (self.connection):
                # cursor.close()
                # self.connection.close()
                print("Symbols Loaded!")

    def geth(self,dfi)-> pandas.DataFrame:
        # print(len(dfi))
        dfi = dfi.reindex(index=dfi.index[::-1])
        dfh = pandas.DataFrame(columns=["t1", "open", "high", "low", "close"])
        # print(dfi.iloc[0]['t1'])
        # print(dfi.iloc[251]['t1'])
        lenn = len(dfi)-1
        if (float(dfi.iloc[0]['t1']) == float(dfi.iloc[lenn]['t1']+lenn*300000)):
            # print("data is approved")
            ut = util.Util()
            over = ut.get_5min_order(dfi.iloc[0]['t1'])
            # print(over)

            ind=int(over)
            # print(dfi.loc[ind])
            i=0
            j=i+20
            ii=0


            while i<j:
                # bla bla

                dfh.at[ii, 't1'] = dfi.iloc[i*12+ind]['t1']
                dfh.at[ii, 'open'] = dfi.iloc[i * 12+11+ind]['open']
                dfh.at[ii, 'close'] = dfi.iloc[i * 12+ind]['close']
                dfh.at[ii, 'high'] = max([dfi.iloc[i * 12+0+ind]['high'], dfi.iloc[i * 12+1+ind]['high'],
                                        dfi.iloc[i * 12+2+ind]['high'], dfi.iloc[i * 12+3+ind]['high'],
                                        dfi.iloc[i * 12+4+ind]['high'], dfi.iloc[i * 12+5+ind]['high'],
                                        dfi.iloc[i * 12+6+ind]['high'], dfi.iloc[i * 12+7+ind]['high'],
                                        dfi.iloc[i * 12+8+ind]['high'], dfi.iloc[i * 12+9+ind]['high'],
                                        dfi.iloc[i * 12+10+ind]['high'], dfi.iloc[i * 12+11+ind]['high']])
                dfh.at[ii, 'low'] = min([dfi.iloc[i * 12 + 0+ind]['low'], dfi.iloc[i * 12 + 1+ind]['low'],
                                        dfi.iloc[i * 12 + 2+ind]['low'], dfi.iloc[i * 12 + 3+ind]['low'],
                                        dfi.iloc[i * 12 + 4+ind]['low'], dfi.iloc[i * 12 + 5+ind]['low'],
                                        dfi.iloc[i * 12 + 6+ind]['low'], dfi.iloc[i * 12 + 7+ind]['low'],
                                        dfi.iloc[i * 12 + 8+ind]['low'], dfi.iloc[i * 12 + 9+ind]['low'],
                                        dfi.iloc[i * 12 + 10+ind]['low'], dfi.iloc[i * 12 + 11+ind]['low']])

                i += 1
                ii+=1
            dfh = dfh.reindex(index=dfh.index[::-1])
            # print (dfh)
        else:
            print("data corrupt for : ", dfi)
        return dfh

    def getohlcv(self, index):
        pass

    def get(self, ta):
        pass

# test =Data('ONTUSDT', '1h')
#
# print(test.data)
def main():
    sym = "AAVE/USDT"
    bnc = Data().binance
    cans = bnc.fetch_ohlcv(symbol=sym, timeframe='5m')
    cans.pop()
    print(cans)

    count = 0
    for ca in cans:
        t = ca[0]
        o = ca[1]
        h = ca[2]
        l = ca[3]
        c = ca[4]
        v = ca[5]

        count = count+1
        dt = datetime.datetime.fromtimestamp(t/1000)

        print("t={} o={} h={} l={} c={} v={}".format(dt,o,h,l,c,v))





if __name__ == '__main__':
    main()