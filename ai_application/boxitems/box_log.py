from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 

import datetime
import os
import re

class Ui_Log_MainWindow(object):
    def setupUi(self, MainWindow):
        self.top    = 25
        self.left   = 5
        self.width  = 255
        self.height = 109
        self.MainWindow = MainWindow
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 

        self.lbl = QLabel("Log Titel Name" , self.MainWindow)
        self.lbl.setStyleSheet("background-color: rgba(0, 57, 94, 150);font-size:15pt;color:lightblue;")
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(15,2,220,35)

        self.LogText = QPlainTextEdit("" , self.MainWindow)
        # self.LogText.setAlignment(Qt.AlignLeft)
        self.LogText.setGeometry(10,50,280,400)

        self.saveBtn = QPushButton(self.MainWindow)
        self.saveBtn.setGeometry(250,5,20,20)

        #====================================================
        self.resetBtn = QPushButton(self.MainWindow)
        self.resetBtn.setGeometry(275,5,20,20)

        self.ResizeBtn = QPushButton(self.MainWindow)
        self.ResizeBtn.setGeometry(285, 445,10,10)

        self.SettingBtn = QPushButton(self.MainWindow)
        self.SettingBtn.setGeometry(260,410,20,20)

class LOGRecord(QDMNodeContentWidget):
    resized = pyqtSignal()

    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.save_icon = self.Path + "/icons/icons_save_icon_30.png"
        self.refresh_icon = self.Path + "/icons/icons_refresh.png"

        self.icon_round_btn = self.Path + "/icons/icons_btn_round10x10.png"
        self.icon_round_green = self.Path + "/icons/icons_btn_round10x10_green.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"

        self.width = 240
        self.height = 40

        self.edge_ruondness = 5.0
        self._brush_background = QBrush(QColor(0, 57, 94, 150))      #QColor with transparent 

        self.Frame_w = 255
        self.Frame_h = 109 

        self.ui = Ui_Log_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.font_size = 13
        self.change_StylSheet = "background-color: rgba(0, 124, 212, 50);font-size:"+ str(self.font_size) + "pt;color:lightblue;"
        self.ui.LogText.setStyleSheet(self.change_StylSheet )

        self.ui.saveBtn.setIcon(QIcon(self.save_icon))
        self.ui.resetBtn.setIcon(QIcon(self.refresh_icon))

        self.ui.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.ui.ResizeBtn.setIcon(QIcon(self.icon_round_btn))
        self.ui.ResizeBtn.setStyleSheet("background-color: transparent; border: 0px;")

        self.red_keyword = "NG"
        self.green_keyword = "OK"
        self.yellow_keyword = "warning"

        self.highlighter = LogHighlighter(self.ui.LogText.document())

        self.ResizeFrame_timer = QtCore.QTimer(self)

        self.resize_result = False
        self.resized.connect(self.ReDrawGeometry)

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['font_size'] = self.font_size
        res['red_keyword'] = self.red_keyword
        res['green_keyword'] = self.green_keyword
        res['yellow_keyword'] = self.yellow_keyword

        res['resize'] = self.resize_result
        res['new_width'] = self.Frame_w
        res['new_height'] = self.Frame_h
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']

            if 'font_size' in data:
                self.font_size = data['font_size']
                self.ui.LogText.setStyleSheet(self.change_StylSheet)

            if 'red_keyword' in data:
                self.red_keyword = data['red_keyword']

            if 'green_keyword' in data:
                self.green_keyword = data['green_keyword']

            if 'yellow_keyword' in data:
                self.yellow_keyword = data['yellow_keyword']

            if 'resize' in data:
                self.resize_result = data['resize']
                if self.resize_result:
                    if 'new_width' in data:
                        self.Frame_w = data['new_width']

                    if 'new_height' in data:
                        self.Frame_h = data['new_height']

                    self.ReDrawGeometry()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def paintEvent(self, event):
        # title
        path_outline = QPainterPath()
        path_outline.addRoundedRect(5, 0, self.width, self.height, self.edge_ruondness, self.edge_ruondness)
        
        painter = QPainter()
        painter.begin(self)

        pen = QPen(QColor("#FFA5FBFF"), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_outline.simplified())

        #================================================
    def ReDrawGeometry(self):
        # print("ReDrawGeometry Frame_w = ", self.Frame_w, " ; self.Frame_h = ", self.Frame_h)
        self.ui.MainWindow.setGeometry(2, 27, int(self.Frame_w), int(self.Frame_h - 5)) 
        self.ui.LogText.setGeometry(10,50,int(self.Frame_w - 20) , int(self.Frame_h - 90))
        self.ui.ResizeBtn.setGeometry(int(self.Frame_w - 15), int(self.Frame_h - 43), 10, 10)
        self.ui.SettingBtn.setGeometry(int(self.Frame_w - 40), int(self.Frame_h - 65), 20, 20)

