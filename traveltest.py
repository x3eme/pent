import requests
import json
import time
import threading

class traveltest:
    def __init__(self):
        # self.pairs = {"BTCTMN", "ETHTMN", "DOGETMN","BCHTMN","LTCTMN","DASHTMN","USDTTMN","XRPTMN","XLMTMN",
        #          "EOSTMN","TRXTMN","ADATMN","BNBTMN","ATOMTMN","MATICTMN","FTMTMN","DOTTMN","SHIBTMN","FILTMN",
        #          "CAKETMN","LINKTMN","UNITMN","RUNETMN","CHZTMN","BTTCTMN","MANATMN","AXSTMN","SANDTMN",
        #          "ENJTMN","ALICETMN","EGLDTMN","AVAXTMN","NEARTMN","XTZTMN","SOLTMN"}
        self.pairs = {"BTCTMN", "ETHTMN", "NEARTMN","XTZTMN","SOLTMN"}
        self.wallexURL = "https://api.wallex.ir/v1/depth?symbol="
        self.nobitexURL = "https://api.nobitex.ir/v2/orderbook/all"
        self.nobitexKey = "1e131e81f4eb930e8022343fc540068b387bb425"

    def getbook(self,exchange, pair):
        if exchange == "nobitex":
            self.URL = self.nobitexURL
        if exchange == "wallex":
            pair = pair
            self.URL = self.wallexURL + pair
        r = requests.get(url=self.URL)  # , params=PARAMS)
        data = r.json()
        # print(data['BTCIRT']['lastUpdate'])
        return data

    def getallbooks(self, exchange):
        if exchange == "nobitex":
            return self.getbook("nobitex", "all")
        # if exchange == "wallex":
        #     for p in self.pairs:
        #         self.getbook("wallex", p)

    def test(self):
        data = ""
        for x in range(400):
            stime = self.wtime("start")

            # self.URL = self.nobitexURL
            # r = requests.get(url=self.URL)  # , params=PARAMS)
            # etime = self.wtime("result received")
            data = self.getallbooks("nobitex")
            # print(data)
            # self.results(data, st, name)
            etime = self.wtime("finish")
            # time.sleep(0.005)

            print("start: " + str(stime) + "finish: " + str(etime)  + " travel:"+ str(etime - stime))
    def wtime(self, strr):
        # print(str(round(time.time() * 1000)) + " " + strr)
        return round(time.time() * 1000)
test = traveltest()
test.test()

#

#

# ------------------------- Hello , these are sample methods we have got here and how they work along with th results ...

# test.nobitex_key() # this gives the Authorization key required for all actions
# test.get_single_balance("rls") #get single symbol balance # 0
# test.get_all_balance() #get all pair balances # rls:0,btc:0,eth:0,ltc:0,usdt:0,xrp:0,bch:0,bnb:0,eos:0,xlm:0,etc:0,trx:0,pmn:0,doge:0,
# test.order_set("buy", "limit", "doge", "rls", "10000", "380") # price is in Rials
# test.order_status("636173386") #returns: matchedAmount: 0 averagePrice: 0
# test.close_orders("limit","doge","rls") #returns: {'status': 'ok'}
