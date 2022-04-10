import logic
import binex
import iranex
import time
import pandas
class arbit:
    def __init__(self):
        self.b = binex.binex()
        self.ir = iranex.iranex()


        self.available_usdt = float(self.ir.get_single_balance("usdt"))
        print("on nobitex available usdt : " + str(self.available_usdt))

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

    def run(self):
        self.log = logic.logic()
        while True:
            # find opportunity
            result_df = self.log.find2()
            result_df = self.log.find()
            if len(result_df)>0 and self.available_usdt > 11:
                print(result_df)
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
                    time.sleep(0.1)

                    # cancel order anyway
                    print(self.ir.close_orders("limit",sym[0:-4],"usdt")) #returns: {'status': 'ok'}

                    # check order quantity fulfilled
                    matchedAmount = float(self.ir.order_status(str(order_id)))  # returns: matchedAmount: 0 averagePrice: 0
                    print("matched Amount : " + str(matchedAmount))
                    if float(matchedAmount) > 0.0:
                        #create binance short order
                        self.b.set_leverage(10,sym)
                        self.b.order_market(sym,"sell",matchedAmount)



            # finally
            print("-----------------------------------------------------")
            time.sleep(1)




ar = arbit()
ar.run()
ar.runc()
# print(ar.b.get_avail_balance())