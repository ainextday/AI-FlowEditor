from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time, sys

class TextTerminal(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.save_icon = self.Path + "/icons/icons_save_icon_30.png"
        self.refresh_icon = self.Path + "/icons/icons_refresh.png"

        self.width = 320
        self.height = 40

        self.edge_roundness = 5.0
        self._brush_background = QBrush(QColor(0, 57, 94, 150))      #QColor with transparent 

        self.lbl = QLabel("Text Titel Name" , self)
        self.lbl.setStyleSheet("background-color: rgba(0, 57, 94, 150);font-size:20pt;color:lightblue;")
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(15,2,310,35)

        self.LogText = QTextEdit("" , self)
        self.LogText.setAlignment(Qt.AlignLeft)
        self.LogText.setStyleSheet("background-color: rgba(0, 124, 212, 50);font-size:17pt;color:lightblue;")
        self.LogText.setGeometry(15,50,355,370)

        self.saveBtn = QPushButton(self)
        self.saveBtn.setGeometry(360,5,20,20)
        self.saveBtn.setIcon(QIcon(self.save_icon))

        #====================================================
        self.resetBtn = QPushButton(self)
        self.resetBtn.setGeometry(330,5,20,20)
        self.resetBtn.setIcon(QIcon(self.refresh_icon))

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def paintEvent(self, event):
        # title
        path_outline = QPainterPath()
        path_outline.addRoundedRect(5, 0, self.width, self.height, self.edge_roundness, self.edge_roundness)
        
        painter = QPainter()
        painter.begin(self)

        pen = QPen(QColor("#FFA5FBFF"), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_outline.simplified())

@register_node(OP_NODE_TEXTTEMINAL)
class Open_Log(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_log.png"
    op_code = OP_NODE_TEXTTEMINAL
    op_title = "Text Terminal"
    content_label_objname = "Text Terminal"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2,3], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.next_payload = {}
        
        self.TextShowLog = ""
        #self.line_matchtime = 0

    def initInnerClasses(self):
        self.content = TextTerminal(self)                   # <----------- init UI with data and widget
        self.grNode = FlowTextTerminal(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.resetBtn.clicked.connect(self.ResetAllLog)
        self.content.saveBtn.clicked.connect(self.OnSaveLog)

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.rx_payload = input_node.eval()

            if self.rx_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                if 'texttitlename' in self.rx_payload:
                    self.content.lbl.setText(str(self.rx_payload['texttitlename']))

                #print("len self.rx_payload['matchtime'] = ", len(self.rx_payload['matchtime']))
                if 'matchtime' in self.rx_payload and len(self.rx_payload['matchtime']) > 1:
                    self.content.LogText.setText("")
                    self.TextShowLog = "Match 1. at Sec : "

                    for i in range(len(self.rx_payload['matchtime'])):
                        if i < len(self.rx_payload['matchtime']) - 1:
                            self.TextShowLog = self.TextShowLog + str(self.rx_payload['matchtime'][i]) + "\nMatch " + str(i +2) + ". at Sec : "
                        else:
                            self.TextShowLog = self.TextShowLog + str(self.rx_payload['matchtime'][i])

                    self.content.LogText.setText(self.TextShowLog)
                    
                    #self.line_matchtime += 1
                    #print("self.line_matchtime = ", self.line_matchtime)

                    #self.rx_payload['matchtime'] = None

                # else:
                    # self.content.LogText.setText("")

        input_node1 = self.getInput(1)
        if not input_node1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.rx_payload1 = input_node1.eval()

            if self.rx_payload1 is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                if 'inputtype' in self.rx_payload1:
                    self.next_payload['inputtype'] = self.rx_payload1['inputtype']

                if 'img' in self.rx_payload1:
                    self.next_payload['img'] = self.rx_payload1['img']

        self.value = self.next_payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        return self.value

    def ResetAllLog(self):
        self.rx_payload['matchtime'] = None
        self.content.LogText.setText("")
        self.LogLine = 0

        self.Global.setGlobal("reset_matchtime", True)

    def OnSaveLog(self):
        print("Save matchtime")

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            #print(fileName)

            file = open(fileName,'w', encoding="utf-8")
            #text = self.textEdit.toPlainText()
            
            file.write(self.TextShowLog)
            file.close()
