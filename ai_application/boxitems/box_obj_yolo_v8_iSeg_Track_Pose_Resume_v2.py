from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import os
import torch
import numpy as np
from datetime import datetime, timedelta

import shutil
import psutil
import glob

import random
import json

import yaml
import cv2
import time

import sys
import pkg_resources

from win32com import client
import win32gui
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, FindWindow, ShowWindow
from win32process import GetWindowThreadProcessId

from win32api import GetSystemMetrics

from ultralytics import YOLO
from ultralytics.utils import ops
from ultralytics.utils.plotting import colors

import ai_application.AI_Module.yolov8.detect as objectDetection
from ai_application.Database.GlobalVariable import *

from openvino.runtime import Core, Model
from typing import Tuple, Dict

from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectDetectV8(QDMNodeContentWidget):
    def initUI(self):
        
        self.Path = os.path.dirname(os.path.abspath(__file__))
        # print("Object Detect self.Path = " , self.Path)
        self.save_icon = self.Path + "/icons/icons_save.png"
        yolo_logo = self.Path + "/icons/icons_yolov8.png"
        self.train_icon = self.Path + "/icons/icons_train.png"

        self.openvino_icon = self.Path + "/icons/icons_openvino_logo.png"

        self.animate_movie = self.Path + "/icons/icons_dane_re.gif"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        
        self.Data = None

        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,2,125,45)
        self.lbl.setStyleSheet("font-size:8pt;")

        self.lblProcess = QLabel("Process : " , self)
        self.lblProcess.setAlignment(Qt.AlignLeft)
        self.lblProcess.setGeometry(10,30,105,45)
        self.lblProcess.setStyleSheet("color: orange; font-size:7pt;")

        self.combo = QComboBox(self)
        self.combo.addItem("Detect")
        self.combo.addItem("iSegment")
        self.combo.addItem("Track")
        self.combo.addItem("Pose")
        self.combo.addItem("Train")

        self.combo.setGeometry(100,30,95,20)
        self.combo.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.combo.setCurrentText("Detect")

        self.checkPreWeight = QCheckBox("PreWeight",self)
        self.checkPreWeight.setGeometry(10,55,90,20)
        self.checkPreWeight.setStyleSheet("color: lightblue; font-size:6pt;")
        self.checkPreWeight.setChecked(True)

        self.comboPreWeight = QComboBox(self)
        self.comboPreWeight.addItem("yolov8n.pt")
        self.comboPreWeight.addItem("yolov8s.pt")
        self.comboPreWeight.addItem("yolov8m.pt")
        self.comboPreWeight.addItem("yolov8l.pt")
        self.comboPreWeight.addItem("yolov8x.pt")

        self.comboPreWeight.setGeometry(100,55,95,20)
        self.comboPreWeight.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.comboPreWeight.setCurrentText("yolov8m.pt")

        self.checkCustom = QCheckBox("Custom : ",self)
        self.checkCustom.setGeometry(10,80,90,20)
        self.checkCustom.setStyleSheet("color: lightblue; font-size:6pt;")
        self.checkCustom.setChecked(False)

        self.lblProjectPath= QLabel("Path:" , self)
        self.lblProjectPath.setAlignment(Qt.AlignLeft)
        self.lblProjectPath.setGeometry(95,85,100,20)
        self.lblProjectPath.setStyleSheet("color: orange; font-size:5pt;")

        self.browsFilesCustome = QPushButton(self)
        self.browsFilesCustome.setGeometry(175,80,20,20)
        self.browsFilesCustome.setIcon(QIcon(self.save_icon))
        self.browsFilesCustome.setVisible(False)


        # self.iSegmentation_Train_Check = QCheckBox("i-Seg",self)
        # self.iSegmentation_Train_Check.setGeometry(10,80,60,20)
        # self.iSegmentation_Train_Check.setStyleSheet("color: #FC03C7; font-size:6pt;")
        # self.iSegmentation_Train_Check.setVisible(False)
        # self.iSegmentation_Train_Check.setChecked(False)

        self.iSegmentation_Train = False

        self.SwitchDetect = QPushButton(self)
        self.SwitchDetect.setGeometry(160,5,37,20)
        self.SwitchDetect.setIcon(QIcon(self.off_icon))
        self.SwitchDetect.setIconSize(QtCore.QSize(37,20))
        self.SwitchDetect.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lblConF = QLabel("Conf:" , self)
        self.lblConF.setAlignment(Qt.AlignLeft)
        self.lblConF.setGeometry(100,118,30,30)
        self.lblConF.setStyleSheet("font-size:6pt;")

        self.editConF = QLineEdit("0.25", self)
        self.editConF.setAlignment(Qt.AlignLeft)
        self.editConF.setGeometry(129,113,65,20)
        self.editConF.setPlaceholderText("Confident")
        self.editConF.setStyleSheet("font-size:8pt;")

        self.lblPayload = QLabel("Yolo Payload" , self)
        self.lblPayload.setAlignment(Qt.AlignLeft)
        self.lblPayload.setGeometry(137,97,65,20)
        self.lblPayload.setStyleSheet("color: #C248E0; font-size:5pt;")

        #====================================================
        # Loading the GIF
        self.labelAnimate = QLabel(self)
        self.labelAnimate.setGeometry(QtCore.QRect(20, 115, 105, 75))
        self.labelAnimate.setMinimumSize(QtCore.QSize(75, 75))
        self.labelAnimate.setMaximumSize(QtCore.QSize(75, 75))

        self.movie = QMovie(self.animate_movie)
        self.labelAnimate.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        self.labelAnimate.setVisible(False)

        #====================================================
        #====================================================
        self.checkBGProcess = QCheckBox("Boot Process",self)
        self.checkBGProcess.setGeometry(100,140,120,20)
        self.checkBGProcess.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.checkBGProcess.setChecked(False)
        self.checkBGProcess.setVisible(False)

        #====================================================
        # OpenVino
        #====================================================

        self.checkOpenVino = QCheckBox("OpenVino",self)
        self.checkOpenVino.setGeometry(100,140,120,20)
        self.checkOpenVino.setStyleSheet("color: #FF961B; font-size:6pt;")
        self.checkOpenVino.setChecked(False)

        self.vino_graphicsView = QGraphicsView(self)
        vino_scene = QGraphicsScene()
        self.vino_pixmap = QGraphicsPixmapItem()
        vino_scene.addItem(self.vino_pixmap)
        self.vino_graphicsView.setScene(vino_scene)

        self.vino_graphicsView.resize(110,40)
        self.vino_graphicsView.setGeometry(QtCore.QRect(12, 155, 120, 45))

        vino_img = QPixmap(self.openvino_icon)
        self.vino_pixmap.setPixmap(vino_img)
        self.vino_pixmap.setVisible(False)

        self.use_openvino_flag = False

        self.openvino_core = Core()
        self.label_map = {}

        self.det_compiled_model = None

        self.editDevice = QLineEdit("GPU", self)
        self.editDevice.setAlignment(Qt.AlignLeft)
        self.editDevice.setGeometry(129,165,65,20)
        self.editDevice.setPlaceholderText("CPU")
        self.editDevice.setStyleSheet("font-size:8pt;")
        self.editDevice.setVisible(False)

        #====================================================
        #====================================================
        #====================================================
        # Train Data

        self.lblTrain = QLabel("Train" , self)
        self.lblTrain.setAlignment(Qt.AlignLeft)
        self.lblTrain.setGeometry(5,120,50,20)
        self.lblTrain.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 5%")
        self.lblTrain.setVisible(False)

        self.lblEpoch = QLabel("Epoch" , self)
        self.lblEpoch.setAlignment(Qt.AlignLeft)
        self.lblEpoch.setGeometry(60,123,50,20)
        self.lblEpoch.setStyleSheet("font-size:6pt;color:lightblue;")
        self.lblEpoch.setVisible(False)

        self.Epoch_sizeEdit = QLineEdit("100", self)
        self.Epoch_sizeEdit.setGeometry(95,120,30,20)
        self.Epoch_sizeEdit.setStyleSheet("font-size:6pt;")
        self.Epoch_sizeEdit.setVisible(False)

        self.lblbatch_size = QLabel("batch" , self)
        self.lblbatch_size.setAlignment(Qt.AlignLeft)
        self.lblbatch_size.setGeometry(130,123,70,20)
        self.lblbatch_size.setStyleSheet("font-size:6pt;color:lightblue;")
        self.lblbatch_size.setVisible(False)

        self.batch_sizeEdit = QLineEdit("4", self)
        self.batch_sizeEdit.setGeometry(165,120,30,20)
        self.batch_sizeEdit.setStyleSheet("font-size:6pt;")
        self.batch_sizeEdit.setVisible(False)

        self.ImageLabelEdit = QLineEdit("", self)
        self.ImageLabelEdit.setGeometry(10,145,160,20)
        self.ImageLabelEdit.setPlaceholderText("Input DIR:Images/Label")
        self.ImageLabelEdit.setStyleSheet("font-size:6pt;")
        self.ImageLabelEdit.setVisible(False)

        self.browsTargetFolder = QPushButton(self)
        self.browsTargetFolder.setGeometry(175,145,20,20)
        self.browsTargetFolder.setIcon(QIcon(self.save_icon))
        self.browsTargetFolder.setVisible(False)

        self.lblSelectImage = QLabel("Raeay for Training !!!" , self)
        self.lblSelectImage.setAlignment(Qt.AlignLeft)
        self.lblSelectImage.setGeometry(15,168,150,20)
        self.lblSelectImage.setStyleSheet("font-size:6pt;")
        self.lblSelectImage.setVisible(False)

        # self.ResCombo = QComboBox(self)
        # self.ResCombo.addItem("640")
        # self.ResCombo.addItem("1280")
        # self.ResCombo.addItem("1920")
        # self.ResCombo.addItem("2560")
        # self.ResCombo.setGeometry(130,165,63,25)
        # self.ResCombo.setStyleSheet("QComboBox"
        #                            "{"
        #                                 "background-color : #33DDFF; font-size:6pt;"
        #                            "}") 
        # self.ResCombo.setVisible(False)

        self.TrainObjectBtn = QPushButton(self)
        self.TrainObjectBtn.setGeometry(160, 190, 35, 35)
        self.TrainObjectBtn.setIconSize(QtCore.QSize(35,35))
        self.TrainObjectBtn.setIcon(QIcon(self.train_icon))
        self.TrainObjectBtn.setVisible(False)
        self.TrainObjectBtn.setEnabled(False)

        self.checkLog = QCheckBox(self)
        self.checkLog.setGeometry(100,168,50,20)
        self.checkLog.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.checkLog.setChecked(True)
        self.showlog = True

        self.checkLog.setVisible(False)

        self.ImageTrainZ = 640

        self.ImageTrainZCombo = QComboBox(self)
        self.ImageTrainZCombo.addItem("640")
        self.ImageTrainZCombo.addItem("416")
        self.ImageTrainZCombo.setGeometry(130,168,65,20)
        self.ImageTrainZCombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33DDFF; font-size:6pt;"
                                   "}")
        self.ImageTrainZCombo.setVisible(False) 

        self.iSegmentation_Train_Check = QCheckBox("i-Seg",self)
        self.iSegmentation_Train_Check.setGeometry(10,80,60,20)
        self.iSegmentation_Train_Check.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.iSegmentation_Train_Check.setVisible(False)
        self.iSegmentation_Train_Check.setChecked(False)

        self.checkResume = QCheckBox("Cont",self)
        self.checkResume.setGeometry(70,80,60,20)
        self.checkResume.setStyleSheet("color:lightblue; font-size:6pt;")
        self.checkResume.setVisible(False)

        self.resume = False

        self.checkUpdateWeight = QCheckBox("Update",self)
        self.checkUpdateWeight.setGeometry(128,80,80,20)
        self.checkUpdateWeight.setStyleSheet("color:orange; font-size:6pt;")
        self.checkUpdateWeight.setVisible(False)

        self.Continue_ImproveWeight = False

        #====================================================
        # Error and warning Label

        self.lblErrorWarning = QLabel("Error: No Weight file !!!" , self)
        self.lblErrorWarning.setAlignment(Qt.AlignLeft)
        self.lblErrorWarning.setGeometry(10,163,185,20)
        self.lblErrorWarning.setStyleSheet("font-size:9pt;color:red;")
        self.lblErrorWarning.setVisible(False)

        #====================================================
        # Add Image
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(115,80)
        self.graphicsView.setGeometry(QtCore.QRect(5, 165, 155, 85))

        img = QPixmap(yolo_logo)
        self.pixmap.setPixmap(img)

        #=====================================================

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(175,200,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.YoloProcess = "Detect"

        self.selectWeight = "preweight"

        self.re_path = self.Path[0:-9]
        
        # replace all instances of '\\' (old) with '/' (new)
        self.re_path = self.re_path.replace("\\", "/" )
        # print("self.re_path:", self.re_path)

        self.YoloWeightPath = self.re_path + "/AI_Module/yolov8/model_data/yolov8m.pt"
        print("self.YoloWeightPath =", self.YoloWeightPath)

        self.dataset_name = self.re_path + "/AI_Module/yolov8/data/coco128.yaml"
        # print("self.dataset_name =", self.dataset_name)

        self.StartProcessDetect_flag = False
        self.model = None

        # ===========================================================

        self.ready_for_training = False
        self.NOF_Image = 0
        self.file_imgname_list = []

        self.NOF_Txt = 0
        self.file_txtname_list = []

        self.first_startTrain = False
        self.startime = None

        self.show_fps = True
        # ===========================================================

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msg.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msg.setStandardButtons(QMessageBox.Ok)

        self.AutoLoadYolo = False

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Running on Background 
        self.process_detect_bg = False
        self.FirstInnitFromStart = True

        self.names = {}
        self.colorList = []

        self.model_name = {}

        self.ProjectLocation = ""
        self.ProjectTrainingLocation = ""

        self.segmentation = False

        self.Global_Object = ""
        self.GlobalObject_key = ""
        self.change_global_key = False

        self.tracker = DeepSort(max_age=10)

        # ==========================================================
        # For EvalChrildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

        # with open(self.dataset_name, "r", encoding="utf8") as stream:
        #     try:
        #         self.names = yaml.safe_load(stream)
        #         # print("self.names = ", self.names['names'])
        #     except yaml.YAMLError as exc:
        #         print(exc)

        # np.random.seed(20)
        # list_of_arrays = np.random.uniform(low=50, high=200, size=(len(self.names['names']),3))
        # # print("list_of_arrays :", list_of_arrays)

        # # colorList = [(0,0,255) , (255,0,0)]
        # self.colorList = [tuple(map(int, array)) for array in list_of_arrays]

        self.reload_weight_info()

    def serialize(self):
        res = super().serialize()
        res['YoloProcess'] = self.YoloProcess
        res['autoloadyolo'] = self.AutoLoadYolo
        res['conf'] = self.editConF.text()

        res['yoloweight_path'] = self.YoloWeightPath
        res['selectweight'] = self.selectWeight
        res['project_locate'] = self.ProjectLocation

        res['bg_detection'] = self.process_detect_bg
        res['segmentation'] = self.segmentation
        res['use_vino'] = self.use_openvino_flag

        res['vino_device'] = self.editDevice.text()
        res['global_obj'] = self.Global_Object
        res['global_key'] = self.GlobalObject_key

        res['show_fps'] = self.show_fps

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'segmentation' in data:
                self.segmentation = data['segmentation']

            if 'selectweight' in data:
                self.selectWeight = data['selectweight']
                if self.selectWeight == "preweight":
                    self.checkPreWeight.setChecked(True)
                    self.checkCustom.setChecked(False)

                elif self.selectWeight == "custom":
                    self.checkCustom.setChecked(True)
                    self.checkPreWeight.setChecked(False)

                    if 'project_locate' in data:
                        self.ProjectLocation = data['project_locate']
                        self.lblProjectPath.setText(self.ProjectLocation)

                        if not self.use_openvino_flag:
                            self.YoloWeightPath = self.ProjectLocation + "/best.pt"
                            self.dataset_name = self.ProjectLocation + "/custom_data.yaml"
                            self.reload_weight_info()

                        self.combo.setEnabled(False)
                        self.comboPreWeight.setEnabled(False)

            if 'autoloadyolo' in data:
                self.AutoLoadYolo = data['autoloadyolo']
                print('autoloadyolo = ', self.AutoLoadYolo)

                if self.AutoLoadYolo:
                    if 'YoloProcess' in data:
                        self.YoloProcess = data['YoloProcess']
                        self.combo.setCurrentText(self.YoloProcess)

                    if self.selectWeight == "preweight":
                        # if not self.segmentation:
                        self.YoloWeightPath = data['yoloweight_path']#self.re_path + "/AI_Module/yolov8/model_data/yolov8m.pt"
                        self.dataset_name = self.re_path + "/AI_Module/yolov8/data/coco128.yaml"

                        # with open(self.dataset_name, "r", encoding="utf8") as stream:
                        #     try:
                        #         self.names = yaml.safe_load(stream)
                        #         # print("self.names = ", self.names['names'])
                        #     except yaml.YAMLError as exc:
                        #         print(exc)
                        
                        self.reload_weight_info()

                    self.model = YOLO(self.YoloWeightPath)
                    # print("\033[93m {}\033[00m".format("self.model :" + str(self.model))) 

                    try:
                        self.model_name = self.model.model.names
                        print("\033[94m {}\033[00m".format("self.model_name :" + str(self.model.model.names)))   
                        self.lblErrorWarning.setVisible(False)

                    except:
                        print("\033[91m {}\033[00m".format("YoloV8 : OpenVino not able to Load model_name"))
                        self.lblErrorWarning.setVisible(True)

                    self.AutoLoadYolo = True
                    self.SwitchDetect.setIcon(QIcon(self.on_icon))

                    self.StartProcessDetect_flag = True

                    self.combo.setEnabled(False)
                    self.comboPreWeight.setEnabled(False)
                    self.checkPreWeight.setEnabled(False)
                    self.checkCustom.setEnabled(False)

                    self.checkOpenVino.setEnabled(False)
                    self.editDevice.setEnabled(False)

                    self.labelAnimate.setVisible(True)
                    self.movie.start()

            if 'bg_detection' in data:
                self.process_detect_bg = data['bg_detection']

            if 'use_vino' in data:
                self.use_openvino_flag = data['use_vino']
                
                if 'vino_device' in data:
                    self.editDevice.setText(data['vino_device'])

                if self.use_openvino_flag:
                    self.checkOpenVino.setChecked(True)
                    self.vino_pixmap.setVisible(True)

                    if self.selectWeight == "preweight":
                        det_model = YOLO(self.re_path + "/AI_Module/yolov8/model_data/yolov8n.pt")
                        self.label_map = det_model.model.names 
                        # print("self.label_map :", self.label_map)
                        # print()

                    elif self.selectWeight == "custom":
                        det_model = YOLO(self.ProjectLocation + "/best.pt")
                        self.label_map = det_model.model.names
                        print("self.label_map :", self.label_map)
                        print()

                    print("deserialize use_vino --> self.YoloWeightPath :", self.YoloWeightPath)

                    self.det_ov_model = self.openvino_core.read_model(self.YoloWeightPath)
            
                    device = self.editDevice.text() # "GPU"
                    if device != "CPU":
                        self.det_ov_model.reshape({0: [1, 3, 640, 640]})
                    self.det_compiled_model = self.openvino_core.compile_model(self.det_ov_model, device)
                    print("\033[93m {}\033[00m".format(str("deserialize --> det_compiled_model :"+ str(self.det_compiled_model))))

                    self.editDevice.setVisible(True)

                else:
                    ...

            if 'conf' in data:
                self.editConF.setText(data['conf'])

            if 'global_obj' in data:
                self.Global_Object = data['global_obj']

            if 'global_key' in data:
                self.GlobalObject_key = data['global_key']

            if 'show_fps' in data:
                self.show_fps = data['show_fps']

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(10, 110, 190, 110)

    # =======================================================================================
    def reload_weight_info(self):
        try:
            with open(self.dataset_name, "r", encoding="utf8") as stream:
                try:
                    self.names = yaml.safe_load(stream)
                    # print("self.names = ", self.names['names'])
                    self.lblErrorWarning.setVisible(False)

                except yaml.YAMLError as exc:
                    print(exc)

        except:
            print("\033[91m {}\033[00m".format("YoloV8 : No such Wight file or directory"))
            self.lblErrorWarning.setVisible(True)

        np.random.seed(40)
        list_of_arrays = np.random.uniform(low=50, high=200, size=(len(self.names['names']),3))
        # print("list_of_arrays :", list_of_arrays)

        # colorList = [(0,0,255) , (255,0,0)]
        self.colorList = [tuple(map(int, array)) for array in list_of_arrays]

        # print("YoloV8 ==> self.YoloWeightPath =", self.YoloWeightPath)
        self.comboPreWeight.setCurrentText(str(self.YoloWeightPath).split("/")[-1])

        # print("YoloV8 ==> self.dataset_name =", self.dataset_name)

    # =======================================================================================
    # Browse AI Custom weight
    def browseSlot(self):
        self.lblErrorWarning.setVisible(False)

        self.ProjectLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.ProjectLocation)

        if not self.use_openvino_flag:
            self.dataset_name = self.ProjectLocation + "/custom_data.yaml"
            self.YoloWeightPath = self.ProjectLocation + "/best.pt"
            
            self.reload_weight_info()

        else:
            det_model = YOLO(self.ProjectLocation + "/best.pt")
            self.label_map = det_model.model.names
            print("browseSlot self.label_map : ", self.label_map)
            
            if os.path.isfile(self.ProjectLocation + "/best.onnx"):
                print("\033[93m {}\033[00m".format("browseSlot No file best.onnx !!! ---> Export onnx the model"))
                    # Export the model
                det_model.export(format="openvino", dynamic=True, half=False)

            self.YoloWeightPath = self.ProjectLocation + "/best.onnx"
            print("\033[96m {}\033[00m".format("browseSlot use_vino --> YoloWeightPath :" + self.YoloWeightPath))

        self.lblProjectPath.setText(self.ProjectLocation)

        # Check if Segmentation
        self.dataset_name = self.ProjectLocation + "/custom_data.yaml"

        isegmet = {}
        try:
            with open(self.dataset_name , "r") as stream:
                try:
                    isegmet = yaml.safe_load(stream)
                    if 'isegment' in isegmet:
                        print("isegment = ", isegmet['isegment'])

                    self.lblErrorWarning.setVisible(False)
                        
                except yaml.YAMLError as exc:
                    print(exc)
        
        except:
            print("\033[91m {}\033[00m".format("YoloV8: No such Weight file or directory: custom_data.yaml'"))
            self.lblErrorWarning.setVisible(True)

        if 'isegment' in isegmet:
            print("isegment['isegment'][0] = ", isegmet['isegment'][0])
            if str(isegmet['isegment'][0]).lower() == 'true':
                self.YoloiSegWeightPath = self.ProjectLocation + "/best.pt"
                self.segmentation = True

                print("browseSlot self.YoloiSegWeightPath: ", self.YoloiSegWeightPath)
            else:
                self.YoloWeightPath = self.ProjectLocation + "/best.pt"
                self.segmentation = False

                print("browseSlot self.YoloWeightPath: ", self.YoloWeightPath)
        else:
            self.YoloWeightPath = self.ProjectLocation + "/best.pt"
            self.segmentation = False

        print("SelectCustom self.content.segmentation : ", self.segmentation)
    
    #Browse Input Image and Label
    def browseLoadImageandLable(self):
        #Clear All Param
        self.NOF_Image = 0
        self.NOF_Txt = 0

        self.file_imgname_list = []
        self.file_txtname_list = []

        self.Input_ImageLable_DIR = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.Input_ImageLable_DIR = ", self.Input_ImageLable_DIR)
        
        self.ImageLabelEdit.setText(self.Input_ImageLable_DIR)

        # Count Number of png file

        for pngfile in glob.iglob(os.path.join(self.Input_ImageLable_DIR, "*.png")):
            self.file_imgname_list.append(pngfile)
            self.NOF_Image += 1

        #  or glob.iglob(os.path.join(self.Input_ImageLable_DIR, "*.jpg")

        print("NOF_PNGImage = ", self.NOF_Image)
        if self.NOF_Image == 0:
            for jpgfile in glob.iglob(os.path.join(self.Input_ImageLable_DIR, "*.jpg")):
                self.file_imgname_list.append(jpgfile)
                self.NOF_Image += 1

        # print("NOF_JPGImage = ", self.NOF_Image)

        # print("self.file_imgname_list = ", self.file_imgname_list)

        # List txt name to list
        for txtfile in glob.iglob(os.path.join(self.Input_ImageLable_DIR, "*.txt")):
            self.file_txtname_list.append(txtfile)
            self.NOF_Txt += 1

        print("NOF_Txt = ", self.NOF_Txt)
        try:
            print("self.file_txtname_list[0] = ", self.file_txtname_list[0])
        except:
            ...

        if self.NOF_Image + 1 == self.NOF_Txt:

            """INPUT_DIR_NAME = self.Input_ImageLable_DIR.split("/")
            print("INPUT_DIR_NAME = ", INPUT_DIR_NAME)
            print("len(INPUT_DIR_NAME) = ", len(INPUT_DIR_NAME))
            print("len InputName = ", len(INPUT_DIR_NAME[len(INPUT_DIR_NAME) - 1]))

            OUTPUT_DIR = self.Input_ImageLable_DIR[0:-len(INPUT_DIR_NAME[len(INPUT_DIR_NAME) - 1])] + "_WeightTraining"""
            #print("OUTPUT_DIR = ", OUTPUT_DIR)

            OUTPUT_DIR = self.Input_ImageLable_DIR + "_WeightYoloV8"
            if self.iSegmentation_Train:
                OUTPUT_DIR = self.Input_ImageLable_DIR + "_WeightYoloV8Seg"

            print("OUTPUT_DIR = ", OUTPUT_DIR)
            if os.path.isdir(OUTPUT_DIR): 
                print ("Folder images exist")

            else:
                os.makedirs(OUTPUT_DIR) 

            self.ProjectTrainingLocation = OUTPUT_DIR

            if os.path.isdir(self.ProjectTrainingLocation + "/images"): 
                print ("Folder images exist")

            else:
                os.makedirs(self.ProjectTrainingLocation + "/images") 
                os.makedirs(self.ProjectTrainingLocation + "/images/train") 
                os.makedirs(self.ProjectTrainingLocation + "/images/val") 

            if os.path.isdir(self.ProjectTrainingLocation + "/labels"): 
                print ("Folder labels exist")

            else:
                os.makedirs(self.ProjectTrainingLocation + "/labels") 
                os.makedirs(self.ProjectTrainingLocation + "/labels/train") 
                os.makedirs(self.ProjectTrainingLocation + "/labels/val") 

            if os.path.isdir(self.ProjectTrainingLocation + "/weight"): 
                print ("Folder weight exist")

            else:
                os.makedirs(self.ProjectTrainingLocation + "/weight") 

            # copy all image in folder Input Image and Label to Output Folder
            # Step 1. Find xxx.img file and copy all to self.ProjectTrainingLocation + "/images/train"
            print("len(self.file_imgname_list) = ", len(self.file_imgname_list))

            for i in range(len(self.file_imgname_list)):
                shutil.copy(self.file_imgname_list[i], self.ProjectTrainingLocation + "/images/train")
            
            # Step 2. Copy 20% random of xxx.img to self.ProjectTrainingLocation + "/images/val"
            random_list = []

            Percent_OfValid = 4
        
            ten_of_NOF_Image = int(self.NOF_Image/Percent_OfValid)
            print("ten_of_NOF_Image = ", ten_of_NOF_Image)
            
            for i in range(ten_of_NOF_Image):
                no_random = random.randint(1, self.NOF_Image)
                if no_random < len(self.file_imgname_list):
                    if no_random not in random_list:
                        random_list.append(no_random)

            print("10% of random_list = ", random_list)
            print("len(random_list) = ", len(random_list))

            for i in range(len(random_list)):
                # print("random_list[", i,"]:", random_list[i])
                
                shutil.copy(self.file_imgname_list[random_list[i]], self.ProjectTrainingLocation + "/images/val")
                # print("self.file_imgname_list[random_list[", i, "]] :", self.file_imgname_list[random_list[i]])

            # Step 3. Find xxx.txt in Folder and copy to self.ProjectTrainingLocation + "/labels/train"
            print("len(self.file_txtname_list) = ", len(self.file_txtname_list))
            for i in range(len(self.file_txtname_list)):
                if self.file_txtname_list[i] == self.Input_ImageLable_DIR + '\classes.txt':
                    shutil.copy(self.file_txtname_list[i], self.ProjectTrainingLocation)
                    print("Save classes.txt to Folder; ", self.ProjectTrainingLocation)
                else:
                    shutil.copy(self.file_txtname_list[i], self.ProjectTrainingLocation + "/labels/train")

            # Step 4. Copy 10% of xxx.txt to self.ProjectTrainingLocation + "/labels/val"
            for i in range(len(random_list)):
                # if self.file_txtname_list[i] != self.Input_ImageLable_DIR + '\classes.txt':
                shutil.copy(self.file_imgname_list[random_list[i]][0:-3] + 'txt', self.ProjectTrainingLocation + "/labels/val")
                # print("shutil.copy(", self.file_imgname_list[random_list[i]][0:-3] + 'txt', ") to ", self.ProjectTrainingLocation, "/labels/val")

            # Step 5. Check New Folder is Empty
            check_folder = 0
            if any(os.scandir(self.ProjectTrainingLocation + "/images/train")):
                print('/images/train is not empty')
                check_folder += 1

            if any(os.scandir(self.ProjectTrainingLocation + "/images/val")):
                print('/images/val is not empty')
                check_folder += 1

            if any(os.scandir(self.ProjectTrainingLocation + "/labels/train")):
                print('/labels/train is not empty')
                check_folder += 1

            if any(os.scandir(self.ProjectTrainingLocation + "/labels/val")):
                print('not empty')
                check_folder += 1

            print("check_folder = ", check_folder)
            if check_folder == 4:

                #Check classes.txt
                if os.path.isfile(self.ProjectTrainingLocation + "/classes.txt"):

                    print("ready to make custom_data.yaml")

                    read_file_name = open(self.ProjectTrainingLocation + "/classes.txt",'r') #, encoding="utf-8")
                    read_names  = read_file_name.read()
                    
                    list_name = read_names.split("\n")
                    print("list_name[-1] : ", list_name[-1])

                    if list_name[-1] == '':
                        list_name.pop(len(list_name) -1)
                    
                    print("list_name = ", list_name)
                    print("len() = ", len(list_name))

                    data_yaml = "train: " + self.ProjectTrainingLocation + "/images/train/"+ "\n" +\
                                "val: " + self.ProjectTrainingLocation + "/images/val/" + "\n" +\
                                "test: " + "\n\n" +\
                                "nc: " + str(len(list_name)) + "\n" +\
                                "names: " + str(list_name)

                    if self.iSegmentation_Train:
                        data_yaml = "train: " + self.ProjectTrainingLocation + "/images/train/"+ "\n" +\
                                    "val: " + self.ProjectTrainingLocation + "/images/val/" + "\n" +\
                                    "test: " + "\n\n" +\
                                    "nc: " + str(len(list_name)) + "\n" +\
                                    "names: " + str(list_name) + "\n" +\
                                    "isegment: [" + str(self.iSegmentation_Train).lower() + "]"

                    file = open(self.ProjectTrainingLocation + "/custom_data.yaml",'w')
                    file.write(str(data_yaml))
                    file.close()

                    self.lblSelectImage.setText("Ready For Training !!")

                    # Check if the 'train' folder exists in the specified path
                    weights_path_folder = self.ProjectTrainingLocation + "/weight"
                    train_folder_exists = os.path.exists(os.path.join(weights_path_folder  , 'train'))

                    if train_folder_exists:
                        # List all directories in the path
                        # self.content.checkResume 

                        subfolders = [f for f in os.listdir(weights_path_folder) if os.path.isdir(os.path.join(weights_path_folder, f))]

                        # Filter out subfolders with names that start with 'train'
                        train_folders = [f for f in subfolders if f.startswith('train')]

                        if train_folders:
                            # Sort the 'train' folders alphabetically and get the latest one
                            latest_train_folder = max(train_folders)
                            weights_folder = os.path.join(weights_path_folder, latest_train_folder, 'weights')
                            
                            if os.path.exists(os.path.join(weights_folder, 'last.pt')):
                                # print(f"'last.pt' file exists in the 'weights' folder of the latest 'train' folder.")
                                self.checkResume.setVisible(True)
                                self.checkUpdateWeight.setVisible(True)

                            else:
                                self.checkResume.setVisible(False)
                                self.checkUpdateWeight.setVisible(False)
                                # print(f"'last.pt' file does not exist in the 'weights' folder of the latest 'train' folder.")
                        else:
                            self.checkResume.setVisible(False)
                            self.checkUpdateWeight.setVisible(False)
                            # print(f"'train' folder exists in {weights_path_folder}, but no 'train' subfolders found.")
                    else:
                        self.checkResume.setVisible(False)
                        self.checkUpdateWeight.setVisible(False)
                        # print(f"'train' folder does not exist in {weights_path_folder}.")

                    self.lblSelectImage.setVisible(True)
                    #Make custom_data.yaml
                    self.ready_for_training = True
                    self.TrainObjectBtn.setEnabled(True)
                    # self.ResCombo.setEnabled(True)
                    
                else:
                    print("No file classes.txt")
                    self.msg.setText(
                        "1. No classes.txt in folder " + self.ProjectTrainingLocation+ "\n" 
                        "2. Please copy from Image Label to folder")
                    retval = self.msg.exec_()
                    print("retval :", retval)

                    if retval == 1024:
                        print("Delete Folder ")
                        os.rmdir(OUTPUT_DIR) 

            else:
                print("Number of XXX.png not equal Number of XXX.txt")
                self.msg.setText("Number of XXX.png not equal Number of XXX.txt")
                retval = self.msg.exec_()
                print("retval :", retval)
                print("type(retval) :", type(retval))

                if retval == 1024:
                    print("Delete Folder ")
                    os.rmdir(OUTPUT_DIR) 

        else:
            print("No. of Image not equal No. of txt\nNo Data in ", self.ProjectTrainingLocation)
            self.msg.setText("No. of Image not equal No. of txt\n" 
                        + "Image = " + str(self.NOF_Image) + "\ntxt = " + str(self.NOF_Txt))
            retval = self.msg.exec_()
            print("retval :", retval)

            if retval == 1024:
                print("Delete Folder ")
                os.rmdir(OUTPUT_DIR) 
        

