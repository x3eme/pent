

from btposition import Btposition

class Btexchange:
    ### API

    def __init__(self):

        self.leverage = 1
        self.order_size = 1000
        self.balance = 1000
        self.stoploss = 3
        self.positions = []
        self.closed_positions = []


    def entry(self, symbol, side, candle, price=None):


        found = False
        #if price is not defined assume we trade at close price
        if price == None:
            pricd = candle[4]

        # candle [timestamp, o,h,l,c]
        if price <=  candle[2] and price >= candle[3]:

            #find existing open position if there is any...
            for p in self.positions:
                if p.symbol == symbol:
                    found = True
                    #if same trad
                    if p.side != side:
                        self.close(symbol, candle)
                        self.entry(symbol, side, candle, price)
                    else:
                        pass
            if not found:
                # symbol, side, positionAmt, leverage, entryPrice, unrealizedProfit = None
                pos =  Btposition(symbol, side, self.getPosAmt(), self.leverage, price)
                self.positions.append(pos)

    def close(self, symbol, candle, price=None):
        if price == None:
            price = candle[4]
        if price <= candle[2] and price >= candle[3]:
            for po in self.positions:
                if po.symbol == symbol:
                    po.closePrice = price
                    po.closet = candle[0]
                    po.unrealizedProfit = (po.closePrice - po.entryPrice)/po.entryPrice
                    self.balance = self.balance + po.unrealizedProfit
                    self.positions.remove(po)
                    self.closed_positions.append(po)


    def update(self, candle):
        stoploss = self.stoploss
        for p in self.positions:
            if p.side == "buy":
                if p.entryPrice - candle[3] >= p.entryPrice * (stoploss/100):
                    self.close(symbol=p.symbol, candle=candle, price=p.entryPrice * ((100-stoploss)/100))
            if p.side == "sell":
                if  candle[2] - p.entryPrice >= p.entryPrice * (stoploss/100):
                    self.close(symbol=p.symbol, candle=candle, price=p.entryPrice * ((100+stoploss)/100))


