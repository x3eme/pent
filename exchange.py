

import ccxt
import logging
import psycopg2
from position import Position
from order import Order
import time
import datetime


def same_symbol(symbol_a, symbol_b):
    symbol1 = symbol_a.replace("/", "").replace("USDT", "/USDT")
    symbol2 = symbol_a.replace("/", "")
    return True if symbol1 == symbol_b or symbol2 == symbol_b else False

class Exchange:
    ### API


    def __init__(self, logger=None):
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

        # self.log = logger
        self.leverage = 10
        self.order_size = 4
        self.allowed_balance = 200
        self.stop_loss_perc = 1


        self.open_positions = []
        self.pair_balance = []
        self.update_open_positions()
        # self.set_leverage(self.leverage)

    def get_avail_balance(self, symbol):
        pass

    def update_open_positions(self):
        balance = self.getBalance()
        positions = balance["info"]["positions"]

        self.open_positions.clear()

        for pos in positions:
            positionAmt = float(pos["positionAmt"])
            if positionAmt != 0:
                symbol = pos["symbol"]   #BTCUSDT
                positionAmt = float(pos["positionAmt"])
                leverage = float(pos["leverage"])
                entryPrice = float(pos["entryPrice"])
                unrealizedProfit = float(pos["unrealizedProfit"])
                positionInitialMargin = float(pos["positionInitialMargin"])
                openOrderInitialMargin = float(pos["openOrderInitialMargin"])

                # symbol,
                # positionAmt,
                # leverage,
                # entryPrice,
                # unrealizedProfit=None,
                # positionInitialMargin=None,
                # openOrderInitialMargin=None):

                p = Position(
                    symbol=symbol,
                    side="buy" if positionAmt>0 else "sell",
                    positionAmt=positionAmt,
                    leverage=leverage,
                    entryPrice=entryPrice,
                    unrealizedProfit=unrealizedProfit,
                    positionInitialMargin=positionInitialMargin,
                    openOrderInitialMargin=openOrderInitialMargin,
                )

                self.open_positions.append(p)

    def set_all_leverage(self, leverage: int):
        markets = self.binance.load_markets()
        try:
            conn = self.connection
            cursor = conn.cursor()
            postgreSQL_select_Query = "SELECT sname FROM symbols"
            cursor.execute(postgreSQL_select_Query)
            kline_records = cursor.fetchall()
            for sym in kline_records:
                symbol = str.upper(sym[0]).replace('USDT','/USDT')
                print("symb " + symbol)
                market = self.binance.markets[symbol]
                response = self.binance.fapiPrivatePostLeverage({
                    'symbol': market['id'],  # market id
                    'leverage': leverage,  # 1-255
                })
                print(response)
        except Exception as e:
            print("error in set leverage:")
            print("Oops!", e.__class__, "occurred.")
            print(e.message)
        finally:
            pass

    def set_leverage(self, leverage: int, symbol):
        markets = self.binance.load_markets()
        print("set leverage to {}".format(leverage))
        try:
            sym = symbol.replace('USDT','/USDT')
            print("symb " + sym)
            market = self.binance.markets[sym]
            response = self.binance.fapiPrivatePostLeverage({
                'symbol': market['id'],  # market id
                'leverage': leverage,  # 1-255
            })
        except Exception as e:
            print("error in set leverage:")
            print("Oops!", e.__class__, "occurred.")
            print(e.message)
        finally:
            pass

    def get_last_price(self, symbol):
        symbol = symbol.replace('/','')
        try:
            self.connection = psycopg2.connect(user=self.dbuser,
                                               password=self.dbpass,
                                               host=self.dbhost,
                                               port=self.dbport,
                                               database=self.dbdb)
            conn = self.connection
            cursor = conn.cursor()
            postgreSQL_select_Query = "SELECT c8 as Close FROM klines WHERE s3 = '{}' order by t1 desc LIMIT 1 ".format(
                symbol)
            cursor.execute(postgreSQL_select_Query)
            kline_records = cursor.fetchall()
            return kline_records[0][0]
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        finally:
            pass

    def getBalance(self):
        balance = self.binance.fetch_balance()
        return balance

    def getFreeBalance(self):
        balance = self.getBalance()
        free = balance["free"]["USDT"]
        return free

    def getUsedBalance(self):
        balance = self.getBalance()
        free = balance["used"]["USDT"]
        return free

    def get_open_positions(self, symbol) -> []:

        symbol = symbol.replace("/", "")
        positions = self.open_positions
        poss = []

        for pos in positions:
            if pos.symbol == symbol:
                poss.append(pos)
        return poss

    def get_open_orders(self, symbol):
        orders = self.binance.fetch_open_orders(symbol)
        ords = []
        for order in orders:
            o = Order((order['symbol']),
                      order['amount'],
                      order['side'],
                      order['id'],
                      order['clientOrderId'],
                      order['price'],
                      )
            ords.append(o)

        return ords

    def stop_loss(self, pos):
        side = "buy" if pos.side == "sell" else "sell"


        stop_price_for_short = pos.entryPrice * 1.01
        stop_price_for_long = pos.entryPrice * 0.99

        symbol = pos.symbol.replace("/","").replace("USDT", "/USDT")
        pos_amt = abs(float(pos.positionAmt))

        print("stoploss {} {} {}".format(side, pos.side, pos_amt))

        if side == "buy":
            self.binance.create_order(
                symbol=symbol,
                type='STOP_MARKET',
                side=side,
                amount=pos_amt,
                params={
                    "stopPrice": stop_price_for_short,
                    "reduceOnly" : True
                }
            )
        else:
            self.binance.create_order(
                symbol=symbol,
                type='STOP_MARKET',
                side=side,
                amount=pos_amt,
                params={
                    "stopPrice": stop_price_for_long,
                    "reduceOnly": True
                }
            )

    def open(self, symbol, side, type, spend, limit=None, stop=None):
        amount = 0
        sym = symbol.replace("USDT","/USDT")
        last_price = self.get_last_price(symbol)
        self.set_leverage(self.leverage, symbol)
        if type == 'limit':
            amount = (self.leverage*spend)/limit
        elif type == 'market':
            amount = (self.leverage*spend)/last_price

        print("to open.. {} {} {}".format(amount, type, last_price))


        pos = Position(symbol, side, amount, self.leverage, last_price)

        #limit orders
        if side == 'buy' and type == "limit":
            self.binance.create_limit_buy_order(sym, amount, limit)
        if side == 'sell' and type == "limit":
            self.binance.create_limit_sell_order(sym, amount, limit)

        #market orders
        if side == 'buy' and type == "market":
            print("open long {}".format(amount))
            self.binance.create_market_buy_order(sym, amount)
        if side == 'sell' and type == "market":
            print("open short {}".format(amount))
            self.binance.create_market_sell_order(sym, amount)

        self.update_open_positions()
        self.stop_loss(pos)

    def close(self, pos: Position):

        side = "buy" if pos.side == "sell" else "sell"

        print('closing a {} position for {}'.format(pos.side, pos.symbol.replace("/","").replace("USDT", "/USDT")))

        symbol = pos.symbol.replace("/","").replace("USDT", "/USDT")
        posAmt = abs(float(pos.positionAmt))
        # print(symbol + " " + str(posAmt) + " " + side)

        order = self.binance.fetch_open_orders(symbol)
        order_id = order[0]["info"]["orderId"]

        if side == "buy":
            self.binance.create_market_buy_order(
                symbol=symbol,
                amount=posAmt,
                params={
                    "reduceOnly": True
                }
            )
            self.binance.cancel_order(id=order_id,symbol=symbol)
        else:
            self.binance.create_market_sell_order(
                symbol=symbol,
                amount=posAmt,
                params={
                    "reduceOnly": True
                }
            )
            self.binance.cancel_order(id=order_id,symbol=symbol)

        self.update_open_positions()

    def open_long(self, symbol):
        print("----------- open long {} --------------".format(symbol))

        have_open_pos = False

        #check if we have money
        free = self.getFreeBalance()

        if free > self.allowed_balance:
            print("{} USDT available. so we are good!".format(free))
            have_money = True
        else:
            print("{} USDT. We are out of money!".format(free))
            have_money = False

        #get open orders for this symbol
        # orders = self.get_open_orders(symbol)
        # for order in orders:
        #     if order.side == "buy":
        #         print("We already have an open long order")
        #         haveOpenOrder = True

        #get open positions for this symbol
        self.update_open_positions()
        positions = self.get_open_positions(symbol)

        for pos in positions:
            if pos.side == "buy":
                print("We already have an open long {} position".format(symbol))
                have_open_pos = True
            elif pos.side == "sell":
                print("We have an open short {} {} position. to be closed first".format(symbol, pos.positionAmt))
                #close the short position
                self.close(pos)
                have_open_pos = False

        if have_money and not have_open_pos:
            print("opening a long {}".format(symbol))
            self.open(symbol, 'buy', 'market', self.order_size)

        print("-------------------------")

    def open_short(self, symbol):
        print("----------- open short {} --------------".format(symbol))

        have_open_pos = False
        have_money = False

        #check if we have money
        free = self.getFreeBalance()

        if free > self.allowed_balance:
            print("we have {} USDT available... so we are good!".format(free))
            have_money = True
        else:
            print("we have {} USDT free. We are out of money!".format(free))
            have_money = False

        #get open orders for this symbol
        # orders = self.get_open_orders(symbol)
        # for order in orders:
        #     if order.side == "buy":
        #         print("We already have an open long order")
        #         haveOpenOrder = True

        #get open positions for this symbol
        self.update_open_positions()
        positions = self.get_open_positions(symbol)

        for pos in positions:
            if pos.side == "sell":
                print("We already have an open short {} position".format(symbol))
                have_open_pos = True
            elif pos.side == "buy":
                print("We have an open long {} {} position. to be closed first.".format(symbol, pos.positionAmt))
                #close the short position
                self.close(pos)
                have_open_pos = False

        if have_money and not have_open_pos:
            print("opening a short {}".format(symbol))
            self.open(symbol, 'sell', 'market', self.order_size)

        print("-------------------------")

    def close_long(self,symbol):
        # print("----------- close long {}--------------".format(symbol))
        positions = self.get_open_positions(symbol)
        for pos in positions:
            if pos.side == "buy" and same_symbol(pos.symbol, symbol):
                self.close(pos)
            elif pos.side == "sell" and same_symbol(pos.symbol, symbol):
                print("fond a short pos for {}".format(symbol))

        # print("-------------------------")

    def close_short(self, symbol):
        # print("----------- close short {}--------------".format(symbol))
        positions = self.get_open_positions(symbol)
        for pos in positions:
            if pos.side == "sell" and same_symbol(pos.symbol, symbol):
                self.close(pos)
            elif pos.side == "buy" and same_symbol(pos.symbol, symbol):
                print("fond a long pos for {}".format(symbol))

        # print("-------------------------")


