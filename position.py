

class Position:


    def __init__(self, symbol, side, positionAmt, leverage, entryPrice, unrealizedProfit=None, positionInitialMargin=None, openOrderInitialMargin=None):

        self.symbol = symbol
        self.positionAmt = positionAmt
        self.leverage = leverage
        self.entryPrice = entryPrice
        self.unrealizedProfit = unrealizedProfit
        self.positionInitialMargin = positionInitialMargin
        self.openOrderInitialMargin = openOrderInitialMargin
        self.side = side


    def get_side(self):
        return self.side


    def __str__(self):
        return self.symbol + " " + self.positionAmt






