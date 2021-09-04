import websockets
import json
import os
import sys
import csv
import psycopg2
import time
import asyncio
import datetime
import threading
import numpy as np
import ccxt  # noqa: E402

# async def save_candle(self,t,T,s,i,f,L,o,c,h,l,v,n,x,q,V,Q,B):
class kline:
    def __init__(self):
        self.dc = True
        print("init kline obj")
        with open('conf.txt', 'r') as file:
            data = file.read().split('\n')
            cn1 = data[0]
            cn2 = data[1]
            cn3 = data[2]
            cn4 = data[3]
            cn5 = data[4]
            self.connection = psycopg2.connect(user=cn1,
                                          password=cn2,
                                          host=cn3,
                                          port=cn4,
                                          database=cn5)
        try:
            cursor = self.connection.cursor()
            postgreSQL_select_Query = "select * from symbols"
            cursor.execute(postgreSQL_select_Query)
            self.symbol_records = cursor.fetchall()

            # print("Print each row and it's columns values")
            for row in self.symbol_records:
                if (row[1]=="btcusdt"):
                    self.first_pair = ''+row[1]+'@kline_5m'  # first pair
                    self.pairs = '{"method": "SUBSCRIBE", "params": ['
                else:
                    self.pairs = self.pairs + '"'+row[1]+'@kline_5m",'
                # print("Id = ", row[0], )
                # print("Model = ", row[1])
                # print("Price  = ", row[2], "\n")
            print("pairs loaded!")
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

        finally:
            # closing database connection.
            if (self.connection):
                pass
                # cursor.close()
                # self.connection.close()
                # print("pairs loaded")
        self.pairs = self.pairs[:-1]
        self.pairs = self.pairs+'],  "id": 1}'
        # print(self.first_pair)
        # print(self.pairs)

        self.url = "wss://fstream.binance.com/ws/"  # steam address

    def retry_fetch_ohlcv(self,exchange, max_retries, symbol, timeframe, since, limit):
        num_retries = 0
        try:
            num_retries += 1
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            # print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
            return ohlcv
        except Exception:
            if num_retries > max_retries:
                raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')
    def scrape_ohlcv(self,exchange, max_retries, symbol, timeframe, since, limit):
        earliest_timestamp = exchange.milliseconds()
        timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        all_ohlcv = []
        while True:
            fetch_since = earliest_timestamp - timedelta
            ohlcv = self.retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit)
            # if we have reached the beginning of history
            if ohlcv[0][0] >= earliest_timestamp:
                break
            earliest_timestamp = ohlcv[0][0]
            all_ohlcv = ohlcv + all_ohlcv
            # print(len(all_ohlcv), 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to', exchange.iso8601(all_ohlcv[-1][0]))
            # if we have reached the checkpoint
            if fetch_since < since:
                break
        return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)
    def write_to_csv(self,filename, data):
        with open(filename, mode='w') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data)
    def getcon(self):
        with open('conf.txt', 'r') as file:
            data = file.read().split('\n')
        return data
    def log(self,text):
        with open("log.txt", "a") as myfile:
            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            # print("date and time =", dt_string)
            myfile.write(dt_string + ":" + text + "\r\n")
    def write_to_sql(self,data, since, symbol, timeFrame):
        # print ("updating 1 candle ...")
        try:


            cursor = self.connection.cursor()

            # Update single record now
            sql_update_query = """Update \"""" + "klines" + """\" set "i4"=%s,"o7" = %s,"h9" = %s,"l10" = %s,"c8" = %s,"v11" = %s where "t1" = %s and "s3"=%s"""
            cursor.execute(sql_update_query,
                           ("5m", data[0][1], data[0][2], data[0][3], data[0][4], data[0][5], data[0][0], symbol))
            self.connection.commit()
            count = cursor.rowcount
            # print(symbol,": ",timeFrame,": ",count, "Record at timeStamp: ",since," updated successfully  into : ",data[0][1],"  ", data[0][2],"  ", data[0][3],"  ", data[0][4],"  ", data[0][5])
            # log(symbol+": "+timeFrame+": ")

        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)
            self.log("Error in update operation")

        # finally:
        # closing database connection.
        # if (connection):
        # cursor.close()
        # connection.close()
        # print("PostgreSQL connection is closed")

        # -------------------------end of update
        data.pop(0)
        if len(data) > 0:
            try:
                cursor = self.connection.cursor()
                sql_insert_query = """ INSERT INTO \"""" + "klines" + """\" ("t1","o7","h9","l10","c8","v11","s3")
                    VALUES(%s,%s,%s,%s,%s,%s,%s)"""

                # executemany() to insert multiple rows rows
                data = [x + [symbol] for x in data]
                result = cursor.executemany(sql_insert_query, data)
                self.connection.commit()
                # print("----------------------------------------------------------------------")
                # print(symbol,": ",timeFrame,": ",len(data), "Record inserted successfully into \""+timeFrame+"\" table")
                # print("----------------------------------------------------------------------")
            except (Exception, psycopg2.Error) as error:
                print("Failed inserting record into \"" + timeFrame + "\" table {}".format(error))
                self.log("Failed inserting record ")

            # finally:
            # closing database connection.
            # if (connection):
            # cursor.close()
            # connection.close()
            # print("PostgreSQL connection is closed")
    def scrape_candles_to_csv(self,filename, exchange_id, max_retries, symbol, timeframe, since, limit):
        # instantiate the exchange by id
        exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,  # required by the Manual
        })
        # convert since from string to milliseconds integer if needed
        if isinstance(since, str):
            since = exchange.parse8601(since)
        # preload all markets from the exchange
        exchange.load_markets()
        # fetch all candles
        ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
        # save them to csv file
        # self.write_to_csv(filename, ohlcv)
        self.write_to_sql(ohlcv)

        # print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)
    def update_min_5(self,exchange_id, max_retries, symbol, timeframe, since, limit):
        # instantiate the exchange by id

        # exchange = getattr(ccxt, exchange_id)({
        #    'enableRateLimit': True,  # required by the Manual
        #    'options': {
        #        'defaultType': 'future',  # ←-------------- quotes and 'future'
        #    },
        # })
        # exchange.options['defaultType'] = 'usdt-margined'
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        # convert since from string to milliseconds integer if needed
        if isinstance(since, str):
            since = exchange.parse8601(since)
        # preload all markets from the exchange
        exchange.load_markets()
        # fetch all candles
        symbol2 = symbol.replace("USDT", "/USDT")
        ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol2, timeframe, since, limit)
        # save them to postgresql database
        self.write_to_sql(ohlcv, since, symbol, timeframe)

        # print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', 'Postgresql')
    def check_and_update(self,symbol):
        # while True:
        symbol = symbol.upper()
        timeFrame = '5m'
        # print("sleeping 5 seconds ...")
        # await asyncio.sleep(2)
        tbl = 'klines'
        symbol2 = symbol.replace("USDT", "/USDT")
        try:
            cursor = self.connection.cursor()
            qq = """select * from \"""" + tbl + """\" where "s3"=%s order by "t1" desc"""
            postgreSQL_select_Query = qq
            cursor.execute(postgreSQL_select_Query, (symbol,))

            # print("Selecting rows from mobile table using cursor.fetchall")
            records = cursor.fetchall()
            if len(records) > 0:

                last_ts = records[0][1]
            else:
                last_ts = 0
            # print("last candle is : ",last_ts)
            self.update_min_5('binance', 3, symbol, timeFrame, last_ts, 100)






        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            data = "Error while fetching data from PostgreSQL" + error
            self.log("Error while fetching data from PostgreSQL")

        # finally:
        # closing database connection.
        # if (connection):
        # cursor.close()
        # connection.close()
        # print("PostgreSQL connection is closed")
    # scrape_candles_to_csv('hamid_1.csv', 'binance', 3, 'BTC/USDT', '15m', '2020-09-29T00:00:00Z', 100)
    # update_min_5('binance', 3, 'BTC/USDT', '5m', '2020-09-29T00:00:00Z', 100)
    def checkall(self):
        print("check all started...")
        strrr = '9'
        print("waiting for a suitable update time ...")
        while strrr == '9' or strrr == '8' or strrr == '7' or strrr == '4' or strrr == '3' or strrr == '2':
            # print ("waiting for a suitable update time ...")
            now = datetime.datetime.now()
            if len(str(now.minute)) == 1:
                strr = '0' + str(now.minute)
            else:
                strr = str(now.minute)
            strrr = strr[1:]
            time.sleep(1)
        print("it's a suitable time!")

        try:
            cursor = self.connection.cursor()
            postgreSQL_select_Query = "select sname from symbols order by id"
            cursor.execute(postgreSQL_select_Query)
            symbol_records = cursor.fetchall()

            # print(len(symbol_records))
            # for row in symbol_records:
            i = 0
            while i < len(symbol_records):
                try:
                    t1 = threading.Thread(target=self.check_and_update, args=(symbol_records[i][0],))
                except:
                    pass
                try:
                    t2 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 1][0],))
                except:
                    pass
                try:
                    t3 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 2][0],))
                except:
                    pass
                try:
                    t4 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 3][0],))
                except:
                    pass
                try:
                    t5 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 4][0],))
                except:
                    pass
                try:
                    t6 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 5][0],))
                except:
                    pass
                try:
                    t7 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 6][0],))
                except:
                    pass
                try:
                    t8 = threading.Thread(target=self.check_and_update, args=(symbol_records[i + 7][0],))
                except:
                    pass
                try:
                    t1.start()
                    t2.start()
                    t3.start()
                    t4.start()
                    t5.start()
                    t6.start()
                    t7.start()
                    t8.start()
                    t1.join()
                    t2.join()
                    t3.join()
                    t4.join()
                    t5.join()
                    t6.join()
                    t7.join()
                    t8.join()
                except:
                    pass
                i = i + 8
            print("check all finished...")
            # for row in symbol_records:
            #
            #     check_and_update(row[1].upper())
        except (Exception, psycopg2.Error) as error:
            print("Error in check all : ", error)





    def convertBT(self,bt):
        start = datetime.datetime.fromtimestamp(bt/1000.0)
        # thisis = start+bt
        return start
    def save_candle(self,t,T,s,i,f,L,o,c,h,l,v,n,x,q,V,Q,B):
        # print(t)

        try:
            cursor = self.connection.cursor()
            sql_insert_query = """ INSERT INTO \"""" + "klines" + """\" ("t1","t2","s3","i4","f5","l6","o7","c8","h9",
                                        "l10","v11","n12","x13","q14","v15","q16","b17")
                                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                        ON CONFLICT ("t1","s3","i4") DO UPDATE SET
                                        ("f5","l6","o7","c8","h9","l10","v11","n12","x13","q14","v15","q16") = 
                                        (EXCLUDED.f5,EXCLUDED.l6,EXCLUDED.o7,EXCLUDED.c8,EXCLUDED.h9,EXCLUDED.l10,
                                        EXCLUDED.v11,EXCLUDED.n12,EXCLUDED.x13,EXCLUDED.q14,EXCLUDED.v15,
                                        EXCLUDED.q16)"""

            cursor.execute(sql_insert_query, (t,T,s,i,f,L,o,c,h,l,v,n,x,q,V,Q,B))
            self.connection.commit()
            # print("successfull insert : ",t,"----",T,":::",s,":::",c,"===")
            # print("data updated")
            # print(self.convertBT(t))
        except psycopg2.Error as e:
            print("Unable to connect!")
            print(e.pgerror)
            print(e.diag.message_detail)

    async def candle_stick_data(self):
        # url = "wss://stream.binance.com:9443/ws/" #steam address
        # futures

        # if not websockets.open:
        #     print('Websocket NOT connected. Trying to reconnect.')
        #     sock = await websockets.connect(self.url+self.first_pair)
        #     msg = json.dumps({"event": "pusher:subscribe", "data": {"channel": "order_book"}})
        #     await sock.send(msg)
        # self.checkall()
        sock = await websockets.connect(self.url+self.first_pair)

        await sock.send(self.pairs)
        # print(f"> {self.pairs}")
        while True:
            try:
                resp = await sock.recv()
            except:
                while not sock.open:
                    try:
                        print('Reconnecting...')
                        self.dc=True
                        time.sleep(1)

                        sock = await websockets.connect(self.url+self.first_pair)
                        await sock.send(self.pairs)
                    except:
                        pass
            js = json.loads(resp)
            if "None" not in resp:
                # print(js)
                # save_candle(js)
                try:
                    self.save_candle(js['k']['t'],js['k']['T'],js['k']['s'],js['k']['i'],js['k']['f'],js['k']['L'],js['k']['o'],js['k']['c'],js['k']['h'],js['k']['l'],js['k']['v'],js['k']['n'],js['k']['x'],js['k']['q'],js['k']['v'],js['k']['Q'],js['k']['B'])
                except Exception  as e :
                    print("error"+ str(e))

k= kline()
asyncio.get_event_loop().run_until_complete(k.candle_stick_data())