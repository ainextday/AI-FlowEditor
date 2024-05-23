import threading
import sys

import requests

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RunWAPIThread(threading.Thread):
    def __init__(self,boxid, url, header=None, api_step=0):
        threading.Thread.__init__(self)

        self.Global = GlobalVariable() 

        self.boxid = boxid
        self.url = url
        self.header = header
        self.api_step = api_step

        self.res = None

        self.url_webapi = [ self.url + '/api/market/ticker',
                            self.url + '/api/servertime',
                            self.url + '/api/market/place-bid',
                            self.url + '/api/market/place-ask']

    def run(self):

        print("box id:", self.boxid)
        print("run feed web api : ", self.url)
        #=== Add while loop or forever loop here ===#

        if self.Global.hasGlobal(self.boxid + "_flag"):
            flag = self.Global.getGlobal(self.boxid + "_flag")

            if flag:
                if self.api_step == 0:
                    self.res = requests.get(url=self.url + '/api/market/ticker')

                if self.api_step == 1:
                    response = requests.get(self.url + '/api/servertime')
                    ts = int(response.text)
                    print('Server time: ' + response.text)

                    data = {
                        'ts': ts,
                    }
                    signature = self.sign(data)
                    data['sig'] = signature

                    # print('Payload with signature: ' + self.json_encode(data))
                    self.rest = requests.post(self.url + '/api/market/balances', headers=self.header, data=self.json_encode(data))


                self.Global.setGlobal(self.boxid, self.res.text)
                self.Global.setGlobal(self.boxid + "_flag", False)

#===============================================================
app = QApplication(sys.argv)
