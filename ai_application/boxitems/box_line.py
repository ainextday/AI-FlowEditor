from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 

import os
import requests
import cv2

class LineNotify(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.Path = os.path.dirname(os.path.abspath(__file__))
        print("Path = ", self.Path)

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"
        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        animate_process = self.Path + "/icons/icons_line.png"

        self.lblInput = QLabel("" , self)
        self.lblInput.setAlignment(Qt.AlignLeft)
        self.lblInput.setGeometry(10,5,100,20)
        self.lblInput.setStyleSheet("color: green; font-size:5pt;")

        self.lbl = QLabel("Img" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,20,45,20)
        self.lbl.setStyleSheet("color: lightblue; font-size:6pt;")

        self.lbl1 = QLabel("Text" , self)
        self.lbl1.setAlignment(Qt.AlignLeft)
        self.lbl1.setGeometry(10,43,85,20)
        self.lbl1.setStyleSheet("color: pink; font-size:6pt;")

        self.lbl2 = QLabel("Trigger" , self)
        self.lbl2.setAlignment(Qt.AlignLeft)
        self.lbl2.setGeometry(10,62,85,20)
        self.lbl2.setStyleSheet("color: orange; font-size:6pt;")

        self.lbl2 = QLabel("Res" , self)
        self.lbl2.setAlignment(Qt.AlignLeft)
        self.lbl2.setGeometry(125,30,45,20)
        self.lbl2.setStyleSheet("color: yellow; font-size:6pt;")

        self.On_Notify = QPushButton(self)
        self.On_Notify.setGeometry(105,5,37,20)
        self.On_Notify.setIcon(QIcon(self.off_icon))
        self.On_Notify.setIconSize(QtCore.QSize(37,20))
        self.On_Notify.setStyleSheet("background-color: transparent; border: 0px;")  

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(120,50,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.edit = QLineEdit(self)
        self.edit.setGeometry(5,77,140,18)
        self.edit.setPlaceholderText("Topic Name")
        self.edit.setAlignment(QtCore.Qt.AlignCenter)
        self.edit.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:8pt;color:white; border: 1px solid white; border-radius: 3%;")

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        # graphicsView.resize(30,30)
        graphicsView.setGeometry(QtCore.QRect(60, 25, 50, 50))

        img = QPixmap(animate_process)
        self.pixmap.setPixmap(img)
        #====================================================

        self.msgAlert = QMessageBox()
        self.msgAlert.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msgAlert.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msgAlert.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #====================================================

        self.lineGlobal_timer = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.lineGlobal_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)


        self.On_Notify_flag = False
        self.line_tokkenize = ""
        self.line_message = ""
        self.topic_name = ""
        self.url = "https://notify-api.line.me/api/notify"

        self.global_key = ""

    def serialize(self):
        res = super().serialize()
        res['notify_flag'] = self.On_Notify_flag
        res['line_tokken'] = self.line_tokkenize
        res['message'] = self.line_message
        res['topic'] = self.topic_name
        res['url'] = self.url
        res['global_key'] = self.global_key

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'notify_flag' in data:
                self.On_Notify_flag = data['notify_flag']
                if self.On_Notify_flag:
                    self.On_Notify.setIcon(QIcon(self.on_icon))

                else:
                    self.On_Notify.setIcon(QIcon(self.off_icon))

            if 'line_tokken' in data:
                self.line_tokkenize = data['line_tokken']

            if 'message' in data:
                self.line_message = data['message']

            if 'topic' in data:
                self.topic_name = data['topic']

            if 'url' in data:
                self.url = data['url']

            if 'global_key' in data:
                self.global_key = data['global_key']
                if len(self.global_key) > 0:
                    self.lineGlobal_timer.start()
                else:
                    self.lineGlobal_timer.stop()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

# ===========================================================
class LineSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class LineSetting ---> Line Setting Function')

        self.content = content
        self.line_tokken = self.content.line_tokkenize
        self.line_message = self.content.line_message
        self.url = self.content.url
        self.key_global = self.content.global_key

        self.title = "LINE Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 400
        self.height = 470
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        #================================================
        # LINE TOKKEN
        self.lbl = QLabel("LINE TOKKEN : ", self)
        self.lbl.setGeometry(QtCore.QRect(10, 5, 120, 20))
        self.lbl.setStyleSheet("color: #42E3C8;")

        self.editTokken = QLineEdit("",self)
        # self.editTokken.setFixedWidth(380)
        self.editTokken.setGeometry(10,30,380,30)
        self.editTokken.setPlaceholderText("LINE TOKKEN")
        self.editTokken.setText(self.line_tokken)

        #================================================
        # Message
        self.lbl1 = QLabel("Fix Message : ", self)
        self.lbl1.setGeometry(QtCore.QRect(10, 90, 100, 20))
        self.lbl1.setStyleSheet("color: #FF9EAA;")

        self.QPlainTextEdit = QtWidgets.QPlainTextEdit(self)
        self.QPlainTextEdit.setGeometry(10, 120, 380, 150) 
        self.QPlainTextEdit.setStyleSheet("color: lightblue; font-size:12pt;")
        self.QPlainTextEdit.setPlainText(self.line_message)

        #================================================
        # Global Key
        self.lbl2 = QLabel("Global Key : ", self)
        self.lbl2.setGeometry(QtCore.QRect(10, 292, 80, 20))
        self.lbl2.setStyleSheet("color: #42E3C8;")

        self.editKey = QLineEdit("",self)
        # self.editKey.setFixedWidth(380)
        self.editKey.setGeometry(110,290,280,30)
        self.editKey.setText(self.key_global)
        self.editKey.setPlaceholderText("Key")

        #================================================
        # URL
        self.lbl3 = QLabel("URL : ", self)
        self.lbl3.setGeometry(QtCore.QRect(10, 330, 50, 20))
        self.lbl3.setStyleSheet("color: #FFDD00;")

        self.editURL = QLineEdit("",self)
        # self.editURL.setFixedWidth(380)
        self.editURL.setGeometry(10,360,380,30)
        self.editURL.setText(self.url)

        #================================================
        # Video Cloud
        self.lbl4 = QLabel("Video Cloud : ", self)
        self.lbl4.setGeometry(QtCore.QRect(10, 400, 100, 20))
        self.lbl4.setStyleSheet("color: orange;")

        self.editCloud = QLineEdit("",self)
        # self.editCloud.setFixedWidth(380)
        self.editCloud.setGeometry(10,430,380,30)
        self.editCloud.setText("")

    def closeEvent(self, event):
        self.content.line_tokkenize = self.editTokken.text()
        self.content.line_message = self.QPlainTextEdit.toPlainText()
        self.content.url = self.editURL.text()
        self.content.global_key = self.editKey.text()

# ===========================================================
@register_node(OP_NODE_LINENOTIFY)
class Open_LineNotify(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_line.png"
    op_code = OP_NODE_LINENOTIFY
    op_title = "Line Notify"
    content_label_objname = "Line Notify"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1,2,3], outputs=[1]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        
        self.payload = {}
        self.in_payload = {}
        self.in_payload1 = {}
        self.in_payload2 = {}

        self.payload_cnt = 0
        self.data = {'message':''}
        self.res = ""

        self.addon_msg = ""
        self.Global_Message = ""

        self.image = None
        self.file = {'imageFile':None}
        self.process_flag = False

    def initInnerClasses(self):
        self.content = LineNotify(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.Global = GlobalVariable()

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)
        self.content.On_Notify.clicked.connect(self.OnNotify)

        self.content.lineGlobal_timer.timeout.connect(self.check_send_withGlobal)
        self.content.lineGlobal_timer.setInterval(50)
        self.content.lineGlobal_timer.start()

    def evalImplementation(self):                 # <
        # Image Input
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.in_payload = input_node.eval()

            if self.in_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                # Process Payload Here !!!
                if 'img' in self.in_payload:
                    self.image = self.in_payload['img']

        # ============================================================
        # Payload
        input_node1 = self.getInput(1)
        if not input_node1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.in_payload1 = input_node1.eval()

            if self.in_payload1 is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                if 'msg' in self.in_payload1:
                    self.addon_msg = self.in_payload1['msg']

        # ======================================================
        # Trigger
        input_node2 = self.getInput(2)
        if not input_node2:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.in_payload2 = input_node2.eval()

            if self.in_payload2 is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                # Process Payload Here !!!
                if "submit" in self.in_payload2: 
                    if self.in_payload2["submit"]:
                        # print("process send Line notify")
                        self.payload_cnt += 1

                        print("self.payload_cnt : ", self.payload_cnt)
                        if self.payload_cnt >= 1 and self.content.On_Notify_flag and not self.process_flag:
                            self.process_flag = True
                            # print("process send Line notify")
                            self.content.lblInput.setText("Processing...")
                            self.process_send_Line()

                    else: 
                        self.payload_cnt = 0
                        self.process_flag = False

                if "result" in self.in_payload2: 
                    if self.in_payload2["result"]:
                        # print("process send Line notify")
                        self.payload_cnt += 1

                        # print("self.payload_cnt : ", self.payload_cnt)
                        if self.payload_cnt >= 1 and self.content.On_Notify_flag and not self.process_flag:
                            self.process_flag = True
                            # print("process send Line notify")
                            self.content.lblInput.setText("Processing...")
                            self.process_send_Line()

                    else: 
                        self.payload_cnt = 0
                        self.process_flag = False


    def process_send_Line(self):
        if len(self.content.line_tokkenize) > 0:
            LINE_HEADERS = {"Authorization":"Bearer " + self.content.line_tokkenize }
            
            if len(self.content.line_message) > 0:
                self.data['message'] = self.content.line_message

                if len(self.addon_msg) > 0 and len(self.Global_Message) > 0:
                    self.data['message'] = self.content.line_message + "\n" + self.addon_msg + "\n" + self.Global_Message
                    # print("Data Message Step 1")

                elif len(self.addon_msg) > 0:
                    self.data['message'] = self.content.line_message + "\n" + self.addon_msg
                    # print("Data Message Step 2")

                elif len(self.Global_Message) > 0:
                    if type(self.Global_Message) == type(str):
                        self.data['message'] = self.content.line_message + "\n" + self.Global_Message

                    elif type(self.Global_Message) == type(dict):
                        self.data['message'] = str(self.content.line_message) + "\n" + str(self.Global_Message['result'])
                        # print("Data Message Step 3")

            else:
                if len(self.addon_msg) > 0 and len(self.Global_Message) > 0:
                    self.data['message'] = self.addon_msg + "\n" + self.Global_Message

                elif len(self.addon_msg) > 0:
                    self.data['message'] = self.addon_msg

                elif len(self.Global_Message) > 0:
                    self.data['message'] = self.Global_Message
                    
            # print(self.data)

            if type(self.image) != type(None):
                # print("self.image : ", self.image)
                if len(self.image) > 100:
                    Image_Parth = self.Path + '/tempdata/Line_ImageCapture.png'
                    cv2.imwrite(Image_Parth, self.image)
                    
                    self.file = {'imageFile':open(Image_Parth,'rb')}
                    # print(self.file)
            
            # print("URL :", self.content.url)

            session = requests.Session()
            self.res = session.post(self.content.url, headers=LINE_HEADERS, files=self.file, data=self.data)

            print("Line Respond : ", self.res.text)
            self.payload['result'] = eval(self.res.text)['message'] 
            if self.payload['result'] == "ok":
                if self.Global.hasGlobal(self.content.global_key):
                    self.Global.removeGlobal(self.content.global_key)

            else:
                self.content.msgAlert.setText("Something Wrong !!!, \nPlease check setting or network")
                retv = self.content.msgAlert.exec_()
                self.Global.removeGlobal(self.content.global_key)

            self.value = self.payload
            self.markDirty(False)
            self.markInvalid(False)

            self.markDescendantsInvalid(False)
            self.markDescendantsDirty()

            #self.grNode.setToolTip("")
            self.evalChildren()

            self.content.lblInput.setText("")
            

        else:
            self.content.msgAlert.setText("Line Tokkenize not exist, \nNeed to add LINE TOKKEN first")
            retval = self.content.msgAlert.exec_()
            # print(retval)


    def OnNotify(self):
        if not self.content.On_Notify_flag:
            self.content.On_Notify.setIcon(QIcon(self.content.on_icon))
            
        else:
            self.content.On_Notify.setIcon(QIcon(self.content.off_icon))

        self.content.On_Notify_flag = not self.content.On_Notify_flag

    def check_send_withGlobal(self):
        if self.Global.hasGlobal(self.content.global_key) and self.content.On_Notify_flag:
            if type(self.Global.getGlobal(self.content.global_key)) != type(None): # is not None

                # print("self.content.global_key :", self.content.global_key)
                # print("self.Global.getGlobal(self.content.global_key) : ", self.Global.getGlobal(self.content.global_key))

                self.Global_Message = self.Global.getGlobal(self.content.global_key)
                # print("Global_Message : ", self.Global_Message)
                # print("type(Global_Message) : ", type(self.Global_Message))

                self.process_send_Line()

    def OnOpen_Setting(self):
        self.LINE_Setting = LineSetting(self.content)
        self.LINE_Setting.show()
