
import data
import hcstra
from exchange import Exchange
# import winsound
import logging



class main:
    def __init__(self):


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


    def run(self):
        self.symbol_records = self.my_data.get_symbols()
        cnt = len(self.symbol_records)
        # print(self.symbol_records)
        while True:
            # let's load all data once ??? i don't know
            totr = cnt*252
            self.strat_log.info("update data...")
            self.my_data.update()

            ii = 0
            while ii<cnt:
                ssyy = self.symbol_records[ii][0].upper()
                hcs = hcstra.Strategy(ssyy,self.my_data.get_5min_by_symbol(ssyy),self.exch, self.ord_log, self.strat_log)
                hcs.exec()
                ii+=1
            # self.data.update()
            # st = rsiStrategy.RSIStrategy(self.data.data)
            # st.exec()

m = main()
m.run()