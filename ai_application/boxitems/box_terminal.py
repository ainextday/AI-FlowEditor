from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtChart import QCandlestickSeries, QChart, QChartView, QCandlestickSet
from PyQt5 import QtChart as qc

import time, sys

#******************************************************************
# from pyqtgraph.Qt import QtCore, QtGui
#import pyqtgraph.opengl as gl
import numpy as np

# from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from random import randint
#******************************************************************

import datetime
import base64

class Ui_Terminal_MainWindow(object):
    def setupUi(self, MainWindow):
        #=======================================

        self.top    = 25
        self.left   = 5
        self.width  = 320
        self.height = 240
        self.MainWindow = MainWindow
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 

        self.Tlabel = QTextEdit("" , self.MainWindow)
        self.Tlabel.setGeometry(2,2,320,240)

        self.lbl = QLabel("" , self.MainWindow)
        self.lbl.setGeometry(2,2,320,240)

        self.graphWidget = pg.PlotWidget(self.MainWindow)
        self.graphWidget.setGeometry(2,2,320,240)

        # =======================================
        # New Update for terminal with QChart
        #========================================
        #QChart
        self.chart = QChart()
        self.chartview = QChartView(self.chart, self.MainWindow)

        #========================================

        self.GraphTitleLable = QLabel("Title", self.MainWindow)

        self.GraphName1 = QLabel("", self.MainWindow)
        self.GraphName2 = QLabel("", self.MainWindow)

        self.lblSetting = QLabel(self.MainWindow)
        self.lblSetting.setGeometry(2,205,318,30)

        self.TextBtn = QPushButton("Payload", self.MainWindow)
        self.TextBtn.setGeometry(7, 210 ,75,20)

        self.ImgBtn = QPushButton("Image", self.MainWindow)
        self.ImgBtn.setGeometry(87, 210,75,20)

        self.GraphBtn = QPushButton("Graph", self.MainWindow)
        self.GraphBtn.setGeometry(167, 210,75,20)

        self.checkBlue = QCheckBox("Blue",self.MainWindow)
        self.checkBlue.setGeometry(247, 210,70,20)

        self.UpdatePosBtn = QPushButton("Update Position", self.MainWindow)
        self.UpdatePosBtn.setGeometry(312, 210,135,20)

        self.status_mouse_pos = QLabel(" Pos : [ 000 , 000 ]" , self.MainWindow)
        self.status_mouse_pos.setGeometry(452, 210,150,20)

        self.ShowBtn = QPushButton(self.MainWindow)
        self.ShowBtn.setGeometry(295, 210,20,20)        #597

        self.ResizeBtn = QPushButton(self.MainWindow)
        self.ResizeBtn.setGeometry(310, 230,10,10)

        #========================================
        
        
