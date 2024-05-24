from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import os

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId
import time

import torch
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw
import datetime
import sys

import shutil

import argparse
import warnings

from ai_application.AI_Module.strhub.data.module import SceneTextDataModule
from ai_application.AI_Module.strhub.models.utils import load_from_checkpoint, parse_model_args

class OCRREADER(QDMNodeContentWidget):
    def initUI(self):
        # parser = argparse.ArgumentParser()
        # args, unknown = parser.parse_known_args()
        # self.kwargs = parse_model_args(unknown)

        self.kwargs = {}

        self.Path = os.path.dirname(os.path.abspath(__file__))
        cmd_image = self.Path + "/icons/icons_cmdimg.png"

        self.browse_icon = self.Path + "/icons/icons_save_ib.png"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        self.animate_movie = self.Path + "/icons/icons_ocr_read.gif"

        self.innit_image_path = self.Path + "/icons/icons_ocr.png"

        self.font_path =  self.Path  + "/font/SarunThangLuang.ttf"

        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,2,125,45)
        self.lbl.setStyleSheet("font-size:8pt;")

        self.SwitchDetect = QPushButton(self)
        self.SwitchDetect.setGeometry(137,5,37,20)
        self.SwitchDetect.setIcon(QIcon(self.off_icon))
        self.SwitchDetect.setIconSize(QtCore.QSize(37,20))
        self.SwitchDetect.setStyleSheet("background-color: transparent; border: 0px;")  

        # ==================================================
        self.combo = QComboBox(self)
        self.combo.addItem("Read")
        self.combo.addItem("Custom")
        self.combo.addItem("Train")

        self.combo.setGeometry(78,30,95,20)
        self.combo.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.combo.setCurrentText("Read")


        self.comboPreWeight = QComboBox(self)
        self.comboPreWeight.addItem("parseq")
        self.comboPreWeight.addItem("parseq_tiny")
        self.comboPreWeight.addItem("abinet")
        self.comboPreWeight.addItem("crnn")
        self.comboPreWeight.addItem("trba")
        self.comboPreWeight.addItem("vitstr")

        self.comboPreWeight.setGeometry(78,55,95,20)
        self.comboPreWeight.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.comboPreWeight.setCurrentText("parseq")


        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(155,85,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        #====================================================
        # Loading the GIF
        self.labelAnimate = QLabel(self)
        self.labelAnimate.setGeometry(QtCore.QRect(10, 28, 75, 60))
        self.labelAnimate.setMinimumSize(QtCore.QSize(60, 75))
        self.labelAnimate.setMaximumSize(QtCore.QSize(60, 75))

        self.movie = QMovie(self.animate_movie)
        self.labelAnimate.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        # self.labelAnimate.setVisible(False)

        # ===================================================
        self.lblConF = QLabel("Conf:" , self)
        self.lblConF.setAlignment(Qt.AlignLeft)
        self.lblConF.setGeometry(78,88,30,30)
        self.lblConF.setStyleSheet("font-size:6pt;")

        self.editConF = QLineEdit("0.5", self)
        self.editConF.setAlignment(Qt.AlignLeft)
        self.editConF.setGeometry(110,85,42,20)
        self.editConF.setPlaceholderText("Confident")
        self.editConF.setStyleSheet("font-size:8pt;")

        # ====================================================
        # Label Input / Output
        self.lblPayload = QLabel("R.Img" , self)
        self.lblPayload.setAlignment(Qt.AlignLeft)
        self.lblPayload.setGeometry(2,26,50,20)
        self.lblPayload.setStyleSheet("color: #0008FF; font-size:5pt;")

        self.lblImgIn = QLabel("Org Img" , self)
        self.lblImgIn.setAlignment(Qt.AlignLeft)
        self.lblImgIn.setGeometry(2,72,50,20)
        self.lblImgIn.setStyleSheet("color: #98012E; font-size:5pt;")

        self.lblImgOut = QLabel("Img + OCR" , self)
        self.lblImgOut.setAlignment(Qt.AlignLeft)
        self.lblImgOut.setGeometry(120,73,60,20)
        self.lblImgOut.setStyleSheet("color: #FF1C6A; font-size:5pt;")

        # ====================================================

        self.device = 'cuda:0'

        self.command = ""

        models = ['parseq', 'parseq_tiny', 'abinet', 'crnn', 'trba', 'vitstr']
        self.StartProcessDetect_flag = False

        self.parseq = None
        self.img_transform = None

        self.font_scale = 3
        self.font_color = "#00FFFF"

        self.beta = 0.2

        self.info = "Waiting"
        self.info2 = "Image"

        self.NumberOf_Char = 3
        self.Image_Global_Name = ""
        self.Label_Global_Name = ""

        self.mode_crop_yolo = False
        self.high_confident_mode = False

        self.setting_image1 = None
        self.setting_image2 = None
        self.setting_image3 = None

        self.param_1a = 11
        self.param_1b = -1
        self.lbl_param1 = ""

        self.param_2a = 11
        self.param_2b = -1
        self.lbl_param2 = ""

        self.param_3a = 15
        self.param_3b = -1
        self.lbl_param3 = ""

        self.hiconf_list = []

        self.read_custom = False
        self.custom_weight_path = ""

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['preweight'] = self.comboPreWeight.currentText()
        res['auto_start'] = self.StartProcessDetect_flag

        res['font_scale'] = self.font_scale
        res['font_color'] = self.font_color
        res['beta'] = self.beta
        res['info'] = self.info
        res['info2'] = self.info2

        res['num_char'] = self.NumberOf_Char
        res['conf'] = float(self.editConF.text())

        res['global_img'] = self.Image_Global_Name
        res['global_lbl'] = self.Label_Global_Name

        # res['input_mode'] = self.mode_crop_yolo
        res['high_confident_mode'] = self.high_confident_mode

        res['param_1a'] = self.param_1a
        res['param_1b'] = self.param_1b

        res['param_2a'] = self.param_2a
        res['param_2b'] = self.param_2b

        res['param_3a'] = self.param_3a
        res['param_3b'] = self.param_3b

        res['read_custom'] = self.read_custom
        res['custom_weight_path'] = self.custom_weight_path

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'preweight' in data:
                self.comboPreWeight.setCurrentText(data['preweight'])

            if 'font_scale' in data:
                self.font_scale = data['font_scale']

            if 'font_color' in data:
                self.font_color = data['font_color']

            if 'beta' in data:
                self.beta = data['beta']

            if 'info' in data:
                self.info = data['info']

            if 'info2' in data:
                self.info2 = data['info2']

            if 'num_char' in data:
                self.NumberOf_Char = data['num_char']

            if 'conf' in data:
                self.editConF.setText(str(data['conf']))

            if 'global_img' in data:  
                self.Image_Global_Name = data['global_img']

            if 'global_lbl' in data:
                self.Label_Global_Name = data['global_lbl']

            # if 'input_mode' in data:
            #     self.mode_crop_yolo = data['input_mode']

            if 'high_confident_mode' in data:
                self.high_confident_mode = data['high_confident_mode']

            if 'param_1a' in data:
                self.param_1a = data['param_1a']

            if 'param_1b' in data:
                self.param_1b = data['param_1b']

            if 'param_2a' in data:
                self.param_2a = data['param_2a']

            if 'param_2b' in data:
                self.param_2b = data['param_2b']

            if 'param_3a' in data:
                self.param_3a = data['param_3a']

            if 'param_3b' in data:
                self.param_3b = data['param_3b']

            if 'read_custom' in data:        
                self.read_custom = data['read_custom']

            if 'custom_weight_path' in data:
                self.custom_weight_path = data['custom_weight_path']

            if 'auto_start' in data:
                self.StartProcessDetect_flag = data['auto_start']
                if self.StartProcessDetect_flag:
                    self.SwitchDetect.setIcon(QIcon(self.on_icon))

                    if self.read_custom:
                        print("\033[92m {}\033[00m".format("Read ORC Custom weight : " + str(self.read_custom)))
                        print("\033[92m {}\033[00m".format("Custom Weight path : " + str(self.custom_weight_path)))

                        self.parseq = load_from_checkpoint(self.custom_weight_path, **self.kwargs).eval().to(self.device)
                        # self.img_transform = SceneTextDataModule.get_transform(self.parseq.hparams.img_size)

                        self.combo.setCurrentText("Custom")
                    
                    else:
                        # Load model and image transforms
                        self.parseq = torch.hub.load('baudm/parseq', self.comboPreWeight.currentText(), pretrained=True).eval()
                        # self.parseq = torch.hub._load_local('baudm/parseq', self.comboPreWeight.currentText(), pretrained=True).eval()

                        self.combo.setCurrentText("Read")
                    
                    self.img_transform = SceneTextDataModule.get_transform(self.parseq.hparams.img_size)
                    #print("self.img_transform :", self.img_transform)

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
# ===========================================================
class OCRSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content
        # print("self.content :", self.content)

        self.title = "OCR Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 1200
        self.height = 955
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
        self.current_beta_lbl = QLabel("Backgroud Beta" , self)
        self.current_beta_lbl.setAlignment(Qt.AlignLeft)
        self.current_beta_lbl.setGeometry(10,575,240,30)
        self.current_beta_lbl.setStyleSheet("color: yellow; font-size:12pt;")

        self.Scale_beta_lbl = QLabel(self)
        self.Scale_beta_lbl.setAlignment(Qt.AlignLeft)
        self.Scale_beta_lbl.setGeometry(250,575,50,30)
        self.Scale_beta_lbl.setStyleSheet("color: yellow; font-size:12pt;")

        self.Scale_beta_lbl.setText("{:.2f}".format(self.content.beta))

        self.Update_increase_beta = QPushButton("+", self)
        self.Update_increase_beta.setGeometry(250,535,50,35)
        self.Update_increase_beta.clicked.connect(self.onUpdateIncrease_beta)

        self.Update_decrease_beta = QPushButton("-", self)
        self.Update_decrease_beta.setGeometry(250,615,50,35)
        self.Update_decrease_beta.clicked.connect(self.onUpdateDecrease_beta)

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

        self.set_high_confident_mode = QCheckBox("High Confident Mode",self)
        self.set_high_confident_mode.setGeometry(10,665,300,20)
        self.set_high_confident_mode.setStyleSheet("color: #FC03C7; font-size:10pt;")

        if self.content.high_confident_mode:
            self.set_high_confident_mode.setChecked(True)
        else:
            self.set_high_confident_mode.setChecked(False)

        self.set_high_confident_mode.stateChanged.connect(self.Set_HCM_Change)

        # Read Custom Weight
        self.set_read_custom = QCheckBox("Read Custom Weight",self)
        self.set_read_custom.setGeometry(10,695,300,20)
        self.set_read_custom.setStyleSheet("color: lightblue; font-size:10pt;")

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(10,725,30,30)
        self.browsFiles.setIcon(QIcon(self.content.browse_icon))
        self.browsFiles.setIconSize(QtCore.QSize(35,30))
        self.browsFiles.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lblPath = QLabel("Select Custom weight path" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(50,730,400,25)
        self.lblPath.setStyleSheet("color: white; font-size:7pt;")

        if self.content.read_custom:
            self.set_read_custom.setChecked(True)
            self.lblPath.setText(self.content.custom_weight_path)
        else:
            self.set_read_custom.setChecked(False)

        self.set_read_custom.stateChanged.connect(self.Set_ReadCustomeWeight)
        self.browsFiles.clicked.connect(self.browseSlot)

        # =======================================================================
        # UI Phase 2
        self.setInfo_edit = QLineEdit("", self)
        self.setInfo_edit.setAlignment(Qt.AlignCenter)
        self.setInfo_edit.setGeometry(520,40,300,25)
        self.setInfo_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setInfo_edit.setPlaceholderText("Infomation 1")
        self.setInfo_edit.setText(self.content.info)

        self.setInfo2_edit = QLineEdit("", self)
        self.setInfo2_edit.setAlignment(Qt.AlignCenter)
        self.setInfo2_edit.setGeometry(520,70,300,25)
        self.setInfo2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setInfo2_edit.setPlaceholderText("Infomation 2")
        self.setInfo2_edit.setText(self.content.info2)

        self.conner_lt = QLabel("Expect Char :" , self)
        self.conner_lt.setAlignment(Qt.AlignLeft)
        self.conner_lt.setGeometry(520,100,120,25)
        self.conner_lt.setStyleSheet("color: yellow; font-size:6pt;")

        self.setNOFChar_edit = QLineEdit("", self)
        self.setNOFChar_edit.setAlignment(Qt.AlignCenter)
        self.setNOFChar_edit.setGeometry(650,100,60,25)
        self.setNOFChar_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setNOFChar_edit.setPlaceholderText("1")
        self.setNOFChar_edit.setText(str(self.content.NumberOf_Char))

        # self.Image_Global_Name = ""
        # self.Label_Global_Name = ""

        self.gb_name = QLabel("Global Image Name:" , self)
        self.gb_name.setAlignment(Qt.AlignLeft)
        self.gb_name.setGeometry(520,135,120,25)
        self.gb_name.setStyleSheet("color: lightblue; font-size:6pt;")
        
        self.gb_name_edit = QLineEdit("", self)
        self.gb_name_edit.setAlignment(Qt.AlignCenter)
        self.gb_name_edit.setGeometry(650,135,175,25)
        self.gb_name_edit.setStyleSheet("color: red; font-size:8pt;")
        self.gb_name_edit.setPlaceholderText("Global Image Name")
        self.gb_name_edit.setText(str(self.content.Image_Global_Name))


        self.lbl_name = QLabel("Global Label Name:" , self)
        self.lbl_name.setAlignment(Qt.AlignLeft)
        self.lbl_name.setGeometry(520,170,120,25)
        self.lbl_name.setStyleSheet("color: orange; font-size:6pt;")

        self.lbl_name_edit = QLineEdit("", self)
        self.lbl_name_edit.setAlignment(Qt.AlignCenter)
        self.lbl_name_edit.setGeometry(650,170,175,25)
        self.lbl_name_edit.setStyleSheet("color: red; font-size:8pt;")
        self.lbl_name_edit.setPlaceholderText("Global Label Name")
        self.lbl_name_edit.setText(str(self.content.Label_Global_Name))

        #=====================================================================
        # Content.Image ImageView
        self.lbl_setting_image1 = QLabel("" , self)
        self.lbl_setting_image1.setAlignment(Qt.AlignLeft)
        self.lbl_setting_image1.setGeometry(530,205,320,240)
        self.lbl_setting_image1.setStyleSheet("background-color: rgba(0, 32, 130, 225); border: 1px solid white; border-radius: 3%")
        # self.update_setting_img(self.content.setting_image)
        
        self.current_beta1a_lbl = QLabel("ADAPTIVE THRESH MEAN" , self)
        self.current_beta1a_lbl.setAlignment(Qt.AlignLeft)
        self.current_beta1a_lbl.setGeometry(860,205,300,30)
        self.current_beta1a_lbl.setStyleSheet("color: yellow; font-size:10pt;")

        self.param1A_edit = QLineEdit("", self)
        self.param1A_edit.setAlignment(Qt.AlignCenter)
        self.param1A_edit.setGeometry(860,245,60,35)
        self.param1A_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.param1A_edit.setPlaceholderText("11")
        self.param1A_edit.setText(str(self.content.param_1a))

        self.param1B_edit = QLineEdit("", self)
        self.param1B_edit.setAlignment(Qt.AlignCenter)
        self.param1B_edit.setGeometry(930,245,60,35)
        self.param1B_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.param1B_edit.setPlaceholderText("-1")
        self.param1B_edit.setText(str(self.content.param_1b))

        self.Update_param1 = QPushButton("Update", self)
        self.Update_param1.setGeometry(1000,245,80,35)
        self.Update_param1.clicked.connect(self.onUpdateParama1)

        self.lbl_OCR1 = QLabel("" , self)
        self.lbl_OCR1.setAlignment(Qt.AlignLeft)
        self.lbl_OCR1.setGeometry(860,300,300,35)
        self.lbl_OCR1.setStyleSheet("color: yellow; font-size:12pt;")

        # ======================================================================

        self.lbl_setting_image2 = QLabel("" , self)
        self.lbl_setting_image2.setAlignment(Qt.AlignLeft)
        self.lbl_setting_image2.setGeometry(530,455,320,240)
        self.lbl_setting_image2.setStyleSheet("background-color: rgba(0, 32, 130, 225); border: 1px solid white; border-radius: 3%")

        self.current_beta1a_lbl = QLabel("ADAPTIVE THRESH GAUSSIAN" , self)
        self.current_beta1a_lbl.setAlignment(Qt.AlignLeft)
        self.current_beta1a_lbl.setGeometry(860,455,300,30)
        self.current_beta1a_lbl.setStyleSheet("color: lightblue; font-size:10pt;")

        self.param2A_edit = QLineEdit("", self)
        self.param2A_edit.setAlignment(Qt.AlignCenter)
        self.param2A_edit.setGeometry(860,490,60,35)
        self.param2A_edit.setStyleSheet("color: lightblue; font-size:8pt;")
        self.param2A_edit.setPlaceholderText("11")
        self.param2A_edit.setText(str(self.content.param_2a))

        self.param2B_edit = QLineEdit("", self)
        self.param2B_edit.setAlignment(Qt.AlignCenter)
        self.param2B_edit.setGeometry(930,490,60,35)
        self.param2B_edit.setStyleSheet("color: lightblue; font-size:8pt;")
        self.param2B_edit.setPlaceholderText("-1")
        self.param2B_edit.setText(str(self.content.param_2b))

        self.Update_param2 = QPushButton("Update", self)
        self.Update_param2.setGeometry(1000,490,80,35)
        self.Update_param2.clicked.connect(self.onUpdateParama2)

        self.lbl_OCR2 = QLabel("" , self)
        self.lbl_OCR2.setAlignment(Qt.AlignLeft)
        self.lbl_OCR2.setGeometry(860,545,300,35)
        self.lbl_OCR2.setStyleSheet("color: lightblue; font-size:12pt;")

        # ======================================================================

        self.lbl_setting_image3 = QLabel("" , self)
        self.lbl_setting_image3.setAlignment(Qt.AlignLeft)
        self.lbl_setting_image3.setGeometry(530,705,320,240)
        self.lbl_setting_image3.setStyleSheet("background-color: rgba(0, 32, 130, 225); border: 1px solid white; border-radius: 3%")

        self.current_beta1a_lbl = QLabel("GAUSSIAN + THRESH_TRUNC" , self)
        self.current_beta1a_lbl.setAlignment(Qt.AlignLeft)
        self.current_beta1a_lbl.setGeometry(860,705,300,30)
        self.current_beta1a_lbl.setStyleSheet("color: white; font-size:10pt;")

        self.param3A_edit = QLineEdit("", self)
        self.param3A_edit.setAlignment(Qt.AlignCenter)
        self.param3A_edit.setGeometry(860,745,60,35)
        self.param3A_edit.setStyleSheet("color: white; font-size:8pt;")
        self.param3A_edit.setPlaceholderText("11")
        self.param3A_edit.setText(str(self.content.param_3a))

        self.param3B_edit = QLineEdit("", self)
        self.param3B_edit.setAlignment(Qt.AlignCenter)
        self.param3B_edit.setGeometry(930,745,60,35)
        self.param3B_edit.setStyleSheet("color: white; font-size:8pt;")
        self.param3B_edit.setPlaceholderText("-1")
        self.param3B_edit.setText(str(self.content.param_3b))

        self.Update_param3 = QPushButton("Update", self)
        self.Update_param3.setGeometry(1000,745,80,35)
        self.Update_param3.clicked.connect(self.onUpdateParama3)

        self.lbl_OCR3 = QLabel("" , self)
        self.lbl_OCR3.setAlignment(Qt.AlignLeft)
        self.lbl_OCR3.setGeometry(860,800,300,35)
        self.lbl_OCR3.setStyleSheet("color: white; font-size:12pt;")

        # ======================================================================

        self.display_timer = QtCore.QTimer(self)
        self.display_timer.timeout.connect(self.update_setting_img)
        self.display_timer.setInterval(10)
        self.display_timer.start()

    #=======================================================================
    # End UI
    #=======================================================================
    def Set_ReadCustomeWeight(self, state):
        if state == QtCore.Qt.Checked:
            self.content.read_custom = True
        else:
            self.content.read_custom = False

    def browseSlot(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Weight Files (*.ckpt)", options=options)

        if files:
            self.fileLocation = files[0]
            print("self.fileLocation :", self.fileLocation)

            # self.content.custom_weight_path = File_Name[len(File_Name) - 1]

            self.content.custom_weight_path = self.fileLocation
            self.content.custom_weight_path = self.content.custom_weight_path.replace('/', '\\')
            
            File_Name = self.fileLocation.split("/")
            print("File_Name :", File_Name)
            file_folder = "\\".join(File_Name[:-1]) + "\\"

            print("file_folder :", file_folder)

            checkpoint_folder = File_Name[len(File_Name) - 2]
            parseq_folder = File_Name[len(File_Name) - 3]

            print("checkpoint_folder :", checkpoint_folder)
            print("parseq_folder :", parseq_folder)

            correct_weight = str(File_Name[len(File_Name) - 1]).split(".")[1]
            print("correct_weight :", correct_weight)
            if correct_weight == "ckpt":
                if checkpoint_folder == "checkpoints" and parseq_folder == "parseq":
                    self.content.read_custom = True
                    self.set_read_custom.setChecked(True)

                    print("self.custom_weight_path = ", self.content.custom_weight_path)
                    self.lblPath.setText(self.content.custom_weight_path)

                else:
                    print("file_folder :", file_folder + "parseq")

                    if os.path.isdir(file_folder + "parseq"): 
                        print ("Folder images exist")

                    else:
                        os.makedirs(file_folder + "parseq")

                        new_file_folder = file_folder + "parseq" + "\\checkpoints"
                        print("new_file_folder :", new_file_folder)

                        os.makedirs(new_file_folder)

                        self.content.custom_weight_path = new_file_folder +"\\" + str(File_Name[len(File_Name) - 1])
                        print("self.custom_weight_path = ", self.content.custom_weight_path)
                        self.lblPath.setText(self.content.custom_weight_path)

                        # Move the file to the 'checkpoints' folder
                        shutil.move(self.fileLocation, self.content.custom_weight_path)

                self.content.parseq = load_from_checkpoint(self.content.custom_weight_path, **self.content.kwargs).eval().to(self.content.device)
                # self.img_transform = SceneTextDataModule.get_transform(self.parseq.hparams.img_size)

                self.content.combo.setCurrentText("Custom")

    def onUpdateParama1(self):    
        if self.content.high_confident_mode:
            if len(self.param1A_edit.text()) > 0:
                self.content.param_1a = int(self.param1A_edit.text())

            if len(self.param1B_edit.text()) > 0:
                self.content.param_1b = int(self.param1B_edit.text())

    def onUpdateParama2(self):    
        if self.content.high_confident_mode:
            if len(self.param2A_edit.text()) > 0:
                self.content.param_2a = int(self.param2A_edit.text())

            if len(self.param2B_edit.text()) > 0:
                self.content.param_2b = int(self.param2B_edit.text())

    def onUpdateParama3(self):    
        if self.content.high_confident_mode:
            if len(self.param3A_edit.text()) > 0:
                self.content.param_3a = int(self.param3A_edit.text())

            if len(self.param3B_edit.text()) > 0:
                self.content.param_3b = int(self.param3B_edit.text())
    
    def update_setting_img(self):
        if self.content.high_confident_mode:
            if type(self.content.setting_image1) != type(None):
                self.lbl_setting_image1.setPixmap(QtGui.QPixmap.fromImage(self.draw_setting_image(self.content.setting_image1)))
                self.lbl_OCR1.setText(self.content.lbl_param1)

            if type(self.content.setting_image2) != type(None):
                self.lbl_setting_image2.setPixmap(QtGui.QPixmap.fromImage(self.draw_setting_image(self.content.setting_image2)))
                self.lbl_OCR2.setText(self.content.lbl_param2)
            
            if type(self.content.setting_image3) != type(None):
                self.lbl_setting_image3.setPixmap(QtGui.QPixmap.fromImage(self.draw_setting_image(self.content.setting_image3)))
                self.lbl_OCR3.setText(self.content.lbl_param3)

    def draw_setting_image(self, image):
        if type(image) != type(None):
            img_height, img_width, img_colors = image.shape
            # scale_w = float(640) / float(img_width)
            # scale_h = float(480) / float(img_height)
            # scale = min([scale_w, scale_h])

            # if scale == 0:
            #     scale = 1
            
            # # image = cv2.resize(image, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            # image = cv2.resize(image, (320, 240))

            # self.yolo_img_height, self.yolo_img_width, _ =  cropped_image.shape

            # # Define the size of the yolo cropped image
            # yolo_img_height = h
            # yolo_img_width = w

            # Define the desired size of the canvas
            canvas_height = 240
            canvas_width = 320

            # Calculate the scaling factors to fit the yolo cropped image into the canvas
            scale_factor = min(canvas_width / img_width, canvas_height / img_height)

            # Calculate the new dimensions of the resized image
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)

            # Resize the yolo cropped image
            resized_yolo_img = cv2.resize(image, (new_width, new_height))

            # Create the canvas with the desired size
            canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

            # Calculate the position to paste the resized image onto the canvas
            start_x = (canvas_width - new_width) // 2
            start_y = (canvas_height - new_height) // 2

            # Paste the resized image onto the canvas
            canvas[start_y:start_y + new_height, start_x:start_x + new_width] = resized_yolo_img
            
            # Draw Rectangle
            # if self.content.setCameraROI:
            #     img = cv2.putText(img  , "scale : W{:.3f} , H{:.3f} ".format(scale_w, scale_h)  , ( 10, 20 ), cv2.FONT_HERSHEY_DUPLEX, 0.7, ( 0, 0, 255 ), 1)
            #     img = cv2.rectangle(img,(int(self.content.setROIX1 * scale_w) , int(self.content.setROIY1 * scale_w)), (int(self.content.setROIX2* scale_w), int(self.content.setROIY2* scale_w)), (0 , 0, 255), 1)

            image = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
            height, width, bpc = image.shape
            bpl = bpc * width
            image = QtGui.QImage(image.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            return image
    
    def Set_HCM_Change(self, state):
        if state == QtCore.Qt.Checked:
            self.content.high_confident_mode = True
        else:
            self.content.high_confident_mode = False

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
        if self.content.font_scale > 3:
            self.content.font_scale = 3
            self.Scale_font_lbl.setText(str(self.content.font_scale))

    def onUpdateDecrease(self):
        self.content.font_scale -= 1
        self.Scale_font_lbl.setText(str(self.content.font_scale))
        if self.content.font_scale < 1:
            self.content.font_scale = 1
            self.Scale_font_lbl.setText(str(self.content.font_scale))

    def onUpdateIncrease_beta(self):
        self.content.beta +=  0.1
        self.Scale_beta_lbl.setText("{:.2f}".format(self.content.beta))
        if self.content.beta > 1:
            self.content.beta = 1
            self.Scale_beta_lbl.setText("{:.2f}".format(self.content.beta))

    def onUpdateDecrease_beta(self):
        self.content.beta -= 0.1
        self.Scale_beta_lbl.setText("{:.2f}".format(self.content.beta))
        if self.content.beta < 0.1:
            self.content.beta = 0.1
            self.Scale_beta_lbl.setText("{:.2f}".format(self.content.beta))

    def update_param(self):
        if len(self.setNOFChar_edit.text()) > 0:
            self.content.NumberOf_Char = int(self.setNOFChar_edit.text())

        if len(self.param1A_edit.text()) > 0:
            self.content.param_1a = int(self.param1A_edit.text())

        if len(self.param1B_edit.text()) > 0:
            self.content.param_1b = int(self.param1B_edit.text())

        if len(self.param2A_edit.text()) > 0:
            self.content.param_2a = int(self.param2A_edit.text())

        if len(self.param2B_edit.text()) > 0:
            self.content.param_2b = int(self.param2B_edit.text())

        if len(self.param3A_edit.text()) > 0:
            self.content.param_3a = int(self.param3A_edit.text())

        if len(self.param3B_edit.text()) > 0:
            self.content.param_3b = int(self.param3B_edit.text())

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 4, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(500, 5, 500, 950)

    def closeEvent(self, event):
        self.content.SettingBtn.setEnabled(True)

        self.content.info = self.setInfo_edit.text()
        self.content.info2 = self.setInfo2_edit.text()

        self.content.Image_Global_Name = self.gb_name_edit.text()
        self.content.Label_Global_Name = self.lbl_name_edit.text()

        self.update_param()
        
# ==================================================================
class Exec_cmdScript:
    def set_cmd_to_foreground(self, hwnd, extra):
        """sets first command prompt to forgeround"""

        if "cmd.exe" in GetWindowText(hwnd):
            SetForegroundWindow(hwnd)
            return

    def get_pid(self):
        """gets process id of command prompt on foreground"""

        window = GetForegroundWindow()
        return GetWindowThreadProcessId(window)[1]
    
    def activate_venv(self, shell, root_path, venv_location):
        """activates venv of the active command prompt"""

        print("root_path : ", root_path)
        
        shell.AppActivate(self.get_pid())
        shell.SendKeys("cd \ {ENTER}")
        shell.SendKeys("%s {ENTER}" % root_path)
        shell.SendKeys(r"cd %s {ENTER}" % venv_location)

    def run_cmd_script(self,shell, script):
        """runs the py script"""

        # shell.SendKeys("cd ../..{ENTER}")
        shell.SendKeys(f"{script}"+ " {ENTER}")

    def open_cmd(self, shell):
        """ opens cmd """

        shell.run("cmd.exe")
        time.sleep(1)

# ==================================================================

@register_node(OP_NODE_OCR)
class Open_OCR(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_ocr.png"
    op_code = OP_NODE_OCR
    op_title = "OCR"
    content_label_objname = "OCR"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2,4], outputs=[5,3,4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

        self.input_ocr_payload = {}
        self.input_org_img = {}

        self.output_ocr_payload = {}
        self.output_ocr_payload_2 = {}
        self.output_org_with_ocr = {}

        self.output_ocr_payload_2['label'] = None
        self.output_ocr_payload_2['conf'] = None
        self.output_ocr_payload_2['result'] = None

        self.label = None
        self.conf = None

        self.Confidence_flag = False
        
        self.image_result = None
        self.OCR_Label = ""

        self.OCR_image_result = None

        self.innit_process = False
        self.end_label_judge = False

        self.OCR_confidence_list = []

        self.most_of_text = []

        self.org_image = None
        self.label_list = []

        self.foundCrop = 0 
        self.new_round_found = True
        self.send_one_time = False

        self.blk_img_detect = 0

    def initInnerClasses(self):
        self.content = OCRREADER(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCholeProcess(self)               # <----------- Box Image Draw in Flow_Node_Base
        self.grNode.width = 180
        self.grNode.height = 135

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)
        self.content.SwitchDetect.clicked.connect(self.StartDetecOCR)

        self.Global = GlobalVariable()

    def evalImplementation(self):                           # <----------- Create Socket range Index

        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.input_ocr_payload = input_node.eval()

            if self.input_ocr_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            elif type(self.input_ocr_payload) != type(None):
                if 'img' in self.input_ocr_payload:
                    if len(str(self.input_ocr_payload['img'])) > 100:# and not np.all(self.input_ocr_payload['img'] == 0):
                        if 'centers' in self.input_ocr_payload:
                            self.output_ocr_payload['centers'] = self.input_ocr_payload['centers']
                    
                        #print("val['img'] = ", val['img'])
                        # if 'fps' in self.input_ocr_payload:
                        #     self.output_ocr_payload['fps'] = 0

                        # if 'clock' in self.input_ocr_payload:
                        #     self.output_ocr_payload['clock'] = self.input_ocr_payload['clock']

                        # if 'run' in self.input_ocr_payload:
                        #     self.output_ocr_payload['run'] = self.input_ocr_payload['run']

                        if 'blink' in self.input_ocr_payload:
                            if self.input_ocr_payload['blink'] == True:
                                self.content.lbl.setText("<font color=#00FF00>-> Image Input</font>")
                            else:
                                self.content.lbl.setText("")

                            self.output_ocr_payload['blink'] = self.input_ocr_payload['blink']
                        
                        # if 'img_h' in self.input_ocr_payload:
                        #     self.output_ocr_payload['img_h'] = self.input_ocr_payload['img_h']

                        # if 'img_w' in self.input_ocr_payload:
                        #     self.output_ocr_payload['img_w'] = self.input_ocr_payload['img_w']

                        if 'inputtype' in self.input_ocr_payload:
                            self.output_ocr_payload['inputtype'] = self.input_ocr_payload['inputtype']
                            # self.pass_payload['img_copy'] = ORG_image

                        if self.content.StartProcessDetect_flag:
                            self.content.movie.start()
                            if type(self.input_ocr_payload['img']) != type(None):
                                self.org_image = self.input_ocr_payload['img']

                                self.crop_image = False
                                if self.content.high_confident_mode:
                                    if 'crop_output' in self.input_ocr_payload:
                                        self.crop_image = self.input_ocr_payload['crop_output']

                                    if self.new_round_found and (not np.all(self.input_ocr_payload['img'] == 0) or not np.all(self.input_ocr_payload['img'] == 255)):
                                        # print("high_confident_mode :")
                                        self.process_OCR_hiConF()
    
                                        # if len(lbl1) > 0 and len(lbl2) > 0 and len(lbl3) > 0 and len(lbl4) > 0 and len(lbl5) > 0:
                                        #     # print("Reset high_confident_mode !!!")
                                        #     self.ResetInput()

                                    if np.all(self.input_ocr_payload['img'] == 0) or np.all(self.input_ocr_payload['img'] == 255):
                                        self.ResetInput()

                                    else:
                                        if not self.crop_image:
                                            # print("No Yolo Image Mode :")
                                            self.process_OCR_hiConF()
                                            self.ResetInput()
                                            # self.content.hiconf_list.clear()

                                else:
                                    # print("OCR Normol mode !!!")
                                    if np.all(self.input_ocr_payload['img'] == 0) or np.all(self.input_ocr_payload['img'] == 255):
                                        self.ResetInput()

                                    else:
                                        # print("self.new_round_found :", self.new_round_found)
                                        if self.new_round_found:

                                            _ , lbl_ = self.parseq_ocr_process(self.input_ocr_payload['img'])
                                            # print("Normal OCR_Label :", lbl_)
                                            # print("Normal Image OCR_Label :", lbl_ )
                                            self.set_payload_output(lbl_)

                                            if 'img_feed' in self.input_ocr_payload:
                                                if self.input_ocr_payload['img_feed']:
                                                    self.ResetInput()


                                if 'crop_output' in self.input_ocr_payload:
                                    if not self.input_ocr_payload['crop_output']:
                                        print("No Output")
                                        self.ResetInput()
                                        self.foundCrop = 0 
                                        if self.new_round_found:
                                            self.content.hiconf_list.clear()
                                            self.new_round_found = False

                                    elif self.input_ocr_payload['crop_output']:
                                        self.content.mode_crop_yolo = True

                                        # print("foundCrop :", self.foundCrop)
                                        self.foundCrop += 1
                                    
                                    if self.foundCrop > 1 and not self.new_round_found:
                                        self.new_round_found = True
                                        # print("self.foundCrop :", self.foundCrop)

                        # else:
                        #     # black_image = np.zeros((480, 640, 3), dtype=np.uint8)
                        #     # image = cv2.putText(black_image  , str(self.content.info) , (150, 150), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), (63, 143, 255), 3)
                        #     # image = cv2.putText(image  , str(self.content.info2) , (170, 300), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), (255, 255, 177), 3)
                        #     self.output_ocr_payload['img'] = self.image_result
                        #     self.output_ocr_payload['inputtype'] = 'img'

                        # if type(self.output_ocr_payload) != type(None): self.sendFixOutputByIndex(self.output_ocr_payload, 0)
                        # if type(self.output_ocr_payload_2) != type(None): self.sendFixOutputByIndex(self.output_ocr_payload_2, 1)

                        # if Black Image or White Image
                        # if np.all(self.input_ocr_payload['img'] == 0) or np.all(self.input_ocr_payload['img'] == 255):
                        #     # print("Input Black Image or White Image !!!!!")
                        #     self.ResetInput()



                    else:
                        # black_image = np.zeros((480, 640, 3), dtype=np.uint8)
                        # image = cv2.putText(black_image  , str(self.content.info) , (150, 150), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), (63, 143, 255), 3)
                        # image = cv2.putText(image  , str(self.content.info2) , (170, 300), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), (255, 255, 177), 3)

                        self.output_ocr_payload['img'] = self.image_result
                        self.output_ocr_payload['inputtype'] = 'img'

                        # self.most_of_text = []

                        if type(self.output_ocr_payload) != type(None): self.sendFixOutputByIndex(self.output_ocr_payload, 0)

        # ===================================================================================================================
        # Input 1
        input_node_1 = self.getInput(1)
        if not input_node_1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.input_org_img = input_node_1.eval()

            if self.input_org_img is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            elif type(self.input_org_img) != type(None):
                if 'img' in self.input_org_img:
                    if type(self.input_org_img['img']) != type(None):
                        # If Image in payload and not black image and For OCR
                        if len(str(self.input_org_img['img'])) > 100:
                            if not (np.all(self.input_org_img['img'] == 0) or np.all(self.input_org_img['img'] == 255)):
                                self.content.lbl.setText("Read Success")
                                self.content.lbl.setStyleSheet("color: #2DD5AC; font-size:8pt;")

                                self.OCR_image_result = self.input_org_img['img']

                                # Get current date and time
                                current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                self.output_org_with_ocr['img_timestamp'] = current_datetime

                                self.blk_img_detect = 0

                                if type(self.OCR_image_result) != type(None):
                                    # Get current date and time
                                    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                    self.output_org_with_ocr['img_timestamp'] = current_datetime

                                    #self.output_ocr_payload_2['most_of_text'] = self.most_of_text
                                    self.content.lbl.setText(self.OCR_Label)
                                    self.content.lbl.setStyleSheet("color: #11CDDE; font-size:8pt;")

                                    blk = np.zeros((480, 640, 3), np.uint8)
                                    blk = cv2.rectangle(blk, (22, 0), (620, 80), (119 , 215, 255), -1)

                                    self.OCR_image_result = cv2.resize(self.OCR_image_result, (640, 480))

                                    # Convert hexadecimal color to BGR
                                    font_color = self.content.font_color.lstrip('#')
                                    bgr_tuple = tuple(int(font_color[i:i+2], 16) for i in (4, 2, 0))

                                    self.OCR_image_result = cv2.putText(self.OCR_image_result  , str(self.OCR_Label) , (25, 70), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), bgr_tuple, 3)

                                    # Use cv2.putText() to add text to the image
                                    self.OCR_image_result = cv2.putText(self.OCR_image_result, self.output_org_with_ocr['img_timestamp'], (30, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (52,159,253), 2)

                                    self.OCR_image_result = cv2.addWeighted(self.OCR_image_result, 1.0, blk, self.content.beta, 1)
                                
                                    self.output_org_with_ocr['img'] = self.OCR_image_result
                                    self.output_org_with_ocr['inputtype'] = 'img'
                                    self.output_org_with_ocr['label'] = self.OCR_Label
                                    
                                    if len(self.content.Image_Global_Name) > 0 and not self.send_one_time:
                                        self.Global.setGlobal(self.content.Image_Global_Name, self.output_org_with_ocr)
                                        self.send_one_time = True

                                    if type(self.output_org_with_ocr) != type(None): self.sendFixOutputByIndex(self.output_org_with_ocr, 2)  

                            # Black or White Color
                            elif np.all(self.input_org_img['img'] == 0) or np.all(self.input_org_img['img'] == 255):
                                self.blk_img_detect += 1
                                # print("self.blk_img_detect :", self.blk_img_detect)
                                if self.blk_img_detect > 5:
                                    self.OCR_image_result = None

                        # If Image in payload and not black image and cannot read OCR
                        elif len(str(self.input_org_img['img'])) > 100 and not self.end_label_judge:  
                            if not (np.all(self.input_org_img['img'] == 0) or np.all(self.input_org_img['img'] == 255)):
                                self.content.lbl.setText("---------")
                                self.content.lbl.setStyleSheet("color: #F84582; font-size:8pt;")

                                self.output_org_with_ocr['img'] = self.input_org_img['img']
                                self.output_org_with_ocr['inputtype'] = 'img'
                                self.output_org_with_ocr['label'] = "---"

                                # Get current date and time
                                current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                self.output_org_with_ocr['img_timestamp'] = current_datetime

                                # if len(self.content.Image_Global_Name) > 0 and not self.send_one_time:
                                #     self.Global.setGlobal(self.content.Image_Global_Name, self.output_org_with_ocr)
                                #     self.send_one_time = True

                else:
                    if not self.innit_process:
                        self.innit_process = True
                        # Read the image
                        initail_image = cv2.imread(self.content.innit_image_path)
                        initail_image = cv2.resize(initail_image, (640, 480))
                        
                        self.output_org_with_ocr['img'] = initail_image
                        self.output_org_with_ocr['inputtype'] = 'img'

                        if type(self.output_org_with_ocr) != type(None): self.sendFixOutputByIndex(self.output_org_with_ocr, 2)      

    # ===========================================================================================================================
    # ===========================================================================================================================
    def build_final_text(self, data):
        # Remove dot ('.') from each string in the data list
        data = [s.replace('.', '') for s in data]

        final_str = ""

        if any(not s for s in data[1:]):
            return final_str + data[0]

        max_length = max(len(s) for s in data)

        for i in range(0, max_length):
            char_count = {}
            
            # Count occurrences of characters at position i in each string
            for string in data:
                if i < len(string):
                    char = string[i]
                    if char in char_count:
                        char_count[char] += 1
                    else:
                        char_count[char] = 1
            
            # Find the character with the highest count
            most_common_char = max(char_count, key=char_count.get)

            # Append the most common character to the final string
            final_str += most_common_char

        return final_str
    
    def process_OCR_hiConF(self):
        lbl1, lbl2, lbl3, lbl4, lbl5 = "", "", "", "", ""

        # Create a new 3 channel image with the same size as the original
        # gray_image = cv2.merge([gray_image, gray_image, gray_image])
        # print("Image shape:", gray_image.shape)
        # print("Image data type:", gray_image.dtype)

        # Orignal Image
        ret1, lbl1 = self.parseq_ocr_process(self.org_image)
        # print("ret1 :", ret1 ," , lbl1 :", lbl1)
        if len(lbl1) > 0:
            self.label_list.append(lbl1)

        # Apply noise_removal_img 
        # noise_removal_img = self.noise_removal(self.org_image)
        # if self.parseq_ocr_process(noise_removal_img):
        #     self.label_list.append(self.OCR_Label)
        
        # Ensure that the image is in the correct data type (CV_8UC1)
        # if gray_image.dtype != 'uint8':
        #     # Convert to 8-bit unsigned integer
        #     gray_image = gray_image.astype('uint8')
            
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(self.org_image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        image_threshold_img = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, self.content.param_1a, self.content.param_1b)
        THRESH_MEAN_img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])
        self.content.setting_image1 = THRESH_MEAN_img 
        ret2, lbl2 = self.parseq_ocr_process(THRESH_MEAN_img)
        # print("ret2 :", ret2 ," , lbl2 :", lbl2)
        if len(lbl2) > 0:
            self.content.lbl_param1 = lbl2
            self.label_list.append(self.content.lbl_param1)

        gray_image = cv2.cvtColor(THRESH_MEAN_img, cv2.COLOR_BGR2GRAY)
        ret,image_threshold_img = cv2.threshold(gray_image,127,255,cv2.THRESH_BINARY_INV)
        THRESH_BINARY_INV_img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])
        ret3, lbl3 = self.parseq_ocr_process(THRESH_BINARY_INV_img)
        # print("ret3 :", ret3 ," , lbl3 :", lbl3)
        if len(lbl3) > 0:
            self.label_list.append(lbl3)

        gray_image = cv2.cvtColor(self.org_image, cv2.COLOR_BGR2GRAY)
        image_threshold_img = cv2.adaptiveThreshold(gray_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,self.content.param_2a, self.content.param_2b)
        GAUSSIAN_img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])
        self.content.setting_image2 = GAUSSIAN_img
        ret4, lbl4 = self.parseq_ocr_process(GAUSSIAN_img)
        # print("ret4 :", ret4 ," , lbl4 :", lbl4)
        if len(lbl4) > 0:
            self.content.lbl_param2 = lbl4
            self.label_list.append(self.content.lbl_param2)

        image_threshold_img = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, self.content.param_3a, self.content.param_3b)
        GAUSSIAN_img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])
        gray_image = cv2.cvtColor(GAUSSIAN_img, cv2.COLOR_BGR2GRAY)
        ret,image_threshold_img = cv2.threshold(gray_image,127,255,cv2.THRESH_TRUNC)
        THRESH_TRUNC_img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])
        self.content.setting_image3 = THRESH_TRUNC_img
        ret5, lbl5 = self.parseq_ocr_process(THRESH_TRUNC_img)
        # print("ret5 :", ret5 ," , lbl5 :", lbl5)
        if len(lbl5) > 0:
            self.content.lbl_param3 = lbl5
            self.label_list.append(self.content.lbl_param3)

        # print("high_confident_mode : self.label_list :", self.label_list)
            
        # print("len(self.content.hiconf_list) :", len(self.content.hiconf_list))
        if len(self.content.hiconf_list) < 1000:
            self.content.hiconf_list += self.label_list
            # self.content.hiconf_list.clear()

        OCR_Label = self.build_final_text(self.content.hiconf_list)    
        # print("high_confident_mode : OCR_Label :", self.OCR_Label)
        self.set_payload_output(OCR_Label)

    # ===========================================================================
    # Send Output Payload
    def set_payload_output(self, label):
        self.OCR_Label = label[:self.content.NumberOf_Char]
        self.output_ocr_payload['img'] = self.image_result
        self.output_ocr_payload['label'] = self.OCR_Label
        self.output_ocr_payload['conf'] = self.OCR_confidence_list
        self.output_ocr_payload['result'] = self.OCR_Label
        #self.output_ocr_payload['label_list'] = self.label_list
        # self.output_ocr_payload['hiconf_list'] = self.content.hiconf_list

        self.output_ocr_payload_2['label'] = self.OCR_Label
        self.output_ocr_payload_2['conf'] = self.OCR_confidence_list
        self.output_ocr_payload_2['result'] = self.OCR_Label
        #self.output_ocr_payload_2['label_list'] = self.label_list
        # self.output_ocr_payload_2['hiconf_list'] = self.content.hiconf_list
        # img_timestamp

        if len(self.content.Label_Global_Name) > 0:
            self.Global.setGlobal(self.content.Label_Global_Name, self.OCR_Label)


        # self.content.lbl.setText("Read Success")
        # self.content.lbl.setStyleSheet("color: #2DD5AC; font-size:8pt;")

        if type(self.output_ocr_payload) != type(None): self.sendFixOutputByIndex(self.output_ocr_payload, 0)
        if type(self.output_ocr_payload_2) != type(None): self.sendFixOutputByIndex(self.output_ocr_payload_2, 1)

        # self.end_label_judge = True

        if type(self.OCR_image_result) != type(None):
            # Get current date and time
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.output_org_with_ocr['img_timestamp'] = current_datetime

            #self.output_ocr_payload_2['most_of_text'] = self.most_of_text
            self.content.lbl.setText(self.OCR_Label)
            self.content.lbl.setStyleSheet("color: #11CDDE; font-size:8pt;")

            blk = np.zeros((480, 640, 3), np.uint8)
            blk = cv2.rectangle(blk, (22, 0), (620, 80), (119 , 215, 255), -1)

            self.OCR_image_result = cv2.resize(self.OCR_image_result, (640, 480))

            # Convert hexadecimal color to BGR
            font_color = self.content.font_color.lstrip('#')
            bgr_tuple = tuple(int(font_color[i:i+2], 16) for i in (4, 2, 0))

            self.OCR_image_result = cv2.putText(self.OCR_image_result  , str(self.OCR_Label) , (25, 70), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), bgr_tuple, 3)

            # Use cv2.putText() to add text to the image
            self.OCR_image_result = cv2.putText(self.OCR_image_result, self.output_org_with_ocr['img_timestamp'], (30, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (52,159,253), 2)

            self.OCR_image_result = cv2.addWeighted(self.OCR_image_result, 1.0, blk, self.content.beta, 1)
        
            self.output_org_with_ocr['img'] = self.OCR_image_result
            self.output_org_with_ocr['inputtype'] = 'img'
            self.output_org_with_ocr['label'] = self.OCR_Label
            
            if len(self.content.Image_Global_Name) > 0 and not self.send_one_time:
                self.Global.setGlobal(self.content.Image_Global_Name, self.output_org_with_ocr)
                self.send_one_time = True

            if type(self.output_org_with_ocr) != type(None): self.sendFixOutputByIndex(self.output_org_with_ocr, 2)  

        # if len(self.most_of_text) > 10:
        #     print("Reset most_of_text > 10")
        #     self.ResetInput()

    def ResetInput(self):
        self.label_list.clear()
        self.most_of_text.clear()
        self.OCR_confidence_list.clear()
        
        self.OCR_Label = ""
        self.content.mode_crop_yolo = False

        # self.end_label_judge = False
        # self.content.lbl.setText("Reset Input")
        # self.content.lbl.setStyleSheet("color: #FF0000; font-size:8pt;")

        self.send_one_time = False


    def noise_removal(self, image):
        # denoising of image saving it into dst image 
        # img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15) 
        # Apply Gaussian Blur
        image = cv2.GaussianBlur(image, (5, 5), 0)

        # Apply Median Blur
        return cv2.medianBlur(image, 5)

    def OnOpen_Setting(self):
        self.content.SettingBtn.setEnabled(False)
        self.OCR_Setting = OCRSetting(self.content)
        self.OCR_Setting.show()


    def StartDetecOCR(self):
        self.content.StartProcessDetect_flag = not self.content.StartProcessDetect_flag
        if not self.content.StartProcessDetect_flag:
            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))
            self.content.movie.stop()

            self.content.mode_crop_yolo = False
            self.content.lbl.setText("Stop")
            self.content.lbl.setStyleSheet("color: #D00C27; font-size:8pt;")

        else:
            self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))

            if self.content.read_custom:
                self.content.parseq = load_from_checkpoint(self.content.custom_weight_path, **self.content.kwargs).eval().to(self.content.device)
                # self.img_transform = SceneTextDataModule.get_transform(self.parseq.hparams.img_size)

                self.content.combo.setCurrentText("Custom")
            
            else:
                # Load model and image transforms
                self.content.parseq = torch.hub.load('baudm/parseq', self.content.comboPreWeight.currentText(), pretrained=True).eval()

                self.content.combo.setCurrentText("Read")

            self.content.img_transform = SceneTextDataModule.get_transform(self.content.parseq.hparams.img_size)
            #print("self.content.img_transform :", self.content.img_transform)

    @torch.inference_mode()
    def parseq_ocr_process(self, image):
        if type(image) != type(None):
            # Convert from BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Convert from numpy array to PIL image
            pil_image = Image.fromarray(image_rgb)

            if self.content.read_custom:
                img = self.content.img_transform(pil_image).unsqueeze(0).to(self.content.device)
            else:
                img = self.content.img_transform(pil_image).unsqueeze(0)

            logits = self.content.parseq(img)
            logits.shape  # torch.Size([1, 26, 95]), 94 characters + [EOS] symbol

            # Greedy decoding
            pred = logits.softmax(-1)
            label, confidence = self.content.parseq.tokenizer.decode(pred)
            # print("label :", label)
            # print("confidence = ", confidence)
            # print(type(confidence[0]))

            # Convert the tensor to a list and round each element to 2 decimal places
            confidence_list = confidence[0].tolist()
            # print("confidence_list:", confidence_list)

            # Truncating the values in the list to 2 decimal places without rounding
            truncated_confidence_list = [int(val * 100) / 100 for val in confidence_list]

            threshold = float(self.content.editConF.text())
            #print("threshold :", threshold)
            # print("type(threshold) :", type(threshold))

            # threshold = 0.9  # Set threshold to 0.9 explicitly
            self.Confidence_flag = False  # Default to False

            #print("len(truncated_confidence_list) :", str(len(truncated_confidence_list)), " , len(self.content.NumberOf_Char + 1) : ", str(self.content.NumberOf_Char + 1))

            #if self.content.mode_crop_yolo:
            if len(truncated_confidence_list) == self.content.NumberOf_Char + 1:
                self.Confidence_flag = True
                for i in range(1, len(truncated_confidence_list)):  # Start from index 1
                    if truncated_confidence_list[i] <= threshold:
                        self.Confidence_flag = False
                        break

            if self.Confidence_flag:
                #print("truncated_confidence_list :", truncated_confidence_list, " ; Result = ", label[0])
                self.most_of_text.append(label[0])
                #print("self.most_of_text = ", self.most_of_text)
                # Create a dictionary to count occurrences
                frequency_dict = {}
                # Count each item's frequency
                for item in self.most_of_text:
                    if item in frequency_dict:
                        frequency_dict[item] += 1
                    else:
                        frequency_dict[item] = 1

                #print("frequency_dict :", frequency_dict)
                # self.output_ocr_payload['frequency_dict'] = frequency_dict
                # Find the most common item
                OCR_Label = max(frequency_dict, key=frequency_dict.get)
                if len(OCR_Label) == self.content.NumberOf_Char:
                    self.OCR_Label = OCR_Label

                else:
                    self.OCR_Label = OCR_Label[0:self.content.NumberOf_Char]

                #print("self.OCR_Label :", self.OCR_Label)
                self.end_label_judge = True

            else:
                # Show Last Label has been found
                self.OCR_Label = label[0]
            # else:
            #     self.Confidence_flag = True
            #     self.OCR_Label = label[0]

            blk = np.zeros((480, 640, 3), np.uint8)
            blk = cv2.rectangle(blk, (22, 0), (620, 80), (119 , 215, 255), -1)
            blk = cv2.rectangle(blk, (20, 440), (620, 465), (224 , 100, 2), -1)

            self.image_result = cv2.resize(image, (640, 480))

            # Convert hexadecimal color to BGR
            font_color = self.content.font_color.lstrip('#')
            bgr_tuple = tuple(int(font_color[i:i+2], 16) for i in (4, 2, 0))

            font = ImageFont.truetype(self.content.font_path, 64)
            self.image_result = Image.fromarray(self.image_result)
            draw = ImageDraw.Draw(self.image_result)
            draw.text((25, -30),  str(self.OCR_Label), font = font, fill = (24, 130, 250, 0))
            self.image_result = np.array(self.image_result)

            # self.image_result = cv2.putText(self.image_result  , str(self.OCR_Label) , (25, 70), cv2.FONT_HERSHEY_DUPLEX, int(self.content.font_scale), bgr_tuple, 3)
            self.image_result = cv2.putText(self.image_result  , str(truncated_confidence_list) , (25, 460), cv2.FONT_HERSHEY_DUPLEX, 0.6, ( 24, 130, 250 ), 1)
            self.image_result = cv2.addWeighted(self.image_result, 1.0, blk, self.content.beta, 1)

            self.OCR_confidence_list = confidence_list

            return self.Confidence_flag, self.OCR_Label
        
        else:
            return False, ""
        
    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(index, self.op_code)
        else:
            self.evalChildren(index)

