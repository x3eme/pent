

class Order:

    def __init__(self, symbol, amount, side, orderId, clientOrderId, price):
        self.symbol = symbol
        self.amount = amount
        self.side = side
        self.orderId = orderId
        self.clientOrderId = clientOrderId
        self.price = price


    def __str__(self):
        return self.symbol + " amt:" + str(self.amount) + " @" + str(self.price) + " side:" + self.side






