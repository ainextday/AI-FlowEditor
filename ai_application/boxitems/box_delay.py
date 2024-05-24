from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


from random import randint
import time, sys
import os
from datetime import datetime

class DelayTime(QDMNodeContentWidget):
    def initUI(self):
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.slot_icon = self.Path + "/icons/icons_slotmc.png"
        self.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
        self.animate_process = self.Path + "/icons/icons_wait_20.gif"

        self.lbl = QLabel("Delay:" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(5,33,40,20)
        self.lbl.setStyleSheet("color: orange")

        self.edit = QLineEdit(self)
        self.edit.setFixedWidth(50)
        self.edit.setGeometry(38,30,50,20)
        self.edit.setPlaceholderText("milisec")

        #=======================================
        #Select Send Only New Data

        self.newoutputdata = True

        self.checkX1 = QCheckBox("Only New Out",self)
        self.checkX1.setGeometry(5,50,85,20)
        self.checkX1.setStyleSheet("color: lightblue")
        self.checkX1.setChecked(True)

        self.lockflow = self.readFlowSetting('LockFlow')
        if self.lockflow == "true":
            self.edit.setEnabled(False)
            self.checkX1.setEnabled(False)

        #=======================================
        # LED 

        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(30,30)
        graphicsView.setGeometry(QtCore.QRect(65, -2, 35, 35))

        self.img = QPixmap(self.bgImagePath)
        self.pixmap.setPixmap(self.img)

        #=======================================

        #====================================================
        # Loading the GIF
        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(5, 5, 20, 20))
        self.label.setMinimumSize(QtCore.QSize(20, 20))
        self.label.setMaximumSize(QtCore.QSize(25, 25))

        self.movie = QMovie(self.animate_process)
        self.label.setMovie(self.movie)
        self.movie.start()
        #====================================================

        self.Delay_Timer = QtCore.QTimer(self)

        self.interval = '1000'
        self.interval_cnt = 0

        self.last_value = ""
        self.DoneSend_Flag = False
        
    def serialize(self):
        res = super().serialize()
        res['delaytime'] = self.edit.text()
        res['sendonlynew'] = self.newoutputdata

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.interval = data['delaytime']
            self.edit.setText(self.interval)
            
            self.newoutputdata = data['sendonlynew']
            if self.newoutputdata:
                self.checkX1.setChecked(True)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def readFlowSetting(self, key):
        settings = QSettings("Flow Setting")
        data = settings.value(key)
        return data

@register_node(OP_NODE_DELAY)
class Open_DELAY(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_delayed_icon.png"
    op_code = OP_NODE_DELAY
    op_title = "Delay"
    content_label_objname = "Delay"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.reciev_datazero = {}

        self.Ready_ProcessDataOut = True
    
    def initInnerClasses(self):
        self.content = DelayTime(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCamera(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.Delay_Timer.timeout.connect(self.update_data)
        if len(self.content.interval) == 0:
            self.content.Delay_Timer.setInterval(1000)
            self.content.edit.setText("1000")
        else:
            self.content.Delay_Timer.setInterval(int(self.content.interval))

        self.content.edit.textChanged.connect(self.ChangedInterval)
        self.content.checkX1.stateChanged.connect(self.SetSendOnlyNewPayload)

    def evalImplementation(self):                 
        # <
        #No Need Input

        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.reciev_datazero = input_node.eval()
        #print("reciev_datazero = ", self.reciev_datazero)

        #print("self.content.last_value = ", self.content.last_value)

        if self.reciev_datazero is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return

        elif self.reciev_datazero is not None:
            """if self.content.newoutputdata:
                if str(self.reciev_datazero) != self.content.last_value and not self.content.DoneSend_Flag:
                    self.content.DoneSend_Flag = True
                    
                    self.content.Delay_Timer.start()

                    self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"
                    self.content.img = QPixmap(self.content.bgImagePath)
                    self.content.pixmap.setPixmap(self.content.img)

                else:
                    #print("self.reciev_datazero == self.last_value")

                    self.payload = None

                    self.content.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
                    self.content.img = QPixmap(self.content.bgImagePath)
                    self.content.pixmap.setPixmap(self.content.img)
            else:

                self.content.Delay_Timer.start()

                self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"
                self.content.img = QPixmap(self.content.bgImagePath)
                self.content.pixmap.setPixmap(self.content.img)

        else:

            self.content.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
            self.content.img = QPixmap(self.content.bgImagePath)
            self.content.pixmap.setPixmap(self.content.img)"""

            if self.Ready_ProcessDataOut:
                self.Ready_ProcessDataOut = False
                
                self.reciev_datazero['delay_timestamp_in'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                self.content.Delay_Timer.start()
                self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"
                self.content.img = QPixmap(self.content.bgImagePath)
                self.content.pixmap.setPixmap(self.content.img)

        # End Input
        #==========================================================================

    def update_data(self):
        # After Timer has Interval
        # print("Delay Update data Payload out !!!")

        self.content.Delay_Timer.stop()

        self.content.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
        self.content.img = QPixmap(self.content.bgImagePath)
        self.content.pixmap.setPixmap(self.content.img)

        self.reciev_datazero['delay_timestamp_out'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.reciev_datazero['submit'] = True

        self.value = self.reciev_datazero
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        self.content.last_value = str(self.reciev_datazero)
        self.content.DoneSend_Flag = False

        self.Ready_ProcessDataOut = True
        self.reciev_datazero['submit'] = False

    def ChangedInterval(self):
        self.content.interval = self.content.edit.text()
        print("Change Delay Interval = ", self.content.interval, " Millisec")
        self.content.Delay_Timer.setInterval(int(self.content.interval))
        self.content.Delay_Timer.start()

    def SetSendOnlyNewPayload(self, state):
        if state == QtCore.Qt.Checked:
            self.content.newoutputdata = True
        else:
            self.content.newoutputdata = False
            self.reciev_datazero = None
            self.last_value = None