class TerminalDebug(QDMNodeContentWidget):
    resized = pyqtSignal()

    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.show_icon = self.Path + "/icons/icons_left_arrow.png"
        self.hide_icon = self.Path + "/icons/icons_right_arrow.png"

        self.icon_round_btn = self.Path + "/icons/icons_btn_round10x10.png"
        self.icon_round_green = self.Path + "/icons/icons_btn_round10x10_green.png"

        self.Frame_w = 320
        self.Frame_h = 240 

        self.ui = Ui_Terminal_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.ui.Tlabel.setAlignment(Qt.AlignLeft)
        self.ui.Tlabel.setStyleSheet("background-color: rgba(0, 124, 212, 50);")

        #=======================================
        # TextView
        self.selectTextMode = True

        #========================================
        # Image View

        self.selectImageMode = False
        self.ui.lbl.setAlignment(Qt.AlignLeft)
        self.ui.lbl.setGeometry(2,0,320,240)
        self.ui.lbl.setVisible(False)

        self.window_width = self.ui.lbl.frameSize().width()
        self.window_height = self.ui.lbl.frameSize().height()

        self.ImgData = None

        self.scale_x = 1
        self.scale_y = 1

        self.new_scale_x = 0
        self.new_scale_y = 0

        self.update_pos_area = False

        #========================================
        # Graph View

        self.selectGraphMode = False

        self.ui.graphWidget.setCentralWidget
        self.ui.graphWidget.setBackground((2, 32, 130, 100))
        self.styles = {'color':'r', 'font-size':'10px'}
        self.xParam = 'Temperature (°C)'
        self.yParam = 'Hour (H)'
        self.ui.graphWidget.setLabel('left', self.xParam, **self.styles)
        self.ui.graphWidget.setLabel('bottom', self.yParam, **self.styles)
        self.ui.graphWidget.showGrid(x=True, y=True)
        self.ui.graphWidget.setVisible(False)

        self.ui.GraphTitleLable.setGeometry(80, 0, 320, 40)
        self.ui.GraphTitleLable.setStyleSheet("color: #EFFAF7; font-size:10pt;")
        self.ui.GraphTitleLable.setVisible(False)

        #========================================
        # Qchart
        # for Test
        # self.data = [('02/06/2023 10:21', '22990.78', '22991.68', '22990.78', '22991.68')]

        self.series = QCandlestickSeries()
        # self.series.setDecreasingColor(Qt.red)
        # self.series.setIncreasingColor(Qt.green)

        self.series.setDecreasingColor(QColor(244, 194, 194))
        self.series.setIncreasingColor(QColor(1, 251, 255))

        self.ma5 = qc.QLineSeries()  # 5-days average data line
        self.tm = []  # stores str type data

        self.x_min, self.x_max, self.y_min, self.y_max = (
            float("inf"),
            -float("inf"),
            float("inf"),
            -float("inf"),
        )

        # # in a loop,  series and ma5 append corresponding data
        # for num, o, h, l, c in self.data:
        #     # Using the same value for open, high, low as the close value
        #     self.series.append(QCandlestickSet(float(o), float(h), float(l), float(c)))
        #     self.tm.append(str(num))

        # self.ui.chart.addSeries(self.series)  # candle
        # # chart.addSeries(ma5)  # ma5 line

        # self.ui.chart.setAnimationOptions(QChart.SeriesAnimations)
        # self.ui.chart.createDefaultAxes()
        # self.ui.chart.legend().hide()

        # self.ui.chart.axisX(self.series).setCategories(self.tm)
        # self.ui.chart.axisX(self.series).setLabelsColor(QColor(57, 196, 191, 255))
        # self.ui.chart.axisY().setLabelsColor(QColor(57, 196, 191, 255))

        # self.ui.chart.setBackgroundBrush(QBrush(QColor(0, 124, 212, 200)))

        self.ui.chart.setVisible(False)
        self.ui.chartview.setGeometry(0,0,325,210)
        self.ui.chartview.setVisible(False)

        #========================================
        # OpenGL View
        """self.w = gl.GLViewWidget(self)
        self.w.setGeometry(0, 0, 320, 240)
        self.w.setVisible(False)"""

        #############################################################################
        #============================================================================
        # Setting Condition
        self.lableSteting_X = int(2)
        self.lableSteting_Y = int(445)

        self.ui.lblSetting.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:13pt;color:lightblue; border: 1px solid white; border-radius: 5%;")

        #========================================
        # Select View
        self.ui.TextBtn.setStyleSheet("background-color: rgba(69, 161, 250, 50);")
        self.ui.ImgBtn.setStyleSheet("background-color: rgba(69, 161, 250, 50);")
        self.ui.GraphBtn.setStyleSheet("background-color: rgba(69, 161, 250, 50);")

        #========================================

        self.ui.checkBlue.setStyleSheet("color: lightblue")
        self.ui.checkBlue.setChecked(False)

        self.convertblue_flag = False

        self.ui.UpdatePosBtn.setStyleSheet("background-color: rgba(69, 161, 250, 50);")
        self.ui.status_mouse_pos.setAlignment(Qt.AlignLeft)

        self.ui.lblSetting.setVisible(False)
        self.ui.TextBtn.setVisible(False)
        self.ui.ImgBtn.setVisible(False)
        self.ui.GraphBtn.setVisible(False)
        self.ui.checkBlue.setVisible(False)
        self.ui.UpdatePosBtn.setVisible(False)
        self.ui.status_mouse_pos.setVisible(False)

        self.ui.ShowBtn.setIcon(QIcon(self.show_icon))
        self.ui.ShowBtn.setStyleSheet("background-color: transparent; border: 0px;")

        self.ui.ResizeBtn.setIcon(QIcon(self.icon_round_btn))
        self.ui.ResizeBtn.setStyleSheet("background-color: transparent; border: 0px;")   
        
        self.showSettingBar_flag = False

        self.X = None
        self.Y = None

        self.CX = 0
        self.CY = 0

        self.EX = 0
        self.EY = 0

        self.ResizeFrame_timer = QtCore.QTimer(self)
        self.display_timer = QtCore.QTimer(self)

        self.Press_Count = 0
        self.startX = 0
        self.startY = 0

        self.currentX = 0
        self.currentY = 0

        self.resize_terminal = False
        self.resized.connect(self.ReDrawGeometry)

    def serialize(self):
        res = super().serialize()
        res['selecttext'] = self.selectTextMode
        res['selectimage'] = self.selectImageMode
        res['selectgraph'] = self.selectGraphMode
        res['convertblue'] = self.convertblue_flag
        res['resize'] = self.resize_terminal
        res['new_width'] = self.Frame_w
        res['new_height'] = self.Frame_h
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.selectTextMode = data['selecttext']
            if self.selectTextMode:
                self.ui.Tlabel.setVisible(True)
                self.ui.lbl.setVisible(False)
                self.ui.graphWidget.setVisible(False)

            self.selectImageMode = data['selectimage']
            if self.selectImageMode:
                self.ui.Tlabel.setVisible(False)
                self.ui.lbl.setVisible(True)
                self.ui.graphWidget.setVisible(False)

            self.selectGraphMode = data['selectgraph']
            if self.selectGraphMode:
                self.ui.Tlabel.setVisible(False)
                self.ui.lbl.setVisible(False)
                self.ui.graphWidget.setVisible(True)

            if 'convertblue' in data:
                self.convertblue_flag = data['convertblue']
                if self.convertblue_flag:
                    self.ui.checkBlue.setChecked(True)

                else:
                    self.ui.checkBlue.setChecked(False)

            if 'resize' in data:
                self.resize_terminal = data['resize']
                if self.resize_terminal:
                    if 'new_width' in data:
                        self.Frame_w = data['new_width']

                    if 'new_height' in data:
                        self.Frame_h = data['new_height']

                    self.ReDrawGeometry()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def mousePressEvent(self, event):
        #if event.button() == Qt.LeftButton & self.globalDrawing==True:
        #self.drawing = True

        self.X = int(event.x() * self.scale_x)
        self.Y = int(event.y() * self.scale_y)

        self.lastPoint = self.ui.lbl.mapFromParent(event .pos()) #this is working fine now
        #print("mousePressEvent ---> self.lastPoint = ", self.lastPoint)
        #self.content.lbl.setPixmap(QPixmap.fromImage(self.image))

        self.display_timer.start()

    def mouseMoveEvent(self, event):
        #if (event.buttons() & Qt.LeftButton) & self.drawing &self.globalDrawing:
        #painter=QPainter(self.image)
        #painter.setPen(QPen(self.brushColor,self.brushSize ,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        #painter.drawLine(self.content.lbl.mapFromParent(event.pos()),self.lastPoint)

        self.lastPoint = self.ui.lbl.mapFromParent(event.pos()) #this is working fine now
        #print("mouseMoveEvent ---> self.lastPoint = ", self.lastPoint)

        self.CX = int(self.lastPoint.x() * self.scale_x)
        self.CY = int(self.lastPoint.y() * self.scale_y)

        #print("self.CX = ", self.CX)
        #print("self.CY = ", self.CY)

        #self.content.lbl.setPixmap(QPixmap.fromImage(self.image))

    def mouseReleaseEvent(self, event):
        #if event.button == Qt.LeftButton & self.globalDrawing:
        #    self.drawing = False
        #    #self.content.lbl.setPixmap(QPixmap.fromImage(self.image))

        self.EX = int(event.x() * self.scale_x)
        self.EY = int(event.y() * self.scale_y)

        self.lastPoint = self.ui.lbl.mapFromParent(event.pos()) #this is working fine now
        self.ui.status_mouse_pos.setText("Pos : [ %d , %d ]" % (self.EX, self.EY))


        self.Press_Count = 0
        # print("self.Press_Count = ", self.Press_Count)

        self.display_timer.stop()

    #================================================
    def ReDrawGeometry(self):
        # print("ReDrawGeometry Frame_w = ", self.Frame_w, " ; self.Frame_h = ", self.Frame_h)
        self.ui.MainWindow.setGeometry(2, 27, int(self.Frame_w - 5), int(self.Frame_h - 30)) 
        self.ui.Tlabel.setGeometry(2,2, int(self.Frame_w), int(self.Frame_h - 5))
        self.ui.lbl.setGeometry(2,2, int(self.Frame_w), int(self.Frame_h - 5))
        self.ui.graphWidget.setGeometry(5, 5, int(self.Frame_w) - 15, int(self.Frame_h - 40))
        self.ui.chartview.setGeometry(0, 0, int(self.Frame_w) - 5, int(self.Frame_h - 60))

        self.ui.GraphTitleLable.setGeometry(80, 0, int(self.Frame_w) - 15, 40)

        self.window_width = self.ui.lbl.frameSize().width()
        self.window_height = self.ui.lbl.frameSize().height()

        self.lableSteting_Y = int(self.Frame_h - 60)

        PosShowBtn_X = 295
        if self.window_width > 640:
            PosShowBtn_X = self.Frame_w - 30

        if self.showSettingBar_flag and self.window_width > 640:
            self.ui.UpdatePosBtn.setVisible(True)
            self.ui.status_mouse_pos.setVisible(True)

        else:
            self.ui.UpdatePosBtn.setVisible(False)
            self.ui.status_mouse_pos.setVisible(False)

        self.ui.lblSetting.setGeometry(2, int(self.lableSteting_Y-5), int(PosShowBtn_X + 23),30)
        self.ui.TextBtn.setGeometry(7, int(self.lableSteting_Y), 75, 20)
        self.ui.ImgBtn.setGeometry(87, int(self.lableSteting_Y), 75, 20)
        self.ui.GraphBtn.setGeometry(167, int(self.lableSteting_Y), 75, 20)
        self.ui.checkBlue.setGeometry(247, int(self.lableSteting_Y), 70, 20)
        self.ui.UpdatePosBtn.setGeometry(312, int(self.lableSteting_Y), 135, 20)
        self.ui.status_mouse_pos.setGeometry(452, int(self.lableSteting_Y), 150, 20)
        self.ui.ShowBtn.setGeometry(int(PosShowBtn_X), int(self.lableSteting_Y), 20, 20)

        self.ui.ResizeBtn.setGeometry(int(self.Frame_w - 15), int(self.Frame_h - 43), 10, 10)

