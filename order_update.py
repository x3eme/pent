from datetime import time

import ccxt


class Order_Update:

    def __init__(self):

        with open('conf.txt', 'r') as file:
            data = file.read().split('\n')
            self.dbuser = data[0]
            self.dbpass = data[1]
            self.dbhost = data[2]
            self.dbport = data[3]
            self.dbdb = data[4]

            self.binance_api_key = data[5]
            self.binance_api_secret = data[6]
        self.binance = ccxt.binance({
            'apiKey': self.binance_api_key,
            'secret': self.binance_api_secret,
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
                "adjustForTimeDifference": True
            }
        })
        self.open_orders = []
        self.open_positions = []


    def update_open_positions(self):
        pass

    def cleanup_orders(self):
        pass

    def update_open_orders(self):
        pass

    def cancel_exp_orders(self):
        pass

    def add_trail_stoploss(self):
        pass

    def update(self):
        pass
        #update open orders
        self.update_open_orders()

        #update open positions
        self.update_open_positions()

        #cancel exp orders
        self.cancel_exp_orders()

        #cleanup closed position orders
        self.cleanup_orders()

        #make sure all open positions have open stoploss orders
        self.add_trail_stoploss()
 





def main():
    update = Order_Update()
    while True:
        try:
            update.update()
            time.sleep(1)
        except:
            print("error in order updates...")


if __name__ == '__main__':
    main()