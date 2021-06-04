import plotly
import plotly.graph_objects as go
from btposition import Btposition
import os
from datetime import date, datetime
import numpy as np
import matplotlib, random


class Plot:

    def __init__(self):
        if not os.path.exists('backtest'):
            os.makedirs('backtest')
        self.fig = go.Figure()



    def export(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H::%M::%S")
        plotly.offline.plot(self.fig, filename='backtest\{}.html'.format(dt_string), auto_open=False)



    def plot(self, positions: Btposition, symbol, start_date):

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
            ts = datetime.fromtimestamp(pos.timestamp/1000)
            print(ts.strftime('%Y-%m-%d %H:%M:%S'))
            timestamp.append(ts)
            currBalance = float(currBalance * ((100 + pos.unrealizedProfit) / 100))
            balance.append(currBalance)

        # Create and style traces
        self.fig.add_trace(go.Scatter(x=timestamp, y=balance, name=symbol,
                                 line=dict(color=self.random_color(), width=4)))

        # Edit the layout
        self.fig.update_layout(title='Balance',
                          xaxis_title='Time',
                          yaxis_title='Balance')

        # fig.show()

    def random_color(self):

        hex_colors_dic = {}
        rgb_colors_dic = {}
        hex_colors_only = []
        for name, hex in matplotlib.colors.cnames.items():
            hex_colors_only.append(hex)
            hex_colors_dic[name] = hex
            rgb_colors_dic[name] = matplotlib.colors.to_rgb(hex)

        return random.choice(hex_colors_only)



def main():
    today = date.today()
    print("Today " + str(today))
    p = Plot()
    p.plot()


if __name__ == '__main__':
    main()
