from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import*
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time, sys

class KEYINPUT(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.edit.setFixedWidth(250)
        self.edit.setGeometry(4,5,180,20)
        self.edit.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 3%;")

        self.sendBtn = QPushButton("SEND", self)
        self.sendBtn.setGeometry(260,5,50,20)

    def serialize(self):
        res = super().serialize()
        res['message'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.edit.setText(data['message'])
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(OP_NODE_KEYINPUT)
class Open_MySQL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_keyinput.png"
    op_code = OP_NODE_KEYINPUT
    op_title = "Input Msg "
    content_label_objname = "Input Msg "

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])     #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = KEYINPUT(self)                       # <----------- init UI with data and widget
        self.grNode = FlowKeyInput(self)                    # <----------- Box Image Draw in Flow_Node_Base

        self.content.sendBtn.clicked.connect(self.start_clicked)

    def evalImplementation(self):                           # <----------- Create Socket range Index
        self.value = self.payload

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()
        
    def start_clicked(self):
        self.payload['msg'] = self.content.edit.text()
        self.payload['result'] = self.content.edit.text()

        self.evalImplementation()                           #<--------- Send Payload to output socke