#============================================================================================
# self.ui.TlabelTraining, self.ui.TlabelLoss, self.ui.NumberProgress, self.ui.progress_bar, self.ui.CPUUsageLabel, self.ui.RAMUsageLabel
#============================================================================================
class Ui_YoloV8Training_MainWindow(object):
    def setupUi(self, MainWindow):

        self.MainWindow = MainWindow

        self.Screen_Width = GetSystemMetrics(0)   
        print("Screen Width =", self.Screen_Width)

        self.title = "AI Training Yolo V8"
        self.top    = 100
        self.left   = int(self.Screen_Width - 1020)
        self.width  = 980
        self.height = 830
        self.MainWindow.setWindowTitle(self.title)
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 
        self.MainWindow.setFixedWidth(self.width)
        self.MainWindow.setFixedHeight(self.height)
        self.MainWindow.setStyleSheet("background-color: rgba(40, 53, 123, 50);")

        self.TlabelTraining = QTextEdit("" , self.MainWindow)
        self.TlabelTraining.setAlignment(Qt.AlignLeft)
        self.TlabelTraining.setFixedSize(800, 735)  
        self.TlabelTraining.setStyleSheet("background-color: rgba(119, 222, 241, 100); font-size:9pt;")
        self.TlabelTraining.setGeometry(2,2,800,735)
        self.TlabelTraining.setReadOnly(True)
        self.TlabelTraining.verticalScrollBar().setVisible(False)

        #==================================================================
        #CPU

        self.CPUTitelLabel = QLabel("CPU Usage" , self.MainWindow)
        self.CPUTitelLabel.setAlignment(Qt.AlignLeft)
        self.CPUTitelLabel.setGeometry(805,15,170,20)
        self.CPUTitelLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.CPUUsageLabel = QLCDNumber(self.MainWindow, digitCount=3)
        self.CPUUsageLabel.setGeometry(810,40,120,50)
        self.CPUUsageLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.CPUPSLabel = QLabel("%" , self.MainWindow)
        self.CPUPSLabel.setAlignment(Qt.AlignLeft)
        self.CPUPSLabel.setGeometry(935,45,50,50)
        self.CPUPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        #==================================================================
        #Memory

        self.RAMTitelLabel = QLabel("Memory Usage" , self.MainWindow)
        self.RAMTitelLabel.setAlignment(Qt.AlignLeft)
        self.RAMTitelLabel.setGeometry(805,115,170,20)
        self.RAMTitelLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.RAMUsageLabel = QLCDNumber(self.MainWindow, digitCount=3)
        self.RAMUsageLabel.setGeometry(810,140,120,50)
        self.RAMUsageLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.RAMPSLabel = QLabel("%" , self.MainWindow)
        self.RAMPSLabel.setAlignment(Qt.AlignLeft)
        self.RAMPSLabel.setGeometry(935,145,50,50)
        self.RAMPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        #==================================================================

        self.TlabelLoss = QTextEdit("Start Training Yolo V8" , self.MainWindow)
        self.TlabelLoss.setAlignment(Qt.AlignLeft)
        self.TlabelLoss.setFixedSize(976, 50)  
        self.TlabelLoss.setStyleSheet("background-color: rgba(119, 222, 241, 100); font-size:13pt; color:lightblue; border: 1px solid white;")
        self.TlabelLoss.setGeometry(2,770,976,50)
        self.TlabelLoss.verticalScrollBar().setVisible(False)

        #==================================================================
        #Progress

        self.ProgressLabel = QLabel("Traing Progressive" , self.MainWindow)
        self.ProgressLabel.setAlignment(Qt.AlignLeft)
        self.ProgressLabel.setGeometry(805,665,170,20)
        self.ProgressLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:10pt;color:lightblue; border: 1px solid white; border-radius: 4%")

        self.NumberProgress = QLCDNumber(self.MainWindow, digitCount=3)
        self.NumberProgress.setGeometry(810,690,120,50)
        self.NumberProgress.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:15pt;color:lightblue; border: 1px solid white; border-radius: 2%")

        self.ProgressPSLabel = QLabel("%" , self.MainWindow)
        self.ProgressPSLabel.setAlignment(Qt.AlignLeft)
        self.ProgressPSLabel.setGeometry(935,695,50,50)
        self.ProgressPSLabel.setStyleSheet("background-color: rgba(40, 53, 123, 0); font-size:23pt;color:lightblue;")

        self.progress_bar = QProgressBar(self.MainWindow)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("background-color: rgba(119, 222, 241, 100); font-size:9pt; color:lightblue; border: 1px solid white;")
        self.progress_bar.setGeometry(3,745,972,20)

        self.training_progress = 0
        self.progress_bar.setValue(int(self.training_progress))
        self.NumberProgress.display(str(int(self.training_progress)))

        # ==================================================================
        # Estimate Finish
        self.EstDoneLabel = QLabel("Estimate\nFinish" , self.MainWindow)
        self.EstDoneLabel.setAlignment(Qt.AlignLeft)
        self.EstDoneLabel.setGeometry(600,775,70,40)
        self.EstDoneLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:blue; border: 1px solid white; border-radius: 2%")

        self.EstFinishLabel = QLabel("", self.MainWindow)
        self.EstFinishLabel.setGeometry(680,775,290,40)
        self.EstFinishLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:14pt;color:blue; border: 1px solid white; border-radius: 2%")

