import logging
from datetime import datetime

from btposition import Btposition


class Btexchange:
    ### API

    def __init__(self):

        self.leverage = 1
        self.order_size = 10000
        self.balance = 10000
        self.stoploss = 3

        self.positions = []
        self.closed_positions = []
        self.totalpnl = 1

    def entry(self, symbol, side, candle, price=None):

        found = False
        # if price is not defined assume we trade at close ce
        if price == None:
            price = candle[4]

        # candle [timestamp, o,h,l,c]
        if price <= float(candle[2]) and price >= float(candle[3]):

            # find existing open position if there is any...
            for p in self.positions:
                if p.symbol == symbol:
                    found = True
                    # if same trad
                    if p.side != side:
                        self.close(symbol, "sell" if side == "buy" else "buy", candle)
                        self.entry(symbol, side, candle, price)
                    else:
                        pass
            if not found:
                # symbol, side, timestamp, positionAmt, leverage, entryPrice, unrealizedProfit = None
                pos = Btposition(symbol, side, candle[0], self.getPosAmt(), self.leverage, price)
                self.positions.append(pos)

    def close(self, symbol, side, candle, price=None):
        if price == None:
            price = candle[4]
        if price <= candle[2] and price >= candle[3]:
            for po in self.positions:
                if po.symbol == symbol and po.side == side:
                    po.closePrice = price
                    po.closet = candle[0]

                    pnlperc = round(((po.closePrice - po.entryPrice) / po.entryPrice) * 100, 2)
                    change_cap_perc = 100 + pnlperc
                    po.unrealizedProfit = pnlperc
                    self.balance = self.balance * (change_cap_perc / 100)
                    self.positions.remove(po)
                    self.closed_positions.append(po)
                    # print("----------")
                    # print(datetime.fromtimestamp(candle[0]/1000))
                    print(po)
                    print("balance: " + str(self.balance) + "(" + str(round(pnlperc, 2)) + ")")

    def update(self, candle):
        for p in self.positions:
            if p.side == "buy":
                if p.entryPrice - candle[3] >= p.entryPrice * (self.stoploss / 100):
                    self.close(symbol=p.symbol, side="buy", candle=candle,
                               price=p.entryPrice * ((100 - self.stoploss) / 100))
            if p.side == "sell":
                if candle[2] - p.entryPrice >= p.entryPrice * (self.stoploss / 100):
                    self.close(symbol=p.symbol, side="sell", candle=candle,
                               price=p.entryPrice * ((100 + self.stoploss) / 100))

    def getPosAmt(self):
        return self.balance
