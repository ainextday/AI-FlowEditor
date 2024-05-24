from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


from random import randint
import os

class RamdomTest(QDMNodeContentWidget):
    def initUI(self):
        Path = os.path.dirname(os.path.abspath(__file__))
        self.slot_icon = Path + "/icons/icons_slotmc.png"

        self.radioState = QRadioButton("START", self)
        self.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : lightyellow"
                                   "}")
        self.radioState.setGeometry(5,4,85,20)

        self.lbl = QLabel("Interval:" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(5,33,50,20)
        self.lbl.setStyleSheet("color: orange")

        self.edit = QLineEdit(self)
        self.edit.setFixedWidth(40)
        self.edit.setGeometry(50,30,40,20)
        self.edit.setPlaceholderText("mSEC")

        #=======================================
        #Select Graph
        self.dataline1 = True
        self.checkX1 = QCheckBox("x1",self)
        self.checkX1.setGeometry(5,50,40,20)
        self.checkX1.setStyleSheet("color: lightblue")
        self.checkX1.setChecked(True)

        self.dataline2 = False
        self.checkX2 = QCheckBox("x2",self)
        self.checkX2.setGeometry(50,50,40,20)
        self.checkX2.setStyleSheet("color: #FC03C7")

        self.Random_timer = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.Random_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        self.startR = False
        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.interval = '1000'
        self.interval_cnt = 0

    def serialize(self):
        res = super().serialize()
        res['autorandom'] = self.startR
        res['interval'] = self.edit.text()
        res['selectlineone'] = self.dataline1
        res['selectlinetwo'] = self.dataline2
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.interval = data['interval']
            self.edit.setText(self.interval)

            self.startR = data['autorandom']
            if self.startR:
                self.Random_timer.start()
                self.radioState.setChecked(True)
            
            if data['selectlineone']:
                self.checkX1.setChecked(True)

            if data['selectlinetwo']:
                self.checkX2.setChecked(True)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_RANDOM)
class Open_RANDOM(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_random.png"
    op_code = OP_NODE_RANDOM
    op_title = "Random"
    content_label_objname = "Random"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        
        self.payload['fps'] = 1
        self.payload['blink'] = True
        self.payload['img'] = None
        self.payload['x1'] = []
        self.payload['y1'] = []
        self.payload['x2'] = []
        self.payload['y2'] = []
        self.payload['x3'] = []
        self.payload['y3'] = []
        self.payload['xParam'] = None
        self.payload['yParam'] = None
        self.payload['inputtype'] = "graph"

        self.range = 20
        self.x1 = list(range(self.range))  # 100 time points
        self.y1 = [randint(0,100) for _ in range(self.range)]  # 100 data points


        self.x2 = list(range(self.range))  # 50 time points
        self.y2 = [randint(0,100) for _ in range(self.range)]  # 50 data points

        self.content.Random_timer.setInterval(int(self.content.interval))

    def initInnerClasses(self):
        self.content = RamdomTest(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCamera(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.radioState.toggled.connect(self.onClicked)
        self.content.Random_timer.timeout.connect(self.update_data)
        self.content.edit.textChanged.connect(self.ChangedInterval)
        self.content.checkX1.stateChanged.connect(self.Createline)
        self.content.checkX2.stateChanged.connect(self.CreateSecondLine)

    def evalImplementation(self):                 # <
        #No Need Input

        self.value = self.payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        return self.value

    def onClicked(self):
        radioButton = self.content.sender()
        if radioButton.isChecked():
            self.StartRandom()
            #print("Redic Button Checked !!!!")
        else:
            self.StopRandom()
            #print("Redic Button UnChecked !!!!")

    def update_data(self):
        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                self.payload['blink'] = True
                self.content.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : grey"
                                   "}") 
            else:
                self.payload['blink'] = False
                self.content.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : lightyellow"
                                   "}") 
            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

        if self.content.dataline1:
            #Drop off the first y element, append a new one.
            self.x1 = self.x1[1:]  # Remove the first y element.
            self.x1.append(self.x1[-1] + 1)  # Add a new value 1 higher than the last.

            self.y1 = self.y1[1:]  # Remove the first 
            self.y1.append(randint(0,100))  # Add a new random value.

        if self.content.dataline2:
            #Drop off the first y element, append a new one.
            self.x2 = self.x2[1:]  # Remove the first y element.
            self.x2.append(self.x2[-1] + 1)  # Add a new value 1 higher than the last.

            self.y2 = self.y2[1:]  # Remove the first 
            self.y2.append(randint(0,100))  # Add a new random value.

        self.payload['x1'] = self.x1
        self.payload['y1'] = self.y1

        self.payload['x2'] = self.x2
        self.payload['y2'] = self.y2

        self.evalImplementation()

    def StartRandom(self):
        self.content.BlinkingState = True
        self.content.Random_timer.start()
        self.content.startR = True

    def StopRandom(self):
        self.content.BlinkingState = False
        self.content.startR = False
        self.content.Random_timer.stop()

    def ChangedInterval(self):
        self.content.interval = self.content.edit.text()
        self.content.radioState.setChecked(False)
        self.content.Random_timer.setInterval(int(self.content.interval))
        self.content.Random_timer.stop()

    def Createline(self, state):
        if state == QtCore.Qt.Checked:
            self.content.dataline1 = True
        else:
            self.content.dataline1 = False

    def CreateSecondLine(self, state):
        if state == QtCore.Qt.Checked:
            self.content.dataline2 = True
        else:
            self.content.dataline2 = False