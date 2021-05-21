

class Btposition:


    def __init__(self, symbol, side, positionAmt, leverage, entryPrice, closePrice=None, unrealizedProfit=None, opent=None,closet=None):

        self.symbol = symbol
        self.side = side
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
        return self.symbol + "," + \
               self.side + "," + \
               self.positionAmt + "," + \
               self.entryPrice + "," + \
               self.closePrice + "," + \
               self.opent + "," + \
               self.closet + "," + \
               self.unrealizedProfit