# =============================================================================================
class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(LogHighlighter, self).__init__(parent)

        self.list_red_color = ["NG"]
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(255, 0, 0, 255))
        #keyword_format.setFontWeight(QFont.Bold)
        self.highlighting_rules = [(re.compile(r"\b%s\b" % keyword), keyword_format) for keyword in self.list_red_color]

        # Light Green Color
        self.list_green_color    = ["OK"]      
        key_green_format = QTextCharFormat()
        key_green_format.setForeground(QColor(11, 255, 118, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_green_format) for keyword in self.list_green_color]

        # Yellow Color 
        self.list_yellow_color   = ["warning"]
        key_payload_format = QTextCharFormat()
        key_payload_format.setForeground(QColor(255, 252, 175, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_payload_format) for keyword in self.list_yellow_color]

    # Hidden Function
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

# =============================================================================================
# =============================================================================================
class LogSetting_Function(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class LogSetting_Function ---> LogSetting_Function')

        self.content = content
        self.xml_dir = ""
        self.out_dir = ""
        self.class_file = ""

        self.file_number = 0

        self.red_keyword = self.content.red_keyword
        self.green_keyword = self.content.green_keyword
        self.yellow_keyword = self.content.yellow_keyword

        self.title = "LogSetting_Function"
        self.top    = 300
        self.left   = 600
        self.width  = 1200
        self.height = 550
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.highlighter = LogHighlighter(self.content.ui.LogText.document())

    def closeEvent(self, event):
        self.content.ui.SettingBtn.setEnabled(True)

# =============================================================================================
# =============================================================================================

@register_node(OP_NODE_LOG)
class Open_Log(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_log.png"
    op_code = OP_NODE_LOG
    op_title = "Log"
    content_label_objname = "Log"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        
        self.TextShowLog = ""
        #self.LogLine = 0

    def initInnerClasses(self):
        self.content = LOGRecord(self)                   # <----------- init UI with data and widget
        self.grNode = FlowLogRecord(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.ui.resetBtn.clicked.connect(self.ResetAllLog)
        self.content.ui.saveBtn.clicked.connect(self.OnSaveLog)

        self.content.ui.SettingBtn.clicked.connect(self.OnOpen_Setting)

        #=============================================================
        # Resizeable
        self.grNode_addr = str(self.grNode)[-13:-1]
        print("Python Function ---> grNode_addr = ", self.grNode_addr)

        self.BoxKey = "ChangeItemFrame:" + self.grNode_addr
        print("self.BoxKey = ", self.BoxKey)

        self.content.ui.ResizeBtn.clicked.connect(self.StartResize_ItemFram)
        self.content.ResizeFrame_timer.timeout.connect(self.update_ItemFrame)

        self.Global = GlobalVariable()
        self.Global.setGlobal("ReadyChangeItemFrame", False)

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
            if 'logtitlename' in self.rx_payload:
                self.content.ui.lbl.setText(str(self.rx_payload['logtitlename']))

            if 'log' in self.rx_payload and self.rx_payload['log'] is not None:
                #print("self.rx_payload['log'] = ", self.rx_payload['log'])
                self.content.ui.LogText.setPlainText(str(self.rx_payload['log']))
                self.content.ui.LogText.verticalScrollBar().setVisible(False)
                self.content.ui.LogText.verticalScrollBar().setValue(self.content.ui.LogText.verticalScrollBar().maximum())
                
                # self.TextShowLog = ""
                
                # for i in range(len(str(self.rx_payload['log']))):
                #     if "In" in str(self.rx_payload['log'][i]):
                #         self.TextShowLog = self.TextShowLog + f"<span style=\"color:#6495ED;\" > {str(self.rx_payload['log'][i])} </span>" + "<br>"
                #         print("Log InStd")
                #     else :
                #         self.TextShowLog = self.TextShowLog + f"<span style=\"color:#ff0000;\" > {str(self.rx_payload['log'][i])} </span>" + "<br>"
                #         print("Log OutStd")

                
                # self.content.ui.LogText.setHtml(self.TextShowLog)
                # self.content.ui.LogText.verticalScrollBar().setValue(self.content.ui.LogText.verticalScrollBar().maximum())
                # #self.LogLine += 1
                # #print("self.LogLine = ", self.LogLine)

                # self.rx_payload['log'] = None

    def ResetAllLog(self):
        self.rx_payload['log'] = None
        self.content.ui.LogText.setPlainText("")
        #self.LogLine = 0

        self.Global.setGlobal("reset_log", True)

    def OnSaveLog(self):
        print("Save Log")

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            #print(fileName)

            file = open(fileName,'w', encoding="utf-8")
            #text = self.textEdit.toPlainText()
            
            file.write(self.TextShowLog)
            file.close()

        #=============================================================
    # Resizeable
    def StartResize_ItemFram(self):
        if not self.Global.getGlobal("ReadyChangeItemFrame"):
            # print("start resize Log")
            self.content.ui.ResizeBtn.setIcon(QIcon(self.content.icon_round_green))
            self.content.ResizeFrame_timer.start()

            self.startTime = datetime.datetime.now().replace(microsecond=0)
            # print("self.startTime = ", self.startTime)
            self.Global.setGlobal("ReadyChangeItemFrame", True)
            self.Global.setGlobal("ReQuestResizeGrAddr", self.grNode_addr)

    def update_ItemFrame(self):
        if self.Global.hasGlobal("ReadyChangeItemFrame"):
            if self.Global.getGlobal("ReadyChangeItemFrame"):

                NowTime = datetime.datetime.now().replace(microsecond=0)
                # print("NowTime = ", NowTime)
                updateTime = NowTime - self.startTime
                minutessince = int(updateTime.total_seconds() / 10)

                if minutessince >= 2:
                    self.content.ResizeFrame_timer.stop()
                    self.content.ui.ResizeBtn.setIcon(QIcon(self.content.icon_round_btn))
                    # print("Stop Resize")
                    self.Global.removeGlobal(self.BoxKey)
                    self.Global.setGlobal("ReadyChangeItemFrame", False)
                
                if self.Global.hasGlobal(self.BoxKey):

                    self.content.Frame_w = self.Global.getGlobal(self.BoxKey)[0]
                    self.content.Frame_h = self.Global.getGlobal(self.BoxKey)[1]

                    self.content.resized.emit()
                    self.content.resize_result = True

            else:
                self.content.ResizeFrame_timer.stop()
                self.content.ui.ResizeBtn.setIcon(QIcon(self.content.icon_round_btn))
                # print("Stop Resize")
                self.Global.removeGlobal(self.BoxKey)

    def OnOpen_Setting(self):

        self.content.ui.SettingBtn.setEnabled(False)
        self.LogSetting_Function = LogSetting_Function(self.content)
        self.LogSetting_Function.show()
            
