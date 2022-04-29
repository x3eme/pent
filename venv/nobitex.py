import asyncio
import requests
import json
import time
import numpy as np


class nobitex:

    def __init__(self):
        self.noburl = "https://api.nobitex.ir/v2/orderbook/all"
        self.book = ""
        self.tt = np.array([])

        self.count = 0
        self.lsendt = 0.0
        self.serial = 0
        self.repeat = 3



    def wtime(self, strr):
        return round(time.time() * 1000)


    #just calculate ma travel time
    def travelupdate(self, time):
        self.tt = np.append(self.tt,time)
        if np.size(self.tt)>10:
            self.tt = np.delete(self.tt,0,None)
        # print(self.tt)
        return np.average(self.tt)

    #sleep for sleeptime and then send a query
    async def getbook(self, serial: int, sleeptime: float):
        await asyncio.sleep(sleeptime)

        isdiff = 0
        diff = 0.0
        lsendt = 0.0
        data = ""

        sendt = time.time()

        future = loop.run_in_executor(None, requests.get, self.noburl)
        # r = requests.get(url=self.noburl)  # , params=PARAMS)
        try:
            r = await future
        except:
            print("server error")
            r = ""
        fin = time.time()

        #first update travel time ma
        travel = fin-sendt
        self.travelupdate(travel)

        try:
            data = r.json()
        except:
            print("format error json")
        # print(travel)

        #if data is different
        if data != self.book:

            print("update " + str(serial) +
                  " sendt: " + str(sendt) +
                  " now: " + str(round(time.time(), 2))[8:] +
                  " travel:" + str(travel))
            #calc. diff & update book
            lsendt = self.lsendt
            diff = sendt - self.lsendt
            isdiff = 1
            self.book = data
        else:
            pass
            # print("same")

        #we have received a response. record that it was the last
        self.lsendt = sendt
        return serial, isdiff, round(diff,2)*1000, sendt, lsendt, travel*1000


    async def main(self, interval, count):
        switch_found = False
        currsendt = 0.0
        travel = 0.0
        currdiff = 0.0

        origsendt = 0.0
        destsendt = 0.0

        while True:
            print("----- loop -----")
            if not switch_found:
                print("no switch")
                for call in asyncio.as_completed([nob.getbook(i, serial) for i in np.arange(0.0, count/10, interval)]):
                    serial, isdiff, diff, sendt, lsendt, travel = await call
                    if isdiff and diff < 500 and sendt > lsendt and lsendt != 0.0 and diff < travel:

                        if self.serial != serial:
                            print(str("from last batch st: {} lsendt {}"))
                        else:
                            switch_found = True
                            origsendt = lsendt
                            destsendt = sendt
                            print(str("switch candid @ {} {} diff: {} st: {} lastst: {} travel time: {}").format(
                                str(round(time.time(),2))[8:],
                                isdiff,
                                diff,
                                str(round(sendt,2))[8:],
                                str(round(lsendt,2))[8:],
                                travel))
                            break
            # switch found
            else:
                self.serial += 1
                print(str("serial: {} opt switch found travel {} diff {} lsendt {}").format(self.serial, travel, diff, str(round(lsendt,2))[8:]))
                switchtime = 1000-travel
                first = 1000-travel-50
                last = 1000-travel+50
                newrange = (100*3)/1000
                print(newrange*2, newrange)
                if first >= 0 and travel < 1000:
                    print(str("first {} last {}").format(first, last))
                    print(str("sleep for {}").format(first/1000))
                    await asyncio.sleep(first/1000)
                    for call in asyncio.as_completed([nob.getbook(i) for i in np.arange(0.0, newrange*2, newrange)]):
                        isdiff, diff, sendt, lsendt, travel = await call
                        print(str("bb isdiff: {} diff: {} sendt: {} lsendt: {} travel: {}").format(isdiff, diff, str(round(sendt,2))[8:], str(round(lsendt,2))[8:], travel))

                        if isdiff and diff < 100 and sendt > lsendt and diff < travel:
                            origsendt = lsendt
                            destsendt = sendt
                            switch_found = True
                            print(str("found again newrange: {} {} {} diff {} st {} lastst {} {}").format(
                                newrange,
                                str(round(time.time(),2))[8:],
                                isdiff,
                                diff,
                                str(rou,nd(sendt,2))[8:],
                                str(round(lsendt,2))[8:],
                                travel))
                            break
                        else:
                            print("not diff")
                else:
                    switch_found = False
                    continue

    async def go(self, interval, window):
        intv = interval
        wind = window
        serial = self.serial

        while True:
            print(str("-- loop -- wind {} intrv {} serial {} {}".format(wind, intv, self.serial, str(round(time.time()))[8:])))
            ops = [nob.getbook(serial, i) for i in np.arange(0.0, wind, intv)]
            for call in asyncio.as_completed(ops):
                serial, isdiff, diff, sendt, lsendt, travel = await call
                if serial == self.serial and isdiff and sendt > lsendt and diff < 300 and travel<800:
                    print(str("found serial {} diff {} sendt {} lsendt {} travel {}").
                          format(serial, diff, str(round(sendt,2))[8:], str(round(lsendt,2))[8:], travel))
                    serial += 1
                    # print(str("serial incre {} {}").format(self.serial, serial))
                    self.serial = serial
                    wind = max(wind/1.2, 0.4)
                    intv = max(intv/2, 0.05)

                    startin = 1000 - travel - diff - 50
                    tt = round(time.time(),2)
                    tts = round(startin/1000,2)
                    tttt = tt+tts
                    print(str("time now {} start in {}").format(str(tt)[6:], str(tts)))
                    if startin>0:
                        time.sleep(startin/1000)

                    self.repeat = 3
                    break
            #no diff found this round
            else:
                if self.repeat == 0:
                    wind = min(wind*1.3,1)
                    intv = min(intv*1.3,0.1)
                    self.repeat = 3
                else:
                    self.repeat = self.repeat - 1
                    # print(str("rep {}").format(self.repeat))













nob = nobitex()
loop = asyncio.get_event_loop()
# attack = asyncio.gather(*[nob.getbook(i) for i in np.arange(0.0, 1.0, 0.1)])
loop.run_until_complete(nob.go(0.1,1))



# for i in range(100):
#     sendt = time.time()
#
#     r = requests.get(url=nob.noburl)  # , params=PARAMS)
#
#     fin = time.time()
#
#     print(fin-sendt)

