"""
Python: How to copy files?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Function              preserves     supports          accepts     copies other
                      permissions   directory dest.   file obj    metadata  
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
shutil.copy              ✔             ✔                 ☐           ☐
shutil.copy2             ✔             ✔                 ☐           ✔
shutil.copyfile          ☐             ☐                 ☐           ☐
shutil.copyfileobj       ☐             ☐                 ✔           ☐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example:

import shutil
shutil.copy('/etc/hostname', '/var/tmp/testhostname')
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
from os import listdir
from os.path import isfile, join

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

"""from ai_application.AI_Module.yolo.yolov3 import Create_Yolov3
from ai_application.AI_Module.yolo.yolov4 import Create_Yolo, compute_loss
from ai_application.AI_Module.yolo.utils import load_yolo_weights, detect_image, detect_video, detect_realtime
#from ai_application.AI_Module.yolo.configs import *"""

import ai_application.AI_Module.yolo.configs as configs
"""import ai_application.AI_Module.yolo.dataset as ds
import ai_application.AI_Module.yolo.evaluate_mAP as gm"""

import ai_application.AI_Module.yolo.training as training

from ai_application.Database.GlobalVariable import *

from tensorflow.python.client import device_lib
import tensorflow as tf

import xml.etree.ElementTree as ET
import glob

import psutil
import shutil

import math
from typing import Union

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

PNOF_File = 0

