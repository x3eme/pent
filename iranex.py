import requests
import json
import time
import threading

class iranex:
    def __init__(self):
        # self.pairs = {"BTCTMN", "ETHTMN", "DOGETMN","BCHTMN","LTCTMN","DASHTMN","USDTTMN","XRPTMN","XLMTMN",
        #          "EOSTMN","TRXTMN","ADATMN","BNBTMN","ATOMTMN","MATICTMN","FTMTMN","DOTTMN","SHIBTMN","FILTMN",
        #          "CAKETMN","LINKTMN","UNITMN","RUNETMN","CHZTMN","BTTCTMN","MANATMN","AXSTMN","SANDTMN",
        #          "ENJTMN","ALICETMN","EGLDTMN","AVAXTMN","NEARTMN","XTZTMN","SOLTMN"}
        self.pairs = {"BTCTMN", "ETHTMN", "NEARTMN","XTZTMN","SOLTMN"}
        self.wallexURL = "https://api.wallex.ir/v1/depth?symbol="
        self.nobitexURL = "https://api.nobitex.ir/v2/orderbook/all"
        self.nobitexKey = "1e131e81f4eb930e8022343fc540068b387bb425"
        self.res1=""
        self.res2=""
        self.res1t = 0
        self.res2t = 0
        self.dic = {"a":0,"b":0,"c":0,"d":0, "e":0, "f":0}
        pass
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

    def order_set(self, type, execution, srcCurrency, dstCurrency, amount, price):
        # type is buy or sell - execution is limit or market - dstCurrency is rls or usdt -
        r = requests.post(
            "https://api.nobitex.ir/market/orders/add",
            data=json.dumps({"type": type, "execution": execution, "srcCurrency": srcCurrency.lower(), "dstCurrency":dstCurrency, "amount": amount, "price": price}),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token ' + self.nobitexKey},
        )
        data = r.json()
        print(data)
        print(data['order']['id'])
        return(data['order']['id'])

    def order_status(self, orderid):
        r = requests.post(
            "https://api.nobitex.ir/market/orders/status",
            data=json.dumps(
                {"id": orderid}),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token ' + self.nobitexKey},
        )
        data = r.json()
        matchedAmount = data['order']['matchedAmount']
        averagePrice = data['order']['averagePrice']
        print("matchedAmount: " + matchedAmount + " averagePrice: " + averagePrice)
        return (matchedAmount)

    def close_orders(self, execution, srcCurrency, dstCurrency):
        r = requests.post(
            "https://api.nobitex.ir/market/orders/cancel-old",
            data=json.dumps(
                {"execution": execution, "srcCurrency": srcCurrency.lower(), "dstCurrency": dstCurrency}),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token ' + self.nobitexKey},
        )
        data = r.json()
        print(data)
        return (data)


    def nobitex_key(self):
        r = requests.post(
            "https://api.nobitex.ir/auth/login/",
            data=json.dumps({"username": "hamid321321hn@gmail.com", "password": "Hamid@@3333", "remember": "yes", "captcha": "api"}),
            headers={"Content-Type": "application/json"},
        )
        data = r.json()
        print(data['key'])
        return data['key']
    def get_single_balance(self, symbol):# rls,btc,eth,ltc,usdt,xrp,bch,bnb,eos,xlm,etc,trx,pmn,doge
        r = requests.post(
            "https://api.nobitex.ir/users/wallets/list",
            data=json.dumps({}),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token ' + self.nobitexKey},
        )
        data = r.json()
        dataOut = ""
        for x in data['wallets']:
            if x['currency']==symbol:
                dataOut = x['balance']
        # print(dataOut)  # rls:0,btc:0,eth:0,ltc:0,usdt:0,xrp:0,bch:0,bnb:0,eos:0,xlm:0,etc:0,trx:0,pmn:0,doge:0,
        return dataOut
    def get_all_balance(self):
        r = requests.post(
            "https://api.nobitex.ir/users/wallets/list",
            data=json.dumps({}),
            headers={'Content-Type': 'application/json', 'Authorization': 'Token '+ self.nobitexKey},
        )
        data = r.json()
        dataOut = ""
        bals={"rls":"0.0"}
        for x in data['wallets']:
            # print(x['currency'] + " : " + x['balance'])
            # dataOut += x['currency'] + ":"+x['balance'] + ","
            bals[x['currency']] = x['balance']
        # print(dataOut)
        return bals
    def results(self,res,stime, name):
        self.res1 = self.res2
        self.res1t = self.res2t
        self.res2 = res
        self.res2t = stime

        #compare for diff
        if self.res1 != self.res2:
            self.dic[name] += 1
            print(name + " diff from : " + str(self.res1t) + " to "+ str(stime) + " diff: " + str(self.res2t - self.res1t))

    def test(self, name, befrest):
        data = ""
        for x in range(400000):
            st = self.wtime(name + " :start")
            stt = float(str(st)[-3:])
            if(stt>befrest and stt<befrest+25):
                self.URL = self.nobitexURL
                r = requests.get(url=self.URL)  # , params=PARAMS)
                # etime = self.wtime("result received")
                data = r.json()
                # print(data)
                self.results(data,st,name)
                self.wtime(name +" :finish")
            time.sleep(0.005)

        # print(str(etime - stime) + " travel")

        return data

    def wtime(self, strr):
        # print(str(round(time.time() * 1000)) + " " + strr)
        return round(time.time() * 1000)
    def test2(self):
        self.a=""
        self.at = 0.0
        self.bt = 0.0
        self.b=""
        for x in range(50):
            # print("---------")
            atime = round(time.time() * 1000)
            self.a = self.b
            self.bt = self.at
            self.b = test.test()
            btime = round(time.time() * 1000)
            ttime = (btime + atime) /2
            self.at = ttime

            print ("tt : " + str(btime-atime))

            sleeptime = 1100 - ttime

            if self.a!=self.b:
                self.wtime("diff")
                # time.sleep(sleeptime / 1000)
                print("from : " +str(self.bt) + " to : " + str(self.at))

            else:
                # print("the same")
                pass
    def run(self,ms):
        x1 = ms
        x2 = ms+100
        for x in range(1000):
            time.sleep(0.001)
            now = int(str(self.wtime("me"))[-3:])
            if now == x1: #and now <x1+10:
                print("found")


