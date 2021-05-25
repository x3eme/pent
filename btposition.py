from datetime import datetime


class Btposition:


    def __init__(self, symbol, side, timestamp, positionAmt, leverage, entryPrice, closePrice=None, unrealizedProfit=None, opent=None,closet=None):

        self.symbol = symbol
        self.side = side
        self.timestamp = timestamp
        self.positionAmt = positionAmt
        self.leverage = leverage
        self.entryPrice = entryPrice
        self.closePrice = closePrice
        self.opent = opent
        self.closet = closet
        self.unrealizedProfit = unrealizedProfit


    def get_side(self):
        return self.side


    def __str__(self):
        return str(datetime.fromtimestamp(self.timestamp/1000)) + "," + \
               self.symbol + "," + \
               self.side + "," + \
               str(self.entryPrice) + "," + \
               str(self.closePrice)