class ObjectTrain(QDMNodeContentWidget):
    def initUI(self):
        super(ObjectTrain).__init__()

        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.play_icon = self.Path + "/icons/icons_play.png"
        self.save_icon = self.Path + "/icons/icons_save.png"
        self.cxmlyolo_icon = self.Path + "/icons/icons_yolo_icon.png"
        self.train_icon = self.Path + "/icons/icons_train.png"
        self.animate_movie = self.Path + "/icons/icons_running.gif"

        self.Data = None

        self.lblTitle = QLabel("Select Training Model" , self)
        self.lblTitle.setAlignment(Qt.AlignLeft)
        self.lblTitle.setGeometry(10,7,185,25)
        self.lblTitle.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:9pt;color:lightblue; border: 1px solid white; border-radius: 5%")

        self.lblModel = QLabel("1.Model : " , self)
        self.lblModel.setAlignment(Qt.AlignLeft)
        self.lblModel.setGeometry(10,40,55,20)
        self.lblModel.setStyleSheet("color: orange; font-size:6pt;")

        self.combo = QComboBox(self)
        self.combo.addItem("yolov3")
        self.combo.addItem("yolov4")

        self.combo.setGeometry(60,40,78,20)
        self.combo.move(68, 40)
        self.combo.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.combo.setCurrentText("yolov4")
                                   
        self.checkTiny = QCheckBox("Tiny",self)
        self.checkTiny.setGeometry(150,41,60,20)
        self.checkTiny.setStyleSheet("color: lightblue; font-size:5pt;")
        self.checkTiny.setChecked(True)

        self.checkTrainChkPoint = QCheckBox("From Checkpoint",self)
        self.checkTrainChkPoint.setGeometry(10,65,1240,20)
        self.checkTrainChkPoint.setStyleSheet("color: lightblue; font-size:6pt;")
        self.checkTrainChkPoint.setChecked(False)

        self.FromTrainFolderEdit = QLineEdit("", self)
        self.FromTrainFolderEdit.setGeometry(135,65,55,20)
        self.FromTrainFolderEdit.setPlaceholderText("Weight")
        self.FromTrainFolderEdit.setVisible(False)

        self.browsPreWeightFiles = QPushButton(self)
        self.browsPreWeightFiles.setGeometry(175,65,20,20)
        self.browsPreWeightFiles.setIcon(QIcon(self.save_icon))
        self.browsPreWeightFiles.setVisible(False)

        #========================================================

        # Dataset for train and Test Folder
        self.lbl1 = QLabel("2.Select Image Label: " , self)
        self.lbl1.setAlignment(Qt.AlignLeft)
        self.lbl1.setGeometry(10,82,150,20)
        self.lbl1.setStyleSheet("color: green; font-size:7pt;")

        self.TrainFolderEdit = QLineEdit("", self)
        self.TrainFolderEdit.setGeometry(10,100,160,20)
        self.TrainFolderEdit.setPlaceholderText("Input DIR:Images/Lable")
        
        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(175,100,20,20)
        self.browsFiles.setIcon(QIcon(self.save_icon))

        #==============================================

        #==============================================
        self.lbl2 = QLabel("3.Ready For Training : " , self)
        self.lbl2.setAlignment(Qt.AlignLeft)
        self.lbl2.setGeometry(10,125,150,20)
        self.lbl2.setStyleSheet("color: yellow; font-size:7pt;")
        self.lbl2.setVisible(False)

        """self.ConXMLYoloBtn = QPushButton(self)
        self.ConXMLYoloBtn.setGeometry(142,125,55,25)
        self.ConXMLYoloBtn.setIcon(QIcon(self.cxmlyolo_icon))
        self.ConXMLYoloBtn.setIconSize(QtCore.QSize(55,20))"""
        #self.ConXMLYoloBtn.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lblPercent = QLabel("0%" , self)
        self.lblPercent.setAlignment(Qt.AlignLeft)
        self.lblPercent.setGeometry(150,130,150,20)
        self.lblPercent.setStyleSheet("color: white; font-size:10pt;")

        #===========================================================

        self.lbl3 = QLabel("4." , self)
        self.lbl3.setAlignment(Qt.AlignLeft)
        self.lbl3.setGeometry(130,155,20,20)
        self.lbl3.setStyleSheet("color: blue; font-size:7pt;")

        self.lblTrain = QLabel("Train" , self)
        self.lblTrain.setAlignment(Qt.AlignLeft)
        self.lblTrain.setGeometry(147,155,50,20)
        self.lblTrain.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 5%")

        self.TrainObjectBtn = QPushButton(self)
        self.TrainObjectBtn.setGeometry(150, 180, 45, 45)
        self.TrainObjectBtn.setIconSize(QtCore.QSize(45,45))
        self.TrainObjectBtn.setIcon(QIcon(self.train_icon))
        self.TrainObjectBtn.setEnabled(False)

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msg.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        self.dataset_dir = self.TrainFolderEdit.text() + "/custom_dataset/"

        self.Dataset_names = ""
        self.Dataset_train = ""
        self.Dataset_test = ""
        self.ProjectTrainingLocation = ""

        self.ready_for_training = False
        self.NOF_Image = 0
        self.file_imgname_list = []

        self.NOF_Xml = 0
        self.file_xmlname_list = []
        
        self.Input_ImageLable_DIR = ""

        self.XMLDataset_names = []
        self.is_subfolder = False

        """#====================================================
        #CLASS INSTANCE
        self.rpb = QRoundProgressBar()
        #CHANGING THE PROGRESSABR STYLE
        self.rpb.rpb_setBarStyle('Hybrid1')

        #CHANGING THE LINE WIDTH
        self.rpb.rpb_setLineWidth(3)

        #PATH WIDTH
        self.rpb.rpb_setPathWidth(75)

        #CHANGING THE PATH COLOR
        self.rpb.rpb_setPathColor((125, 255, 255))

        #SETTING THE VALUE
        self.rpb.rpb_setValue(55)

        self.graphicsRPB = QGraphicsView(self)
        sceneRPB = QGraphicsScene()
        sceneRPB.addItem(self.rpb)
        self.graphicsRPB.setScene(sceneRPB)"""

        self.bar = QRoundProgressBar(self)
        self.bar.setFixedSize(85, 85)
        self.bar.setGeometry(8, 140, 95, 95)
        self.bar.setStyleSheet("background-color: #ffffff")

        self.bar.setDataPenWidth(3)
        self.bar.setOutlinePenWidth(3)
        self.bar.setDecimals(1)
        self.bar.setFormat('%v | 100%')
        # self.bar.resetFormat()
        self.bar.setNullPosition(90)
        self.bar.setBarStyle(QRoundProgressBar.StyleDonut)
        self.bar.setDataColors([(0., QColor.fromRgb(255,0,0)), (0.5, QColor.fromRgb(255,255,0)), (1., QColor.fromRgb(0,255,0))])
        self.bar.setMaximun(100)
        self.bar.setMinimun(0)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)

        self.myLongTask = TaskThread()
        #self.bar.set_range(0, 100)

        #====================================================
        # Loading the GIF
        self.label_Running = QLabel(self)
        self.label_Running.setGeometry(QtCore.QRect(5, 150, 95, 75))
        self.label_Running.setMinimumSize(QtCore.QSize(94, 75))
        self.label_Running.setMaximumSize(QtCore.QSize(94, 75))

        self.movie = QMovie(self.animate_movie)
        self.label_Running.setMovie(self.movie)
        self.label_Running.setVisible(False)
        #self.movie.start()

        self.checkLog = QCheckBox("Log",self)
        self.checkLog.setGeometry(100,205,50,20)
        self.checkLog.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.checkLog.setChecked(True)
        self.showlog = True

        self.Darknet_weights = None
        self.YOLO_TYPE = "yolov4"

        # Train options
        self.TRAIN_YOLO_TINY             = True
        self.TRAIN_SAVE_BEST_ONLY        = True # saves only best model according validation loss (True recommended)
        self.TRAIN_SAVE_CHECKPOINT       = False # saves all best validated checkpoints in training process (may require a lot disk space) (False recommended)
        self.TRAIN_MODEL_NAME            = f"{self.YOLO_TYPE}_custom"

        if self.YOLO_TYPE == "yolov4":
            if self.TRAIN_YOLO_TINY:
                self.Darknet_weights = configs.YOLO_V4_TINY_WEIGHTS  
            else:
                self.Darknet_weights = configs.YOLO_V4_WEIGHTS
        if self.YOLO_TYPE == "yolov3":
            if self.TRAIN_YOLO_TINY:
                self.Darknet_weights = configs.YOLO_V3_TINY_WEIGHTS  
            else:
                self.Darknet_weights = configs.YOLO_V3_WEIGHTS
                
        if self.TRAIN_YOLO_TINY: self.TRAIN_MODEL_NAME += "_Tiny"

        self.TRAIN_FROM_CHECKPOINT = False

        self.Animate_timer = QtCore.QTimer(self)
        self.Browse_timer = QtCore.QTimer(self)

    def serialize(self):
        res = super().serialize()
        res['model'] = self.YOLO_TYPE
        res['tiny'] = self.TRAIN_YOLO_TINY
        res['datasetfolder'] = self.TrainFolderEdit.text()
        res['train_from_checkpoint'] = self.TRAIN_FROM_CHECKPOINT
        
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.YOLO_TYPE = data['model']
            self.TRAIN_YOLO_TINY = data['tiny']

            if 'datasetfolder' in data:
                self.TrainFolderEdit.setText(str(data['datasetfolder']))

            if 'train_from_checkpoint' in data:
                self.TRAIN_FROM_CHECKPOINT = data['train_from_checkpoint']
                if self.TRAIN_FROM_CHECKPOINT:
                    if self.Load_YoloWeight_file(str(data['datasetfolder'])):
                        self.checkTrainChkPoint.setChecked(True)
                        self.FromTrainFolderEdit.setVisible(True)
                        self.browsPreWeightFiles.setVisible(True)
                else:
                    self.checkTrainChkPoint.setChecked(False)
                    self.FromTrainFolderEdit.setVisible(False)
                    self.browsPreWeightFiles.setVisible(False)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def browseWeightFolder(self):
        self.FromTrainFolderEdit.setText(str(QFileDialog.getExistingDirectory(self, "Select Directory")))

    #===================================================================================================
    # Browse to train Yolo
    def browseDatasetFolder(self):
        self.Input_ImageLable_DIR = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.Input_ImageLable_DIR = ", self.Input_ImageLable_DIR)

        self.TrainFolderEdit.setText(self.Input_ImageLable_DIR)
        self.Browse_timer.start()
        
