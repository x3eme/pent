import datetime
import ccxt
class Util:

    def __init__(self):
        pass

    def update_ta(self, symbol, interval, t, key, value):
        pass
    def get_current_5m_ts(self) :
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        retval  = '2017-08-17T00:00:00Z'
        retval = exchange.parse8601(retval)
        return retval
    def get_5min_order(self,ts):
        a=(ts/100000)
        b= ((a % 36)/3)+1
        return b
x=Util()
# print(x.get_5min_order(1620486000000))

