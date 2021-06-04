import plotly
import plotly.graph_objects as go
from btposition import Btposition
import os
from datetime import date
import numpy as np


class Plot:

    def __init__(self):
        if not os.path.exists('backtest'):
            os.makedirs('backtest')

    def plot(self, positions: Btposition):

        # return self.timestamp + "," + \
        #     self.symbol + "," + \
        #     self.side + "," + \
        #     str(self.entryPrice) + "," + \
        #     str(self.closePrice) + "," + \
        #     str(self.unrealizedProfit)
        #
        # np.random.seed(1)
        #
        # N = 100
        # random_x = np.linspace(0, 1, N)
        # random_y0 = np.random.randn(N) + 5
        # random_y1 = np.random.randn(N)
        # random_y2 = np.random.randn(N) - 5
        timestamp = []
        balance = []
        currBalance = 100

        for pos in positions:
            timestamp.append(pos.timestamp)

            currBalance = float(currBalance * ((100 + pos.unrealizedProfit) / 100))
            balance.append(currBalance)

        fig = go.Figure()
        # Create and style traces
        fig.add_trace(go.Scatter(x=timestamp, y=balance, name='Balance',
                                 line=dict(color='royalblue', width=4)))

        # Edit the layout
        fig.update_layout(title='Balance',
                          xaxis_title='Time',
                          yaxis_title='Balance')

        fig.show()

        # fig.show()
        plotly.offline.plot(fig, filename='{}-{}.html'.format(), auto_open=False)


def main():
    today = date.today()
    print("Today " + str(today))
    p = Plot()
    p.plot()


if __name__ == '__main__':
    main()
