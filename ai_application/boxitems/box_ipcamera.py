from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QDate, QTimer, QTime, Qt
import PyQt5.QtWidgets as Wid

import time, sys

# pip3 install pafy
# pip3 install youtube-dl
# importing pafy module for windows os
import pafy

class IPCamera(QDMNodeContentWidget):
    def initUI(self):
        Path = os.path.dirname(os.path.abspath(__file__))
        self.refresh_icon = Path + "/icons/icons_refresh.png"
        self.play_icon = Path + "/icons/icons_play.png"
        self.pause_icon = Path + "/icons/icons_pause.png"
        self.save_icon = Path + "/icons/icons_save.png"

        self.Data = None

        self.edit = QLineEdit("", self)
        self.edit.setGeometry(8,2,80,20)
        self.edit.setPlaceholderText("URL :")

        self.connectbtn = QPushButton(self)
        self.connectbtn.setGeometry(24,27,50,20)
        self.connectbtn.setIcon(QIcon(self.play_icon))

        self.refreshbtn = QPushButton(self)
        self.refreshbtn.setGeometry(82,27,20,20)
        self.refreshbtn.setIcon(QIcon(self.refresh_icon))

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(95,2,20,20)
        self.browsFiles.setIcon(QIcon(self.save_icon))

        self.toggle = False
        self.IPCamera_timer = QtCore.QTimer(self)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.fileLocation = ""
        self.url = ""
        self.source = ""

    def serialize(self):
        res = super().serialize()
        res['URL'] = self.edit.text()
        res['ipcamrun'] = self.toggle
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['URL']
            self.source = value[12:19]
            if self.source == 'youtube':
                print("Souce from youtube !!!")
                self.url = value
                self.video = pafy.new(self.url)
                self.best = self.video.getbest(preftype="mp4")

            self.edit.setText(value)
            self.toggle = data['ipcamrun']
            if self.toggle:
                self.connectbtn.setIcon(QIcon(self.pause_icon))
                self.IPCamera_timer.start()
                self.browsFiles.setEnabled(False)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def browseSlot(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Video Files (*.mp4)", options=options)
        
        if files:
            self.fileLocation = files[0]
            self.edit.setText(str(self.fileLocation))
        
@register_node(OP_NODE_IPCAMERA)
class Open_IPCAMERA(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_ipcam.png"
    op_code = OP_NODE_IPCAMERA
    op_title = "IP / MP4 / IMG"
    content_label_objname = "ipcamera"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.payload['fps'] = 1
        self.payload['blink'] = True
        self.payload['img'] = None
        self.payload['x1'] = [1,2,3,4,5]
        self.payload['y1'] = [1,2,3,4,5]
        self.payload['x2'] = [1,2,3,4,5]
        self.payload['y2'] = [5,4,3,2,1]
        self.payload['x3'] = [1,2,3,4,5]
        self.payload['y3'] = [5,1,3,4,1]
        self.payload['xParam'] = None
        self.payload['yParam'] = None
        self.payload['inputtype'] = "img"

        self.frame = None
        self.source_type = None

    def initInnerClasses(self):
        self.content = IPCamera(self)                       # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceDetect(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.IPCamera_timer.timeout.connect(self.ipcam_update_frame)
        self.content.IPCamera_timer.setInterval(100)

        self.content.connectbtn.clicked.connect(self.ipcameraConnect)
        self.content.refreshbtn.clicked.connect(self.ChangedCamURL)

        self.content.edit.textChanged.connect(self.ChangedCamURL)
        self.content.browsFiles.clicked.connect(self.content.browseSlot)

        self.CamCapture = cv2.VideoCapture(self.content.edit.text())

    def evalImplementation(self):                       # <----------- Create Socket range Index
        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        return self.value

    def ipcameraConnect(self):
        if self.source_type == 'image':
            self.payload['fps'] = 1
            self.payload['blink'] = False
            self.image = cv2.imread(self.content.edit.text())
            self.payload['img'] = cv2.resize(self.image, dsize=(640, 480), interpolation=cv2.INTER_AREA)

            self.evalImplementation()                   #<--------- Send Payload to output socket
        else:
            if self.content.toggle == False:
                if len(self.content.edit.text()) > 0:
                    self.content.connectbtn.setIcon(QIcon(self.content.pause_icon))
                    self.content.IPCamera_timer.start()
                    self.content.browsFiles.setEnabled(False)
                else:
                    self.payload['fps'] = time.time()
                    self.payload['blink'] = True
                    self.payload['img'] = "No link or URL !!!"

            else:
                self.content.connectbtn.setIcon(QIcon(self.content.play_icon))
                self.content.IPCamera_timer.stop()
                self.content.browsFiles.setEnabled(True)

            self.content.toggle = not self.content.toggle

    def ipcam_update_frame(self):
        
        self.payload['fps'] = time.time()

        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                self.payload['blink'] = True
            else:
                self.payload['blink'] = False

            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

        ret, self.frame = self.CamCapture.read()
        self.frame = cv2.resize(self.frame, dsize=(640, 480), interpolation=cv2.INTER_AREA)
        self.payload['img'] = self.frame

        self.evalImplementation()                   #<--------- Send Payload to output socket

    def ChangedCamURL(self):
        if self.content.edit.text() is not None:
            value = self.content.edit.text()
            b = value[12:19]
            if b == 'youtube':
                print("Souce from youtube !!!")
                self.url = value
                self.video = pafy.new(self.url)
                self.best = self.video.getbest(preftype="mp4")

                self.CamCapture = cv2.VideoCapture(self.content.edit.text())
                self.CamCapture.open(self.best.url)

            else:
                b = value[-3:len(value)]
                #print("Check type if source is image b = ", b)
                if b == 'png' or b == 'jpg' or b == 'JPG' or b == 'jpeg':
                    print("source is  image !!!")
                    self.source_type = 'image'
                else:
                    self.source_type = None
                    self.CamCapture = cv2.VideoCapture(self.content.edit.text())
        else:
            self.payload['fps'] = time.time()
            self.payload['blink'] = True
            self.payload['img'] = "No link or URL !!!"