@register_node(OP_NODE_TERMINAL)
class Open_TERMINAL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_terminal2.png"
    op_code = OP_NODE_TERMINAL
    op_title = "Terminal"
    content_label_objname = "Terminal"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.rx_payload = {}
        self.rx_payload['img'] = None
        self.rx_payload['blink'] = None
        self.rx_payload['fps'] = None
        self.rx_payload['x1'] = []
        self.rx_payload['y1'] = []
        self.rx_payload['x2'] = []
        self.rx_payload['y2'] = []
        self.rx_payload['x3'] = []
        self.rx_payload['y3'] = []
        self.rx_payload['xParam'] = None
        self.rx_payload['yParam'] = None

        self.rx_payload['name1'] = ""
        self.rx_payload['name2'] = ""

        """n_data = 50
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]"""

        self.range = 50
        self.rx_payload['x1'] = list(range(50))  # 100 time points
        self.rx_payload['y1'] = [randint(0,100) for _ in range(50)]  # 100 data points

        self.rx_payload['x2'] = list(range(50))  # 100 time points
        self.rx_payload['y2'] = [randint(0,100) for _ in range(50)]  # 100 data points

        self.rx_payload['x3'] = list(range(50))  # 100 time points
        self.rx_payload['y3'] = [randint(0,100) for _ in range(50)]  # 100 data points

        self.pen = pg.mkPen(color=(0, 0, 255))
        self.pen_2 = pg.mkPen(color=(252, 3, 199))
        self.pen_3 = pg.mkPen(color=(252, 74, 3))

        self.data_line =  self.content.ui.graphWidget.plot(self.rx_payload['x1'], self.rx_payload['y1'], pen=self.pen)
        self.data_line_2 =  self.content.ui.graphWidget.plot(self.rx_payload['x2'], self.rx_payload['y2'], pen=self.pen_2)
        self.data_line_3 =  self.content.ui.graphWidget.plot(self.rx_payload['x3'], self.rx_payload['y3'], pen=self.pen_3)

        self.alpha = 1.3
        self.beta = 40

        self.select_position = []

        self.frame = np.zeros((240, 320, 3), np.uint8)
        self.barinframe = False

        self.date_time = ""
        self.datetime_lates = ""

        self.init_chart = False
        self.init_onetime = False

    def initInnerClasses(self):
        self.content = TerminalDebug(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsTerminal(self)  # <----------- Box Image Draw in Flow_Node_Base

        #=============================================================
        # Resizeable
        self.grNode_addr = str(self.grNode)[-13:-1]
        self.BoxKey = "ChangeItemFrame:" + self.grNode_addr

        self.content.ui.TextBtn.clicked.connect(self.changeToTextMode)
        self.content.ui.ImgBtn.clicked.connect(self.changeToImageMode)
        self.content.ui.GraphBtn.clicked.connect(self.changeToGraphMode)

        self.content.ui.checkBlue.stateChanged.connect(self.SelectConvertBlue)

        self.content.display_timer.timeout.connect(self.update_data)
        self.content.display_timer.setInterval(10)

        self.content.ui.ResizeBtn.clicked.connect(self.StartResize_ItemFram)
        self.content.ResizeFrame_timer.timeout.connect(self.update_ItemFrame)

        self.content.ui.ShowBtn.clicked.connect(self.ShowSettingBar)

        self.content.ui.UpdatePosBtn.clicked.connect(self.UpdatePosition)
        self.Global = GlobalVariable()
        self.Global.setGlobal("ReadyChangeItemFrame", False)

        self.Terminal_ID = "Terminal_ID" + self.grNode_addr
        print("\033[96m {}\033[00m".format(self.Terminal_ID))

        self.ListGlobalTerminalBox = []
        if self.Global.hasGlobal("GlobalTerminalBoxID"):
            self.ListGlobalTerminalBox = list(self.Global.getGlobal("GlobalTerminalBoxID"))

            self.ListGlobalTerminalBox.append(self.Terminal_ID)
            self.Global.setGlobal("GlobalTerminalBoxID", self.ListGlobalTerminalBox)

        else:
            self.ListGlobalTerminalBox.append(self.Terminal_ID)
            self.Global.setGlobal("GlobalTerminalBoxID", self.ListGlobalTerminalBox)

    def evalImplementation(self):                 # <----------- To Create Socket
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
                return

            else:
                # Operate Process Here !!!!!

                if self.content.selectTextMode:
                    self.content.ui.Tlabel.setText(str(self.rx_payload))
                    
                if self.content.selectImageMode:
                    if 'mqtt_payload' in self.rx_payload:
                        if len(self.rx_payload['mqtt_payload']) > 255:

                            # Decoding the message
                            img = base64.b64decode(self.rx_payload['mqtt_payload'])

                            # converting into numpy array from buffer
                            npimg = np.frombuffer(img, dtype=np.uint8)
                            # Decode to Original Frame
                            self.frame = cv2.imdecode(npimg, 1)

                            self.barinframe = False
                            self.update_frame(self.frame)

                    else:
                        if 'inputtype' in self.rx_payload:
                            if self.rx_payload['inputtype'] == 'img':
                                self.content.selectGraphMode = False
                                self.content.ui.graphWidget.setVisible(False)
                                self.content.ui.GraphBtn.setEnabled(False)

                                if 'img' in self.rx_payload:

                                    if self.content.convertblue_flag:
                                        #Converting image to RGB Space
                                        B,G,R = cv2.split(self.rx_payload['img'])
                                        zeros=np.zeros(self.rx_payload['img'].shape[:2],dtype="uint8")
                                        self.rx_payload['img'] = cv2.merge([B,zeros,zeros])

                                        #Changing the contrast and brightness of an image!
                                        # https://docs.opencv.org/3.4/d3/dc1/tutorial_basic_linear_transform.html
                            
                                        self.rx_payload['img'] = cv2.convertScaleAbs(self.rx_payload['img'], alpha=self.alpha, beta=self.beta)

                                    # Get the height and width of the image
                                    height, width = self.rx_payload['img'].shape[:2]
                                    if height < 480 or width < 640:
                                        self.barinframe = False
                                    else:
                                        self.barinframe = True

                                    self.update_frame(self.rx_payload['img'])
                            else:
                                self.content.selectGraphMode = True
                                self.content.ui.graphWidget.setVisible(True)
                                self.content.ui.GraphBtn.setEnabled(True)
                                self.content.ui.lbl.setVisible(False)

                        
                if self.content.selectGraphMode:
                    if 'inputtype' in self.rx_payload:
                        if self.rx_payload['inputtype'] == 'graph':

                            self.content.ui.graphWidget.clear()

                            if 'titlename' in self.rx_payload:
                                self.content.ui.GraphTitleLable.setText(self.rx_payload['titlename'])
                                self.content.ui.GraphTitleLable.setVisible(True)

                            self.content.selectImageMode = False
                            self.content.ui.lbl.setVisible(False)   
                            self.content.ui.ImgBtn.setEnabled(False)
                            self.content.ui.graphWidget.setVisible(True)

                            if 'charttype' in self.rx_payload:
                                self.content.ui.graphWidget.setVisible(False)
                                self.content.ui.chartview.setVisible(True)

                            if 'df' in self.rx_payload:
                                if type(self.rx_payload['df']) != type(None):
                                    # self.rx_payload['df'].apply(self.to_tuple, axis=1).tolist()
                                    data = self.rx_payload['df']
                                    if len(data) == 0 and not self.init_chart:
                                        self.init_chart = True

                                    elif len(data) > 0 and self.init_chart:
                                        date_time = data[0]
                                        self.update_qchart(data, date_time)
                                    else:
                                        if len(data) > 0 and not self.init_chart:
                                            self.init_chart = True
                                            
                                            print("Another new case have many data in self.series but still not innit Qchart")
                                            date_time = data[0]

                                            print("date_time : ", date_time)
                                            self.update_qchart(data, date_time)


                            if 'x1' in self.rx_payload and 'y1' in self.rx_payload:
                                if self.rx_payload['x1'] is not None and self.rx_payload['y1'] is not None:
                                    # self.data_line.setData(self.rx_payload['x1'], self.rx_payload['y1'])  # Update the data.
                                    if 'name1' in self.rx_payload:
                                        self.content.ui.graphWidget.plot(x = self.rx_payload['x1'], y=self.rx_payload['y1'],
                                            pen='g', name = self.rx_payload['name1'])
                                    else:
                                        self.content.ui.graphWidget.plot(x = self.rx_payload['x1'], y=self.rx_payload['y1'],
                                            pen='g', name = "name")
                            else:
                                self.data_line.setData([0,0,0,0,0], [0,0,0,0,0])  # Update the data.

                            if 'x2' in self.rx_payload and 'y2' in self.rx_payload:
                                if self.rx_payload['x2'] is not None and self.rx_payload['y2'] is not None:
                                    self.data_line_2.setData(self.rx_payload['x2'], self.rx_payload['y2'])  # Update the data 2.
                                    self.content.ui.graphWidget.plot(x = self.rx_payload['x2'], y = self.rx_payload['y2'],
                                        pen='r', name = self.rx_payload['name2'])

                                if 'name2' in self.rx_payload:
                                    ...

                            else:
                                self.data_line_2.setData([0,0,0,0,0], [0,0,0,0,0])  # Update the data 2.

                            if 'x3' in self.rx_payload and 'y3' in self.rx_payload:       
                                if self.rx_payload['x3'] is not None and self.rx_payload['y3'] is not None:
                                    self.data_line_3.setData(self.rx_payload['x3'], self.rx_payload['y3'])  # Update the data 3.
                            else:
                                self.data_line_3.setData([0,0,0,0,0], [0,0,0,0,0])  # Update the data 3.

                            if 'xParam' in self.rx_payload and 'yParam' in self.rx_payload:
                                if self.rx_payload['xParam'] is not None and self.rx_payload['yParam'] is not None:
                                    self.content.ui.graphWidget.setLabel('left', self.rx_payload['xParam'], **self.content.styles)
                                    self.content.ui.graphWidget.setLabel('bottom', self.rx_payload['yParam'], **self.content.styles)

                            if 'TensorLSTM_Chart' in self.rx_payload:
                                if self.rx_payload['TensorLSTM_Chart'] is not None:
                                    if self.rx_payload['TensorLSTM_Chart']:
                                        # Add vertical line at x=15
                                        vLine = pg.InfiniteLine(angle=90, movable=False, pos=15)
                                        self.content.ui.graphWidget.addItem(vLine)

                            if 'TensorLSTM_All' in self.rx_payload:
                                if self.rx_payload['TensorLSTM_All'] is not None:
                                    if self.rx_payload['TensorLSTM_All']:
                                        # Add vertical line and rectangle at x=closedf.shape[0]
                                        vLine2 = pg.InfiniteLine(angle=90, movable=False, pos=self.rx_payload['closedf'].shape[0])
                                        self.content.ui.graphWidget.addItem(vLine2)
                                        # vRect = pg.RectItem(self.rx_payload['closedf'].shape[0], self.content.ui.graphWidget.getPlotItem().vb.viewRect().bottom(),
                                        #                                     self.rx_payload['pred_days'] + 6, self.content.ui.graphWidget.getPlotItem().vb.viewRect().height())
                                        # vRect.setBrush(pg.mkBrush(255, 0, 0, 120))
                                        # self.content.ui.graphWidget.addItem(vRect)
                                                                                                        
                        else:
                            self.content.ui.Tlabel.setText(str(self.rx_payload))

                            self.content.selectImageMode = True
                            self.content.ui.ImgBtn.setEnabled(True)
                            self.content.ui.graphWidget.setVisible(False)

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
                    self.content.resize_terminal = True

            else:
                self.content.ResizeFrame_timer.stop()
                self.content.ui.ResizeBtn.setIcon(QIcon(self.content.icon_round_btn))
                # print("Stop Resize")
                self.Global.removeGlobal(self.BoxKey)

    #======================================================================
    def draw_dashboard_frame(self, image):
        h, w, c = image.shape

        # Initialize black image of same dimensions for drawing the rectangles
        blk = np.zeros(image.shape, np.uint8)

        blk = cv2.line(blk, (15,10), (20,5), (236,231,0), 2)    #Bright Turquoise #/
        blk = cv2.line(blk, (15,10), (15,35), (236,231,0), 2)   #|
        blk = cv2.line(blk, (5,45), (15,35), (236,231,0), 2)    #/

        blk = cv2.line(blk, (5,45), (5, h-100 ), (236,231,0), 2)    #|
        blk = cv2.line(blk, (5,h-100), (5, h-20), (255,0,0), 3)     #||
        blk = cv2.line(blk, (5,h-20), (20, h-8), (255,0,0), 2)      #  \
        blk = cv2.line(blk, (20,h-8), (w-10, h-8), (255,0,0), 2)     #   ---------

        blk = cv2.line(blk, (w-10, h-8), (w-10, 255), (255,0,0), 3)    #||

        blk = cv2.line(blk, (w-10, 255), (w-10, 30), (236,231,0), 2)  #|
        blk = cv2.line(blk, (w-10, 30), (w-30, 5), (255,0,0), 2)        #\
        blk = cv2.line(blk, (w-200, 5), (w-30, 5), (255,0,0), 1)        #--
        blk = cv2.line(blk, (w-180, 15), (w-20, 15), (255,0,0), 1)      #--

        # Generate result by blending both images (opacity of rectangle image is 0.90 = 90 %)
        image = cv2.addWeighted(image, 1.0, blk, 0.90, 1)

        return image

    #======================================================================

    def update_frame(self, img):
        
        if img is not None and len(str(img)) > 250:
            if 'fps' in self.rx_payload:
                if self.rx_payload['fps'] != "Not Display":
                    t = self.rx_payload['fps']
                    if time.time() == t:
                        pass
                    else:
                        fps = 1.0 / (time.time() - t)
                        cv2.putText(img , "FPS: %f" % (fps), (20, 30),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if self.barinframe:
                img = self.draw_dashboard_frame(img)

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.content.window_width) / float(img_width)
            scale_h = float(self.content.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1
            
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)

            self.content.ui.lbl.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            self.content.ui.lbl.setText(str(img))

    def changeToTextMode(self):
        self.content.selectTextMode = True
        self.content.selectImageMode = False
        self.content.selectGraphMode = False

        self.content.ui.Tlabel.setVisible(True)
        self.content.ui.lbl.setVisible(False)
        self.content.ui.graphWidget.setVisible(False)

        #print("Select Text Mode !!!")

    def changeToImageMode(self):
        self.content.selectTextMode = False
        self.content.selectImageMode = True 
        self.content.selectGraphMode = False

        self.content.ui.Tlabel.setVisible(False)       #<--- OFF'''
        self.content.ui.lbl.setVisible(True)           #<--- ON
        self.content.ui.graphWidget.setVisible(False)

        #print("Select Image Mode !!!")

    def changeToGraphMode(self):
        self.content.selectTextMode = False
        self.content.selectImageMode = False 
        self.content.selectGraphMode = True

        self.content.ui.Tlabel.setVisible(False)       #<--- OFF'''
        self.content.ui.lbl.setVisible(False)           
        self.content.ui.graphWidget.setVisible(True)       #<--- ON
        #self.content.graphWidget.clear()
        #print("Select Graph Mode !!!")

    def update_data(self):
        self.content.Press_Count += 1
        #print("Timer Count = ", self.content.Press_Count)

        if self.content.Press_Count <= 1:
            self.content.startX = self.content.X
            self.content.startY = self.content.Y

            #print("self.content.startX = ", self.content.startX)
            #print("self.content.startY = ", self.content.startY)

            self.content.ui.UpdatePosBtn.setText("Update Position")

            self.content.update_pos_area = False

        if self.content.Press_Count > 50:
            #print("Draw Rectangle")

            self.content.ui.UpdatePosBtn.setText("Update Working Area")

            self.content.currentX = self.content.CX
            self.content.currentY = self.content.CY

            #print("self.content.currentX = ", self.content.currentX)
            #print("self.content.currentY = ", self.content.currentY)

            if 'img' in self.rx_payload:
                if len(str(self.rx_payload['img'])) > 50:
                    image = self.rx_payload['img']

                    cv2.rectangle(image, (int(self.content.startX), int(self.content.startY)), (int(self.content.currentX), int(self.content.currentY)), (255, 0, 0), 2)  

                    self.barinframe = True
                    self.update_frame(image)

                    #Clear Image
                    image = None

                    self.content.update_pos_area = True

    def update_qchart(self, data, date_time):
        if self.init_chart and not self.init_onetime:
            self.init_onetime = True

            self.content.ui.chart.setVisible(True)

            print("init_chart data : ", data)
            # print("data[0] : ", data[0])
            # print("data[1] : ", data[1])
            # print("data[2] : ", data[2])
            # print("data[3] : ", data[3])
            # print("data[4] : ", data[4])

            # Using the same value for open, high, low as the close value
            self.content.series.append(QCandlestickSet(float(data[1]), float(data[2]), float(data[3]), float(data[4])))
            self.content.tm.append(str(date_time))
            # self.content.x_min = min(self.content.x_min, date_time)
            # self.content.x_max = max(self.content.x_max, date_time)
            self.content.y_min = min(self.content.y_min, float(data[1]), float(data[2]), float(data[3]), float(data[4]))
            self.content.y_max = max(self.content.y_max, float(data[1]), float(data[2]), float(data[3]), float(data[4]))

            self.content.ui.chart.addSeries(self.content.series)  # candle
            # chart.addSeries(ma5)  # ma5 line

            self.content.ui.chart.setAnimationOptions(QChart.SeriesAnimations)
            self.content.ui.chart.createDefaultAxes()
            self.content.ui.chart.legend().hide()

            self.content.ui.chart.axisY(self.content.series).setMin(self.content.y_min)
            self.content.ui.chart.axisY(self.content.series).setMax(self.content.y_max)
            self.content.ui.chart.axisX(self.content.series).setCategories(self.content.tm)
            self.content.ui.chart.axisX(self.content.series).setLabelsColor(QColor(57, 196, 191, 255))
            self.content.ui.chart.axisY().setLabelsColor(QColor(57, 196, 191, 255))

            self.content.ui.chart.setBackgroundBrush(QBrush(QColor(0, 124, 212, 200)))
            self.datetime_lates = date_time
        
        else:
            if date_time != self.datetime_lates:
                # print("Update data : ", data)
                # print("type(data) : ", type(data))
                # print("data[0] : ", data[0])
                # print("data[1] : ", data[1])
                # print("data[2] : ", data[2])
                # print("data[3] : ", data[3])
                # print("data[4] : ", data[4])

                self.content.series.append(QCandlestickSet(float(data[1]), float(data[2]), float(data[3]), float(data[4])))
                # ma5.append(QPointF(num, m))
                self.content.tm.append(str(date_time))
                # self.content.x_min = min(self.content.x_min, date_time)
                # self.content.x_max = max(self.content.x_max, date_time)
                self.content.y_min = min(self.content.y_min, float(data[1]), float(data[2]), float(data[3]), float(data[4]))
                self.content.y_max = max(self.content.y_max, float(data[1]), float(data[2]), float(data[3]), float(data[4]))


                # Update QChart
                # print("self.content.series count: ", self.content.series.count())
                # print("self.content.tm : ", self.content.tm)

                self.content.ui.chart.axisY(self.content.series).setMin(self.content.y_min)
                self.content.ui.chart.axisY(self.content.series).setMax(self.content.y_max)
                self.content.ui.chart.axisX(self.content.series).setCategories(self.content.tm)
                self.datetime_lates = date_time

    def ShowSettingBar(self):
        self.content.showSettingBar_flag = not self.content.showSettingBar_flag

        if self.content.showSettingBar_flag:
            self.content.ui.ShowBtn.setIcon(QIcon(self.content.hide_icon))
            self.content.ui.lblSetting.setVisible(True)
            self.content.ui.TextBtn.setVisible(True)
            self.content.ui.ImgBtn.setVisible(True)
            self.content.ui.GraphBtn.setVisible(True)
            self.content.ui.checkBlue.setVisible(True)

            if self.content.window_width > 640:
                self.content.ui.UpdatePosBtn.setVisible(True)
                self.content.ui.status_mouse_pos.setVisible(True)

        else:
            self.content.ui.ShowBtn.setIcon(QIcon(self.content.show_icon))
            self.content.ui.lblSetting.setVisible(False)
            self.content.ui.TextBtn.setVisible(False)
            self.content.ui.ImgBtn.setVisible(False)
            self.content.ui.GraphBtn.setVisible(False)
            self.content.ui.checkBlue.setVisible(False)

            if self.content.window_width > 640:
                self.content.ui.UpdatePosBtn.setVisible(False)
                self.content.ui.status_mouse_pos.setVisible(False)


    def SelectConvertBlue(self, state):
        if state == QtCore.Qt.Checked:
            self.content.convertblue_flag = True

        else:
            self.content.convertblue_flag = False         

    def UpdatePosition(self):
        print("Update Position from Teminal to other Box")
        self.select_position = (self.content.startX, self.content.startY, self.content.currentX, self.content.currentY)

        if self.content.update_pos_area:
            self.Global.setGlobal("teminal_pos_select", self.select_position)

            self.content.new_scale_x = (self.content.currentX - self.content.startX)/640
            self.content.new_scale_y = (self.content.currentY - self.content.startY)/480

            print("self.content.new_scale_x = ", self.content.new_scale_x)
            print("self.content.new_scale_y = ", self.content.new_scale_y)

            self.new_image_scale = (self.content.new_scale_x, self.content.new_scale_y)
            print("self.new_image_scale = ", self.new_image_scale)

            self.Global.setGlobal("new_image_scale", self.new_image_scale)

        else:
            print("Click to upate Position")
            self.Global.setGlobal("teminal_selectpos", self.select_position)