#===============================================================
from time import sleep

class TaskThread(QtCore.QThread):
   notifyProgress = QtCore.pyqtSignal(int)

   def run(self):
       for i in range(101):
            self.notifyProgress.emit(i)
            sleep(0.1)

class QRoundProgressBar(QWidget):

    StyleDonut = 1
    StylePie = 2
    StyleLine = 3

    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    UF_VALUE = 1
    UF_PERCENT = 2
    UF_MAX = 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self.min = 0
        self.max = 100
        self.value = 25

        self.nullPosition = self.PositionTop
        self.barStyle = self.StyleDonut
        self.outlinePenWidth =1
        self.dataPenWidth = 1
        self.rebuildBrush = False
        self.format = "%p%"
        self.decimals = 1
        self.updateFlags = self.UF_PERCENT
        self.gradientData = []
        self.donutThicknessRatio = 0.75

    def setRange(self, min, max):
        self.min = min
        self.max = max

        if self.max < self.min:
            self.max, self.min = self.min, self.max

        if self.value < self.min:
            self.value = self.min
        elif self.value > self.max:
            self.value = self.max

        if not self.gradientData:
            self.rebuildBrush = True
        self.update()

    def setMinimun(self, min):
        self.setRange(min, self.max)

    def setMaximun(self, max):
        self.setRange(self.min, max)

    def setValue(self, val):
        if self.value != val:
            if val < self.min:
                self.value = self.min
            elif val > self.max:
                self.value = self.max
            else:
                self.value = val
            self.update()

    def setNullPosition(self, position):
        if position != self.nullPosition:
            self.nullPosition = position
            if not self.gradientData:
                self.rebuildBrush = True
            self.update()

    def setBarStyle(self, style):
        if style != self.barStyle:
            self.barStyle = style
            self.update()

    def setOutlinePenWidth(self, penWidth):
        if penWidth != self.outlinePenWidth:
            self.outlinePenWidth = penWidth
            self.update()

    def setDataPenWidth(self, penWidth):
        if penWidth != self.dataPenWidth:
            self.dataPenWidth = penWidth
            self.update()

    def setDataColors(self, stopPoints):
        if stopPoints != self.gradientData:
            self.gradientData = stopPoints
            self.rebuildBrush = True
            self.update()

    def setFormat(self, format):
        if format != self.format:
            self.format = format
            self.valueFormatChanged()

    def resetFormat(self):
        self.format = ''
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.decimals:
            self.decimals = count
            self.valueFormatChanged()

    def setDonutThicknessRatio(self, val):
        self.donutThicknessRatio = max(0., min(val, 1.))
        self.update()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QRectF(1, 1, outerRadius-2, outerRadius-2)

        buffer = QImage(outerRadius, outerRadius, QImage.Format_ARGB32)
        buffer.fill(0)

        p = QPainter(buffer)
        p.setRenderHint(QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # background
        #self.drawBackground(p, buffer.rect())

        # base circle
        self.drawBase(p, baseRect)

        # data circle
        arcStep = 360.0 / (self.max - self.min) * self.value
        self.drawValue(p, baseRect, self.value, arcStep)

        # center circle
        innerRect, innerRadius = self.calculateInnerRect(baseRect, outerRadius)
        self.drawInnerBackground(p, innerRect)

        # text
        self.drawText(p, innerRect, innerRadius, self.value)

        # finally draw the bar
        p.end()

        painter = QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, self.palette().background())

    def drawBase(self, p, baseRect):
        bs = self.barStyle
        if bs == self.StyleDonut:
            p.setPen(QPen(self.palette().shadow().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StylePie:
            p.setPen(QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StyleLine:
            p.setPen(QtGui.QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawEllipse(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2))

    def drawValue(self, p, baseRect, value, arcLength):
        # nothing to draw
        if value == self.min:
            return

        # for Line style
        if self.barStyle == self.StyleLine:
            p.setPen(QtGui.QPen(self.palette().highlight().color(), self.dataPenWidth))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawArc(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2),
                      self.nullPosition * 16,
                      -arcLength * 16)
            return

        # for Pie and Donut styles
        dataPath = QtGui.QPainterPath()
        dataPath.setFillRule(QtCore.Qt.WindingFill)

        # pie segment outer
        dataPath.moveTo(baseRect.center())
        dataPath.arcTo(baseRect, self.nullPosition, -arcLength)
        dataPath.lineTo(baseRect.center())

        p.setBrush(self.palette().highlight())
        p.setPen(QtGui.QPen(self.palette().shadow().color(), self.dataPenWidth))
        p.drawPath(dataPath)

    def calculateInnerRect(self, baseRect, outerRadius):
        # for Line style
        if self.barStyle == self.StyleLine:
            innerRadius = outerRadius - self.outlinePenWidth
        else:    # for Pie and Donut styles
            innerRadius = outerRadius * self.donutThicknessRatio

        delta = (outerRadius - innerRadius) / 2.
        innerRect = QtCore.QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawInnerBackground(self, p, innerRect):
        if self.barStyle == self.StyleDonut:
            p.setBrush(self.palette().alternateBase())

            cmod = p.compositionMode()
            p.setCompositionMode(QtGui.QPainter.CompositionMode_Source)

            p.drawEllipse(innerRect)

            p.setCompositionMode(cmod)

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.format:
            return

        text = self.valueToText(value)

        # !!! to revise
        f = self.font()
        # f.setPixelSize(innerRadius * max(0.05, (0.35 - self.decimals * 0.08)))
        #f.setPixelSize(innerRadius * 1.8 / len(text))
        p.setFont(f)

        textRect = innerRect
        p.setPen(self.palette().text().color())
        p.drawText(textRect, QtCore.Qt.AlignCenter, text)

    def valueToText(self, value):
        textToDraw = self.format

        format_string = '{' + ':.{}f'.format(self.decimals) + '}'

        if self.updateFlags & self.UF_VALUE:
            textToDraw = textToDraw.replace("%v", format_string.format(value))

        if self.updateFlags & self.UF_PERCENT:
            percent = (value - self.min) / (self.max - self.min) * 100.0
            textToDraw = textToDraw.replace("%p", format_string.format(percent))

        if self.updateFlags & self.UF_MAX:
            m = self.max - self.min + 1
            textToDraw = textToDraw.replace("%m", format_string.format(m))

        return textToDraw

    def valueFormatChanged(self):
        self.updateFlags = 0

        if "%v" in self.format:
            self.updateFlags |= self.UF_VALUE

        if "%p" in self.format:
            self.updateFlags |= self.UF_PERCENT

        if "%m" in self.format:
            self.updateFlags |= self.UF_MAX

        self.update()

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            dataBrush = QtGui.QConicalGradient()
            dataBrush.setCenter(0.5,0.5)
            dataBrush.setCoordinateMode(QtGui.QGradient.StretchToDeviceMode)

            for pos, color in self.gradientData:
                dataBrush.setColorAt(1.0 - pos, color)

            # angle
            dataBrush.setAngle(self.nullPosition)

            p = self.palette()
            p.setBrush(QtGui.QPalette.Highlight, dataBrush)
            self.setPalette(p)

#===============================================================
class TraingYolo(QtWidgets.QMainWindow):
    def __init__(self, content, YOLO_TYPE, TRAIN_YOLO_TINY, parent=None):
        super().__init__(parent)

        self.Global = GlobalVariable()
        self.content = content

        self.tiny = ""
        if TRAIN_YOLO_TINY:
            self.tiny = " Tiny"

        self.title = "AI Training Yolo Type : " + YOLO_TYPE + self.tiny
        self.top    = 100
        self.left   = 400
        self.width  = 980
        self.height = 826
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(40, 53, 123, 50);")

        self.Traing_Process = ""
        self.Traing_Loss = ""

        self.TlabelTraining = QTextEdit("" , self)
        self.TlabelTraining.setAlignment(Qt.AlignLeft)
        self.TlabelTraining.setFixedSize(800, 735)  
        self.TlabelTraining.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:9pt;")
        self.TlabelTraining.setGeometry(2,2,800,735)
        self.TlabelTraining.setReadOnly(True)
        self.TlabelTraining.verticalScrollBar().setVisible(False)

        #self.horScrollBar = self.TlabelTraining.horizontalScrollBar()
        #self.verScrollBar = self.TlabelTraining.setVerticalScrollBar()

        """self.horScrollBar = self.TlabelTraining.horizontalScrollBar()
        self.scrollIsAtEnd = self.verScrollBar.maximum() - self.verScrollBar.value() <= 10
        if self.scrollIsAtEnd:
            self.verScrollBar.setValue(self.verScrollBar.maximum()) # Scrolls to the bottom
            self.horScrollBar.setValue(0) # scroll to the left"""        

        #==================================================================
        #CPU

        self.CPUTitelLabel = QLabel("CPU Usage" , self)
        self.CPUTitelLabel.setAlignment(Qt.AlignLeft)
        self.CPUTitelLabel.setGeometry(805,15,170,20)
        self.CPUTitelLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.CPUUsageLabel = QLCDNumber(self, digitCount=3)
        self.CPUUsageLabel.setGeometry(810,40,120,50)
        self.CPUUsageLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.CPUPSLabel = QLabel("%" , self)
        self.CPUPSLabel.setAlignment(Qt.AlignLeft)
        self.CPUPSLabel.setGeometry(935,45,50,50)
        self.CPUPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        #==================================================================
        #Memory

        self.RAMTitelLabel = QLabel("Memory Usage" , self)
        self.RAMTitelLabel.setAlignment(Qt.AlignLeft)
        self.RAMTitelLabel.setGeometry(805,115,170,20)
        self.RAMTitelLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.RAMUsageLabel = QLCDNumber(self, digitCount=3)
        self.RAMUsageLabel.setGeometry(810,140,120,50)
        self.RAMUsageLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.RAMPSLabel = QLabel("%" , self)
        self.RAMPSLabel.setAlignment(Qt.AlignLeft)
        self.RAMPSLabel.setGeometry(935,145,50,50)
        self.RAMPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        #==================================================================

        self.TlabelLoss = QTextEdit("" , self)
        self.TlabelLoss.setAlignment(Qt.AlignLeft)
        self.TlabelLoss.setFixedSize(976, 50)  
        self.TlabelLoss.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:13pt; color:lightblue; border: 1px solid white;")
        self.TlabelLoss.setGeometry(2,770,976,50)
        self.TlabelLoss.verticalScrollBar().setVisible(False)

        #==================================================================
        #Progress

        self.ProgressLabel = QLabel("Traing Progressive" , self)
        self.ProgressLabel.setAlignment(Qt.AlignLeft)
        self.ProgressLabel.setGeometry(805,665,170,20)
        self.ProgressLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:10pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.NumberProgress = QLCDNumber(self, digitCount=3)
        self.NumberProgress.setGeometry(810,690,120,50)
        self.NumberProgress.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.ProgressPSLabel = QLabel("%" , self)
        self.ProgressPSLabel.setAlignment(Qt.AlignLeft)
        self.ProgressPSLabel.setGeometry(935,695,50,50)
        self.ProgressPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:9pt; color:lightblue; border: 1px solid white;")
        self.progress_bar.setGeometry(3,745,972,20)

        self.Terminal_timer = QtCore.QTimer(self)
        self.Terminal_timer.timeout.connect(self.TerminalPrint_interval)
        self.Terminal_timer.setInterval(50)
        self.Terminal_timer.start()

        self.Training_Process = ""
        self.Training_Loss = ""
        self.Training_Step = ""

        self.training_progress = 0
        self.progress_bar.setValue(int(self.training_progress))
        self.NumberProgress.display(str(int(self.training_progress)))

    def TerminalPrint_interval(self):
        if self.Global.hasGlobal('Debug_Training'):
            self.TlabelTraining.setText(str(self.Global.getGlobal('Debug_Training')))

        if self.Global.hasGlobal('Training_Process'):
            self.TlabelTraining.setText(str(self.Global.getGlobal('Training_Process')))
            self.TlabelTraining.verticalScrollBar().setValue(self.TlabelTraining.verticalScrollBar().maximum())

        if self.Global.hasGlobal('Training_Loss'):
            self.TlabelLoss.setText(str(self.Global.getGlobal('Training_Loss')))

        cpu_percent = psutil.cpu_percent(interval=0.5)
        self.CPUUsageLabel.display(str(int(cpu_percent)))

        Usage_virtual_memory = psutil.virtual_memory().percent
        self.RAMUsageLabel.display(str(int(Usage_virtual_memory)))

        if self.Global.hasGlobal('Training_Precent'):
                self.training_progress = str(self.Global.getGlobal('Training_Precent'))
                if self.Global.hasGlobal('Training_Step'):
                    if self.Global.getGlobal('Training_Step') == 'End':
                        self.progress_bar.setValue(int(100))
                        self.NumberProgress.display(str(int(100)))

                        self.TlabelLoss.setText(str(self.Global.getGlobal('Training_Step')) + " : Training Completed")
                        self.Terminal_timer.stop()

                        shutil.copy(self.content.ProjectTrainingLocation + "/dataset_names.txt", self.content.ProjectTrainingLocation + "/checkpoints/dataset_names.txt") # complete target filename given
                else:
                    #print("self.training_progress = ", self.training_progress)
                    self.progress_bar.setValue(int(self.training_progress))
                    self.NumberProgress.display(str(int(self.training_progress)))

    def get_available_gpus():
        local_device_protos = device_lib.list_local_devices()
        return [x.name for x in local_device_protos if x.device_type == 'GPU']

    #================================================
    #Close AI Training ---> Save Check Point
    def closeEvent(self, event):
        self.Terminal_timer.stop()
        print("AI Yolo Training Log is closed !!!")

        #self.Global.setGlobal('Stop_Training', True)

#===============================================================
@register_node(OP_NODE_OBJTRAIN)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_training.png"
    op_code = OP_NODE_OBJTRAIN
    op_title = "Train YoloV3_V4"
    content_label_objname = "Train YoloV3_V4"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[2]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = ObjectTrain(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCholeProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.combo.activated[str].connect(self.onChanged)
        self.content.checkTiny.stateChanged.connect(self.ConsiderTiny)
        self.content.checkTrainChkPoint.stateChanged.connect(self.TraingFromCheckPoint)

        self.content.browsPreWeightFiles.clicked.connect(self.content.browseWeightFolder)
        self.content.browsFiles.clicked.connect(self.content.browseDatasetFolder)

        #self.content.ConXMLYoloBtn.clicked.connect(self.run_XML_to_YOLOv3)
        self.content.TrainObjectBtn.clicked.connect(self.trainingObject)

        self.content.checkLog.stateChanged.connect(self.SelectShowLog)

        self.Global = GlobalVariable()

        self.content.Animate_timer.timeout.connect(self.CheckIfEnd_interval)
        self.content.Animate_timer.setInterval(500)

        self.content.Browse_timer.timeout.connect(self.Process_File)
        self.content.Browse_timer.setInterval(1000)

        self.content.myLongTask.notifyProgress.connect(self.on_progress)

    def evalImplementation(self):                 # <
        
        self.value = self.payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value

    def onChanged(self, text):
        print("Select Model = ", text)
        print("self.content.Path = ", self.content.Path)
        if text == "yolov3":
            if self.content.TRAIN_YOLO_TINY:
                self.content.checkTiny.setChecked(True)
            else:
                self.content.checkTiny.setChecked(False)

        elif text == "yolov4":
            if self.content.TRAIN_YOLO_TINY:
                self.content.checkTiny.setChecked(True)

            else:
                self.content.checkTiny.setChecked(False)

        self.content.YOLO_TYPE = text

        if self.content.YOLO_TYPE == "yolov4":
            if self.content.TRAIN_YOLO_TINY:
                self.content.Darknet_weights = configs.YOLO_V4_TINY_WEIGHTS 
            else:
                self.content.Darknet_weights = configs.YOLO_V4_WEIGHTS

        if self.content.YOLO_TYPE == "yolov3":
            if self.content.TRAIN_YOLO_TINY:
                self.content.Darknet_weights = configs.YOLO_V3_TINY_WEIGHTS  
            else:
                self.content.Darknet_weights = configs.YOLO_V3_WEIGHTS

        if self.content.TRAIN_YOLO_TINY: self.content.TRAIN_MODEL_NAME += "_Tiny"

    def ConsiderTiny(self, state):
        if state == QtCore.Qt.Checked:
            self.content.TRAIN_YOLO_TINY = True
            print("Select Yolo-Tiny")
        else:
            self.content.TRAIN_YOLO_TINY = False
            print("No need Yolo-Tiny !!!")

        if self.content.YOLO_TYPE == "yolov4":
            if self.content.TRAIN_YOLO_TINY:
                self.content.Darknet_weights = configs.YOLO_V4_TINY_WEIGHTS 
            else:
                self.content.Darknet_weights = configs.YOLO_V4_WEIGHTS

        if self.content.YOLO_TYPE == "yolov3":
            if self.content.TRAIN_YOLO_TINY:
                self.content.Darknet_weights = configs.YOLO_V3_TINY_WEIGHTS  
            else:
                self.content.Darknet_weights = configs.YOLO_V3_WEIGHTS

        if self.content.TRAIN_YOLO_TINY: self.content.TRAIN_MODEL_NAME += "_Tiny"

    def TraingFromCheckPoint(self, state):
        self.content.TRAIN_FROM_CHECKPOINT = not self.content.TRAIN_FROM_CHECKPOINT

        if self.content.TRAIN_FROM_CHECKPOINT:
            self.content.FromTrainFolderEdit.setVisible(True)
            self.content.browsPreWeightFiles.setVisible(True)

        else:
            self.content.FromTrainFolderEdit.setVisible(False)
            self.content.browsPreWeightFiles.setVisible(False)

    def SelectShowLog(self, state):
        if state == QtCore.Qt.Checked:
            self.content.showlog = True
            self.AI_TrainingYolo = TraingYolo(self.content.YOLO_TYPE, self.content.TRAIN_YOLO_TINY)
            self.AI_TrainingYolo.show()
        else:
            self.content.showlog = False

    def CheckIfEnd_interval(self):
        if self.Global.hasGlobal('Training_Step'):
            if self.Global.getGlobal('Training_Step') == 'End':

                print("CheckIfEnd_interval = ", self.Global.getGlobal('Training_Step'))

                self.content.label_Running.setVisible(False)
                self.content.movie.stop()

                self.content.TrainObjectBtn.setEnabled(True)

                self.content.Animate_timer.stop()

    #=========================================================================
    def Process_File(self):
        self.content.Browse_timer.stop()

        self.content.NOF_Image = 0
        self.content.NOF_Xml = 0

        # Step 1. Check
        # Count Number of png file
        for pngfile in glob.iglob(os.path.join(self.content.Input_ImageLable_DIR, "*.png")):
            self.content.file_imgname_list.append(pngfile)
            self.content.NOF_Image += 1

        print("NOF_Image = ", self.content.NOF_Image)

        # List txt name to list
        for pngfile in glob.iglob(os.path.join(self.content.Input_ImageLable_DIR, "*.xml")):
            self.content.file_xmlname_list.append(pngfile)
            self.content.NOF_Xml += 1

        # Step 2 Compare Number of Image and Number of Xml file
        print("NOF_Xml = ", self.content.NOF_Xml)
        if self.content.NOF_Image == self.content.NOF_Xml:

            OUTPUT_DIR = self.content.Input_ImageLable_DIR + "_WeightYolo"

            print("OUTPUT_DIR = ", OUTPUT_DIR)
            if os.path.isdir(OUTPUT_DIR): 
                print ("Folder images exist")

            else:
                os.makedirs(OUTPUT_DIR) 

            self.content.ProjectTrainingLocation = OUTPUT_DIR

            if os.path.isdir(self.content.ProjectTrainingLocation + "/checkpoints"): 
                print ("Folder checkpoints exist")

            else:
                os.makedirs(self.content.ProjectTrainingLocation + "/checkpoints") 

            if os.path.isdir(self.content.ProjectTrainingLocation + "/custom_dataset"): 
                print ("Folder dataset exist")

            else:
                os.makedirs(self.content.ProjectTrainingLocation + "/custom_dataset") 

            if os.path.isdir(self.content.ProjectTrainingLocation + "/custom_dataset/train"): 
                print ("Folder train exist")

            else:
                os.makedirs(self.content.ProjectTrainingLocation + "/custom_dataset/train") 

            if os.path.isdir(self.content.ProjectTrainingLocation + "/custom_dataset/test"): 
                print ("Folder test exist")

            else:
                os.makedirs(self.content.ProjectTrainingLocation + "/custom_dataset/test") 

            NOF_File = 0
            files = os.listdir(self.content.Input_ImageLable_DIR)
            # iterating over all the files in
            # the source directory
            global PNOF_File
            PNOF_File = ""

            self.on_start()
            for fname in files:
                # copying the files to the
                # destination directory
                shutil.copy2(os.path.join(self.content.Input_ImageLable_DIR,fname), self.content.ProjectTrainingLocation + "/custom_dataset/train")
                shutil.copy2(os.path.join(self.content.Input_ImageLable_DIR,fname), self.content.ProjectTrainingLocation + "/custom_dataset/test")
                NOF_File += 1

                PNOF_File = str(int((NOF_File/(self.content.NOF_Image*2)) * 100)) + "%"
                print("PNOF_File = ", PNOF_File)
                self.content.lblPercent.setText(PNOF_File)
                #self.bar.setValue(PNOF_File)

            # Step 3 Make XML to Yolo

            self.dataset_dir = self.content.ProjectTrainingLocation + "/custom_dataset/"
        
            self.Dataset_names = self.content.ProjectTrainingLocation + "/dataset_names.txt"
            self.Dataset_train = self.content.ProjectTrainingLocation + "/dataset_train.txt"
            self.Dataset_test = self.content.ProjectTrainingLocation + "/dataset_test.txt"

            print("Convert XML to Yolo !!!")
            NOF_File = 0

            for i, folder in enumerate(['train','test']):
                with open([self.Dataset_train,self.Dataset_test][i], "w") as file:
                    print(os.getcwd()+self.dataset_dir+folder)
                    img_path = os.path.join(self.dataset_dir+folder)
                    if self.content.is_subfolder:
                        for directory in os.listdir(img_path):
                            xml_path = os.path.join(img_path, directory)
                            self.ParseXML(xml_path, file)
                    else:
                        self.ParseXML(img_path, file)
                        print("img_path = " , img_path)

                NOF_File += 1

                PNOF_File = str(int((NOF_File/(self.content.NOF_Image)) * 100)) + "%"
                print("ParseXML = ", PNOF_File)
                self.content.lblPercent.setText(PNOF_File)

            print("Dataset_names:", self.content.XMLDataset_names)
            if len(self.content.XMLDataset_names) > 0:
                with open(self.Dataset_names, "w") as file:
                    for name in self.content.XMLDataset_names:
                        file.write(str(name)+'\n')

            if os.path.isfile(self.Dataset_names) and os.path.isfile(self.Dataset_train) and os.path.isfile(self.Dataset_test):
                print ("File exist")

                self.content.lbl2.setVisible(True)
                self.content.TrainObjectBtn.setEnabled(True)

            else:
                print ("File not exist, Need to convert XMLtoYolo first")
                self.content.msg.setText(
                        "File Train not exist, \nNeed to convert XMLtoYolo first \nAnd Select Dataset Folder")

                retval = self.content.msg.exec_()
                print("retval = ", retval)

        else:
            print("No. of Image not equal No. of Xml\nNo Data in ", self.content.ProjectTrainingLocation)
            self.content.msg.setText("No. of Image not equal No. of Xml\n" 
                        + "Image = " + str(self.content.NOF_Image) + "\nXml = " + str(self.content.NOF_Xml))
            retval = self.content.msg.exec_()

    def ParseXML(self, img_folder, file):
        for xml_file in glob.glob(img_folder+'/*.xml'):
            tree=ET.parse(open(xml_file))
            root = tree.getroot()
            image_name = root.find('filename').text
            img_path = img_folder+'/'+image_name
            for i, obj in enumerate(root.iter('object')):
                difficult = obj.find('difficult').text
                cls = obj.find('name').text
                if cls not in self.content.XMLDataset_names:
                    self.content.XMLDataset_names.append(cls)
                cls_id = self.content.XMLDataset_names.index(cls)
                xmlbox = obj.find('bndbox')
                OBJECT = (str(int(float(xmlbox.find('xmin').text)))+','
                        +str(int(float(xmlbox.find('ymin').text)))+','
                        +str(int(float(xmlbox.find('xmax').text)))+','
                        +str(int(float(xmlbox.find('ymax').text)))+','
                        +str(cls_id))
                img_path += ' '+OBJECT
            print(img_path)
            file.write(img_path+'\n')

    #========================================================================================================

    def Load_YoloWeight_file(self, location_path):
        if os.path.isfile(location_path + "/dataset_names.txt"):
            self.weightFile_valid_1 = True

        if os.path.exists(location_path + "/checkpoints"):
            self.weightFile_valid_2 = True 
    
        if self.weightFile_valid_1 and self.weightFile_valid_2:
            onlyfiles = [f for f in listdir(location_path + "/checkpoints") if isfile(join(location_path + "/checkpoints", f))]
            print("File in folder[2] = ", onlyfiles[2])
            if onlyfiles[2] == "yolov3_custom_Tiny.index":
                self.YOLO_TYPE = "yolov3"
                self.TRAIN_YOLO_TINY = True

            elif onlyfiles[2] == "yolov3_custom.index":
                self.YOLO_TYPE = "yolov3"
                self.TRAIN_YOLO_TINY = False

            elif onlyfiles[2] == "yolov4_custom_Tiny.index":
                self.YOLO_TYPE = "yolov4"
                self.TRAIN_YOLO_TINY = True

            elif onlyfiles[2] == "yolov4_custom.index":
                self.YOLO_TYPE = "yolov4"
                self.TRAIN_YOLO_TINY = False

            return True

        else:
            print("No weight file in folder")
            self.msg.setText("No weight file in folder")
            retval = self.msg.exec_()

            return False

    def on_start(self):
        self.content.myLongTask.start()

    def on_progress(self, i):
        self.content.bar.setValue(i)
        print("Progress ", i, "%")

    #=========================================================================
    def trainingObject(self):

        self.content.dataset_dir = self.content.ProjectTrainingLocation + "/custom_dataset/"
        print("trainingObject ---> self.content.dataset_dir = ", self.content.dataset_dir)

        self.content.Dataset_names = self.content.ProjectTrainingLocation + "/dataset_names.txt"
        self.content.Dataset_train = self.content.ProjectTrainingLocation + "/dataset_train.txt"
        self.content.Dataset_test = self.content.ProjectTrainingLocation + "/dataset_test.txt"

        self.content.bar.setVisible(False)

        if os.path.isfile(self.content.Dataset_names):
            print ("File exist")

            self.Global.setGlobal('Stop_Training', False)

            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
            device = device_lib.list_local_devices()
            print("device_list = ", device)

            gpus = tf.config.experimental.list_physical_devices('GPU')
            print(f'\nGPUs = {gpus}')

            if len(gpus) > 0:
                try: tf.config.experimental.set_memory_growth(gpus[0], True)
                except RuntimeError: pass

            self.content.TrainObjectBtn.setEnabled(False)
            self.content.label_Running.setVisible(True)
            self.content.movie.start()

            if self.content.showlog:
                self.AI_TrainingYolo = TraingYolo(self.content, self.content.YOLO_TYPE, self.content.TRAIN_YOLO_TINY)
                self.AI_TrainingYolo.show()

            training_app = training.app

            #Dataset_Folder, Darknet_weights, YOLO_TYPE, TRAIN_YOLO_TINY, TRAIN_FROM_CHECKPOINT, TRAIN_SAVE_BEST_ONLY, TRAIN_SAVE_CHECKPOINT, Weight_Folder
            training.TraingThread(self.content.ProjectTrainingLocation, self.content.Darknet_weights, 
                self.content.YOLO_TYPE, self.content.TRAIN_YOLO_TINY, self.content.TRAIN_FROM_CHECKPOINT, self.content.TRAIN_SAVE_BEST_ONLY,
                self.content.TRAIN_SAVE_CHECKPOINT, self.content.ProjectTrainingLocation).start()

            training_app.exec_()
            #self.train()

            self.content.Animate_timer.start()

        else:
            print ("File not exist, Need to convert XMLtoYolo first")
            self.content.msg.setText(
                    "File Train not exist, \nNeed to convert XMLtoYolo first \nAnd Select Dataset Folder")

            retval = self.content.msg.exec_()
            print("retval = ", retval)

            