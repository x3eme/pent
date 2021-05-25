import plotly.graph_objects as go
from btposition import Btposition
import os
from datetime import date



class Plot:

    def __init__(self):
        if not os.path.exists('backtest'):
            os.makedirs('backtest')




    def plot(positions: Btposition, starttime, endtime):

        # return self.timestamp + "," + \
        #     self.symbol + "," + \
        #     self.side + "," + \
        #     str(self.entryPrice) + "," + \
        #     str(self.closePrice) + "," + \
        #     str(self.unrealizedProfit)
        #
        pass



def main():
    today = date.today()
    print("Today " + str(today))


if __name__ == '__main__':
    main()