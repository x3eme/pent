# -*- coding: utf-8 -*-

import os
import sys
import csv
import psycopg2
import time
import asyncio
import datetime

# -----------------------------------------------------------------------------

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402
cn1=""
cn2=""
cn3=""
cn4=""
cn5=""

# -----------------------------------------------------------------------------

def retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    num_retries = 0
    try:
        num_retries += 1
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        # print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
        return ohlcv
    except Exception:
        if num_retries > max_retries:
            raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')


def scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    earliest_timestamp = exchange.milliseconds()
    timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
    timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
    timedelta = limit * timeframe_duration_in_ms
    all_ohlcv = []
    while True:
        fetch_since = earliest_timestamp - timedelta
        ohlcv = retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit)
        # if we have reached the beginning of history
        if ohlcv[0][0] >= earliest_timestamp:
            break
        earliest_timestamp = ohlcv[0][0]
        all_ohlcv = ohlcv + all_ohlcv
        #print(len(all_ohlcv), 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to', exchange.iso8601(all_ohlcv[-1][0]))
        # if we have reached the checkpoint
        if fetch_since < since:
            break
    return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)


def write_to_csv(filename, data):
    with open(filename, mode='w') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(data)
def getcon():
    with open('conf.txt', 'r') as file:
        data = file.read().split('\n')
    return data
def log(text):
    with open("log.txt", "a") as myfile:
        now = datetime.datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        #print("date and time =", dt_string)
        myfile.write(dt_string+":"+text+"\r\n")
def write_to_sql(data,since,symbol,timeFrame):
    #print ("updating 1 candle ...")
    try:
        connection = psycopg2.connect(user=cn1,
                                        password=cn2,
                                        host=cn3,
                                        port=cn4,
                                        database=cn5)

        cursor = connection.cursor()


        # Update single record now
        sql_update_query = """Update \""""+timeFrame+"""\" set "open" = %s,"high" = %s,"low" = %s,"close" = %s,"vol" = %s where "timeStamp" = %s and "symbol"=%s"""
        cursor.execute(sql_update_query, (data[0][1], data[0][2], data[0][3], data[0][4], data[0][5], data[0][0],symbol))
        connection.commit()
        count = cursor.rowcount
        print(symbol,": ",timeFrame,": ",count, "Record at timeStamp: ",since," updated successfully  into : ",data[0][1],"  ", data[0][2],"  ", data[0][3],"  ", data[0][4],"  ", data[0][5])
        #log(symbol+": "+timeFrame+": ")

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        log("Error in update operation")

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")


    #-------------------------end of update
    data.pop(0)
    if len(data)>0:
        try:
            connection = psycopg2.connect(user=cn1,
                                        password=cn2,
                                        host=cn3,
                                        port=cn4,
                                        database=cn5)
            cursor = connection.cursor()
            sql_insert_query = """ INSERT INTO \""""+timeFrame+"""\" ("timeStamp","open","high","low","close","vol","symbol")
                VALUES(%s,%s,%s,%s,%s,%s,%s)"""

            # executemany() to insert multiple rows rows
            data = [x + [symbol] for x in data]
            result = cursor.executemany(sql_insert_query, data)
            connection.commit()
            print("----------------------------------------------------------------------")
            print(symbol,": ",timeFrame,": ",len(data), "Record inserted successfully into \""+timeFrame+"\" table")
            print("----------------------------------------------------------------------")
        except (Exception, psycopg2.Error) as error:
            print("Failed inserting record into \""+timeFrame+"\" table {}".format(error))
            log("Failed inserting record ")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #print("PostgreSQL connection is closed")


def scrape_candles_to_csv(filename, exchange_id, max_retries, symbol, timeframe, since, limit):
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
    ohlcv = scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
    # save them to csv file
    write_to_csv(filename, ohlcv)
    write_to_sql(ohlcv)

    #print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)


