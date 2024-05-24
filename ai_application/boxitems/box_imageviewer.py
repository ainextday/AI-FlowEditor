from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
import glob
import datetime
import cv2

import sys

class Ui_ImageVeiwer_MainWindow(object):
    def setupUi(self, MainWindow):
        self.top    = 25
        self.left   = 5
        self.width  = 320
        self.height = 240
        self.MainWindow = MainWindow
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 

        self.imageLabel = QLabel(self.MainWindow)
        self.scrollArea = QScrollArea(self.MainWindow)

        self.BrowseBtn = QPushButton(self.MainWindow)
        self.BrowseBtn.setGeometry(0, 222,20,20)

        self.LeftBtn = QPushButton(self.MainWindow)
        self.LeftBtn.setGeometry(40, 225,40,20)

        self.RightBtn = QPushButton(self.MainWindow)
        self.RightBtn.setGeometry(220, 225,40,20)

        self.Run_cbox = QCheckBox("Slide", self.MainWindow)
        self.Run_cbox.setGeometry(270,212,60,25)

        self.No_imageLabel = QLabel("0", self.MainWindow)
        self.No_imageLabel.setGeometry(155, 220,50,20)

        self.editImgInput = QLineEdit("0", self.MainWindow)
        self.editImgInput.setGeometry(100,220,50,20)
        self.editImgInput.setPlaceholderText("Jump")
        self.editImgInput.setStyleSheet("font-size:8pt;")

        self.ResizeBtn = QPushButton(self.MainWindow)
        self.ResizeBtn.setGeometry(312, 232,10,10)

