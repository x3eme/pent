import websockets
import json
import os
import sys
import csv

import time
import asyncio
import datetime
import threading

import ccxt  # noqa: E402
import pandas

class binbook:
    def __init__(self):
        self.dc = True

        print("init binance socket ...")
        self.bbook = pandas.DataFrame(columns=["symbol", "bid", "ask"], data=[["btcusdt","0","0"],["bnbusdt","0","0"],["ethusdt","0","0"],["bchusdt","0","0"],["xrpusdt","0","0"],["eosusdt","0","0"],["ltcusdt","0","0"],["trxusdt","0","0"],["etcusdt","0","0"],["linkusdt","0","0"],["xlmusdt","0","0"],["adausdt","0","0"],["xmrusdt","0","0"],["dashusdt","0","0"],["zecusdt","0","0"],["xtzusdt","0","0"],["atomusdt","0","0"],["ontusdt","0","0"],["iotausdt","0","0"],["batusdt","0","0"],["vetusdt","0","0"],["neousdt","0","0"],["qtumusdt","0","0"],["iostusdt","0","0"],["thetausdt","0","0"],["algousdt","0","0"],["zilusdt","0","0"],["kncusdt","0","0"],["zrxusdt","0","0"],["compusdt","0","0"],["omgusdt","0","0"],["dogeusdt","0","0"],["sxpusdt","0","0"],["kavausdt","0","0"],["bandusdt","0","0"],["rlcusdt","0","0"],["wavesusdt","0","0"],["mkrusdt","0","0"],["snxusdt","0","0"],["dotusdt","0","0"],["defiusdt","0","0"],["yfiusdt","0","0"],["balusdt","0","0"],["crvusdt","0","0"],["trbusdt","0","0"],["runeusdt","0","0"],["sushiusdt","0","0"],["srmusdt","0","0"],["egldusdt","0","0"],["solusdt","0","0"],["icxusdt","0","0"],["storjusdt","0","0"],["blzusdt","0","0"],["uniusdt","0""0"],["avaxusdt","0","0"],["ftmusdt","0","0"],["hntusdt","0","0"],["enjusdt","0","0"],["flmusdt","0","0"],["tomousdt","0","0"],["renusdt","0","0"],["ksmusdt","0","0"],["nearusdt","0","0"],["aaveusdt","0","0"],["filusdt","0","0"],["rsrusdt","0","0"],["lrcusdt","0","0"],["maticusdt","0","0"],["oceanusdt","0","0"],["cvcusdt","0","0"],["belusdt","0","0"],["ctkusdt","0","0"],["axsusdt","0","0"],["alphausdt","0","0"],["zenusdt","0","0"],["sklusdt","0","0"],["grtusdt","0","0"],["1inchusdt","0","0"],["acrousdt","0","0"],["chzusdt","0","0"],["sandusdt","0","0"],["ankrusdt","0","0"],["lunausdt","0","0"],["btsusdt","0","0"],["litusdt","0","0"],["unfiusdt","0","0"],["dodousdt","0","0"],["reefusdt","0","0"],["rvnusdt","0","0"],["sfpusdt","0","0"],["xemusdt","0","0"],["cotiusdt","0","0"],["chrusdt","0","0"],["manausdt","0","0"],["aliceusdt","0","0"],["hbarusdt","0","0"],["oneusdt","0","0"],["linausdt","0","0"],["stmxusdt","0","0"],["dentusdt","0","0"],["celrusdt","0","0"],["hotusdt","0","0"],["mtlusdt","0","0"],["ognusdt","0","0"],["nknusdt","0","0"],["scusdt","0","0"],["dgbsdt","0","0"],["1000shibusdt","0","0"],["icpusdt","0","0"],["bakeusdt","0","0"],["gtcusdt","0","0"],["btcdomusdt","0","0"],["tlmusdt","0","0"],["iotxusdt","0","0"],["audiousdt","0","0"],["rayusdt","0","0"],["c98usdt","0","0"],["maskusdt","0","0"],["atausdt","0","0"],["dydxusdt","0","0"],["1000xecusdt","0","0"],["galausdt","0","0"],["celousdt","0","0"],["arusdt","0","0"],["klayusdt","0","0"],["arpausdt","0","0"],["ctsiusdt","0","0"],["lptusdt","0","0"],["ensusdt","0","0"],["peopleusdt","0","0"],["antusdt","0","0"],["roseusdt","0","0"],["duskusdt","0","0"],["flowusdt","0","0"],["imxusdt","0","0"],["api3usdt","0","0"],["ancusdt","0","0"],["gmtusdt","0","0"],["apeusdt","0","0"],["bnxusdt","0","0"],["woousdt","0","0"],["fttusdt","0","0"]])

        self.url = "wss://fstream.binance.com/ws/"  # stream address

    def startit(self):
        time.sleep(2)
        print("starting binance socket ...")
        asyncio.get_event_loop().run_until_complete(self.orders_data())
    def getcon(self):
        with open('conf.txt', 'r') as file:
            data = file.read().split('\n')
        return data

    def convertBT(self,bt):
        start = datetime.datetime.fromtimestamp(bt/1000.0)
        # thisis = start+bt
        return start
    async def orders_data(self):
        sock = await websockets.connect(self.url+"btcusdt@depth5")
        await sock.send(json.dumps(
                {
                    "method": "SUBSCRIBE",
                    "params": ['bnbusdt@depth5','ethusdt@depth5','bchusdt@depth5','xrpusdt@depth5','eosusdt@depth5','ltcusdt@depth5','trxusdt@depth5','etcusdt@depth5','linkusdt@depth5','xlmusdt@depth5','adausdt@depth5','xmrusdt@depth5','dashusdt@depth5','zecusdt@depth5','xtzusdt@depth5','atomusdt@depth5','ontusdt@depth5','iotausdt@depth5','batusdt@depth5','vetusdt@depth5','neousdt@depth5','qtumusdt@depth5','iostusdt@depth5','thetausdt@depth5','algousdt@depth5','zilusdt@depth5','kncusdt@depth5','zrxusdt@depth5','compusdt@depth5','omgusdt@depth5','dogeusdt@depth5','sxpusdt@depth5','kavausdt@depth5','bandusdt@depth5','rlcusdt@depth5','wavesusdt@depth5','mkrusdt@depth5','snxusdt@depth5','dotusdt@depth5','defiusdt@depth5','yfiusdt@depth5','balusdt@depth5','crvusdt@depth5','trbusdt@depth5','runeusdt@depth5','sushiusdt@depth5','srmusdt@depth5','egldusdt@depth5','solusdt@depth5','icxusdt@depth5','storjusdt@depth5','blzusdt@depth5','uniusdt@depth5','avaxusdt@depth5','ftmusdt@depth5','hntusdt@depth5','enjusdt@depth5','flmusdt@depth5','tomousdt@depth','renusdt@depth5','ksmusdt@depth5','nearusdt@depth5','aaveusdt@depth5','filusdt@depth5','rsrusdt@depth5','lrcusdt@depth5','maticusdt@depth5','oceanusdt@depth5','cvcusdt@depth5','belusdt@depth5','ctkusdt@depth5','axsusdt@depth5','alphausdt@depth5','zenusdt@depth5','sklusdt@depth5','grtusdt@depth5','1inchusdt@depth5','acrousdt@depth5','chzusdt@depth5','sandusdt@depth5','ankrusdt@depth5','lunausdt@depth5','btsusdt@depth5','litusdt@depth5','unfiusdt@depth5','dodousdt@depth5','reefusdt@depth5','rvnusdt@depth5','sfpusdt@depth5','xemusdt@depth5','cotiusdt@depth5','chrusdt@depth5','manausdt@depth5','aliceusdt@depth5','hbarusdt@depth5','oneusdt@depth5','linausdt@depth5','stmxusdt@depth5','dentusdt@depth5','celrusdt@depth5','hotusdt@depth5','mtlusdt@depth5','ognusdt@depth5','nknusdt@depth5','scusdt@depth5','dgbusdt@depth5','1000shibusdt@depth5','icpusdt@depth5','bakeusdt@depth5','gtcusdt@depth5','btcdomusdt@depth5','tlmusdt@depth5','iotxusdt@depth5','audiousdt@depth5','rayusdt@depth5','c98usdt@depth5','maskusdt@depth5','atausdt@depth5','dydxusdt@depth5','1000xecusdt@depth5','galausdt@depth5','celousdt@depth5','arusdt@depth5','klayusdt@depth5','arpausdt@depth5','ctsiusdt@depth5','lptusdt@depth5','ensusdt@depth5','peopleusdt@depth5','antusdt@depth5','roseusdt@depth5','duskusdt@depth5','flowusdt@depth5','imxusdt@depth5','api3usdt@depth5','ancusdt@depth5','gmtusdt@depth5','apeusdt@depth5','bnxusdt@depth5','woousdt@depth5','fttusdt@depth5'],
                    "id": 1,
                }))
        while True:
            try:
                resp = await sock.recv()
            except:
                while not sock.open:
                    try:
                        print('Reconnecting...')
                        self.dc=True
                        time.sleep(1)
                        sock = await websockets.connect(self.url+self.first_pair)
                        await sock.send(self.pairs)
                    except:
                        pass
            js = json.loads(resp)
            # print(resp)
            if "None" not in resp and "result" not in resp:
                try:
                    ss = str(js["s"]).lower()
                    bb = str(js["b"][0][0])
                    aa = str(js["a"][0][0])
                    ssind = int(self.bbook.index[self.bbook['symbol'] == ss].values[0])
                    self.bbook.at[ssind,'bid'] = bb
                    self.bbook.at[ssind, 'ask'] = aa
                    # print(self.bbook)
                    # print(ss + ": best bid : " + bb + " best ask : "+ aa)
                except:
                    pass
                    # print("error in : " + js["s"] + "    " + resp)
# b = binbook()
# asyncio.get_event_loop().run_until_complete(b.orders_data())