import logic
import binex
import iranex
import time
import pandas
import threading
import binbook
import asyncio

class arbit:
    def __init__(self):
        self.b = binex.binex()
        self.ir = iranex.iranex()
        self.bdata=""
        self.dataisnew = False
        self.available_usdt = float(self.ir.get_single_balance("usdt"))
        print("on nobitex available usdt : " + str(self.available_usdt))
        self.log = logic.logic()
        self.res1 = ""
        self.res2 = ""
        self.res1t = 0
        self.res2t = 0
        self.dic = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "f": 0, "g": 0, "h": 0, "i": 0, "j": 0}
        self.bindata = binbook.binbook()

        # y = threading.Thread(target=asyncio.get_event_loop().run_until_complete(self.bindata.orders_data()), args=())
        # y.start()

    def runc(self):
        # check for converg.
        while True:
            time.sleep(8)
            bals = self.ir.get_all_balance()
            for key, value in bals.items():
                symb = key + "usdt"
                if float(value) != 0.0 and symb != "rlsusdt" and symb != "usdtusdt":
                    if self.log.check_for_convergence(symb):
                        print("convergence happened !!")
                        # if converg. close both positions
                        order_id2 = self.ir.order_set("sell", "market", symb, "usdt", str(value), "0")
                        self.b.close_position(symb, "buy", value)
    def updatebinancedata(self): # deprecated
        # print("hi")
        self.bindata.startit()
        # while True:
        #     self.bdata = self.b.get_last_prices()
        #     time.sleep(1)
    def run(self):
        # time.sleep(4)
        while True:
            # a=self.wtime("start")
            # print("run strated ...")
            # if self.bdata !="" and self.dataisnew:    this is also deprecated we check repeatedly ....
            # self.dataisnew = False
            # find opportunity
            # result_df = self.log.find2(self.res2)
            result_df = self.log.find(self.res2, self.bindata.bbook)
            if len(result_df)>0 and self.available_usdt > 11:
                print("-------------------------------------------------------------------------")
                print(self.res2)
                print(result_df)
                # print(self.bindata.bbook)

                for index, row in result_df.iterrows():
                    sym = row['symbol']
                    price = row['price']
                    symAmount = row['totalvol']
                    usdtAmount = row['usdtvol']
                    actionAmount = self.available_usdt / price

                    # place limit order on ir exchange
                    order_id = self.ir.order_set("buy", "limit", sym[0:-4], "usdt", str(actionAmount), price) # price is in Rials
                    print("nobitex buy filled id : " + str(order_id))
                    # sleep for 0.1 sec
                    time.sleep(3)

                    # check order quantity fulfilled
                    matchedAmount = float(self.ir.order_status(str(order_id)))  # returns: matchedAmount: 0 averagePrice: 0
                    print("matched Amount : " + str(matchedAmount))

                    # cancel order anyway
                    self.ir.close_orders("limit", sym[0:-4], "usdt")  # returns: {'status': 'ok'}



                    # frequency = 2500  # Set Frequency To 2500 Hertz
                    # duration = 1000  # Set Duration To 1000 ms == 1 second
                    # winsound.Beep(frequency, duration)
                    if float(matchedAmount) > 0.0:
                        #create binance short order
                        self.b.set_leverage(10,sym)
                        self.b.order_market(sym,"sell",matchedAmount)
                        self.updateAvailableUsdtAmount()
            # finally
            # print("-----------------------------------------------------") dont print anything ...
            # b = self.wtime("finish")
            # print(str(b-a))
            time.sleep(0.001)

    def results(self, res, stime, name):
        self.res1 = self.res2
        self.res1t = self.res2t
        self.res2 = res
        self.res2t = stime

        # compare for diff
        if self.res1 != self.res2:
            # self.dataisnew  =True
            self.dic[name] += 1
            print(name + " diff from : " + str(self.res1t) + " to " + str(stime) + " diff: " + str(
                self.res2t - self.res1t))

    def updateAvailableUsdtAmount(self):
        self.available_usdt = float(self.ir.get_single_balance("usdt"))
        print("New Balance : " + str(self.available_usdt))
        time.sleep(12)
    def test(self, name, befrest):
        data = ""
        # print("hi")
        while True:
            st = self.wtime(name + " :start")
            # stt = float(str(st)[-3:])
            # self.URL = self.nobitexURL
            # r = requests.get(url=self.URL)  # , params=PARAMS)
            # etime = self.wtime("result received")
            data = self.ir.getallbooks("nobitex")
            # print(data)


            self.results(data, st, name)
            self.wtime(name + " :finish")
            time.sleep(0.005)

        # print(str(etime - stime) + " travel")

        # return data

    def wtime(self, strr):
        # print(str(round(time.time() * 1000)) + " " + strr)
        return round(time.time() * 1000)


test = arbit()
# test.test("a")

a = threading.Thread(target=test.test, args=("a", 100))
a.start()
time.sleep(0.01)

b = threading.Thread(target=test.test, args=("b", 200))
b.start()
time.sleep(0.01)

c = threading.Thread(target=test.test, args=("c", 300))
c.start()
#
time.sleep(0.01)
d = threading.Thread(target=test.test, args=("d", 400))
d.start()

time.sleep(0.01)
e = threading.Thread(target=test.test, args=("e", 500))
e.start()
time.sleep(0.01)

f = threading.Thread(target=test.test, args=("f", 600))
f.start()
time.sleep(0.01)

g = threading.Thread(target=test.test, args=("g", 700))
g.start()

time.sleep(0.01)
h = threading.Thread(target=test.test, args=("h", 800))
h.start()

time.sleep(0.01)
i = threading.Thread(target=test.test, args=("i", 900))
i.start()

time.sleep(0.01)
j = threading.Thread(target=test.test, args=("j", 0))
j.start()




z = threading.Thread(target = test.run,args=())
z.start()

x = threading.Thread(target = test.updateAvailableUsdtAmount(),args =() )
x.start()
y = threading.Thread(target = test.updatebinancedata(),args=())
y.start()


a.join()
b.join()
c.join()
d.join()
e.join()
f.join()
g.join()
h.join()
i.join()
j.join()

print(test.dic)

# ar = arbit()
# ar.run()
# ar.runc()
# print(ar.b.get_avail_balance())