class ImageViewer(QDMNodeContentWidget):
    resized = pyqtSignal()

    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.left_image = self.Path + "/icons/icon_left_arrow2.png"
        self.right_image = self.Path + "/icons/icons_right_arrow2.png"

        self.save_icon = self.Path + "/icons/icons_save.png"
        self.icon_round_btn = self.Path + "/icons/icons_btn_round10x10.png"
        self.icon_round_green = self.Path + "/icons/icons_btn_round10x10_green.png"

        self.Frame_w = 320
        self.Frame_h = 240 

        self.ui = Ui_ImageVeiwer_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.ui.imageLabel.setBackgroundRole(QPalette.Base)
        self.ui.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.imageLabel.setScaledContents(True)

        self.ui.BrowseBtn.setIcon(QIcon(self.save_icon))

        self.ui.LeftBtn.setIcon(QIcon(self.left_image))
        self.ui.LeftBtn.setStyleSheet("background-color: transparent; border: 1px;")

        self.ui.RightBtn.setIcon(QIcon(self.right_image))
        self.ui.RightBtn.setStyleSheet("background-color: transparent; border: 1px;")

        self.ui.Run_cbox.setStyleSheet("background-color: rgba(0, 124, 212, 150); color: white; font-size:5pt;")
        self.ui.No_imageLabel.setAlignment(Qt.AlignCenter)
        self.ui.No_imageLabel.setStyleSheet("background-color: rgba(0, 124, 212, 150); color: white; font-size:7pt;")

        self.ui.editImgInput.setAlignment(Qt.AlignCenter)
        self.ui.editImgInput.setStyleSheet("background-color: rgba(0, 124, 212, 150); color: white; font-size:7pt;")

        self.ui.ResizeBtn.setIcon(QIcon(self.icon_round_btn))
        self.ui.ResizeBtn.setStyleSheet("background-color: transparent; border: 0px;")

        self.resize_imageview = False
        self.NOF_Image = 0
        self.file_imgname_list = []

        self.fileLocation = ""
        self.autoslide_flag = False
        self.Current_Image = 0

        self.short_key_flag = False

        self.ResizeFrame_timer = QtCore.QTimer(self)
        self.display_timer = QtCore.QTimer(self)

        self.startTime = datetime.datetime.now().replace(microsecond=0)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = GlobaTimer.getGlobal("GlobalTimerApplication")

            self.ListGlobalTimer.append(self.ResizeFrame_timer)
            self.ListGlobalTimer.append(self.display_timer)
            
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['autoslide'] = self.autoslide_flag
        res['image_path'] = self.fileLocation
        res['resize'] = self.resize_imageview
        res['new_width'] = self.Frame_w
        res['new_height'] = self.Frame_h
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'resize' in data:
                self.resize_terminal = data['resize']
                if self.resize_terminal:
                    if 'new_width' in data:
                        self.Frame_w = data['new_width']

                    if 'new_height' in data:
                        self.Frame_h = data['new_height']

                    self.ReDrawGeometry()

            if 'autoslide' in data:
                self.autoslide_flag = data['autoslide']
                if self.autoslide_flag:
                    self.ui.Run_cbox.setChecked(True)
                    self.display_timer.start()

                else:
                    self.ui.Run_cbox.setChecked(False)
                    self.display_timer.stop()

            if 'image_path' in data:
                self.fileLocation = data['image_path']
                if len(self.fileLocation) > 0:
                    self.reload_image_list()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def reload_image_list(self):
        self.NOF_Image = 0
        self.file_imgname_list = []
        # Count Number of png file

        image_type = ["*.png", "*.jpeg", "*.jpg", "*.bmp", "*.gif"]
        for filetype in range(len(image_type)):
            for pngfile in glob.iglob(os.path.join(self.fileLocation,image_type[filetype])):
                self.file_imgname_list.append(pngfile)
                self.NOF_Image += 1

        print("NOF_Image = ", self.NOF_Image)
        print("self.file_imgname_list[0] = ", self.file_imgname_list[0])

        self.ui.imageLabel.setPixmap(QPixmap.fromImage(QImage(self.file_imgname_list[0])).scaled(self.Frame_w , self.Frame_h - 5, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.ui.imageLabel.adjustSize()

        self.label_width = self.ui.imageLabel.frameSize().width()
        self.label_height = self.ui.imageLabel.frameSize().height()

        print("self.label_width = ", self.label_width)
        print("self.label_height = ", self.label_height)

        self.Current_Image = 0
        self.ui.No_imageLabel.setText("/ " + str(self.NOF_Image - 1))
        self.ui.editImgInput.setText(str(self.Current_Image))
        self.display_timer.start()

    def DrawImagePixmap(self):
        self.ui.imageLabel.setPixmap(QPixmap.fromImage(QImage(self.file_imgname_list[self.Current_Image])).scaled(self.Frame_w , self.Frame_h - 10, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.ui.imageLabel.adjustSize()

    def browseSlot(self):
        self.fileLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.fileLocation)

        self.reload_image_list()

    def OpenLeft_Image(self):
        self.Current_Image -= 1

        if self.Current_Image < 0:
            self.Current_Image = 0
            self.DrawImagePixmap()

        else:
            self.DrawImagePixmap()

        # self.ui.No_imageLabel.setText(str(self.Current_Image) + " / " + str(self.NOF_Image - 1))
        self.ui.No_imageLabel.setText("/ " + str(self.NOF_Image - 1))
        self.ui.editImgInput.setText(str(self.Current_Image))
        self.display_timer.start()

    def OpenRight_Image(self):
        if not self.short_key_flag:
            self.Current_Image += 1
            if self.Current_Image <= self.NOF_Image - 1:
                self.DrawImagePixmap()

            else:
                self.Current_Image = self.NOF_Image -1
                self.DrawImagePixmap()

        else:
            if self.ui.editImgInput.text().isnumeric():
                self.Current_Image = int(self.ui.editImgInput.text())
                print("Jump -> Current_Image :", self.Current_Image)
            
                self.DrawImagePixmap()
                self.short_key_flag = False


        # self.ui.No_imageLabel.setText(str(self.Current_Image) + " / " + str(self.NOF_Image - 1))
        self.ui.No_imageLabel.setText("/ " + str(self.NOF_Image - 1))
        self.ui.editImgInput.setText(str(self.Current_Image))
        self.display_timer.start()

@register_node(OP_NODE_IMAGEVIEWER)
class Open_TERMINAL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_imageveiwer.png"
    op_code = OP_NODE_IMAGEVIEWER
    op_title = "ImageViewer"
    content_label_objname = "ImageViewer"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.tx_payload = {}

        self.NowTime = datetime.datetime.now().replace(microsecond=0)
        self.updateTime = None
        self.minutessince = 0

    def initInnerClasses(self):
        self.content = ImageViewer(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsTerminal(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.ui.BrowseBtn.clicked.connect(self.content.browseSlot)

        self.content.ui.LeftBtn.clicked.connect(self.content.OpenLeft_Image)
        self.content.ui.RightBtn.clicked.connect(self.content.OpenRight_Image)

        self.content.ui.Run_cbox.stateChanged.connect(self.AutoSlide)

        self.content.display_timer.timeout.connect(self.update_Image_payload)
        self.content.ui.editImgInput.textChanged[str].connect(self.UpdateCurrentImage)

    def evalImplementation(self):                 # <----------- To Create Socket
        self.value = self.tx_payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(op_code=self.op_code)
        else:
            self.evalChildren()

    def AutoSlide(self, state):
        if state == QtCore.Qt.Checked:
            self.content.autoslide_flag = True
            
            self.content.startTime = datetime.datetime.now().replace(microsecond=0)
            self.content.display_timer.start()

        else:
            self.content.autoslide_flag = False
            self.content.display_timer.stop()

    def ImagRead_Payload(self):
        image = cv2.imread(self.content.file_imgname_list[self.content.Current_Image])
        h, w, _ = image.shape
        self.tx_payload['img'] = image
        self.tx_payload['img_h'] = h
        self.tx_payload['img_w'] = w
        self.tx_payload['inputtype'] = "img"
        self.tx_payload['img_feed'] = True
        self.tx_payload['clock'] = datetime.datetime.now().strftime("%H:%M:%S")

        img_name = str(self.content.file_imgname_list[self.content.Current_Image])
        self.tx_payload['img_name'] =  img_name.replace('\\', '/')

    def UpdateCurrentImage(self, text):
        #print(len(text))
        if len(text) == 0:
            self.content.short_key_flag = True
            # print("self.content.short_key_flag :", self.content.short_key_flag)

        if self.content.short_key_flag and len(text) > 0:
            self.content.Current_Image = int(str(text).isnumeric())
            # print()

    def update_Image_payload(self):
        if self.content.Current_Image >= self.content.NOF_Image - 1:
            self.content.Current_Image = 0

        elif self.content.Current_Image < 0:
            self.content.Current_Image = self.content.NOF_Image

        if not self.content.autoslide_flag:
            self.ImagRead_Payload()

            self.content.display_timer.stop()
            self.evalImplementation()

        else:
            if self.minutessince >= 1:
                
                # self.content.ui.No_imageLabel.setText(str(self.content.Current_Image) + " / " + str(self.content.NOF_Image - 1))
                self.content.ui.No_imageLabel.setText("/ " + str(self.content.NOF_Image - 1))
                self.content.ui.editImgInput.setText(str(self.content.Current_Image))
                self.content.Current_Image += 1

                self.content.ui.imageLabel.setPixmap(QPixmap.fromImage(QImage(self.content.file_imgname_list[self.content.Current_Image])).scaled(self.content.Frame_w, self.content.Frame_h - 10, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                self.content.ui.imageLabel.adjustSize()

                self.ImagRead_Payload()
                self.evalImplementation()

                self.content.startTime = datetime.datetime.now().replace(microsecond=0)
                self.minutessince = 0

            else:
                self.NowTime = datetime.datetime.now().replace(microsecond=0)
                self.updateTime = self.NowTime - self.content.startTime
                self.minutessince = int(self.updateTime.total_seconds() / 1.1)

                