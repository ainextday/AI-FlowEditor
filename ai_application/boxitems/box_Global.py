from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MySQL(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.setGlobal = QCheckBox("setGlobal()",self)
        self.setGlobal.setGeometry(10,5,90,20)
        self.setGlobal.setStyleSheet("color: lightblue; font-size:5pt;")
        self.setGlobal_flag = False

        self.getGlobal = QCheckBox("getGlobal()",self)
        self.getGlobal.setGeometry(10,30,90,20)
        self.getGlobal.setStyleSheet("color: lightgreen; font-size:5pt;")
        self.getGlobal_flag = False

        self.editkey = QLineEdit(self)
        self.editkey.setGeometry(10,60,80,20)
        self.editkey.setStyleSheet("color: white; font-size:6pt;")
        self.editkey.setPlaceholderText("Key")

        self.allGlobal_lbl = QLabel("Value", self)
        self.allGlobal_lbl.setGeometry(QtCore.QRect(75, 20, 40, 20))
        self.allGlobal_lbl.setStyleSheet("color: orange; font-size:4pt;")

        self.allGlobal_lbl = QLabel("All", self)
        self.allGlobal_lbl.setGeometry(QtCore.QRect(82, 42, 30, 20))
        self.allGlobal_lbl.setStyleSheet("color: pink; font-size:4pt;")

        self.keydata = ""

        self.getGlobal_timer = QtCore.QTimer(self)
        self.TimerBlinkCnt = 0
        self.BlinkingState = False

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.getGlobal_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['setGlobal'] = self.setGlobal_flag
        res['getGlobal'] = self.getGlobal_flag
        res['key'] = self.editkey.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']

            if 'key' in data:
                self.keydata = data['key']
                self.editkey.setText(self.keydata)

            if 'setGlobal' in data:
                self.setGlobal_flag = data['setGlobal']

                if self.setGlobal_flag:
                    self.setGlobal.setChecked(True)
                    self.getGlobal_timer.stop()
                    self.setGlobal.setStyleSheet("color: blue; font-size:5pt;font-weight:200;")

                else:
                    self.setGlobal.setChecked(False)
                    self.setGlobal.setStyleSheet("color: lightblue font-size:5pt;")

            if 'getGlobal' in data:
                self.getGlobal_flag = data['getGlobal']

                if self.getGlobal_flag:
                    self.getGlobal.setChecked(True)
                    self.getGlobal_timer.start()

                else:
                    self.getGlobal.setChecked(False)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_GLOBAL)