test = iranex()
# test.test("a")
a = threading.Thread(target = test.test,args=("a",450))
a.start()
time.sleep(0.1)

b = threading.Thread(target = test.test,args=("b",475))
b.start()
time.sleep(0.1)

c = threading.Thread(target = test.test,args=("c",500))
c.start()
#
time.sleep(0.1)
d = threading.Thread(target = test.test,args=("d",525))
d.start()

#
e = threading.Thread(target = test.test,args=("e",550))
e.start()
time.sleep(0.1)

f = threading.Thread(target = test.test,args=("f",575))
f.start()
time.sleep(0.1)

a.join()
b.join()
c.join()
d.join()
e.join()
f.join()

print(test.dic)


#

#
# g = threading.Thread(target = test.test,args=("g",9))
# g.start()

# time.sleep(0.1)
# h = threading.Thread(target = test.test,args=("h",0))
# h.start()
# ------------------------- Hello , these are sample methods we have got here and how they work along with th results ...

# test.nobitex_key() # this gives the Authorization key required for all actions
# test.get_single_balance("rls") #get single symbol balance # 0
# test.get_all_balance() #get all pair balances # rls:0,btc:0,eth:0,ltc:0,usdt:0,xrp:0,bch:0,bnb:0,eos:0,xlm:0,etc:0,trx:0,pmn:0,doge:0,
# test.order_set("buy", "limit", "doge", "rls", "10000", "380") # price is in Rials
# test.order_status("636173386") #returns: matchedAmount: 0 averagePrice: 0
# test.close_orders("limit","doge","rls") #returns: {'status': 'ok'}
