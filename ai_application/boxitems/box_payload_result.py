from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import*
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import datetime

class Ui_Result_MainWindow(object):
    def setupUi(self, MainWindow):
        self.top    = 25
        self.left   = 5
        self.width  = 255
        self.height = 109
        self.MainWindow = MainWindow
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 

        self.graphicsView = QGraphicsView(self.MainWindow)
        self.graphicsView.resize(255,82)
        self.graphicsView.setGeometry(QtCore.QRect(0, 2, 255, 82))

        self.scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()

        self.edit = QLineEdit(self.MainWindow)
        self.edit.setGeometry(40,5,125,20)
        
        self.label = QLabel("Result", self.MainWindow)
        self.label.setGeometry(30,29,180,35)

        self.lcd = QLCDNumber(self.MainWindow, digitCount=8)
        self.lcd.setGeometry(40,29,180,35)

        self.ResizeBtn = QPushButton(self.MainWindow)
        self.ResizeBtn.setGeometry(242, 72,10,10)

        self.SettingBtn = QPushButton(self.MainWindow)
        self.SettingBtn.setGeometry(230,5,20,20)

class PAYLOADRESULT(QDMNodeContentWidget):
    resized = pyqtSignal()

    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.bgImage = self.Path + "/icons/icons_tube_re.png"

        self.icon_round_btn = self.Path + "/icons/icons_btn_round10x10.png"
        self.icon_round_green = self.Path + "/icons/icons_btn_round10x10_green.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"

        self.Frame_w = 255
        self.Frame_h = 109 

        self.ui = Ui_Result_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)
        
        self.img = QPixmap(self.bgImage)
        self.ui.pixmap.setPixmap(self.img)

        self.ui.scene.addItem(self.ui.pixmap)
        self.ui.graphicsView.setScene(self.ui.scene)

        self.ui.SettingBtn.setIcon(QIcon(self.setting_icon))
       
        self.ui.edit.setPlaceholderText("---")
        self.ui.edit.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.edit.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:8pt;color:white; border: 1px solid white; border-radius: 3%;")
        
        self.font_color = "#00FFFF"
        
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.label.setFont(QFont('Tahoma', 12))
        self.ui.label.setStyleSheet("background-color: black; 'font-family: Tahoma; 'font-size:12pt; color:"+ self.font_color + ";")

        self.font_scale = 12
        self.font_data = "background-color: black; black; font-size:" + str(self.font_scale) + "pt; color:"+ self.font_color + ";"

        #create QLCDNumber object

        #give background color for the lcd number
        self.ui.lcd.setStyleSheet("""QLCDNumber { 
            background-color: rgba(0, 170, 255, 20); 
            color: lightblue; }""")

        self.ui.lcd.setVisible(False)

        self.ui.ResizeBtn.setIcon(QIcon(self.icon_round_btn))
        self.ui.ResizeBtn.setStyleSheet("background-color: transparent; border: 0px;")

        self.ResizeFrame_timer = QtCore.QTimer(self)

        self.resize_result = False
        self.resized.connect(self.ReDrawGeometry)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.Data
        res['comment'] = self.ui.edit.text()
        res['resize'] = self.resize_result
        res['new_width'] = self.Frame_w
        res['new_height'] = self.Frame_h

        res['font_scale'] = self.font_scale
        res['font_color'] = self.font_color
        
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            if 'comment' in data:
                self.ui.edit.setText(str(data['comment']))
            
            if 'resize' in data:
                self.resize_result = data['resize']
                if self.resize_result:
                    if 'new_width' in data:
                        self.Frame_w = data['new_width']

                    if 'new_height' in data:
                        self.Frame_h = data['new_height']

                    self.ReDrawGeometry()

            if 'font_scale' in data:
                self.font_scale = data['font_scale']

            if 'font_color' in data:
                self.font_color = data['font_color']

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    #================================================
    def ReDrawGeometry(self):
        # print("ReDrawGeometry Frame_w = ", self.Frame_w, " ; self.Frame_h = ", self.Frame_h)
        scale_width = self.Frame_w/255
        scale_height = self.Frame_h/109
    
        self.ui.MainWindow.setGeometry(2, 27, int(self.Frame_w), int(self.Frame_h - 5)) 
        self.ui.pixmap.setPixmap(self.img.scaled(int(self.Frame_w - 10), int(self.Frame_h - 35), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.ui.pixmap.update()
        self.ui.graphicsView.setGeometry(QtCore.QRect(0, 2, int(self.Frame_w - 5), int(self.Frame_h - 30)))

        # print("Scale Width = ", scale_width)
        # print("Scale Height = ", scale_height)

        self.ui.label.setGeometry(int(30*scale_width),int(29*scale_height), int(180*scale_width), int(33*scale_height))
        self.font_scale = int(18*scale_height)
        self.font_data = "background-color: black; black; font-size:" + str(self.font_scale) + "pt; color:lightblue;"
        self.ui.label.setStyleSheet(self.font_data)

        # lcd_data = """QLCDNumber { 
        #     background-color: rgba(0, 170, 
        # self.ui.lcd.setStyleSheet(255, 20); 
        #     color: lightblue; }""")

        self.ui.SettingBtn.setGeometry(int(self.Frame_w) - 30 ,5,20,20)

        # self.ui.lcd.setGeometry(40,29,180,35)
        self.ui.lcd.setGeometry(int(40*scale_width), int(29*scale_height), int(180*scale_width), int(35*scale_height))

        self.ui.ResizeBtn.setGeometry(int(self.Frame_w - 15), int(self.Frame_h - 43), 10, 10)

# ====================================================================================================
# ====================================================================================================
class ResultSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content
        # print("self.content :", self.content)

        self.title = "Result Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 1200
        self.height = 720
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.current_font_lbl = QLabel("Current Font Scale" , self)
        self.current_font_lbl.setAlignment(Qt.AlignLeft)
        self.current_font_lbl.setGeometry(10,50,240,30)
        self.current_font_lbl.setStyleSheet("color: yellow; font-size:12pt;")

        self.Scale_font_lbl = QLabel(self)
        self.Scale_font_lbl.setAlignment(Qt.AlignLeft)
        self.Scale_font_lbl.setGeometry(250,50,50,30)
        self.Scale_font_lbl.setStyleSheet("color: yellow; font-size:12pt;")

        self.Scale_font_lbl.setText(str(self.content.font_scale))

        self.Update_increase = QPushButton("+", self)
        self.Update_increase.setGeometry(250,10,50,35)
        self.Update_increase.clicked.connect(self.onUpdateIncrease)

        self.Update_decrease = QPushButton("-", self)
        self.Update_decrease.setGeometry(250,90,50,35)
        self.Update_decrease.clicked.connect(self.onUpdateDecrease)

        self.color_font_lbl = QLabel("Font Color" , self)
        self.color_font_lbl.setAlignment(Qt.AlignLeft)
        self.color_font_lbl.setGeometry(10,130,150,40)
        self.color_font_lbl.setStyleSheet("color: green; font-size:12pt;")

        self._font_lbl = QLabel("#97E8FF", self)
        self._font_lbl.setAlignment(Qt.AlignLeft)
        self._font_lbl.setGeometry(160,130,150,40)
        self._font_lbl.setStyleSheet("color: green; font-size:12pt;")

        # =========================================================
        # Define the table dimensions
        num_rows = 5
        num_columns = 7
        cell_size = 60  # Cell size in pixels for a square

        # Initialize the table widget without adding it to a layout
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(num_rows)  
        self.tableWidget.setColumnCount(num_columns)
        self.tableWidget.setGeometry(10, 185, 450, 350)

        # Set each row and column to be square-shaped
        for i in range(num_columns):
            self.tableWidget.setColumnWidth(i, cell_size)
        for i in range(num_rows):
            self.tableWidget.setRowHeight(i, cell_size)

        # List of colors to display
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#97E8FF", "#CBCEF1",
                  "#00FFFF", "#800000", "#808000", "#008080", "#800080", "#B91477", "#FCFAF9",
                  "#FFA500", "#A52A2A", "#8B4513", "#2F4F4F", "#DEB887", "#5BC8FF", "#BAEAE6",
                  "#5F9EA0", "#7FFF00", "#D2691E", "#FF7F50", "#6495ED", "#FFD06E", "#F0CFEC",
                  "#489BF2", "#FF766E", "#334B8A", "#2FA38A", "#FEFDFB", "#FAEFE8", "#FEFADA"]

        # Populate the table with colors
        for i, color in enumerate(colors):
            row, col = divmod(i, num_columns)
            item = QTableWidgetItem()
            item.setBackground(QColor(color))
            self.tableWidget.setItem(row, col, item)

        # Event to capture the click
        self.tableWidget.cellClicked.connect(self.cell_clicked)
        self.font_color = None
        

    def cell_clicked(self, row, column):
        item = self.tableWidget.item(row, column)
        if item is not None:  # Check if the item is not None
            color = item.background().color()
            self.content.font_color = color.name()
            # print(f"Selected color: {self.content.font_color}")

            self._font_lbl.setText(self.content.font_color)

    def onUpdateIncrease(self):
        self.content.font_scale +=  1
        self.Scale_font_lbl.setText(str(self.content.font_scale))

    def onUpdateDecrease(self):
        self.content.font_scale -= 1
        self.Scale_font_lbl.setText(str(self.content.font_scale))
        if self.content.font_scale < 5:
            self.content.font_scale = 5
            self.Scale_font_lbl.setText(str(self.content.font_scale))

    def closeEvent(self, event):
        self.content.ui.SettingBtn.setEnabled(True)

@register_node(OP_NODE_PAYLOADRESULT)
class Open_PAYLOADRESULT(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_lcd_green_icon.jpg"
    op_code = OP_NODE_PAYLOADRESULT
    op_title = "Result"
    content_label_objname = "Result"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.payload['result'] = None

    def initInnerClasses(self):
        self.content = PAYLOADRESULT(self)                   # <----------- init UI with data and widget
        self.grNode = FlowKeyLCDLabel(self)          # <----------- Box Image Draw in Flow_Node_Base

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

        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.payload = input_node.eval()

        if self.payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return

        elif 'result' in self.payload and self.payload['result'] is not None:
            self.content.ui.label.setVisible(True)

            if len(str(self.payload["result"])) > 0:
                #print("Payload Input")
                #print(len(str(self.payload['result'])))
                if len(str(self.payload['result'])) > 10:
                    self.font_data = "background-color: black; black; font-size:" + str(self.content.font_scale) + "pt; color:" + self.content.font_color+ ";"
                    self.content.ui.label.setStyleSheet(self.font_data)
                    
                else:
                    self.font_data = "background-color: black; black; font-size:" + str(self.content.font_scale + 6) + "pt; color:" + self.content.font_color + ";"
                    self.content.ui.label.setStyleSheet(self.font_data)

                self.content.ui.label.setText(str(self.payload['result']))

        elif 'clock' in self.payload and self.payload['clock'] is not None:
            if len(self.payload["clock"]) > 0:
                #print("type(self.payload['clock']) = ", type(self.payload['clock']))

                #self.content.label.setStyleSheet("background-color: black; font-size:30pt; color:lightblue;")
                #self.content.label.setText(str(self.payload['clock']))

                self.content.ui.label.setVisible(False)
                self.content.ui.lcd.setVisible(True)
                #displat the system time in the lcd
                self.content.ui.lcd.display(str(self.payload['clock']))

    #=============================================================
    # Resizeable
    def StartResize_ItemFram(self):
        if not self.Global.getGlobal("ReadyChangeItemFrame"):
            # print("start resize Terminal")
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
        self.CAM_Setting = ResultSetting(self.content)
        self.CAM_Setting.show()
        self.content.ui.SettingBtn.setEnabled(False)