# -----------------------------------------------------------------------------
def update_min_5(exchange_id, max_retries, symbol, timeframe, since, limit):
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)({
        'enableRateLimit': True,  # required by the Manual
    })
    exchange.options['defaultType'] = 'future'
    # convert since from string to milliseconds integer if needed
    if isinstance(since, str):
        since = exchange.parse8601(since)
    # preload all markets from the exchange
    exchange.load_markets()
    # fetch all candles
    ohlcv = scrape_ohlcv(exchange, max_retries,symbol, timeframe, since, limit)
    # save them to postgresql database
    write_to_sql(ohlcv,since,symbol,timeframe)

    #print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', 'Postgresql')


# -----------------------------------------------------------------------------
async def check_and_update(symbol,timeFrame):
    while True:
        #print("sleeping 5 seconds ...")
        await asyncio.sleep(2)

        try:
            connection = psycopg2.connect(user=cn1,
                                        password=cn2,
                                        host=cn3,
                                        port=cn4,
                                        database=cn5)
            cursor = connection.cursor()
            qq = """select * from \""""+timeFrame+"""\" where "symbol"=%s order by "timeStamp" desc"""
            postgreSQL_select_Query = qq
            cursor.execute(postgreSQL_select_Query, (symbol,))

            #print("Selecting rows from mobile table using cursor.fetchall")
            records = cursor.fetchall()
            if len(records)>0:

                last_ts = records[0][1]
            else:
                last_ts = 0
            #print("last candle is : ",last_ts)
            update_min_5('binance', 3, symbol, timeFrame, last_ts, 100)






        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            data = "Error while fetching data from PostgreSQL"+error
            log("Error while fetching data from PostgreSQL")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #print("PostgreSQL connection is closed")


#scrape_candles_to_csv('hamid_1.csv', 'binance', 3, 'BTC/USDT', '15m', '2020-09-29T00:00:00Z', 100)
#update_min_5('binance', 3, 'BTC/USDT', '5m', '2020-09-29T00:00:00Z', 100)

cn1 = getcon()[0]
cn2 = getcon()[1]
cn3 = getcon()[2]
cn4 = getcon()[3]
cn5 = getcon()[4]
print("Database config data loaded!")

loop = asyncio.get_event_loop()

loop.create_task(check_and_update('BTC/USDT', '5m'))
loop.create_task(check_and_update('BTC/USDT', '15m'))
loop.create_task(check_and_update('BTC/USDT', '1h'))
loop.create_task(check_and_update('BTC/USDT', '4h'))
#loop.create_task(check_and_update('BTC/USDT', '1d'))

loop.create_task(check_and_update('ETH/USDT', '5m'))
loop.create_task(check_and_update('ETH/USDT', '15m'))
loop.create_task(check_and_update('ETH/USDT', '1h'))
loop.create_task(check_and_update('ETH/USDT', '4h'))
#loop.create_task(check_and_update('ETH/USDT', '1d'))

loop.create_task(check_and_update('DOT/USDT', '5m'))
loop.create_task(check_and_update('DOT/USDT', '15m'))
loop.create_task(check_and_update('DOT/USDT', '4h'))
loop.create_task(check_and_update('DOT/USDT', '1h'))
#loop.create_task(check_and_update('DOT/USDT', '1d'))

loop.create_task(check_and_update('LINK/USDT', '5m'))
loop.create_task(check_and_update('LINK/USDT', '15m'))
loop.create_task(check_and_update('LINK/USDT', '4h'))
loop.create_task(check_and_update('LINK/USDT', '1h'))
#loop.create_task(check_and_update('DOT/USDT', '1d'))

loop.create_task(check_and_update('ATOM/USDT', '5m'))
loop.create_task(check_and_update('ATOM/USDT', '15m'))
loop.create_task(check_and_update('ATOM/USDT', '4h'))
loop.create_task(check_and_update('ATOM/USDT', '1h'))
#loop.create_task(check_and_update('DOT/USDT', '1d'))

loop.create_task(check_and_update('OMG/USDT', '5m'))
loop.create_task(check_and_update('OMG/USDT', '15m'))
loop.create_task(check_and_update('OMG/USDT', '4h'))
loop.create_task(check_and_update('OMG/USDT', '1h'))
#loop.create_task(check_and_update('DOT/USDT', '1d'))






loop.run_forever()

