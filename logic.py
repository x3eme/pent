import iranex
import binex
import pandas

class logic:

    def __init__(self):
        # initials
        self.b = binex.binex()
        self.ir = iranex.iranex()
        self.founds = pandas.DataFrame(columns=["symbol", "price", "totalvol", "usdtvol","shortdata"])

        # minimum Arbitrage
        self.minDiff = 0.5
        self.minconv = 0.0
        self.minDiff2 = 1



        # get current positions:
        self.opports = {}

    def checkall(self):
        ################################ GET DATA
        self.bp = b.get_last_prices()
        self.irp = ir.getallbooks("nobitex")

        ###############################

        # 1-get usdt to irt price
        # usdtp = self.irp['USDTIRT']['lastTradePrice']


        ################################ CHECK ARBITRAGE CHANCE
        for key in self.irp:
            value = self.irp[key]
            # if "IRT" in key and "USDTIRT" not in key and "DAI" not in key and "SHIB" not in key and "PMN" not in key and "SOL" not in key:
            #     bsymbol = key[0:-3]+"/USDT"
            #
            #     irprice = value['asks'][0][0]
            #     irvol = value['asks'][0][1]
            #     bprice = self.bp[bsymbol]['bid']
            #     diffpercent = 100 - (float(bprice) * float(usdtp) * 100 / float(irprice))
            #     if diffpercent > self.minDiff:
            #         print(key + " : Diff : " + str(diffpercent) + " Vol: " + str(irvol))

            if "USDT" in key and "USDTIRT" not in key and "DAI" not in key and "SHIB" not in key and "PMN" not in key and "SOL" not in key:
                bsymbol = key[0:-4]+"/USDT"
                # print(value['asks'][0][0])
                # irprice = value['lastTradePrice']
                irprice = value['asks'][0][0]
                irvol = value['asks'][0][1]
                bprice = self.bp[bsymbol]['bid']
                diffpercent = 100 - (float(bprice) * 100 / float(irprice))
                if diffpercent > self.minDiff:
                    print(key + " : Diff : " + str(diffpercent) + " Vol: " + str(irvol))


    def find(self,ldata,bdata)-> pandas.DataFrame:
        #go thru pairs
        #if a pair has min perc. record it in oppt. list
        #sort list from best to worst
        #return best oppt. pair.
        # self.data = ldata
        # print("going to find ...")
        self.shortdata = ""
        self.founds = self.founds[0:0]
        self.chances = 0
        self.worstgood = 0
        self.bp = bdata
        self.irp = ldata
        # print(self.irp)
        for key in self.irp:
            value = self.irp[key]
            if "USDT" in key and "USDTIRT" not in key and "DAI" not in key and "SHIB" not in key and "PMN" not in key and "SOL" not in key:
                bsymbol = key[0:-4]+"/USDT"
                totalAmount = 0.0
                totalUsdtAmount = 0.0

                # get binance best sell(bid) price ...
                # bprice = self.bp[bsymbol]['bid']
                ssind = int(self.bp.index[self.bp['symbol'] == key[0:-4].lower()+"usdt"].values[0])
                self.bprice = float(self.bp.loc[ssind, 'bid'])
                self.shortdata = "binance:" + str(self.bprice)
                # print(self.bprice)
                # self.bbook.at[ssind, 'bid'] = bb
                # self.bbook.at[ssind, 'ask'] = aa
                if self.bprice != 0.0:
                    # print(bdata)
                    self.shortdata += " nobitex buys: p"+str(value['asks'][0][0]) + " v:"+str(value['asks'][0][1])+" - "
                    for ask in value['bids']:
                        irprice = ask[0]
                        irvol = ask[1]

                        diffpercent = ((float(self.bprice) * 100) / float(irprice)) - 100
                        if diffpercent > self.minDiff:
                            self.shortdata += " nobitex sells: p" + str(irprice) + " v:"+str(irvol)+" - "
                            usdtAmount = (float(irvol) * float(irprice))
                            totalUsdtAmount += usdtAmount
                            totalAmount += float(irvol)
                            self.worstgood = irprice
                            print(key + ": binance : " + str(self.bprice) +" nobitex: "+ str(irprice)+" : Diff : " + str(diffpercent) + " Vol(usdt): " + str(usdtAmount))
                    if totalUsdtAmount > 11:
                        print("Accepted Arbitrage position on : " + key + " with usdt Amount of : " + str(totalUsdtAmount))
                        new_row = {'symbol': key, 'price': float(self.worstgood), 'totalvol': totalAmount, 'usdtvol': totalUsdtAmount, 'shortdata':self.shortdata}
                        # append row to the dataframe
                        self.founds = self.founds.append(new_row, ignore_index=True)
                        self.chances += 1
        # print(self.chances)
        return self.founds
    def find_converge(self,ldata,bdata,symbol):

        # self.data = ldata
        # print("going to find ...")
        # self.chances = 0
        # self.worstgood = 0
        self.new_row={}
        self.bp = bdata
        self.irp = ldata
        # # print(self.irp)
        for key in self.irp:
            value = self.irp[key]
            if key.lower() == symbol:
                print(value)
                bsymbol = key[0:-4]+"/USDT"
                totalAmount = 0.0
                totalUsdtAmount = 0.0
        #
                # get binance best sell(bid) price ...
                # bprice = self.bp[bsymbol]['bid']
                ssind = int(self.bp.index[self.bp['symbol'] == key[0:-4].lower()+"usdt"].values[0])
                self.bprice = float(self.bp.loc[ssind, 'ask'])
                # print(self.bprice)
                # self.bbook.at[ssind, 'bid'] = bb
                # self.bbook.at[ssind, 'ask'] = aa
                if self.bprice != 0.0:
                    # print(bdata)
                    for ask in value['asks']:
                        irprice = ask[0]
                        irvol = ask[1]

                        diffpercent = ((float(irprice) * 100) / float(self.bprice)) - 100
                        if diffpercent > self.minDiff:
                            usdtAmount = (float(irvol) * float(irprice))
                            totalUsdtAmount += usdtAmount
                            totalAmount += float(irvol)
                            self.worstgood = irprice
                            print(key + ": binance : " + str(self.bprice) +" nobitex: "+ str(irprice)+" : Diff : " + str(diffpercent) + " Vol(usdt): " + str(usdtAmount))
                    if totalUsdtAmount > 11:
                        print("Accepted Arbitrage position on : " + key + " with usdt Amount of : " + str(totalUsdtAmount))
                        self.new_row = {'symbol': key, 'price': float(self.worstgood), 'totalvol': totalAmount, 'usdtvol': totalUsdtAmount}
        #                 # append row to the dataframe
        #                 self.founds = self.founds.append(new_row, ignore_index=True)
        #                 self.chances += 1
        print(self.new_row)
        return self.new_row
    def find2(self,ldata)-> pandas.DataFrame:
        #go thru pairs
        #if a pair has min perc. record it in oppt. list
        #sort list from best to worst
        #return best oppt. pair.
        self.founds = self.founds[0:0]
        self.chances = 0
        self.worstgood = 0
        self.bp = self.b.get_last_prices()
        self.irp = ldata
        # print(self.irp)
        for key in self.irp:
            value = self.irp[key]
            if "USDT" in key and "USDTIRT" not in key and "DAI" not in key and "SHIB" not in key and "PMN" not in key and "SOL" not in key:
                bsymbol = key[0:-4]+"/USDT"
                totalAmount = 0.0
                totalUsdtAmount = 0.0
                irprice = value['asks'][0][0]
                bprice = self.bp[bsymbol]['bid']
                diffpercent = ((float(bprice) * 100) / float(irprice)) - 100
                if diffpercent > self.minDiff2:

                    print("bid on : " + key + ": binance : " + str(bprice) +" nobitex: "+ str(irprice)+" : Diff : " + str(diffpercent))
                    pass
                    # print("Accepted Arbitrage position on : " + key + " with usdt Amount of : " + str(totalUsdtAmount))
                    # new_row = {'symbol': key, 'price': float(self.worstgood), 'totalvol': totalAmount, 'usdtvol': totalUsdtAmount}
                    # # append row to the dataframe
                    # self.founds = self.founds.append(new_row, ignore_index=True)
                    # self.chances += 1
        # print(self.chances)
        return self.founds
    def calcminperc(self):
        #calc minimum profitable percentage diff
        #for now lets assume its 1%
        return 1

    def check_for_convergence(self, sym):
        bin_price = float(self.b.get_ask(sym))
        ir_price = float(self.irp[sym]['asks'][0])
        conv_ratio = 0.0

        if (((ir_price*100) / bin_price) -100) > conv_ratio:
            return True
        else:
            return False










# log = logic()
# log.find()




