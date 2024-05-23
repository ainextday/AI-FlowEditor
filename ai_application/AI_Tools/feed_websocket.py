import threading
import sys

import websocket
import json
import pandas as pd 
import dateutil.parser
from datetime import timedelta

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RunWSThread(threading.Thread):
    def __init__(self, socket, box_id):
        threading.Thread.__init__(self)

        self.Global = GlobalVariable() 

        self.socket = socket
        self.box_id = box_id

        self.minutes_processed = {}
        self.minute_candlesticks = []
        self.current_tick = None
        self.previous_tick = None

        self.process = True

        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.socket, on_open=self.on_open, on_message=self.on_message)
        
        # # Close connection
        # self.ws.close()
        # # Continue with the program

    def run(self):
        print("run feed ws from websocket : ", self.socket)
        #=== Add while loop or forever loop here ===#

        while self.process:
            
            self.ws.run_forever()

            if self.Global.hasGlobal("WS_Process"):
                self.process = self.Global.getGlobal("WS_Process")
                self.Global.removeGlobal("WS_Process")

        self.ws.close()
        print("stop feed data from websocket : ", self.socket)
        print("process : ", self.process)
        # websocket.enableTrace(False)

    def on_open(self, ws):
        print("Connection is opened")
        subscribe_msg = {
            "type": "subscribe",
            "channels": [
                {
                "name": "ticker",
                "product_ids": [
                    "BTC-USD"
                    ]
                }

            ]
        }

        self.ws.send(json.dumps(subscribe_msg))

    def on_message(self, ws, message):
        if self.process:
            self.previous_tick = self.current_tick
            self.current_tick = json.loads(message)

            # print(current_tick)
            # print("=== Received Tick ===")
            # print(f"{self.current_tick['price']} @ {self.current_tick['time']}")

            tick_datetime_object = dateutil.parser.parse(self.current_tick['time'])
            timenow = tick_datetime_object + timedelta(hours=8)
            tick_dt = timenow.strftime("%m/%d/%Y %H:%M")
            # print(tick_datetime_object.minute)
            # print(tick_dt)

            if not tick_dt in self.minutes_processed:
                # print("This is a new candlestick")
                self.minutes_processed[tick_dt] = True

                if len(self.minute_candlesticks) > 0:
                    self.minute_candlesticks[-1]['close'] = self.previous_tick['price']

                self.minute_candlesticks.append({
                    'minute': tick_dt,
                    'open': self.current_tick['price'],
                    'high': self.current_tick['price'],
                    'low': self.current_tick['price']
                    })

                df = pd.DataFrame(self.minute_candlesticks[:-1])
                self.Global.setGlobal(self.box_id, df)
                # df.to_csv("bitcoin_data_tut.csv")

            if len(self.minute_candlesticks) > 0:
                current_candlestick = self.minute_candlesticks[-1]
                if self.current_tick['price'] > current_candlestick['high']:
                    current_candlestick['high'] = self.current_tick['price']
                if self.current_tick['price'] < current_candlestick['low']:
                    current_candlestick['low'] = self.current_tick['price']

                # print("== Candlesticks ==")
                # for candlestick in self.minute_candlesticks:
                #     print(candlestick)

#===============================================================
app = QApplication(sys.argv)

