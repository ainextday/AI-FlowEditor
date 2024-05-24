from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time, sys

class SubmitButton(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.SettingBtn = QPushButton("SUBMIT", self)
        self.SettingBtn.setGeometry(10,10,75,35)

        self.ToggleMode = QCheckBox("Toggle",self)
        self.ToggleMode.setGeometry(95,5,80,20)
        self.ToggleMode.setStyleSheet("color: lightblue; font-size:5pt;")
        self.ToggleMode.setChecked(True)
        self.ToggleMode_flag = True

        self.IntervalMode = QCheckBox("Interval",self)
        self.IntervalMode.setGeometry(95,30,80,20)
        self.IntervalMode.setStyleSheet("color: lightgreen; font-size:5pt;")
        self.IntervalMode_flag = False

        self.IntervalMSEC = QLineEdit(self)
        self.IntervalMSEC.setGeometry(165,30,55,20)
        self.IntervalMSEC.setStyleSheet("color: lightgreen; font-size:6pt;")
        self.IntervalMSEC.setPlaceholderText("mSEC")

        self.edit = QLineEdit(self)
        self.edit.setGeometry(160,5,60,20)
        self.edit.setPlaceholderText("---")
        self.edit.setAlignment(QtCore.Qt.AlignCenter)
        self.edit.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:6pt;color:white; border: 1px solid white; border-radius: 2%;")

        self.BtnInterval_timer = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.BtnInterval_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        # self.interval = '1000'
        self.fromOnload = False
        self.fromOnload_flag = False

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['toggle'] = self.ToggleMode_flag
        res['interval'] = self.IntervalMode_flag
        res['intervalms'] = self.IntervalMSEC.text()
        res['comment'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'message' in data:
                self.Data = data['message']

            if 'interval' in data:
                self.IntervalMode_flag = data['interval']
                if self.IntervalMode_flag:

                    self.interval = data['intervalms']
                    self.IntervalMSEC.setText(self.interval)

                    self.IntervalMode.setChecked(True)

                    self.BtnInterval_timer.setInterval(int(self.interval))
                    self.BtnInterval_timer.start()

            if 'toggle' in data:
                self.ToggleMode_flag = data['toggle']
                if self.ToggleMode_flag:
                    self.ToggleMode.setChecked(True)
                    self.fromOnload = True
                    self.BtnInterval_timer.start()

            if 'comment' in data:
                self.edit.setText(str(data['comment']))

            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_BUTTON)
class Open_BUTTON(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_button.png"
    op_code = OP_NODE_BUTTON
    op_title = "Button"
    content_label_objname = "Button"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = SubmitButton(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsButton(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.SettingBtn.clicked.connect(self.submitProcess)
        self.content.ToggleMode.stateChanged.connect(self.SelectToggleFunction)
        self.content.IntervalMode.stateChanged.connect(self.SelectIntervalFunction)
        self.content.IntervalMSEC.textChanged.connect(self.ChangedInterval)

        self.content.BtnInterval_timer.timeout.connect(self.button_interval)
        # self.content.BtnInterval_timer.setInterval(2000)
        self.content.BtnInterval_timer.start()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        
        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

    def submitProcess(self):
        if not self.content.IntervalMode_flag:
            if not self.content.ToggleMode_flag:
                self.payload['submit'] = True
                self.evalImplementation()

            else:
                self.payload['submit'] = True
                self.evalImplementation()

                self.content.BtnInterval_timer.setInterval(2000)
                self.content.BtnInterval_timer.start()

    def SelectToggleFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.ToggleMode_flag = True
            self.content.IntervalMode_flag = False
            self.content.IntervalMode.setChecked(False)

        else:
            self.content.ToggleMode_flag = False

    def SelectIntervalFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.IntervalMode_flag = True
            self.content.ToggleMode_flag = False
            self.content.ToggleMode.setChecked(False)

            self.content.BtnInterval_timer.setInterval(int(self.content.IntervalMSEC.text()))
            self.content.BtnInterval_timer.start()

        else:
            self.content.IntervalMode_flag = False
            self.content.BtnInterval_timer.stop()

    def button_interval(self):
        if self.content.ToggleMode_flag:
            if not self.content.fromOnload:
                self.payload['submit'] = False
                self.evalImplementation() 
                self.content.BtnInterval_timer.stop()

            else:
                if not self.content.fromOnload_flag:
                    self.payload['submit'] = True
                    self.evalImplementation() 

                    self.content.BtnInterval_timer.setInterval(1000)

                else:
                    self.payload['submit'] = False
                    self.evalImplementation() 
                    self.content.BtnInterval_timer.stop()
    
                self.content.fromOnload_flag = not self.content.fromOnload_flag
                print("First click with self.payload['submit'] : ", self.payload['submit'])
                
        else:
            if self.content.TimerBlinkCnt >= 2:
                self.content.TimerBlinkCnt = 0
                if self.content.BlinkingState:
                    self.payload['submit'] = True
                    self.evalImplementation()

                    self.content.IntervalMode.setText("Interval")
                    
                else:
                    self.payload['submit'] = False
                    self.evalImplementation()  

                    self.content.IntervalMode.setText("")
                    
                self.content.BlinkingState = not self.content.BlinkingState

            self.content.TimerBlinkCnt += 1
            # print("self.content.TimerBlinkCnt : ", self.content.TimerBlinkCnt)
        
        # print("self.content.ToggleMode_flag : ", self.content.ToggleMode_flag)

    def ChangedInterval(self):
        # self.content.interval = self.content.IntervalMSEC.text()

        self.content.BtnInterval_timer.setInterval(int(self.content.IntervalMSEC.text()))
        self.content.BtnInterval_timer.start