import ccxt

class binex:

    def __init__(self):
        self.ex = ccxt.binance({
            'apiKey': 'PdrOQxCfl40l11UOUrlQBVweoIcuX4LBkQUUGvMl8gsTsPWsGFiSdU3oQllKJVCp',
            'secret': 'YF9rWjve77q5frFy6HRRG52oixIRET9VMV4lZXEhTrGWq2LVzuT4DM2YvcjhEsCP',
            'enableRateLimit': True,  # required https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })

    def set_leverage(self, leverage: int, symbol):
        markets = self.ex.load_markets()
        # print("set leverage to {}".format(leverage))
        try:
            sym = symbol.replace('USDT','/USDT')
            print("symb " + sym)
            market = self.ex.markets[sym]
            response = self.ex.fapiPrivatePostLeverage({
                'symbol': market['id'],  # market id
                'leverage': leverage,  # 1-255
            })
        except Exception as e:
            print("error in set leverage:")
            print("Oops!", e.__class__, "occurred.")
        finally:
            pass


    def get_last_prices(self):
        lastprices = self.ex.fetch_bids_asks()
        # print(lastprices)
        return lastprices

    def get_ask(self,pair):
        prices = self.get_last_prices()
        pair = str(pair).replace("/","").replace("USDT", "/USDT")
        return prices[pair]["ask"]

    def get_bid(self,pair):
        prices = self.get_last_prices()
        pair = str(pair).replace("/","").replace("USDT", "/USDT")
        return prices[pair]["bid"]


    def order_market(self,pair,side, amount):
        pair = str(pair).replace("/","").replace("USDT", "/USDT")
        if side == 'buy':
            print("open long {}".format(amount))
            self.ex.create_market_buy_order(pair, amount)
        if side == 'sell':
            print("open short {}".format(amount))
            self.ex.create_market_sell_order(pair, amount)

    def close_position(self,pair, side, amount):

        symbol = pair.symbol.replace("/","").replace("USDT", "/USDT")
        posAmt = abs(float(amount))
        # print(symbol + " " + str(posAmt) + " " + side)

        if side == "buy":
            self.binance.create_market_buy_order(
                symbol=symbol,
                amount=posAmt,
                params={
                    "reduceOnly": True
                }
            )
        else:
            self.binance.create_market_sell_order(
                symbol=symbol,
                amount=posAmt,
                params={
                    "reduceOnly": True
                }
            )

    def get_all_positions(self):
        open_positions = []
        balance = self.ex.fetch_balance()
        positions = balance['info']['positions']
        for p in positions:
            # print(p)
            if float(p["positionAmt"]) != 0.0:
                symbol = p["symbol"]
                position_amount = p["positionAmt"]
                entry_price = p["entryPrice"]
                side = ["positionSide"]
                open_positions.append([symbol,position_amount,entry_price])
        return open_positions

    def get_avail_balance(self):
        bal = self.ex.fetch_balance()
        return bal["info"]["availableBalance"]

    def get_total_balance(self):
        bal = self.ex.fetch_balance()
        return bal["info"]["totalWalletBalance"]


b = binex()

# print("---")
#
print(b.set_leverage(10,"BTCUSDT"))
# print(b.get_all_positions())

# print(b.get_bid("BTCUSDT"))


# st = []
#
# for i in range(10):
#     st.append(["hh",i,"bb"])
#
#
# for i in st:
#     print(i)