class Open_MySQL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_global.png"
    op_code = OP_NODE_GLOBAL
    op_title = "Global"
    content_label_objname = "Global"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[3,5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.eval()

    def initInnerClasses(self):
        self.content = MySQL(self)                   # <----------- init UI with data and widget
        self.grNode = FlowPayloadGlobal(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.Global = GlobalVariable()

        self.content.setGlobal.stateChanged.connect(self.setPayloadGlobal)
        self.content.getGlobal.stateChanged.connect(self.getPayloadGlobal)

        self.content.getGlobal_timer.timeout.connect(self.global_update_msg)
        #self.content.getGlobal_timer.setInterval(500)

    def evalImplementation(self):                       # <----------- Create Socket range Index

        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.rx_payload = input_node.eval()

        if self.rx_payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        else:  
            self.content.keydata = self.content.editkey.text()

            if self.content.setGlobal_flag:
                #print("self.content.setGlobal_flag = ", self.content.setGlobal_flag)
                #print("setGlobal , self.content.keydata = ", self.content.keydata)
                #print("setGlobal , self.rx_payload = ", self.rx_payload)

                if len(self.content.keydata) > 0:
                    if self.content.keydata == 'sql':
                            #print("Set Global key ",self.content.keydata, " , from result = ", self.rx_payload['msg'])
                            if 'msg' in self.rx_payload:
                                self.Global.setGlobal(self.content.keydata, str(self.rx_payload['msg']))

                            elif 'result' in self.rx_payload:
                                self.Global.setGlobal(self.content.keydata, str(self.rx_payload['result']))

                            elif 'sql' in self.rx_payload:
                                self.Global.setGlobal(self.content.keydata, str(self.rx_payload['sql']))
                    
                    else:
                        self.Global.setGlobal(self.content.keydata, self.rx_payload)

                    """if 'msg' in self.rx_payload:
                        if len(str(self.rx_payload['msg'])) > 0:
                            #print("Set Global key ",self.content.keydata, " , from msg = ", self.rx_payload['msg'])
                            self.Global.setGlobal(self.content.keydata, str(self.rx_payload['msg']))

                    elif 'result' in self.rx_payload:
                        if len(str(self.rx_payload['result'])) > 0:
                            #print("Set Global key ",self.content.keydata, " , from result = ", self.rx_payload['msg'])
                            self.Global.setGlobal(self.content.keydata, str(self.rx_payload['result']))

                    elif 'sql' in self.rx_payload:
                        if len(str(self.rx_payload['sql'])) > 0:
                            #print("Set Global key ",self.content.keydata, " , from result = ", self.rx_payload['msg'])
                            self.Global.setGlobal(self.content.keydata, str(self.rx_payload['sql']))
        
                    else:
                        self.Global.setGlobal(self.content.keydata, self.rx_payload)"""

    def setPayloadGlobal(self, state):
        if state == QtCore.Qt.Checked:
            self.content.setGlobal_flag = True
            self.content.getGlobal_flag = False
            self.content.getGlobal_timer.stop()
            self.content.getGlobal.setChecked(False)

            self.content.setGlobal.setStyleSheet("color: blue; font-size:5pt;font-weight:450;")

        else:
            self.content.setGlobal_flag = False

            self.content.setGlobal.setStyleSheet("color: lightblue; font-size:5pt;font-weight:200;")

            if self.Global.hasGlobal(self.content.editkey.text()):
                self.Global.removeGlobal(self.content.editkey.text())

    def getPayloadGlobal(self, state):
        if state == QtCore.Qt.Checked:
            self.content.getGlobal_flag = True
            self.content.setGlobal_flag = False
            self.content.getGlobal_timer.start()
            self.content.setGlobal.setChecked(False)

            self.content.setGlobal.setStyleSheet("color: lightblue; font-size:5pt;font-weight:200;")

        else:
            self.content.getGlobal.setText("getGlobal()")
            self.content.getGlobal_flag = False
            self.content.getGlobal_timer.stop()

    def global_update_msg(self):
        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                self.content.getGlobal.setText("getGlobal()")
                self.content.keydata = self.content.editkey.text()
                #print("self.content.keydata = ", self.content.keydata)

                self.content.setGlobal.setStyleSheet("color: lightblue; font-size:5pt;font-weight:200;")

                if len(self.content.keydata) > 0:
                    if self.Global.hasGlobal(self.content.keydata):
            
                        self.payload = self.Global.getGlobal(self.content.keydata)
                        #print("self.payload = ", self.payload)             
                        
                        self.sendFixOutputByIndex(self.payload, 0)  # <----------- Push payload to value

                key_list = []
                all_global_key = self.Global.allGlobal()[0]
                # print("len(all_global_key):", len(all_global_key))
                key_list = list(all_global_key)

                value_list = []
                all_global_value = self.Global.allGlobal()[1]
                # print("len(all_global_value):", len(all_global_value))

                value_list =  list(all_global_value)
                # print("value_list :", value_list)

                str_all_global = ""
                for i in range(len(value_list)):
                    if type(value_list[i]) == list:
                        if str(key_list[i]) != "GlobalTimerApplication" and str(key_list[i]) != "GlobalTerminalBoxID" and str(key_list[i]) != "StopMediaPlayer" \
                            and str(key_list[i]) != "GlobalTimerApplication" and str(key_list[i]) != "ListGlobalUSBDevice" and str(key_list[i]) != "ReQuestResizeGrAddr" \
                            and str(key_list[i]) != "teminal_pos_select" and str(key_list[i]) != "new_image_scale" and str(key_list[i]) != "teminal_selectpos" \
                            and str(key_list[i]) != "historydate" and str(key_list[i]) != "WebOTR" and str(key_list[i]) != "WS_Process" and str(key_list[i]) != "GlobalCameraBoxID" \
                            and str(key_list[i]) != "GlobalCameraApplication" and str(key_list[i]) != "Camera_MissingCH" and str(key_list[i]) != "Scan_USB_CameraSys":

                            str_all_global = str_all_global + str(key_list[i]) + " = " + str(value_list[i]) + "\n"

                    elif type(value_list[i]) == dict:
                        str_all_global = str_all_global + ""

                    elif type(value_list[i]) == bool:
                        if str(key_list[i]) == "ReadyChangeItemFrame":
                            str_all_global = str_all_global + ""
                    else:
                        str_all_global = str_all_global + str(key_list[i]) +" = " + str(value_list[i]) + "\n"
                
                # print("str_all_global:", str_all_global)

                # self.sendFixOutputByIndex('\n'.join(list(self.Global.allGlobal()[0])), 1)
                self.sendFixOutputByIndex(str_all_global, 1)

            else:
                self.content.getGlobal.setText("")
            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren(index)

  