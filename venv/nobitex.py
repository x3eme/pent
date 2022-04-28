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
    async def getbook(self, sleeptime: float):
        await asyncio.sleep(sleeptime)

        isdiff = 0
        diff = 0.0
        lsendt = 0.0





        print(str(sleeptime)[0:3] + " " + str(round(time.time(),2))[8:])
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


        data = r.json()
        print(travel)

        #if data is different
        if data != self.book:
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
        return isdiff, round(diff,2)*1000, sendt, lsendt, travel*1000


    async def main(self, interval, count):
        switch_found = False
        sendt = 0.0
        travel = 0.0
        diff = 0.0
        difff = 0.0

        while True:
            print("start-------")
            if not switch_found:
                for call in asyncio.as_completed([nob.getbook(i) for i in np.arange(0.0, count/10, interval)]):
                    isdiff, diff, sendt, lsendt, travel = await call
                    if diff < 200 and sendt > lsendt and lsendt != 0.0 and diff < travel:
                        switch_found = True
                        print(str("{} {} diff: {} st: {} lastst: {} travel time: {}").format(
                            str(round(time.time(),2))[8:],
                            isdiff,
                            diff,
                            str(round(sendt,2))[8:],
                            str(round(lsendt,2))[8:],
                            travel))
                        difff = diff
                        continue
            # switch found
            else:
                print(time.time())
                print(str("switch found travel {} diff {}").format(travel, difff))
                switchtime = 1000-travel
                first = 1000-travel-100
                last = 1000-travel+100
                newrange = 0.25
                if first >= 0 and travel < 1000:
                    print(str("first {} last {}").format(first, last))
                    await asyncio.sleep(first/1000)
                    for call in asyncio.as_completed([nob.getbook(i) for i in np.arange(0.0, newrange, newrange/5)]):
                        isdiff, diff, sendt, lsendt, travel = await call
                        if diff < 200 and sendt > lsendt and lsendt != 0.0 and diff < travel:
                            switch_found = True
                            print(str("found again newrange: {} {} {} diff {} st {} lastst {} {}").format(
                                newrange,
                                str(round(time.time(),2))[8:],
                                isdiff,
                                diff,
                                str(round(sendt,2))[8:],
                                str(round(lsendt,2))[8:],
                                travel))
                            continue
                else:
                    switch_found = False
                    continue







nob = nobitex()
loop = asyncio.get_event_loop()
# attack = asyncio.gather(*[nob.getbook(i) for i in np.arange(0.0, 1.0, 0.1)])
loop.run_until_complete(nob.main(0.1,10))
print(nob.mindiff*1000)






# for i in range(100):
#     sendt = time.time()
#
#     r = requests.get(url=nob.noburl)  # , params=PARAMS)
#
#     fin = time.time()
#
#     print(fin-sendt)

