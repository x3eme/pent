import sqlite3
import ta
from ta import utils
import pandas
import time
import data
import binance
import psycopg2
from binance import Client
from binance.enums import HistoricalKlinesType
import winsound
import datetime

class Historical:
    def __init__(self):

        # initialize parameters
        self.market_type="futures"
        self.tf = "15m" #5m-15m-1h
        self.mode = "update"#insert
        self.final_date = "04/06/2021"

        if (self.market_type == "spot"):
            self.market = HistoricalKlinesType.SPOT
            self.database = "data.db"
        else:
            self.market = HistoricalKlinesType.FUTURES
            self.database = "data-futures.db"
        if(self.tf=="5m"):
            self.interval = Client.KLINE_INTERVAL_5MINUTE
        elif(self.tf=="15m"):
            self.interval = Client.KLINE_INTERVAL_15MINUTE
        elif (self.tf == "1h"):
            self.interval = Client.KLINE_INTERVAL_1HOUR

    def add_ta(self,pair,interval):
        # check if table already exists ??????
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute(
            "SELECT * FROM " + pair + "_" + interval + "_TA")
        rows = c.fetchall()
        dfch = pandas.DataFrame(rows)
        if(len(dfch)>1):
            # donothing
            print("doing nothing about : " + pair)
            # pass
        else:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                "SELECT timespan1, CAST(open as float) as open ,CAST(high as float) as high ,CAST(low as float) as low ,CAST(close as float) as close,CAST(volume as float) as volume FROM " + pair + "_" + interval + " order by timespan1")
            rows = c.fetchall()
            df = pandas.DataFrame(rows)
            df.columns = [desc[0] for desc in c.description]
            # Clean nan values
            df = utils.dropna(df)

            # print(df.columns)

            # Add all ta features filling nans values
            df = ta.add_all_ta_features(
                df, "open", "high", "low", "close", "volume", fillna=True
            )

            # print(df.columns)
            # print(len(df.columns))
            # print(df)
            self.save_data_with_ta(df,pair,interval)

    def get_klines(self,pair):
        self.tts = 1000000000000
        if(self.mode=="insert"):
            self.tts = 1000000000000
        else:
            self.tts = self.get_last_timespan(pair)


        if(self.tts>time.mktime(datetime.datetime.strptime(self.final_date, "%d/%m/%Y").timetuple())*1000):
            pass
        else:
            try:
                # client = binance.Client()
                client = binance.Client("PdrOQxCfl40l11UOUrlQBVweoIcuX4LBkQUUGvMl8gsTsPWsGFiSdU3oQllKJVCp", "YF9rWjve77q5frFy6HRRG52oixIRET9VMV4lZXEhTrGWq2LVzuT4DM2YvcjhEsCP", {"timeout": 800})
                # for y in ["apple", "banana", "cherry"]
                klines = client.get_historical_klines(pair, self.interval, str(self.tts),"1, 1, 2022",klines_type=self.market)
                # print(klines[0][0])
                print(str(len(klines))+" candles saved!")# , " 5min candle for Jan")
                self.save_data(klines,pair)
            except Exception as e:
                print("some errors here in :" + pair + " about: "+ str(e))
    def get_last_timespan(self,pair):
        last_ts = 1000000000
        try:
            if pair == '1INCHUSDT':
                pair = 'A1INCHUSDT'

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute("SELECT timespan1, CAST(open as float) as open ,CAST(high as float) as high ,CAST(low as float) as low ,CAST(close as float) as close,volume FROM " + pair+"_"+self.tf + " order by timespan1 desc LIMIT 1")
            rows = c.fetchall()
            df = pandas.DataFrame(rows)
            df.columns = [desc[0] for desc in c.description]
            # print(df["timespan1"][0])
            last_ts = int(df["timespan1"][0])/1000
            last_dt = datetime.datetime.fromtimestamp(last_ts)
            print(last_dt)
            # now delete that last candle
            c = conn.cursor()
            c.execute("DELETE FROM " + pair+"_"+self.tf + " where timespan1="+str(last_ts*1000)+"")
            conn.commit()
        except:
            pass
        return last_ts*1000
    def save_data_with_ta(self,rows,pair,interval):
        # print(t)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        if pair=='1INCHUSDT':
            pair='A1INCHUSDT'
        # pair="DEFIUSDT"
        c.execute("CREATE TABLE IF NOT EXISTS "+pair+"_"+interval+"_TA" + """ (timespan1, open, high, low, close, volume, volume_adi,
       volume_obv, volume_cmf, volume_fi, volume_mfi, volume_em,
       volume_sma_em, volume_vpt, volume_nvi, volume_vwap,
       volatility_atr, volatility_bbm, volatility_bbh, volatility_bbl,
       volatility_bbw, volatility_bbp, volatility_bbhi,
       volatility_bbli, volatility_kcc, volatility_kch, volatility_kcl,
       volatility_kcw, volatility_kcp, volatility_kchi,
       volatility_kcli, volatility_dcl, volatility_dch, volatility_dcm,
       volatility_dcw, volatility_dcp, volatility_ui, trend_macd,
       trend_macd_signal, trend_macd_diff, trend_sma_fast,
       trend_sma_slow, trend_ema_fast, trend_ema_slow, trend_adx,
       trend_adx_pos, trend_adx_neg, trend_vortex_ind_pos,
       trend_vortex_ind_neg, trend_vortex_ind_diff, trend_trix,
       trend_mass_index, trend_cci, trend_dpo, trend_kst,
       trend_kst_sig, trend_kst_diff, trend_ichimoku_conv,
       trend_ichimoku_base, trend_ichimoku_a, trend_ichimoku_b,
       trend_visual_ichimoku_a, trend_visual_ichimoku_b, trend_aroon_up,
       trend_aroon_down, trend_aroon_ind, trend_psar_up,
       trend_psar_down, trend_psar_up_indicator,
       trend_psar_down_indicator, trend_stc, momentum_rsi,
       momentum_stoch_rsi, momentum_stoch_rsi_k, momentum_stoch_rsi_d,
       momentum_tsi, momentum_uo, momentum_stoch,
       momentum_stoch_signal, momentum_wr, momentum_ao, momentum_kama,
       momentum_roc, momentum_ppo, momentum_ppo_signal,
       momentum_ppo_hist, others_dr, others_dlr, others_cr)""")
        c.execute("delete from "+pair+"_"+interval+"_TA")
        c.executemany('insert into ' + pair + "_" + interval + "_TA" + ' values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', rows.values.tolist())
        conn.commit()
    def save_data(self,rows,pair):
        # print(t)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        if pair=='1INCHUSDT':
            pair='A1INCHUSDT'
        # pair="DEFIUSDT"
        c.execute("CREATE TABLE IF NOT EXISTS "+pair+"_"+self.tf+" (timespan1, open, high, low, close, volume,timespan2,f1,f2,f3,f4,f5)")
        c.executemany('insert into '+ pair+"_"+self.tf + ' values (?,?,?,?,?,?,?,?,?,?,?,?)', rows)
        conn.commit()
    def start(self):
        self.my_data = data.Data()
        self.symbol_records = self.my_data.get_symbols()
        cnt = len(self.symbol_records)
        # print(cnt)
        ii = 0
        while ii < cnt:
            ssyy = self.symbol_records[ii][0].upper()
            # ssyy = "DEFIUSDT"
            print("going for : "+ssyy)
            self.get_klines(ssyy)
            # self.rename(ssyy)
            ii += 1
    def start_TA(self,interval):
        self.my_data = data.Data()
        self.symbol_records = self.my_data.get_symbols()
        cnt = len(self.symbol_records)
        # print(cnt)
        ii = 0
        while ii < cnt:
            ssyy = self.symbol_records[ii][0].upper()
            # ssyy = "DEFIUSDT"
            print("going for : "+ssyy)
            self.add_ta(ssyy, interval)
            # self.rename(ssyy)
            ii += 1

    def rename(self,pair):
        if pair=='1INCHUSDT':
            pair='A1INCHUSDT'
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute("alter table "+pair+" rename to "+ pair+ "_5m"+";")
            conn.commit()
        except:
            pass
his = Historical()
his.start_TA("5m")
# his.start()