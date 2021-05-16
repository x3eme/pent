
import data
import hcstra
from exchange import Exchange
# import winsound
import logging
import time
import traceback



class main:
    def __init__(self):
        pass
    def run(self):
        cnt = 0
        try:
            date_strftime_format = "%d-%b-%y %H:%M:%S"

            self.ord_log = logging.getLogger('order')
            strategy_handler = logging.FileHandler('orders.log')
            formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=date_strftime_format)
            strategy_handler.setFormatter(formatter)
            self.ord_log.addHandler(strategy_handler)
            self.ord_log.setLevel(logging.INFO)

            self.strat_log = logging.getLogger('strategy')
            strategy_handler = logging.FileHandler('strategy.log')
            formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=date_strftime_format)
            strategy_handler.setFormatter(formatter)
            self.strat_log.addHandler(strategy_handler)
            self.strat_log.setLevel(logging.INFO)

            self.my_data = data.Data()
            self.exch = Exchange(self.ord_log)

            self.symbol_records = self.my_data.get_symbols()
            cnt = len(self.symbol_records)
            # print(self.symbol_records)
        except Exception as e:
            print('There was an error during initialization: ' + str(e))
            traceback.print_exc()
        wait_sec = 0
        while True:
            try:
                # let's load all data once ??? i don't know
                self.strat_log.info("update data...")
                self.my_data.update()

                # check that data is not outdated
                if not self.my_data.data_is_live():
                    break

                print("------------------------------------------------")
                ii = 0
                while ii < cnt:
                    ssyy = self.symbol_records[ii][0].upper()
                    hcs = hcstra.Strategy(ssyy, self.my_data.get_5min_by_symbol(ssyy), self.exch, self.ord_log, self.strat_log)
                    hcs.exec()
                    ii += 1
                wait_sec = 0
            except Exception as e:
                print('There was an error during main loop: ' + str(e))
                traceback.print_exc()
                if wait_sec<10:
                    wait_sec += 1
                print("sleeping : ", wait_sec)
                time.sleep(wait_sec)
m = main()
m.run()