class ActivateVenv:
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

        time.sleep(1)
        print("root_path :", root_path)

        shell.AppActivate(self.get_pid())
        shell.SendKeys("cd \ {ENTER}")
        shell.SendKeys("%s {ENTER}" % root_path)
        shell.SendKeys(r"cd %s {ENTER}" % venv_location)
        # shell.SendKeys("activate {ENTER}")

    def run_cmd(self, venv_location):
        print("venv_location :", venv_location)
        # Replace 'your_directory_path' with the directory you want to navigate to
        # directory_path = r'C:\Users\User\Documents\AI_FlowEditor_BUILD_25OCT2023_1355\ai_application\AI_Module\train\yolov8'

        try:
            # Create a new instance of the Windows Script Host Shell object
            shell = client.Dispatch("WScript.Shell")
            
            # Run CMD
            shell.run("cmd.exe")

            # Wait for a brief moment to ensure CMD has started
            time.sleep(1)  # Adjust the sleep duration as needed

            # Find the Command Prompt window and bring it to the foreground
            cmd_window = FindWindow(None, "Command Prompt")
            if cmd_window:
                ShowWindow(cmd_window, win32gui.SW_RESTORE)
                SetForegroundWindow(cmd_window)

            # Change the working directory in CMD
            shell.SendKeys(f"cd {venv_location}\n")
            time.sleep(0.5)
            shell.SendKeys("{ENTER}")
            time.sleep(0.5)
            shell.SendKeys("python train.py {ENTER}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_cuda_version(self):
        # Check if the nvcc command is available (part of the CUDA Toolkit)
        try:
            nvcc_output = os.popen('nvcc --version').read()
        except Exception:
            return "CUDA not found"

        # Extract the CUDA version from the output
        lines = nvcc_output.strip().split('\n')
        for line in lines:
            if line.startswith('Cuda compilation tools'):
                cuda_version = line.split()[-1]
                return cuda_version

        return "CUDA version not found"

    def run_py_script(self,shell):
        """runs the py script"""

        required = {'torch', 'torchvision', 'torchaudio', 'tqdm', 'av', 'protobuf==3.20.3',
                    'pyyaml','opencv-python','pandas','matplotlib',
                    'seaborn', 'tensorboard', 'thop', 'ultralytics'}

        installed = {pkg.key for pkg in pkg_resources.working_set}
        print("installed : ", installed)

        missing = required - installed

        print()
        print("missing : ", missing)

        install_torch_flag = False

        if missing:
            list_command = list(missing)
            print("list_command : ", list_command)
            print("len(list_command) : ", len(list_command))

            for i in range(len(list_command)):
                print(list_command[i])
                if str(list_command[i]) == "torch":
                    print("Installing torch", i)
                    list_command.pop(i)
                    install_torch_flag = True
                    break

            for i in range(len(list_command)):
                if str(list_command[i]) == "torchvision":
                    print("Installing torchvision", i)
                    list_command.pop(i)
                    install_torch_flag = True
                    break

            for i in range(len(list_command)):
                if str(list_command[i]) == "torchaudio":
                    print("Installing torchaudio", i)
                    list_command.pop(i)
                    install_torch_flag = True
                    break

            if install_torch_flag:
                print("Install Torch Vision")
                cuda_version = str(self.get_cuda_version())[0:5]
                print(f"CUDA Version: {cuda_version}")

                if cuda_version == "V11.3":
                    # shell.SendKeys("pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113 --no-cache {ENTER}")
                    shell.SendKeys("pip --default-timeout=1000 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu113")

                elif cuda_version == "V11.8":
                    shell.SendKeys("pip --default-timeout=1000 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

                elif cuda_version == "V12.1":
                    shell.SendKeys("pip --default-timeout=1000 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

            print("New list_command : ", list_command)
            if len(list_command) > 0:
                left_missing = list_command
                print("left_missing : ", left_missing)
            
                for l in range(len(left_missing)):
                    shell.SendKeys("pip install " + str(left_missing[l]) + "{ENTER}")

        else:
            print("python library already installed")

        # shell.SendKeys("cd ../..{ENTER}")
        shell.SendKeys("python train.py {ENTER}")

    def open_cmd(self, shell):
        """ opens cmd """

        shell.run("cmd.exe")
        time.sleep(1)

class TraingYolo(QtWidgets.QMainWindow):
    def __init__(self, content, preWeights_path, custom_data_yaml_path, project_traindata_path, batch_size, epoch_size, segmentation, resume, update, imgsz, solution, parent=None):
        super().__init__(parent)

        self.content = content
        # self.Global = GlobalVariable()

        self.PreWeight_path = preWeights_path
        print("self.PreWeight_path  = ", self.PreWeight_path )

        self.Path = self.PreWeight_path[0:-21]
        print("self.Path = ", self.Path)

        self.custom_data_path = custom_data_yaml_path
        print("self.custom_data_path = ", self.custom_data_path)

        self.project_traindata_path = project_traindata_path
        print("self.project_traindata_path = ", self.project_traindata_path)

        self.batch_size = batch_size
        print("self.batch_size = ", self.batch_size)
        print("type(self.batch_size) = ", type(self.batch_size))

        self.Epoch_Size = epoch_size
        print("self.Epoch_Size = ", self.Epoch_Size)
        print("type(self.Epoch_Size) = ", type(self.Epoch_Size))

        self.segmentation = segmentation
        print("self.segmentation = ", self.segmentation)

        self.resume = resume
        print("self.resume = ", self.resume)

        self.solution = solution
        print("self.solution : ", self.solution)

        self.ui = Ui_YoloV8Training_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.ui.TlabelTraining.setText("Prepare Data for Taining Yolo V8\n" + 
                                    "PreWeight_path  = " + self.PreWeight_path  + "\n" +
                                    "Path = " + self.Path + "\n" +
                                    "project_traindata_path = " + self.project_traindata_path + "\n" +
                                    "batch_size = " + str(self.batch_size) + "\n" +
                                    "Epoch_Size = " + str(self.Epoch_Size) + "\n" +
                                    "segmentation = " + str(self.segmentation)+ "\n" +
                                    "resume = " + str(self.resume) + "\n" + 
                                    "imgsz = [" + str(imgsz) + " , " + str(imgsz) + "]")

        self.Terminal_timer = QtCore.QTimer(self)
        self.Terminal_timer.timeout.connect(self.TerminalPrint_interval)
        self.Terminal_timer.setInterval(50)
        
        self.Training_AI_Str = {}

        self.Training_Process = ""
        self.Training_Loss = ""
        self.Training_Step = ""

        self.StartTraining_timer = QtCore.QTimer(self)
        self.StartTraining_timer.timeout.connect(self.StartTraining_interval)
        self.StartTraining_timer.setInterval(1000)
        self.StartTraining_timer.start()

        # self.Training_File_Path = ""
        # if not self.segmentation:
        self.Training_File_Path = self.content.re_path + '/AI_Module/train/yolov8'

        # else:
        #     self.Training_File_Path = self.content.re_path + '/AI_Module/yolov8'

        print("TraingYolo --> self.Training_File_Path : ", self.Training_File_Path)

        if self.solution == "Train":
            if os.path.isfile(self.Training_File_Path + "/yolo_cache.txt"):
                os.remove(self.Training_File_Path + "/yolo_cache.txt")

            opt_data = {}
            opt_data["data"] = self.custom_data_path + '/custom_data.yaml'
            # opt_data["hyp"] = self.Path + '/data/hyps/hyp.scratch-low.yaml'
            opt_data["epochs"] = str(self.Epoch_Size)
            opt_data["device"] = self.content.device
            opt_data["batch_size"] = str(self.batch_size)
            if self.content.ImageTrainZ == 640:
                opt_data["imgsz"] = self.content.ImageTrainZ
            elif self.content.ImageTrainZ == 416:
                opt_data["imgsz"] = [self.content.ImageTrainZ, self.content.ImageTrainZ]

            opt_data["project"] = self.project_traindata_path + '/weight/'
            opt_data['segment'] = self.segmentation
            opt_data['resume'] = self.resume

            if update:
                print("Training Additional Image ")

            if self.resume or update:
                opt_data["weights"] = self.check_resume()
            else:
                opt_data["weights"] = self.PreWeight_path

            OPT_Training = self.Training_File_Path      #boxitems
            print("Yolo V8 Opt Training : ", OPT_Training)
            print("opt_data :", opt_data)

            with open(OPT_Training + "/yolo_opt.txt", 'w') as f:
                f.writelines(str(json.dumps(opt_data)))

            root_part = self.Training_File_Path[0:2]

            shell = client.Dispatch("WScript.Shell")
            run_venv = ActivateVenv()
            run_venv.open_cmd(shell)
            # EnumWindows(run_venv.set_cmd_to_foreground, None)
            run_venv.activate_venv(shell, root_part, self.Training_File_Path)

            # Hard Code Training for RTX4090
            # run_venv.run_cmd(self.Training_File_Path)

            run_venv.run_py_script(shell)

            # ========================================
            # Calculate Estimate Trianing Finish
            self.NowTime = None
            self.SpendTime_Sec = None
            self.EstimateDone = None

            self.current_pc = 0

            if not self.content.first_startTrain:
                self.content.first_startTrain = True
                self.content.startime = datetime.now()

            # ========================================

        self.Terminal_timer.start()

    def StartTraining_interval(self):
        self.StartTraining_timer.stop()

        # self.opt = self.parse_opt()
        # self.main(self.opt)
        #g:\My Drive\AI-Flow-Editor\ai_application\boxitems

        # self.SubGlobalV8.setGlobal('YoloV8_opt', self.opt)
        # self.SubGlobalV8.setGlobal('YoloV8_waiting_opt', False)
        
    # =================================================================================

    def TerminalPrint_interval(self):

        cpu_percent = psutil.cpu_percent(interval=0.5)
        self.ui.CPUUsageLabel.display(str(int(cpu_percent)))

        Usage_virtual_memory = psutil.virtual_memory().percent
        self.ui.RAMUsageLabel.display(str(int(Usage_virtual_memory)))

        # ========================================
        # Calculate Estimate Trianing Finish
        self.NowTime = datetime.now()
        if type(self.content.startime) != type(None):
            self.SpendTime_Sec = self.NowTime - self.content.startime
            seconds = self.SpendTime_Sec.total_seconds()

        # ========================================

        yolov8_cache = self.Training_File_Path + "/yolo_cache.txt"
        # print("yolov8_cache :", yolov8_cache)

        if os.path.isfile(yolov8_cache):
            Training_AI_Cache = open(yolov8_cache,'r') #, encoding="utf-8")
            str_Cache  = Training_AI_Cache.read()

            self.Training_AI_Status = {}

            if len(str_Cache) > 2:
                self.Training_AI_Status  = json.loads(str_Cache)
                # print("Training_AI_Str = ", self.Training_AI_Status)

            if 'Debug_Training' in self.Training_AI_Status:
                if self.Training_AI_Status['Debug_Training']:
                    self.ui.TlabelTraining.setText(str(self.Training_AI_Status['Debug_Training']))

            if 'Training_Process' in self.Training_AI_Status:
                if self.Training_AI_Status['Training_Process']:
                    self.ui.TlabelTraining.setText(str(self.Training_AI_Status['Training_Process']))
                    self.ui.TlabelTraining.verticalScrollBar().setValue(self.ui.TlabelTraining.verticalScrollBar().maximum())

            if 'Training_Loss' in self.Training_AI_Status:
                if self.Training_AI_Status['Training_Loss']:
                    self.ui.TlabelLoss.setText(str(self.Training_AI_Status['Training_Loss']))

            if 'Training_Precent' in self.Training_AI_Status:

                # if self.Training_AI_Status['Training_Precent']:
                self.training_progress = str(self.Training_AI_Status['Training_Precent'])
                if 'Training_Step' in self.Training_AI_Status:
                    if self.Training_AI_Status["Training_Step"] == 'End':
                        self.ui.progress_bar.setValue(int(100))
                        self.ui.NumberProgress.display(str(int(100)))

                        self.ui.TlabelLoss.setStyleSheet("background-color: rgba(119, 222, 241, 100); font-size:13pt; color:lightgreen; border: 1px solid white;")
                        self.ui.TlabelLoss.setText(str(self.Training_AI_Status['Training_Precent']) + " : Training Completed in " + str(self.Training_AI_Status['Traing_Time']) + " hours.")
                        self.Terminal_timer.stop()

                        self.content.first_startTrain = False

                else:
                    # print("self.training_progress = ", self.training_progress)
                    # print("self.content.Epoch_sizeEdit.text() = ", self.content.Epoch_sizeEdit.text())

                    percent_training = int(int(self.training_progress) * 100 / int(self.content.Epoch_sizeEdit.text()))
                    # self.current_pc = percent_training
                    # print("percent_training = ", percent_training)

                    # =================================================================
                    # Find SpendTime in Seconds
                    if percent_training > 0:
                        self.EstimateDone = int(int(100 * (seconds))/percent_training)

                        # 👇️ convert string to datetime object
                        if self.current_pc != percent_training:
                            result = self.content.startime + timedelta(seconds=self.EstimateDone)
                            # print("Estimate Finish", str(result.strftime("%d-%m-%Y  [ %H:%M ]")))
                            self.ui.EstFinishLabel.setText(str(result.strftime("%d-%m-%Y  [ %H:%M ]")))

                            self.current_pc = percent_training
                            # print("self.current_pc :", self.current_pc)

                    # ==================================================================

                    self.ui.progress_bar.setValue(percent_training)
                    self.ui.NumberProgress.display(str(percent_training))

            # Check Resume feature Available
            self.check_resume()

        else:
            # print("No file yolo_cache.txt !!!")
            ...

    def check_resume(self):
        # Check if the 'train' folder exists in the specified path
        weights_path_folder = self.project_traindata_path + "/weight"
        train_folder_exists = os.path.exists(os.path.join(weights_path_folder  , 'train'))

        if train_folder_exists:
            # List all directories in the path
            # self.content.checkResume 

            subfolders = [f for f in os.listdir(weights_path_folder) if os.path.isdir(os.path.join(weights_path_folder, f))]

            # Filter out subfolders with names that start with 'train'
            train_folders = [f for f in subfolders if f.startswith('train')]

            if train_folders:
                # Sort the 'train' folders alphabetically and get the latest one
                latest_train_folder = max(train_folders)
                weights_folder = os.path.join(weights_path_folder, latest_train_folder, 'weights')
                # print("weights_folder :", weights_folder)
                
                if os.path.exists(os.path.join(weights_folder, 'last.pt')):
                    # print(f"'last.pt' file exists in the 'weights' folder of the latest 'train' folder.")
                    self.content.checkResume.setVisible(True)
                    self.content.checkResume.setEnabled(False)

                    original_path = weights_folder + "/last.pt"
                    converted_path = original_path.replace("\\", "/")

                    return converted_path

                else:
                    self.content.checkResume.setVisible(False)
                    # print(f"'last.pt' file does not exist in the 'weights' folder of the latest 'train' folder.")

                    return ""
            else:
                self.content.checkResume.setVisible(False)
                # print(f"'train' folder exists in {weights_path_folder}, but no 'train' subfolders found.")

                return ""
        else:
            self.content.checkResume.setVisible(False)
            print(f"'train' folder does not exist in {weights_path_folder}.")

            return ""

    #========================================================================================
    #========================================================================================
    #Close AI Training ---> Save Check Point
    def closeEvent(self, event):
        self.content.TrainObjectBtn.setEnabled(True)
        print("AI Yolo Training Log is closed !!!")

        self.content.checkLog.setChecked(False)
        self.Terminal_timer.stop()

        self.content.checkResume.setEnabled(True)

        with open(self.Training_File_Path + "/yolo_cache.txt", 'w') as f:
            f.writelines(str(""))

# ===========================================================
class YOLOV8Setting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content
        self.WeightLocation = ""

        self.title = "YOLOV8 Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 800
        self.height = 470
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.lbl = QLabel("Send Output to Global Key: ", self)
        self.lbl.setGeometry(QtCore.QRect(10, 5, 250, 20))
        self.lbl.setStyleSheet("color: #42E3C8;")

        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.edit.setGeometry(280,4,200,25)
        self.edit.setPlaceholderText("Global Object Key")
        self.edit.setText(self.content.GlobalObject_key)

        self.editGlobalObject = QPlainTextEdit("",self)
        # self.editGlobalObject.setFixedWidth(380)
        self.editGlobalObject.setGeometry(10,35,780,250)
        self.editGlobalObject.setStyleSheet("background-color: rgba(19, 21, 91, 225);font-size:12pt;color:#42E3C8;")
        self.editGlobalObject.setPlaceholderText("Global Object")

        self.editGlobalObject.setPlainText(str(self.content.Global_Object))

        self.edit.textChanged.connect(self.ChangedKey)

        # Convert YoloV8 to ONNX
        self.lbl_ConvertONNX = QLabel("Convert YoloV8 to ONNX", self)
        self.lbl_ConvertONNX.setGeometry(QtCore.QRect(10, 300, 250, 30))
        self.lbl_ConvertONNX.setStyleSheet("color: lightgreen; font-size:10pt;")

        self.editBrowsWeightFile = QLineEdit("",self)
        self.editBrowsWeightFile.setGeometry(10,335,780,30)
        self.editBrowsWeightFile.setPlaceholderText("          Select Path best.pt")
        
        self.browsWeightFiles = QPushButton(self)
        self.browsWeightFiles.setGeometry(15,340,20,20)
        self.browsWeightFiles.setIcon(QIcon(self.content.save_icon))

        self.browsWeightFiles.clicked.connect(self.browseWeightSlot)

        self.ConverONNXtBtn = QPushButton("Convert ONNX",self)
        self.ConverONNXtBtn.setGeometry(10,370,120,30)
        self.ConverONNXtBtn.clicked.connect(self.ConvertYoloV8toONNX)

        self.ConverNCNNtBtn = QPushButton("Convert NCNN",self)
        self.ConverNCNNtBtn.setGeometry(140,370,120,30)
        self.ConverNCNNtBtn.clicked.connect(self.ConvertYoloV8toNCNN)

    def browseWeightSlot(self):
        self.WeightLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory")) 
        print("self.fileLocation = ", self.WeightLocation)

        self.editBrowsWeightFile.setText("          " + self.WeightLocation + "/best.pt")

    def ConvertYoloV8toONNX(self):
        if len(self.WeightLocation) > 0:
            det_model = YOLO(self.WeightLocation + "/best.pt")
            if not os.path.isfile(self.WeightLocation + "/best.onnx"):
                print("\033[93m {}\033[00m".format("No file best.onnx !!! ---> Export onnx the model"))
                # Export the model
                det_model.export(format="onnx")

        else:
            self.content.msg.setText("Connot Convert ONNX !!!\n No weight file in folder")
            retval = self.content.msg.exec_()

    def ConvertYoloV8toNCNN(self):
        if len(self.WeightLocation) > 0:
            # Export the model to NCNN with arguments
            det_model = YOLO(self.WeightLocation + "/best.pt")
            if not os.path.isfile(self.WeightLocation + "/best.bin"):
                print("\033[93m {}\033[00m".format("No file best.bin !!! ---> Export ncnn the model"))
                # det_model.export(format='ncnn', half=True, imgsz=640)
                det_model.export(format='ncnn', simplify=True)

        else:
            self.content.msg.setText("Connot Convert NCNN !!!\n No weight file in folder")
            retval = self.content.msg.exec_()

    def ChangedKey(self):
        self.content.change_global_key = True

    def closeEvent(self, event):
        self.content.Global_Object = self.editGlobalObject.toPlainText()
        self.content.GlobalObject_key = self.edit.text()
        self.content.SettingBtn.setEnabled(True)

#============================================================================================
#============================================================================================

@register_node(OP_NODE_OBJYOLOV8)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_objyolo8.png"
    op_code = OP_NODE_OBJYOLOV8
    op_title = "Yolo V8"
    content_label_objname = "Yolo V8"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[3,5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.input_payload = {}
        self.pass_payload = {}
        self.copy_payload = {}

        # Pose
        self.skeleton = [
            [16, 14],
            [14, 12],
            [17, 15],
            [15, 13],
            [12, 13],
            [6, 12],
            [7, 13],
            [6, 7],
            [6, 8],
            [7, 9],
            [8, 10],
            [9, 11],
            [2, 3],
            [1, 2],
            [1, 3],
            [2, 4],
            [3, 5],
            [4, 6],
            [5, 7],
        ]

        self.limb_color = colors.pose_palette[[9, 9, 9, 9, 7, 7, 7, 0, 0, 0, 0, 0, 16, 16, 16, 16, 16, 16, 16]]
        self.kpt_color = colors.pose_palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]

        self.pose_image = None
        self.pose_point = []
        self.pose_skeleton = []

    def initInnerClasses(self):
        self.content = ObjectDetectV8(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCholeProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.combo.activated[str].connect(self.onChangedProcess)
        self.content.comboPreWeight.activated[str].connect(self.onChangedPreWeight)

        self.content.checkPreWeight.stateChanged.connect(self.SelectPreWieght)
        self.content.checkCustom.stateChanged.connect(self.SelectCustom)

        self.content.iSegmentation_Train_Check.stateChanged.connect(self.SelectiSegPreweight)

        self.content.SwitchDetect.clicked.connect(self.StartDetecOBJ)
        self.content.browsFilesCustome.clicked.connect(self.content.browseSlot)

        self.content.browsTargetFolder.clicked.connect(self.content.browseLoadImageandLable)
        self.content.TrainObjectBtn.clicked.connect(self.trainingObject)

        # self.content.checkBGProcess.stateChanged.connect(self.SelectBG_Detection)
        self.content.checkOpenVino.stateChanged.connect(self.SelectIntel_CPUAndGPU)

        self.content.checkLog.stateChanged.connect(self.SelectShowLog)
        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

        self.content.checkResume.stateChanged.connect(self.SelectResumeTraining)
        self.content.checkUpdateWeight.stateChanged.connect(self.SelectWeightUpdateTraining)

        self.content.ImageTrainZCombo.activated[str].connect(self.onTrainingResChanged)

        self.Global = GlobalVariable()

        self.grNode_addr = str(self.grNode)[-13:-1]
        self.YOLOV8_ID = "YoloV8" + self.grNode_addr
        # print("initInnerClasses YoloV8 = ", self.YOLOV8_ID)
        print("\033[91m {}\033[00m".format("initInnerClasses YoloV8 : " + self.YOLOV8_ID))

    def evalImplementation(self):                 # <
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.input_payload = input_node.eval()

            if self.input_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                # return

            else:
                # Operate Process Here !!!!!
                if 'img' in self.input_payload:
                    if len(str(self.input_payload['img'])) > 100 and not (np.all(self.input_payload['img'] == 0) or np.all(self.input_payload['img'] == 255)):
                        if 'centers' in self.input_payload:
                            self.pass_payload['centers'] = self.input_payload['centers']
                            self.copy_payload['centers'] = self.input_payload['centers']
                    
                        #print("val['img'] = ", val['img'])
                        if 'fps' in self.input_payload and self.content.show_fps:
                            self.pass_payload['fps'] = self.input_payload['fps']
                            self.copy_payload['fps'] = self.input_payload['fps']

                        if 'clock' in self.input_payload:
                            self.pass_payload['clock'] = self.input_payload['clock']
                            self.copy_payload['clock'] = self.input_payload['clock']

                        if 'run' in self.input_payload:
                            self.pass_payload['run'] = self.input_payload['run']
                            self.copy_payload['run'] = self.input_payload['run']

                        if 'img_h' in self.input_payload:
                            self.pass_payload['img_h'] = self.input_payload['img_h']
                            self.copy_payload['img_h'] = self.input_payload['img_h']

                        if 'img_w' in self.input_payload:
                            self.pass_payload['img_w'] = self.input_payload['img_w']
                            self.copy_payload['img_w'] = self.input_payload['img_w']

                        if 'blink' in self.input_payload:
                            if self.input_payload['blink'] == True:
                                self.content.lbl.setText("<font color=#00FF00>-> Image Input</font>")
                            else:
                                self.content.lbl.setText("")

                            self.pass_payload['blink'] = self.input_payload['blink']

                        if 'inputtype' in self.input_payload:
                            self.pass_payload['inputtype'] = self.input_payload['inputtype']
                            self.copy_payload['inputtype'] = self.input_payload['inputtype']
                            # self.pass_payload['img_copy'] = ORG_image

                        self.pass_payload['obj_found'] = 0
                        self.pass_payload['yolo_boxes'] = []
                        self.pass_payload['img'] = self.input_payload['img']
                        # print("self.input_payload['img'] :", self.input_payload['img'])

                        if self.content.StartProcessDetect_flag:
                            if self.content.YoloProcess == "Detect" or self.content.YoloProcess == "iSegment" or self.content.YoloProcess == "Track":
                                if not self.content.use_openvino_flag:
                                    if self.content.process_detect_bg:
                                        if self.content.FirstInnitFromStart:
                                            # self.start_bootProcess()
                                            self.content.checkBGProcess.setChecked(True)

                                        self.Global.setGlobal("img"+self.YOLOV8_ID, self.input_payload['img'])
                                        if self.Global.hasGlobal("results"+self.YOLOV8_ID):
                                            results = self.Global.getGlobal("results"+self.YOLOV8_ID)
                                            # print("process_detect_bg; resulte :", results)

                                            self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.plot_boxes(results, self.input_payload['img'] , conf_thres= float(self.content.editConF.text()))
                                            results = self.Global.removeGlobal("results"+self.YOLOV8_ID)
                                    else:
                                        # Main YoloV8 Dectection
                                        self.copy_payload['img'] = self.input_payload['img']
                                        if not self.content.segmentation:
                                            # print("self.input_payload['img'] :", self.input_payload['img'])
                                            if self.content.YoloProcess == "Track":
                                                self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.track_yolov8(self.input_payload['img'], conf_thres= float(self.content.editConF.text()))
                                            
                                            else:
                                                self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.detect_yolov8(self.input_payload['img'], conf_thres= float(self.content.editConF.text()))

                                        else:
                                            if self.content.YoloProcess == "Track":
                                                ...
                                            
                                            else:
                                                self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.detect_yolov8_iSeg(self.input_payload['img'], conf_thres= float(self.content.editConF.text()))
                            
                                    self.copy_payload['obj_found'] = self.pass_payload['obj_found']
                                    self.copy_payload['yolo_boxes'] = self.pass_payload['yolo_boxes']

                                else:
                                    detections = self.openvino_detect(self.input_payload['img'], self.content.det_compiled_model)[0]
                                    self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.openvino_draw_results(detections, self.input_payload['img'], self.content.label_map, conf_thres= float(self.content.editConF.text()))
                        
                                self.Global.setGlobal(self.content.GlobalObject_key, self.pass_payload)

                            elif self.content.YoloProcess == "Pose":
                                # Run batched inference on a list of images

                                results = self.content.model.predict(self.input_payload['img'], show=False, verbose=False)
                                # results = self.score_frame(self.input_payload['img'])

                                # Process results list
                                self.pose_point = []
                                self.pose_skeleton = []
                                
                                for result in results:
                                    # boxes = result.boxes  # Boxes object for bounding box outputs
                                    # masks = result.masks  # Masks object for segmentation masks outputs
                                    keypoints = result.keypoints  # Keypoints object for pose outputs
                                    # probs = result.probs  # Probs object for classification outputs

                                    for keypoint in keypoints:
                                        # print("keypoint.conf[0] :", keypoint.conf.tolist()[0])
                                        # print("keypoint.data[0] :", int(keypoint.data.tolist()[0]))
                                        # self.pose_point, self.pose_skeleton, self.pose_image = self.kpts(keypoint.data[0], self.input_payload['img'])
                                        self.pose_image = self.kpts(keypoint.data[0], self.input_payload['img'])
                                
                                self.pass_payload['pose_point'] = self.pose_point
                                self.pass_payload['pose_skeleton'] = self.pose_skeleton
                                self.pass_payload['img'] = self.pose_image
                                self.copy_payload['img'] = self.input_payload['img']

                        else:
                            results = self.Global.removeGlobal(self.content.GlobalObject_key)

                        self.sendFixOutputByIndex(self.pass_payload, 0)
                        # print("self.copy_payload : ", self.copy_payload)
                        self.sendFixOutputByIndex(self.copy_payload, 1)
                        
                    else:
                        self.content.lbl.setText("<font color='red'>Wrong Input !!!</font>")

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

    # ====================================================================================
    def OnOpen_Setting(self):
        self.YOLOV8_Setting = YOLOV8Setting(self.content)
        self.YOLOV8_Setting.show()
        self.content.SettingBtn.setEnabled(False)

    # ====================================================================================
    # ====================================================================================
    def start_bootProcess(self):
        self.content.FirstInnitFromStart = False
        self.Global.setGlobal("run"+self.YOLOV8_ID, True)
        self.content.process_detect_bg = True

        Detection_app = objectDetection.app
        objectDetection.DetectionThread(self.content.model, self.YOLOV8_ID).start()
        Detection_app.exec_()


    def StartDetecOBJ(self):
        self.content.StartProcessDetect_flag = not self.content.StartProcessDetect_flag

        if not self.content.StartProcessDetect_flag:
            self.content.model = None

            self.content.combo.setEnabled(True)
            self.content.comboPreWeight.setEnabled(True)
            self.content.checkPreWeight.setEnabled(True)
            self.content.checkCustom.setEnabled(True)
            # self.content.comboGPU.setEnabled(True)

            self.content.checkOpenVino.setEnabled(True)
            self.content.editDevice.setEnabled(True)

            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))

            self.content.labelAnimate.setVisible(False)
            self.content.movie.stop()

            self.content.AutoLoadYolo = False

            if self.content.process_detect_bg:
                self.Global.setGlobal("run"+self.YOLOV8_ID, False)

            if self.content.YoloProcess == "Pose":
                self.content.comboPreWeight.clear()
                self.content.comboPreWeight.addItem("YOLOv8n-pose.pt")
                self.content.comboPreWeight.addItem("YOLOv8s-pose.pt")
                self.content.comboPreWeight.addItem("YOLOv8m-pose.pt")
                self.content.comboPreWeight.addItem("YOLOv8l-pose.pt")
                self.content.comboPreWeight.addItem("YOLOv8x-pose.pt")
                self.content.comboPreWeight.addItem("YOLOv8x-pose-p6.pt")

        else:

            self.content.checkOpenVino.setEnabled(False)
            self.content.editDevice.setEnabled(False)

            self.content.checkPreWeight.setEnabled(False)
            self.content.checkCustom.setEnabled(False)

            if  self.content.use_openvino_flag:
                if self.content.selectWeight == "preweight": 
                    det_model = YOLO(self.content.re_path + "/AI_Module/yolov8/model_data/yolov8n.pt")
                    self.content.label_map = det_model.model.names

                print("self.content.YoloWeightPath:", self.content.YoloWeightPath)
                self.det_ov_model = self.content.openvino_core.read_model(self.content.YoloWeightPath)
        
                device = self.content.editDevice.text() #"GPU"
                if device != "CPU":
                    self.det_ov_model.reshape({0: [1, 3, 640, 640]})
                self.content.det_compiled_model = self.content.openvino_core.compile_model(self.det_ov_model, device)
                print("\033[93m {}\033[00m".format(str("StartDetecOBJ --> det_compiled_model :"+ str(self.content.det_compiled_model))))

                self.content.AutoLoadYolo = True
                self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))

                self.content.comboPreWeight.setEditable(False)

            else:
                if self.content.YoloProcess == "Detect" or self.content.YoloProcess == "iSegment" or self.content.YoloProcess == "Track":
                    try:
                        self.content.model = YOLO(self.content.YoloWeightPath)
                        # print("\033[93m {}\033[00m".format("self.model :" + str(self.content.model)))    

                        self.content.model_name = self.content.model.model.names
                        print("\033[94m {}\033[00m".format("self.model_name :" + str(self.content.model.model.names))) 

                        self.content.AutoLoadYolo = True
                        self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))

                        self.content.labelAnimate.setVisible(True)
                        self.content.movie.start()

                        self.content.combo.setEnabled(False)
                        self.content.comboPreWeight.setEnabled(False)
                        self.content.checkPreWeight.setEnabled(False)
                        self.content.checkCustom.setEnabled(False)

                        if self.content.process_detect_bg:
                            self.start_bootProcess()

                        self.content.lblErrorWarning.setVisible(False)
                    
                    except:
                        # print("\033[94m {}\033[00m".format("YoloV8 : No such Weight file or directory: best.pt")) 
                        self.content.lblErrorWarning.setVisible(True)

                elif self.content.YoloProcess == "Pose":
                        self.content.model = YOLO(self.content.YoloWeightPath)
                        # print("\033[93m {}\033[00m".format("Pose --> self.model :" + str(self.content.model)))   

                        self.content.AutoLoadYolo = True
                        self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))

                else:
                    self.content.labelAnimate.setVisible(False)
                    self.content.movie.stop()

                    self.content.model = None

                    if self.content.process_detect_bg:
                        self.Global.setGlobal("run"+self.YOLOV8_ID, False)

                    torch.cuda.empty_cache()
            
    def onChangedProcess(self, text):
        print("onChangedProcess : ", text)
        if text == "Detect":

            # Visible True
            self.content.YoloProcess = "Detect"
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.checkCustom.setVisible(True)
            self.content.checkCustom.setEnabled(True)

            # self.content.comboGPU.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)
            # self.content.checkBGProcess.setVisible(True)
            self.content.lblConF.setVisible(True)
            self.content.SettingBtn.setVisible(True)

            self.content.checkOpenVino.setVisible(True)
            if self.content.use_openvino_flag:
                self.content.vino_pixmap.setVisible(True)
            else:
                self.content.vino_pixmap.setVisible(False)

            # Visible False
            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)
            self.content.checkLog.setVisible(False)
            self.content.checkResume.setVisible(False)
            self.content.checkUpdateWeight.setVisible(False)

            self.content.iSegmentation_Train_Check.setVisible(False)
            self.content.ImageTrainZCombo.setVisible(False)

            self.content.comboPreWeight.clear()
            if not self.content.use_openvino_flag:
                self.content.comboPreWeight.addItem("yolov8n.pt")
                self.content.comboPreWeight.addItem("yolov8s.pt")
                self.content.comboPreWeight.addItem("yolov8m.pt")
                self.content.comboPreWeight.addItem("yolov8l.pt")
                self.content.comboPreWeight.addItem("yolov8x.pt")

            else:
                self.content.comboPreWeight.addItem("yolov8n.onnx")
                self.content.comboPreWeight.addItem("yolov8s.onnx")
                self.content.comboPreWeight.addItem("yolov8m.onnx")
                self.content.comboPreWeight.addItem("yolov8l.onnx")
                self.content.comboPreWeight.addItem("yolov8x.onnx")

                self.content.editDevice.setVisible(True)

            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128.yaml"
            self.content.reload_weight_info()
            
            self.content.segmentation = False
            # self.content.lblSegmentation.setVisible(False)

        elif text == "iSegment":
            # Visible True
            self.content.YoloProcess = "iSegment"
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.checkCustom.setVisible(True)
            self.content.checkCustom.setEnabled(True)

            self.content.lblConF.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)
            self.content.SettingBtn.setVisible(True)

            self.content.checkOpenVino.setVisible(True)
            if self.content.use_openvino_flag:
                self.content.vino_pixmap.setVisible(True)
            else:
                self.content.vino_pixmap.setVisible(False)

            # Visible False
            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)

            self.content.checkLog.setVisible(False)
            self.content.checkResume.setVisible(False)
            self.content.checkUpdateWeight.setVisible(False)

            self.content.iSegmentation_Train_Check.setVisible(False)
            self.content.ImageTrainZCombo.setVisible(False)

            self.content.comboPreWeight.clear()
            if not self.content.use_openvino_flag:
                self.content.comboPreWeight.addItem("yolov8n-seg.pt")
                self.content.comboPreWeight.addItem("yolov8s-seg.pt")
                self.content.comboPreWeight.addItem("yolov8m-seg.pt")
                self.content.comboPreWeight.addItem("yolov8l-seg.pt")
                self.content.comboPreWeight.addItem("yolov8x-seg.pt")
            else:
                self.content.comboPreWeight.addItem("yolov8n-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8s-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8m-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8l-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8x-seg.onnx")

                self.content.editDevice.setVisible(True)

            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128.yaml"
            self.content.segmentation = True

        elif text == "Pose":

            # Visible True
            self.content.YoloProcess = "Pose"

            self.content.comboPreWeight.clear()
            self.content.comboPreWeight.addItem("YOLOv8n-pose.pt")
            self.content.comboPreWeight.addItem("YOLOv8s-pose.pt")
            self.content.comboPreWeight.addItem("YOLOv8m-pose.pt")
            self.content.comboPreWeight.addItem("YOLOv8l-pose.pt")
            self.content.comboPreWeight.addItem("YOLOv8x-pose.pt")
            self.content.comboPreWeight.addItem("YOLOv8x-pose-p6.pt")

            self.content.segmentation = False
        
        elif text == "Track":

            # Visible True
            self.content.YoloProcess = "Track"
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.checkCustom.setVisible(True)
            self.content.checkCustom.setEnabled(True)

            # self.content.comboGPU.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)
            # self.content.checkBGProcess.setVisible(True)
            self.content.lblConF.setVisible(True)
            self.content.SettingBtn.setVisible(True)

            # Visible False
            self.content.checkOpenVino.setVisible(False)
            self.content.vino_pixmap.setVisible(False)

            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)
            self.content.checkLog.setVisible(False)
            self.content.checkResume.setVisible(False)
            self.content.checkUpdateWeight.setVisible(False)

            self.content.ImageTrainZCombo.setVisible(False) 

        elif text == "Train":
            self.content.YoloProcess = "Train"

            # Visible True
            self.content.checkPreWeight.setChecked(True)
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(False)

            # Visible False
            self.content.checkCustom.setVisible(False)
            self.content.lblProjectPath.setVisible(False)

            self.content.browsFilesCustome.setVisible(False)
            # self.content.comboGPU.setVisible(False)
            self.content.editConF.setVisible(False) 
            # self.content.checkBGProcess.setVisible(False)
            self.content.lblConF.setVisible(False)

            self.content.checkOpenVino.setVisible(False)
            self.content.vino_pixmap.setVisible(False)

            self.content.editDevice.setVisible(False)
            self.content.SettingBtn.setVisible(False)

            self.content.lblEpoch.setVisible(True)
            self.content.Epoch_sizeEdit.setVisible(True)

            self.content.lblbatch_size.setVisible(True)
            self.content.batch_sizeEdit.setVisible(True)
            self.content.lblTrain.setVisible(True)
            self.content.ImageLabelEdit.setVisible(True)
            self.content.browsTargetFolder.setVisible(True)
            #self.content.lblSelectImage.setVisible(True)
            self.content.TrainObjectBtn.setVisible(True)
            # self.content.ResCombo.setVisible(True)

            self.content.checkLog.setVisible(True)
            # self.content.checkResume.setVisible(True)
            self.content.ImageTrainZCombo.setVisible(True) 

            self.content.iSegmentation_Train_Check.setVisible(True)

            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))

            self.content.labelAnimate.setVisible(False)
            self.content.movie.stop()

            self.content.AutoLoadYolo = False


    def onChangedPreWeight(self, text):
        self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/" + text
        print("\033[96m {}\033[00m".format("onChangedPreWeight : self.content.YoloPreWeightPath = "+ str(self.content.YoloWeightPath)))
        self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128.yaml"

    def SelectPreWieght(self, state):
        if state == QtCore.Qt.Checked:
            self.content.browsFilesCustome.setVisible(False)
            self.content.checkCustom.setChecked(False)
            self.content.comboPreWeight.setEnabled(True)

            self.content.selectWeight = "preweight"
            self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/" + str(self.content.comboPreWeight.currentText())
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128.yaml"

            # with open(self.content.dataset_name, "r", encoding="utf8") as stream:
            #     try:
            #         self.content.names = yaml.safe_load(stream)
            #         # print("self.names = ", self.names['names'])
            #     except yaml.YAMLError as exc:
            #         print(exc)

            if not self.content.use_openvino_flag:
                self.content.reload_weight_info()

            else:
                det_model = YOLO(self.content.re_path + "/AI_Module/yolov8/model_data/yolov8n.pt")
                self.content.label_map = det_model.model.names 

                self.det_ov_model = self.content.openvino_core.read_model(self.content.YoloWeightPath)
        
                device = self.content.editDevice.text()  # "GPU"
                if device != "CPU":
                    self.det_ov_model.reshape({0: [1, 3, 640, 640]})
                self.content.det_compiled_model = self.content.openvino_core.compile_model(self.det_ov_model, device)
                print("\033[93m {}\033[00m".format(str("SelectPreWieght --> det_compiled_model :"+ str(self.content.det_compiled_model))))

        else:
            self.content.checkCustom.setChecked(True)

    def SelectiSegPreweight(self, state):
        print("Select i-Segmentation Preweight for Training")
        self.content.comboPreWeight.clear()

        if state == QtCore.Qt.Checked:
            self.content.comboPreWeight.addItem("yolov8n-seg.pt")
            self.content.comboPreWeight.addItem("yolov8s-seg.pt")
            self.content.comboPreWeight.addItem("yolov8m-seg.pt")
            self.content.comboPreWeight.addItem("yolov8l-seg.pt")
            self.content.comboPreWeight.addItem("yolov8x-seg.pt")

            self.content.iSegmentation_Train = True
            self.content.comboPreWeight.setCurrentText("yolov8m-seg.pt")

            # self.content.YoloiSegWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/yolov5m-seg.pt"
            # print("onChangedPreWeight : self.content.YoloiSegWeightPath = ", self.content.YoloiSegWeightPath)    
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128-seg.yaml"

            # Force fix image size as 640
            self.content.ImageTrainZ = 640
            print("self.content.ImageTrainZ =", self.content.ImageTrainZ)

            # self.content.ResCombo.setCurrentText(str(self.content.ImageTrainZ))
            # self.content.ResCombo.setEnabled(False)

        else:
            # self.content.ResCombo.setEnabled(True)

            self.content.comboPreWeight.addItem("yolov8n.pt")
            self.content.comboPreWeight.addItem("yolov8s.pt")
            self.content.comboPreWeight.addItem("yolov8m.pt")
            self.content.comboPreWeight.addItem("yolov8l.pt")
            self.content.comboPreWeight.addItem("yolov8x.pt")

            self.content.iSegmentation_Train = False
            self.content.comboPreWeight.setCurrentText("yolov8m.pt")

            # self.content.YoloiSegWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/yolov8m.pt"
            # print("onChangedPreWeight : self.content.YoloiSegWeightPath = ", self.content.YoloiSegWeightPath)    
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov8/data/coco128-seg.yaml"

        print("self.content.iSegmentation_Train = ", self.content.iSegmentation_Train)

    def SelectCustom(self, state):
        if state == QtCore.Qt.Checked:
            self.content.browsFilesCustome.setVisible(True)
            self.content.checkPreWeight.setChecked(False)
            self.content.comboPreWeight.setEnabled(False)

            self.content.selectWeight = "custom"

            if len(self.content.ProjectLocation) > 0:
                self.content.dataset_name = self.content.ProjectLocation + "/custom_data.yaml"

            else:
                self.content.dataset_name = ""

            print("self.content.ProjectLocation : ", self.content.ProjectLocation)
            print("self.content.dataset_name : ", self.content.dataset_name)

            try:
                f = open(self.content.dataset_name)
                self.content.lblErrorWarning.setVisible(False)

            except FileNotFoundError:
                self.content.lblErrorWarning.setVisible(True)

        else:
            self.content.checkPreWeight.setChecked(True)

    def onChangedCPU(self, select):
        ...

    def onTrainingResChanged(self, select):
        self.content.ImageTrainZ = int(select)
        print("Check Trining Image Resolution : ", select)

    def SelectBG_Detection(self, state):
        if state == QtCore.Qt.Checked:
            self.start_bootProcess()

        else:
            self.Global.removeGlobal("img"+self.YOLOV8_ID)
            self.Global.setGlobal("run"+self.YOLOV8_ID, False)

            self.content.process_detect_bg = False
        
        print("self.content.process_detect_bg :", self.content.process_detect_bg)

    def SelectIntel_CPUAndGPU(self, state):
        if state == QtCore.Qt.Checked:
            self.content.vino_pixmap.setVisible(True)
            self.content.use_openvino_flag = True

            print("SelectIntel_CPUAndGPU --> YoloProcess :", self.content.YoloProcess)
            self.content.comboPreWeight.clear()

            if self.content.YoloProcess == "Detect":
                self.content.comboPreWeight.addItem("yolov8n.onnx")
                self.content.comboPreWeight.addItem("yolov8s.onnx")
                self.content.comboPreWeight.addItem("yolov8m.onnx")
                self.content.comboPreWeight.addItem("yolov8l.onnx")
                self.content.comboPreWeight.addItem("yolov8x.onnx")

            elif self.content.YoloProcess == "iSegment":
                self.content.comboPreWeight.addItem("yolov8n-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8s-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8m-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8l-seg.onnx")
                self.content.comboPreWeight.addItem("yolov8x-seg.onnx")

            print("len(self.content.YoloWeightPath) :", len(self.content.YoloWeightPath))
            print("SelectIntel_CPUAndGPU --> self.content.YoloWeightPath :", self.content.YoloWeightPath)

            check_preweight = self.content.YoloWeightPath.split(".")
            print("check_preweight[-1]:", check_preweight[-1])

            if self.content.selectWeight == "preweight":
                if check_preweight[-1] == "pt":
                    self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/yolov8n.onnx"
                    print("New SelectIntel_CPUAndGPU --> self.content.YoloWeightPath :", self.content.YoloWeightPath)

            elif self.content.selectWeight == "custom":
                det_model = YOLO(self.content.ProjectLocation + "/best.pt")
                self.content.label_map = det_model.model.names
                print("SelectIntel_CPUAndGPU self.label_map :", self.content.label_map)
                print("len(self.label_map):", len(self.content.label_map))

                if not os.path.isfile(self.content.ProjectLocation + "/best.onnx"):
                    print("\033[93m {}\033[00m".format("No file best.onnx !!! ---> Export onnx the model"))
                    # Export the model
                    det_model.export(format="openvino", dynamic=True, half=False)

                self.content.YoloWeightPath = self.content.ProjectLocation + "/best.onnx"
                print("\033[96m {}\033[00m".format("SelectIntel_CPUAndGPU use_vino --> YoloWeightPath :" + self.content.YoloWeightPath))

            self.content.editDevice.setVisible(True)

        else:
            self.content.vino_pixmap.setVisible(False)
            self.content.use_openvino_flag = False

            self.content.editDevice.setVisible(False)

            self.content.StartProcessDetect_flag = False
            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))

            self.content.comboPreWeight.clear()

            if self.content.YoloProcess == "Detect":
                self.content.comboPreWeight.addItem("yolov8n.pt")
                self.content.comboPreWeight.addItem("yolov8s.pt")
                self.content.comboPreWeight.addItem("yolov8m.pt")
                self.content.comboPreWeight.addItem("yolov8l.pt")
                self.content.comboPreWeight.addItem("yolov8x.pt")

                check_preweight = self.content.YoloWeightPath.split(".")
                print("check_preweight[-1]:", check_preweight[-1])

                if check_preweight[-1] == "onnx":
                    if self.content.selectWeight == "preweight":

                        self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/yolov8m.pt"
                        print("New SelectIntel_CPUAndGPU --> self.content.YoloWeightPath :", self.content.YoloWeightPath)

                        self.content.comboPreWeight.setCurrentText("yolov8m.pt")

                    elif self.content.selectWeight == "custom":
                        self.content.YoloWeightPath = self.content.ProjectLocation + "/best.pt"

            elif self.content.YoloProcess == "iSegment":
                self.content.comboPreWeight.addItem("yolov8n-seg.pt")
                self.content.comboPreWeight.addItem("yolov8s-seg.pt")
                self.content.comboPreWeight.addItem("yolov8m-seg.pt")
                self.content.comboPreWeight.addItem("yolov8l-seg.pt")
                self.content.comboPreWeight.addItem("yolov8x-seg.pt")

                check_preweight = self.content.YoloWeightPath.split(".")
                print("check_preweight[-1]:", check_preweight[-1])

                if check_preweight[-1] == "onnx":
                    self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov8/model_data/yolov8m-seg.pt"
                    print("New SelectIntel_CPUAndGPU --> self.content.YoloWeightPath :", self.content.YoloWeightPath)

                    self.content.comboPreWeight.setCurrentText("yolov8m-seg.pt")

            self.content.combo.setEnabled(True)
            self.content.comboPreWeight.setEnabled(True)

    # =============================================================================
    # Pose 
    # =============================================================================
    def kpts(self, kpts, image, shape=(640, 640), radius=10, kpt_line=True):
        # print("keypoints :", kpts)
        # print("kpts.shape :", kpts.shape)

        """
        Plot keypoints on the image.

        Args:
            kpts (tensor): Predicted keypoints with shape [17, 3]. Each keypoint has (x, y, confidence).
            shape (tuple): Image shape as a tuple (h, w), where h is the height and w is the width.
            radius (int, optional): Radius of the drawn keypoints. Default is 5.
            kpt_line (bool, optional): If True, the function will draw lines connecting keypoints
                                       for human pose. Default is True.

        Note: `kpt_line=True` currently only supports human pose plotting.
        """
        # if self.pil:
        #     # Convert to numpy first
        #     self.im = np.asarray(self.im).copy()
        nkpt, ndim = kpts.shape
        # print("nkpt :", nkpt)
        # print("ndim :", ndim)

        # pose_point = []

        is_pose = nkpt == 17 and ndim in {2, 3}
        kpt_line &= is_pose  # `kpt_line=True` for now only supports human pose plotting

        # pose_skeleton = []
        if kpt_line:
            ndim = kpts.shape[-1]
            for i, sk in enumerate(self.skeleton):
                pos1 = (int(kpts[(sk[0] - 1), 0]), int(kpts[(sk[0] - 1), 1]))
                pos2 = (int(kpts[(sk[1] - 1), 0]), int(kpts[(sk[1] - 1), 1]))

                if ndim == 3:
                    conf1 = kpts[(sk[0] - 1), 2]
                    conf2 = kpts[(sk[1] - 1), 2]
                    if conf1 < 0.5 or conf2 < 0.5:
                        continue
                if pos1[0] % shape[1] == 0 or pos1[1] % shape[0] == 0 or pos1[0] < 0 or pos1[1] < 0:
                    continue
                if pos2[0] % shape[1] == 0 or pos2[1] % shape[0] == 0 or pos2[0] < 0 or pos2[1] < 0:
                    continue

                self.pose_skeleton.append({i:(pos1, pos2)})
                image = cv2.line(image, pos1, pos2, [int(x) for x in self.limb_color[i]], thickness=2, lineType=cv2.LINE_AA)

        for i, k in enumerate(kpts):
            color_k = [int(x) for x in self.kpt_color[i]] if is_pose else colors(i)
            x_coord, y_coord = k[0], k[1]
            if x_coord % shape[1] != 0 and y_coord % shape[0] != 0:
                if len(k) == 3:
                    conf = k[2]
                    if conf < 0.5:
                        continue

                self.pose_point.append({i:(int(x_coord), int(y_coord))})
                image = cv2.circle(image, (int(x_coord), int(y_coord)), radius, color_k, -1, lineType=cv2.LINE_AA)
                image = cv2.putText(image  , str(i), (int(x_coord) - 6, int(y_coord) + 5), cv2.FONT_HERSHEY_DUPLEX, 0.4, ( 206, 0, 255 ), 1)

        return image

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """

        results = self.content.model.predict(source=frame, show=False, verbose=False)
        return results

    def plot_boxes(self, results, frame, conf_thres):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """

        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}
        frame = cv2.resize(frame, (self.input_payload['img_w'],self.input_payload['img_h']))

        # print("plot_boxes_results :", results)

        for r in results:
            bboxes = r.boxes  # Boxes object for bbox outputs
            # print("len(bboxes) :", len(bboxes))

            if len(bboxes) > 0:
                # obj_found = len(bboxes)

                for boxs in bboxes:

                    # print("boxs.cls.tolist()[0] :", int(boxs.cls.tolist()[0]))
                    # # print("boxs.conf.tolist()[0] :", boxs.conf.tolist()[0])
                    classid = int(boxs.cls.tolist()[0])
                    # print("classid :", classid)

                    label = self.content.names['names'][classid]
                    conf = int(boxs.conf.tolist()[0]*100)

                    label_display = label + " : " + str(conf) + " %"

                    if conf > int(conf_thres * 100):

                        obj_found += 1

                        # Convert tensor to list
                        x1, y1, x2, y2 = int(boxs.xyxy.tolist()[0][0]), int(boxs.xyxy.tolist()[0][1]), int(boxs.xyxy.tolist()[0][2]), int(boxs.xyxy.tolist()[0][3])
                        yolo_boxes.append({'x1':int(x1), 'y1':int(y1), 'x2':int(x2), 'y2': int(y2), 'score': int(conf), 'obj': self.content.names['names'][classid]})

                        frame = cv2.rectangle(frame,(x1,y1),(x2,y2), self.content.colorList[classid], thickness=1,lineType=cv2.LINE_AA)
                        frame = cv2.rectangle(frame,(x1, y1 - 15),(x1 + len(label_display)*6,y1), self.content.colorList[classid], -1)
                        frame = cv2.putText(frame, label_display, (x1, y1-5),0, 0.3, (255,255,255), thickness=1,lineType=cv2.LINE_AA)

        # frame = cv2.resize(frame, (1280,800), interpolation = cv2.INTER_AREA)

        return obj_found, yolo_boxes, frame
            
    def detect_yolov8(self, image, conf_thres):

        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}

        try:
            results = self.score_frame(image)
            # print("results :", results)
        
            obj_found, yolo_boxes, image = self.plot_boxes(results, image , conf_thres)
        except:
            # print("\033[91m {}\033[00m".format("YoloV8 : No weight file loaded !!!"))  
            self.content.lblErrorWarning.setVisible(True)  

        return obj_found, yolo_boxes, image
    
    def detect_yolov8_iSeg(self, image, conf_thres):
        results = self.content.model.predict(source=image, verbose=False)
        frame = results[0].plot()

        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}

        for r in results:
            bboxes = r.boxes  # Boxes object for bbox outputs
            
            if len(bboxes) > 0:
                # obj_found = len(bboxes)

                for boxs in bboxes:

                    classid = int(boxs.cls.tolist()[0])
                    label = self.content.names['names'][classid]
                    conf = int(boxs.conf.tolist()[0]*100)

                    label_display = label + " : " + str(conf) + " %"

                    if conf > int(conf_thres * 100):

                        obj_found += 1

                        # Convert tensor to list
                        x1, y1, x2, y2 = int(boxs.xyxy.tolist()[0][0]), int(boxs.xyxy.tolist()[0][1]), int(boxs.xyxy.tolist()[0][2]), int(boxs.xyxy.tolist()[0][3])
                        yolo_boxes.append({'x1':int(x1), 'y1':int(y1), 'x2':int(x2), 'y2': int(y2), 'score': int(conf), 'obj': self.content.names['names'][classid]})

                        frame = cv2.rectangle(frame,(x1,y1),(x2,y2), self.content.colorList[classid], thickness=1,lineType=cv2.LINE_AA)
                        frame = cv2.rectangle(frame,(x1, y1 - 15),(x1 + len(label_display)*6,y1), self.content.colorList[classid], -1)
                        frame = cv2.putText(frame, label_display, (x1, y1-5),0, 0.3, (255,255,255), thickness=1,lineType=cv2.LINE_AA)

        return obj_found, yolo_boxes, frame
    
    def track_yolov8(self, frame, conf_thres):
        
        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}
        class_id = 0
        conf = 0

        # initialize the list of bounding boxes and confidences
        results = []

        ######################################
        # DETECTION
        ######################################
        detections = self.content.model(frame, verbose=False)[0]

        # loop over the detections
        for data in detections.boxes.data.tolist():
            # extract the confidence (i.e., probability) associated with the prediction
            confidence = data[4]
            conf = int(confidence*100)

            # filter out weak detections by ensuring the 
            # confidence is greater than the minimum confidence
            if float(confidence) < conf_thres:
                continue


            # if conf > int(conf_thres * 100):

            obj_found += 1

            # if the confidence is greater than the minimum confidence,
            # get the bounding box and the class id
            xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            class_id = int(data[5])
            # add the bounding box (x, y, w, h), confidence and class id to the results list
            results.append([[xmin, ymin, xmax - xmin, ymax - ymin], confidence, class_id])

            label = self.content.names['names'][class_id]
            label_display = label + " : " + str(conf) + " %"

            frame = cv2.rectangle(frame,(xmin,ymin),(xmax,ymax), self.content.colorList[class_id], thickness=1,lineType=cv2.LINE_AA)
            frame = cv2.rectangle(frame,(xmin, ymin - 15),(xmin + len(label_display)*6,ymin), self.content.colorList[class_id], -1)
            frame = cv2.putText(frame, label_display, (xmin, ymin-5),0, 0.3, (255,255,255), thickness=1,lineType=cv2.LINE_AA)

        ######################################
        # TRACKING
        ######################################

        # update the tracker with the new detections
        tracks = self.content.tracker.update_tracks(results, frame=frame)
        # loop over the tracks
        for track in tracks:
            # if the track is not confirmed, ignore it
            if not track.is_confirmed():
                continue

            # get the track id and the bounding box
            track_id = track.track_id
            ltrb = track.to_ltrb()
            # print("ltrb :", ltrb)

            xmin, ymin, xmax, ymax = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])

        
            # frame = cv2.rectangle(frame,(xmin,ymin),(xmax,ymax), (255,0,0), thickness=1,lineType=cv2.LINE_AA)
            # frame = cv2.rectangle(frame,(xmin, ymin - 15),(xmin + 30,ymin), self.content.colorList[class_id], -1)
            # frame = cv2.putText(frame, label_display, (xmin, ymin-5),0, 0.3, (255,255,255), thickness=1,lineType=cv2.LINE_AA)

            yolo_boxes.append({'x1':int(xmin), 'y1':int(ymin), 'x2':int(xmax), 'y2': int(ymax), 'score': int(conf), 'obj': self.content.names['names'][class_id], 'id':track_id})
            frame = cv2.putText(frame, str('id: ' + track_id), (xmin+3, ymin+10),0, 0.3, (0,255,0), thickness=1,lineType=cv2.LINE_AA)
        
        return obj_found, yolo_boxes, frame


    #=========================================================================
    # OpenVino Process
    def plot_one_box(self, box:np.ndarray, img:np.ndarray, color:Tuple[int, int, int] = None, mask:np.ndarray = None, label:str = None, line_thickness:int = 5):
        """
        Helper function for drawing single bounding box on image
        Parameters:
            x (np.ndarray): bounding box coordinates in format [x1, y1, x2, y2]
            img (no.ndarray): input image
            color (Tuple[int, int, int], *optional*, None): color in BGR format for drawing box, if not specified will be selected randomly
            mask (np.ndarray, *optional*, None): instance segmentation mask polygon in format [N, 2], where N - number of points in contour, if not provided, only box will be drawn
            label (str, *optonal*, None): box label string, if not provided will not be provided as drowing result
            line_thickness (int, *optional*, 5): thickness for box drawing lines
        """
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = color or [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
        if mask is not None:
            image_with_mask = img.copy()
            mask
            cv2.fillPoly(image_with_mask, pts=[mask.astype(int)], color=color)
            img = cv2.addWeighted(img, 0.5, image_with_mask, 0.5, 1)
        return img

    def openvino_draw_results(self, results:Dict, source_image:np.ndarray, label_map:Dict, conf_thres:float):
        """
        Helper function for drawing bounding boxes on image
        Parameters:
            image_res (np.ndarray): detection predictions in format [x1, y1, x2, y2, score, label_id]
            source_image (np.ndarray): input image for drawing
            label_map; (Dict[int, str]): label_id to class name mapping
        Returns:
            
        """

        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}
        
        boxes = results["det"]
        masks = results.get("segment")
        h, w = source_image.shape[:2]
        for idx, (*xyxy, conf, lbl) in enumerate(boxes):

            # obj_found = len(boxes)

            label = f'{label_map[int(lbl)]}' + " : " + str(int(conf*100)) + " %"

            if conf > conf_thres:
                mask = masks[idx] if masks is not None else None
                source_image = self.plot_one_box(xyxy, source_image, mask=mask, label=label, color=colors(int(lbl)), line_thickness=1)

                list_xyxy = [int(t) for t in xyxy]

                # print(list_xyxy)
                
                # Convert tensor to list
                x1, y1, x2, y2 = int(list_xyxy[0]), int(list_xyxy[1]), int(list_xyxy[2]), int(list_xyxy[3])
                yolo_boxes.append({'x1':int(x1), 'y1':int(y1), 'x2':int(x2), 'y2': int(y2), 'score': f'{conf:.2f}', 'obj': label_map[int(lbl)]})

                obj_found += 1

        return obj_found, yolo_boxes, source_image

    def openvino_letterbox(self, img: np.ndarray, new_shape:Tuple[int, int] = (640, 640), color:Tuple[int, int, int] = (114, 114, 114), auto:bool = False, scale_fill:bool = False, scaleup:bool = False, stride:int = 32):
        """
        Resize image and padding for detection. Takes image as input, 
        resizes image to fit into new shape with saving original aspect ratio and pads it to meet stride-multiple constraints
        
        Parameters:
        img (np.ndarray): image for preprocessing
        new_shape (Tuple(int, int)): image size after preprocessing in format [height, width]
        color (Tuple(int, int, int)): color for filling padded area
        auto (bool): use dynamic input size, only padding for stride constrins applied
        scale_fill (bool): scale image to fill new_shape
        scaleup (bool): allow scale image if it is lower then desired input size, can affect model accuracy
        stride (int): input padding stride
        Returns:
        img (np.ndarray): image after preprocessing
        ratio (Tuple(float, float)): hight and width scaling ratio
        padding_size (Tuple(int, int)): height and width padding size
        
        
        """
        # Resize and pad image while meeting stride-multiple constraints
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better test mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scale_fill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return img, ratio, (dw, dh)

    def preprocess_image(self, img0: np.ndarray):
        """
        Preprocess image according to YOLOv8 input requirements. 
        Takes image in np.array format, resizes it to specific size using letterbox resize and changes data layout from HWC to CHW.
        
        Parameters:
        img0 (np.ndarray): image for preprocessing
        Returns:
        img (np.ndarray): image after preprocessing
        """
        # resize
        img = self.openvino_letterbox(img0)[0]
        
        # Convert HWC to CHW
        img = img.transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        return img
    
    def image_to_tensor(self, image:np.ndarray):
        """
        Preprocess image according to YOLOv8 input requirements. 
        Takes image in np.array format, resizes it to specific size using letterbox resize and changes data layout from HWC to CHW.
        
        Parameters:
        img (np.ndarray): image for preprocessing
        Returns:
        input_tensor (np.ndarray): input tensor in NCHW format with float32 values in [0, 1] range 
        """
        input_tensor = image.astype(np.float32)  # uint8 to fp32
        input_tensor /= 255.0  # 0 - 255 to 0.0 - 1.0
        
        # add batch dimension
        if input_tensor.ndim == 3:
            input_tensor = np.expand_dims(input_tensor, 0)
        return input_tensor
    
    def postprocess(
        self,
        pred_boxes:np.ndarray, 
        input_hw:Tuple[int, int], 
        orig_img:np.ndarray, 
        min_conf_threshold:float = 0.25, 
        nms_iou_threshold:float = 0.7, 
        agnosting_nms:bool = False, 
        max_detections:int = 300,
        pred_masks:np.ndarray = None,
        retina_mask:bool = False
        ):
        """
        YOLOv8 model postprocessing function. Applied non maximum supression algorithm to detections and rescale boxes to original image size
        Parameters:
            pred_boxes (np.ndarray): model output prediction boxes
            input_hw (np.ndarray): preprocessed image
            orig_image (np.ndarray): image before preprocessing
            min_conf_threshold (float, *optional*, 0.25): minimal accepted confidence for object filtering
            nms_iou_threshold (float, *optional*, 0.45): minimal overlap score for removing objects duplicates in NMS
            agnostic_nms (bool, *optiona*, False): apply class agnostinc NMS approach or not
            max_detections (int, *optional*, 300):  maximum detections after NMS
            pred_masks (np.ndarray, *optional*, None): model ooutput prediction masks, if not provided only boxes will be postprocessed
            retina_mask (bool, *optional*, False): retina mask postprocessing instead of native decoding
        Returns:
        pred (List[Dict[str, np.ndarray]]): list of dictionary with det - detected boxes in format [x1, y1, x2, y2, score, label] and segment - segmentation polygons for each element in batch
        """
        nms_kwargs = {"agnostic": agnosting_nms, "max_det":max_detections}
        # if pred_masks is not None:
        #     nms_kwargs["nm"] = 32
        preds = ops.non_max_suppression(
            torch.from_numpy(pred_boxes),
            min_conf_threshold,
            nms_iou_threshold,
            nc=len(self.content.label_map),
            **nms_kwargs
        )
        results = []
        proto = torch.from_numpy(pred_masks) if pred_masks is not None else None

        for i, pred in enumerate(preds):
            shape = orig_img[i].shape if isinstance(orig_img, list) else orig_img.shape
            if not len(pred):
                results.append({"det": [], "segment": []})
                continue
            if proto is None:
                pred[:, :4] = ops.scale_boxes(input_hw, pred[:, :4], shape).round()
                results.append({"det": pred})
                continue
            if retina_mask:
                pred[:, :4] = ops.scale_boxes(input_hw, pred[:, :4], shape).round()
                masks = ops.process_mask_native(proto[i], pred[:, 6:], pred[:, :4], shape[:2])  # HWC
                segments = [ops.scale_segments(input_hw, x, shape, normalize=False) for x in ops.masks2segments(masks)]
            else:
                masks = ops.process_mask(proto[i], pred[:, 6:], pred[:, :4], input_hw, upsample=True)
                pred[:, :4] = ops.scale_boxes(input_hw, pred[:, :4], shape).round()
                segments = [ops.scale_segments(input_hw, x, shape, normalize=False) for x in ops.masks2segments(masks)]
            results.append({"det": pred[:, :6].numpy(), "segment": segments})
        return results

    def openvino_detect(self, image:np.ndarray, model:Model):
        """
        OpenVINO YOLOv8 model inference function. Preprocess image, runs model inference and postprocess results using NMS.
        Parameters:
            image (np.ndarray): input image.
            model (Model): OpenVINO compiled model.
        Returns:
            detections (np.ndarray): detected boxes in format [x1, y1, x2, y2, score, label]
        """
        num_outputs = len(model.outputs)
        preprocessed_image = self.preprocess_image(image)
        input_tensor = self.image_to_tensor(preprocessed_image)
        result = model(input_tensor)
        boxes = result[model.output(0)]
        masks = None
        if num_outputs > 1:
            masks = result[model.output(1)]
        input_hw = input_tensor.shape[2:]
        detections = self.postprocess(pred_boxes=boxes, input_hw=input_hw, orig_img=image, pred_masks=masks)
        return detections
    

    #=========================================================================
    def SelectShowLog(self, state):
        if state == QtCore.Qt.Checked:
            self.content.showlog = True

            YoloPreWeightPath = self.content.YoloWeightPath
            # if self.content.iSegmentation_Train:
            #     YoloPreWeightPath = self.content.YoloiSegWeightPath

            self.AI_TrainingYolo = TraingYolo(self.content, YoloPreWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()),
                                            int(self.content.Epoch_sizeEdit.text()), self.content.iSegmentation_Train, self.content.resume, self.content.Continue_ImproveWeight, self.content.ImageTrainZ, solution="Log")
            self.AI_TrainingYolo.show()
        else:
            self.content.showlog = False

    def SelectResumeTraining(self, state):
        if state == QtCore.Qt.Checked:
            self.content.resume = True

            self.content.Continue_ImproveWeight = False
            self.content.checkUpdateWeight.setChecked(False)
        else:
            self.content.resume = False

    def SelectWeightUpdateTraining(self, state):
        if state == QtCore.Qt.Checked:
            self.content.Continue_ImproveWeight = True

            self.content.resume = False
            self.content.checkResume.setChecked(False)

        else:
            self.content.Continue_ImproveWeight = False

    def trainingObject(self):
        self.content.TrainObjectBtn.setEnabled(False)
        # self.content.ResCombo.setEnabled(False)

        YoloPreWeightPath = self.content.YoloWeightPath
        # if self.content.iSegmentation_Train:
        #     YoloPreWeightPath = self.content.YoloiSegWeightPath

        self.AI_TrainingYolo = TraingYolo(self.content, YoloPreWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()),
                                            int(self.content.Epoch_sizeEdit.text()), self.content.iSegmentation_Train, self.content.resume, self.content.Continue_ImproveWeight, self.content.ImageTrainZ, solution="Train")
 
        self.AI_TrainingYolo.show()

        # CacheTraining = self.content.re_path + '/Database/'       #boxitems
        # print("Yolo V5 CacheTraining : ", CacheTraining)
        # with open(CacheTraining + "yolo_cache.txt", 'w') as f:
        #     f.writelines("True")

        #training_app = YoloV5Traing(self.content.YoloWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()))
        #training_app.show()

        #training_app.exec_()