def main():
    # some initialization
    date_strftime_format = "%d-%b-%y %H:%M:%S"
    order_logger = logging.getLogger('order')
    strategy_handler = logging.FileHandler('orders.log')
    formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=date_strftime_format)
    strategy_handler.setFormatter(formatter)
    order_logger.addHandler(strategy_handler)
    order_logger.setLevel(logging.INFO)

    #
    # strategy_logger = logging.getLogger('strategy')
    # strategy_handler = logging.FileHandler('strategy.log')
    # formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=date_strftime_format)
    # strategy_handler.setFormatter(formatter)
    # strategy_logger.addHandler(strategy_handler)
    # strategy_logger.setLevel(logging.INFO)

    #
    # order_logger.info("stuffhh")
    # strategy_logger.info("str stuffhh")




    ###################################################################################
    # create the exchange
    bnc = Exchange()
    num = 1

    date_string = "08/22/2021"
    date = datetime.datetime.strptime(date_string, "%m/%d/%Y")
    timestamp = int(datetime.datetime.timestamp(date)*1000)
    print(timestamp)

    orders = bnc.binance.fetch_closed_orders(since=timestamp, symbol="ADA/USDT")
    for order in orders:
        symbol = order['symbol']
        type = "close" if order['info']['reduceOnly']==True else "open"
        side = "LONG" if order['info']['side']=="BUY" else "SHRT"

        print("{}. {} {}\t\t{}\t{}\t\t{}".format(num,symbol,type, side, order['datetime'].replace("T", " "), order))
        num=num+1


    ###################################################################################

    # (side, type, symbol, limit, stop, spend)

    # bnc.update_open_positions()

    # markets = bnc.binance.load_markets()
    #
    # symbol = "BTC/USDT"
    # market = bnc.binance.market(symbol)
    #
    # response = bnc.binance.fapiPrivatePostLeverage({
    #     'symbol': market['id'],  # market id
    #     'leverage': 2,  # 1-255
    # })
    # print(response)

    # bnc.open_long("DODOUSDT")

    # print("Check if position is still open:")
    # poss = bnc.get_open_positions("DODO/USDT")
    # for pos in poss:
    #     print(pos)
    #     print("close {}".format(pos))
    #     bnc.close(pos)

if __name__ == '__main__':
    main()




