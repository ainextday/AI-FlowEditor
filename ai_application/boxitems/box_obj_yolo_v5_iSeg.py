from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import os

import numpy as np
import time
from datetime import datetime, timedelta

# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
from pathlib import Path

import torch
import torch.distributed as dist
import torch.backends.cudnn as cudnn
import cv2

from ai_application.AI_Module.yolov5.models.common import DetectMultiBackend

from ai_application.AI_Module.yolov5.utils.general import (check_img_size, non_max_suppression, scale_boxes)
                                                         
from ai_application.AI_Module.yolov5.utils.plots import Annotator, colors
from ai_application.AI_Module.yolov5.utils.torch_utils import select_device

from ai_application.AI_Module.yolov5.utils.augmentations import letterbox
from ai_application.AI_Module.yolov5.utils.segment.general import process_mask

# from ai_application.Database.GlobalVariable import *

import ast
import shutil
import psutil
import glob

import random
import json
import yaml

import GPUtil
import sys
import pkg_resources

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId

from win32api import GetSystemMetrics

LOCAL_RANK = int(os.getenv('LOCAL_RANK', -1))  # https://pytorch.org/docs/stable/elastic/run.html
RANK = int(os.getenv('RANK', -1))
WORLD_SIZE = int(os.getenv('WORLD_SIZE', 1))

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/"

@torch.no_grad()
class ObjectDetect(QDMNodeContentWidget):
    def initUI(self):
        
        self.Path = os.path.dirname(os.path.abspath(__file__))
        print("Object Detect self.Path = " , self.Path)
        self.save_icon = self.Path + "/icons/icons_save.png"
        yolo_logo = self.Path + "/icons/icons_yolov5.png"
        self.train_icon = self.Path + "/icons/icons_train.png"

        self.animate_movie = self.Path + "/icons/icons_dane_re.gif"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"
        

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
        # self.combo.addItem("Track")
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
        self.comboPreWeight.addItem("yolov5s.pt")
        self.comboPreWeight.addItem("yolov5m.pt")
        self.comboPreWeight.addItem("yolov5l.pt")
        self.comboPreWeight.addItem("yolov5x.pt")

        self.comboPreWeight.setGeometry(100,55,95,20)
        self.comboPreWeight.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.comboPreWeight.setCurrentText("yolov5m.pt")

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
        self.browsFilesCustome.setEnabled(False)


        self.iSegmentation_Train_Check = QCheckBox("i-Segmentation",self)
        self.iSegmentation_Train_Check.setGeometry(10,80,120,20)
        self.iSegmentation_Train_Check.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.iSegmentation_Train_Check.setVisible(False)
        self.iSegmentation_Train_Check.setChecked(False)

        self.iSegmentation_Train = False

        self.SwitchDetect = QPushButton(self)
        self.SwitchDetect.setGeometry(160,5,37,20)
        self.SwitchDetect.setIcon(QIcon(self.off_icon))
        self.SwitchDetect.setIconSize(QtCore.QSize(37,20))
        self.SwitchDetect.setStyleSheet("background-color: transparent; border: 0px;")  


        self.lblGPU = QLabel("GPU:" , self)
        self.lblGPU.setAlignment(Qt.AlignLeft)
        self.lblGPU.setGeometry(100,118,30,30)
        self.lblGPU.setStyleSheet("font-size:6pt;")

        self.NOF_GPU = GPUtil.getAvailable()
        print("self.NOF_GPU = ", self.NOF_GPU)

        self.comboGPU = QComboBox(self)
        for i in range(len(self.NOF_GPU)):
            self.comboGPU.addItem(str(self.NOF_GPU[i]))

        self.comboGPU.addItem("CPU")

        self.comboGPU.setGeometry(130,115,63,20)
        self.comboGPU.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : lightblue; font-size:7pt;"
                                   "}") 

        self.device = 'cpu' #select_device(0)
        if len(self.NOF_GPU) > 0:
            self.comboGPU.setCurrentText(str(self.NOF_GPU[0]))
            self.device = 0
        else:
            self.comboGPU.setCurrentText("cpu")

        self.lblConF = QLabel("Conf:" , self)
        self.lblConF.setAlignment(Qt.AlignLeft)
        self.lblConF.setGeometry(100,145,30,30)
        self.lblConF.setStyleSheet("font-size:6pt;")

        self.editConF = QLineEdit("0.25", self)
        self.editConF.setAlignment(Qt.AlignLeft)
        self.editConF.setGeometry(129,140,65,20)
        self.editConF.setPlaceholderText("Confident")
        self.editConF.setStyleSheet("font-size:8pt;")

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

        self.ImageTrainZ = 640

        self.ResCombo = QComboBox(self)
        self.ResCombo.addItem("640")
        self.ResCombo.addItem("1280")
        self.ResCombo.addItem("1920")
        self.ResCombo.addItem("2560")
        self.ResCombo.setGeometry(130,165,63,25)
        self.ResCombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33DDFF; font-size:6pt;"
                                   "}") 
        # self.ResCombo.setVisible(False)

        self.TrainObjectBtn = QPushButton(self)
        self.TrainObjectBtn.setGeometry(160, 190, 35, 35)
        self.TrainObjectBtn.setIconSize(QtCore.QSize(35,35))
        self.TrainObjectBtn.setIcon(QIcon(self.train_icon))
        self.TrainObjectBtn.setVisible(False)
        self.TrainObjectBtn.setEnabled(False)

        self.checkLog = QCheckBox("",self)
        self.checkLog.setGeometry(100,168,50,20)
        self.checkLog.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.checkLog.setChecked(True)
        self.showlog = True

        #====================================================
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

        self.YoloProcess = "Detect"

        self.re_path = self.Path[0:-9]
        
        # replace all instances of '\\' (old) with '/' (new)
        self.re_path = self.re_path.replace("\\", "/" )
        # print("self.re_path:", self.re_path)

        self.YoloWeightPath = self.re_path + "/AI_Module/yolov5/model_data/yolov5m.pt"
        print("self.YoloWeightPath = ", self.YoloWeightPath)

        self.dataset_name = self.re_path + "/AI_Module/yolov5/data/coco128.yaml"
        print("self.dataset_name = ", self.dataset_name)

        self.selectWeight = "preweight"

        self.YoloiSegWeightPath = self.re_path + "/AI_Module/yolov5/model_data/yolov5n-seg.pt"

        self.StartProcessDetect_flag = False
        self.AutoLoadYolo = False

        self.model = None #DetectMultiBackend(self.YoloWeightPath, device=self.device, dnn=False, data=self.dataset_name, fp16=False)
        self.stride = None
        self.names = None 
        self.pt = None 
        
        #self.model.stride, self.model.names, self.model.pt
        #print("self.names = ", self.names)

        self.imgsz = None
        #check_img_size((640, 640), s=self.stride)  # check image size

        self.ProjectLocation = ""
        self.device_usage = None

        self.Input_ImageLable_DIR = ""
        self.ProjectTrainingLocation = ""

        self.batch_size = self.batch_sizeEdit.text()

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msg.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msg.setStandardButtons(QMessageBox.Ok)

        self.ready_for_training = False
        self.NOF_Image = 0
        self.file_imgname_list = []

        self.NOF_Txt = 0
        self.file_txtname_list = []

        self.segmentation = False

        self.first_startTrain = False
        self.startime = None

    def serialize(self):
        res = super().serialize()
        res['YoloProcess'] = self.YoloProcess
        res['autoloadyolo'] = self.AutoLoadYolo
        res['selectweight'] = self.selectWeight

        res['yoloweight_path'] = self.YoloWeightPath
        res['isegweight_path'] = self.YoloiSegWeightPath
        res['dataset_name'] = self.dataset_name
        res['device'] = self.device
        res['stride'] = str(self.stride)
        res['names'] = str(self.names)
        res['pt'] = self.pt
        res['conf'] = self.editConF.text()
        res['project_locate'] = self.ProjectLocation
        res['imagelabel_locate'] = self.Input_ImageLable_DIR
        res['loadimage_label'] = self.ProjectTrainingLocation
        res['batch_size'] = self.batch_sizeEdit.text()
        res['epoch_size'] = self.Epoch_sizeEdit.text()
        res['ready_training'] = self.ready_for_training
        res['imagez'] = self.ImageTrainZ
        res['segmentation'] = self.segmentation

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

                        if not self.segmentation:
                            self.YoloWeightPath = self.ProjectLocation + "/best.pt"
                        else:
                            self.YoloiSegWeightPath = self.ProjectLocation + "/best.pt"

                        self.dataset_name = self.ProjectLocation + "/custom_data.yaml"

                        self.combo.setEnabled(False)
                        self.comboPreWeight.setEnabled(False)

            if 'conf' in data:
                self.editConF.setText(data['conf'])

            if 'imagez' in data:
                self.ImageTrainZ = data['imagez']
                self.ResCombo.setCurrentText(str(self.ImageTrainZ))

            if 'project_locate' in data:
                self.ProjectLocation = data['project_locate']


            if 'autoloadyolo' in data:
                self.AutoLoadYolo = data['autoloadyolo']
                print('autoloadyolo = ', self.AutoLoadYolo)

                if self.AutoLoadYolo:
                    if 'YoloProcess' in data:
                        self.YoloProcess = data['YoloProcess']
                        self.combo.setCurrentText(self.YoloProcess)

                    if self.selectWeight == "preweight":
                        if not self.segmentation:
                            self.YoloWeightPath = data['yoloweight_path']#self.re_path + "/AI_Module/yolov5/model_data/yolov5m.pt"
                            self.dataset_name = self.re_path + "/AI_Module/yolov5/data/coco128.yaml"

                        else:
                            self.YoloiSegWeightPath = data['isegweight_path']
                            self.dataset_name = self.re_path + "/AI_Module/yolov5/data/coco128-seg.yaml"

                            self.combo.setEnabled(False)
                            self.comboPreWeight.setEnabled(False)

                    else:
                        if 'yoloweight_path' in data:
                            self.YoloWeightPath = data['yoloweight_path']

                        if 'dataset_name' in data:
                            self.dataset_name = data['dataset_name']

                    if 'device' in data:
                        self.device = data['device']

                    if 'stride' in data:
                        self.stride = int(data['stride'])

                    if 'names' in data:
                        self.names = ast.literal_eval(data['names'])

                    if 'pt' in data:
                        self.pt = data['pt']

                    self.device_usage = select_device(self.device)
                    print("self.device_usage = ", self.device_usage)
                    print("self.YoloWeightPath = ", self.YoloWeightPath)
                    print("self.dataset_name = ", self.dataset_name)

                    if not self.segmentation:
                        WeightPath = self.YoloWeightPath
                    
                    else:
                        WeightPath = self.YoloiSegWeightPath

                    self.model = DetectMultiBackend(WeightPath, device=self.device_usage, dnn=False, data=self.dataset_name, fp16=False)
                    self.imgsz = check_img_size((self.ImageTrainZ, self.ImageTrainZ), s=self.stride)  # check image size
                    print("===> New Image Size : ", self.imgsz)

                    self.SwitchDetect.setIcon(QIcon(self.on_icon))

                    self.labelAnimate.setVisible(True)
                    self.movie.start()

                    self.StartProcessDetect_flag = True

                else:
                    self.SwitchDetect.setIcon(QIcon(self.off_icon))

                    self.labelAnimate.setVisible(False)
                    self.movie.stop()

                    self.StartProcessDetect_flag = False

            if 'imagelabel_locate' in data:
                self.Input_ImageLable_DIR = data['imagelabel_locate']
                self.ImageLabelEdit.setText(self.Input_ImageLable_DIR)

            if 'loadimage_label' in data:
                self.ProjectTrainingLocation = data['loadimage_label']

            if 'batch_size' in data:
                self.batch_size = data['batch_size']
                self.batch_sizeEdit.setText(self.batch_size)

            if 'epoch_size' in data:
                self.Epoch_sizeEdit.setText(str(data['epoch_size']))

            if 'ready_training' in data:
                self.ready_for_training = data['ready_training']
                if self.ready_for_training:
                    self.lblSelectImage.setText("Ready For Training !!")
                    self.lblSelectImage.setVisible(True)

                    self.TrainObjectBtn.setEnabled(True)

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
    # Browse AI Custom weight
    def browseSlot(self):
        self.ProjectLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.ProjectLocation)

        self.lblProjectPath.setText(self.ProjectLocation)

        # Check if Segmentation
        self.dataset_name = self.ProjectLocation + "/custom_data.yaml"

        isegmet = {}
        with open(self.dataset_name , "r") as stream:
            try:
                isegmet = yaml.safe_load(stream)
                if 'isegment' in isegmet:
                    print("isegment = ", isegmet['isegment'])
                    
            except yaml.YAMLError as exc:
                print(exc)

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

        print("NOF_JPGImage = ", self.NOF_Image)

        #print("self.file_imgname_list = ", self.file_imgname_list)

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

            OUTPUT_DIR = self.Input_ImageLable_DIR + "_WeightYoloV5"
            if self.iSegmentation_Train:
                OUTPUT_DIR = self.Input_ImageLable_DIR + "_WeightYoloV5Seg"

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

            Percent_OfValid = 3
        
            ten_of_NOF_Image = int(self.NOF_Image/Percent_OfValid)
            print("ten_of_NOF_Image = ", ten_of_NOF_Image)
            for i in range(ten_of_NOF_Image):
                no_random = random.randint(1, self.NOF_Image)
                if no_random not in random_list:
                    random_list.append(no_random)

            #print("10% of random_list = ", random_list)
            print("len(random_list) = ", len(random_list))

            for i in range(len(random_list)):
                shutil.copy(self.file_imgname_list[random_list[i]], self.ProjectTrainingLocation + "/images/val")

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
                #     shutil.copy(self.file_txtname_list[random_list[i]], self.ProjectTrainingLocation + "/labels/val")

                shutil.copy(self.file_imgname_list[random_list[i]][0:-3] + 'txt', self.ProjectTrainingLocation + "/labels/val")
                print("shutil.copy(", self.file_imgname_list[random_list[i]][0:-3] + 'txt', ") to ", self.ProjectTrainingLocation, "/labels/val")

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
                        list_name.pop(len(list_name)-1)

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

                    self.lblSelectImage.setVisible(True)
                    #Make custom_data.yaml
                    self.ready_for_training = True
                    self.TrainObjectBtn.setEnabled(True)
                    self.ResCombo.setEnabled(True)
                    
                else:
                    print("No file classes.txt")
                    self.msg.setText(
                        "1. No classes.txt in folder " + self.ProjectTrainingLocation+ "\n" 
                        "2. Please copy from Image Label to folder")
                    retval = self.msg.exec_()
                    print("retval :", retval)

            else:
                print("Number of XXX.png not equal Number of XXX.txt")
                self.msg.setText("Number of XXX.png not equal Number of XXX.txt")
                retval = self.msg.exec_()
                print("retval :", retval)

        else:
            print("No. of Image not equal No. of txt\nNo Data in ", self.ProjectTrainingLocation)
            self.msg.setText("No. of Image not equal No. of txt\n" 
                        + "Image = " + str(self.NOF_Image) + "\ntxt = " + str(self.NOF_Txt))
            retval = self.msg.exec_()
            print("retval :", retval)
            

#============================================================================================
# self.ui.TlabelTraining, self.ui.TlabelLoss, self.ui.NumberProgress, self.ui.progress_bar, self.ui.CPUUsageLabel, self.ui.RAMUsageLabel
#============================================================================================
class Ui_YoloV5Training_MainWindow(object):
    def setupUi(self, MainWindow):

        self.MainWindow = MainWindow

        self.Screen_Width = GetSystemMetrics(0)   
        print("Screen Width =", self.Screen_Width)

        self.title = "AI Training Yolo V5"
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

        self.TlabelLoss = QTextEdit("Start Training Yolo V5" , self.MainWindow)
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
        self.ProgressLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:9pt;color:lightblue; border: 1px solid white; border-radius: 4%")

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
        self.EstDoneLabel.setStyleSheet("background-color: rgba(85, 149, 193, 225); font-size:8pt;color:yellow; border: 1px solid white; border-radius: 2%")

        self.EstFinishLabel = QLabel(self.MainWindow)
        self.EstFinishLabel.setGeometry(680,775,290,40)
        self.EstFinishLabel.setStyleSheet("background-color: rgba(119, 222, 241, 225); font-size:14pt;color:yellow; border: 1px solid white; border-radius: 2%")


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
        print("root_path : ", root_path)

        shell.AppActivate(self.get_pid())
        shell.SendKeys("cd \ {ENTER}")
        shell.SendKeys("%s {ENTER}" % root_path)
        shell.SendKeys(r"cd %s {ENTER}" % venv_location)
        # shell.SendKeys("activate {ENTER}")

    def run_py_script(self,shell):
        """runs the py script"""

        required = {'torch', 'torchvision', 'torchaudio', 'tqdm', 'numpy==1.23.3',
                    'pyyaml','opencv-python','pandas','matplotlib',
                    'seaborn', 'tensorboard'}

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
                # shell.SendKeys("pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113 {ENTER}")
                shell.SendKeys("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu113")

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
    def __init__(self, content, preWeights_path, custom_data_yaml_path, project_traindata_path, batch_size, epoch_size, segmentation, solution, parent=None):
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

        self.solution = solution
        print("self.solution : ", self.solution)

        self.ui = Ui_YoloV5Training_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.ui.TlabelTraining.setText("Prepare Data for Taining Yolo V5\n" + 
                                    "PreWeight_path  = " + self.PreWeight_path  + "\n" +
                                    "Path = " + self.Path + "\n" +
                                    "project_traindata_path = " + self.project_traindata_path + "\n" +
                                    "batch_size = " + str(self.batch_size) + "\n" +
                                    "Epoch_Size = " + str(self.Epoch_Size) + "\n" +
                                    "segmentation = " + str(self.segmentation))

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

        if not self.segmentation:
            self.Training_File_Path = self.content.re_path + '/AI_Module/train/yolov5'

        else:
            self.Training_File_Path = self.content.re_path + '/AI_Module/train/yolov5_seg'

        print("self.Training_File_Path : ", self.Training_File_Path)

        if self.solution == "Train":
            if os.path.isfile(self.Training_File_Path + "/yolo_cache.txt"):
                os.remove(self.Training_File_Path + "/yolo_cache.txt")

            opt_data = {}
            opt_data["weights"] = self.PreWeight_path
            opt_data["data"] = self.custom_data_path + '/custom_data.yaml'
            # opt_data["hyp"] = self.Path + '/data/hyps/hyp.scratch-low.yaml'
            opt_data["epochs"] = str(self.Epoch_Size)
            opt_data["batch_size"] = str(self.batch_size)
            opt_data["imgsz"] = str(self.content.ImageTrainZ)
            opt_data["project"] = self.project_traindata_path + '/weight/'

            OPT_Training = self.Training_File_Path      #boxitems
            print("Yolo V5 Opt Training : ", OPT_Training)

            with open(OPT_Training + "/yolo_opt.txt", 'w') as f:
                f.writelines(str(json.dumps(opt_data)))

            root_part = self.Training_File_Path[0:2]

            shell = client.Dispatch("WScript.Shell")
            run_venv = ActivateVenv()
            run_venv.open_cmd(shell)
            # EnumWindows(run_venv.set_cmd_to_foreground, None)
            run_venv.activate_venv(shell, root_part, self.Training_File_Path)
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

        # self.SubGlobalV5.setGlobal('YoloV5_opt', self.opt)
        # self.SubGlobalV5.setGlobal('YoloV5_waiting_opt', False)
        
        
    # =================================================================================

    def TerminalPrint_interval(self):

        cpu_percent = psutil.cpu_percent(interval=0.5)
        self.ui.CPUUsageLabel.display(str(int(cpu_percent)))

        Usage_virtual_memory = psutil.virtual_memory().percent
        self.ui.RAMUsageLabel.display(str(int(Usage_virtual_memory)))

        # ========================================
        # Calculate Estimate Trianing Finish
        self.NowTime = datetime.now()
        self.SpendTime_Sec = self.NowTime - self.content.startime
        seconds = self.SpendTime_Sec.total_seconds()

        # ========================================

        if os.path.isfile(self.Training_File_Path + "/yolo_cache.txt"):
            Training_AI_Cache = open(self.Training_File_Path + "/yolo_cache.txt",'r') #, encoding="utf-8")
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
                    #print("self.training_progress = ", self.training_progress)
                    #print("self.content.Epoch_sizeEdit.text() = ", self.content.Epoch_sizeEdit.text())

                    percent_training = int(int(self.training_progress) * 100 / int(self.content.Epoch_sizeEdit.text()))
                    #print("percent_training = ", percent_training)

                    # =================================================================
                    # Find SpendTime in Seconds
                    if percent_training > 0:
                        self.EstimateDone = int(int(100 * (seconds))/percent_training)

                        # 👇️ convert string to datetime object
                        if self.current_pc != percent_training:
                            result = self.content.startime + timedelta(seconds=self.EstimateDone)
                            self.ui.EstFinishLabel.setText(str(result.strftime("%d-%m-%Y  [ %H:%M ]")))

                            self.current_pc = percent_training

                    # ==================================================================

                    self.ui.progress_bar.setValue(percent_training)
                    self.ui.NumberProgress.display(str(percent_training))
        
        else:
            print("No file yolo_cache.txt !!!")


    #========================================================================================
    #========================================================================================
    #Close AI Training ---> Save Check Point
    def closeEvent(self, event):
        self.content.TrainObjectBtn.setEnabled(True)
        print("AI Yolo Training Log is closed !!!")

        self.content.checkLog.setChecked(False)
        self.Terminal_timer.stop()

        with open(self.Training_File_Path + "/yolo_cache.txt", 'w') as f:
            f.writelines(str(""))

#============================================================================================
#============================================================================================

@register_node(OP_NODE_OBJYOLOV5)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_objyolo5.png"
    op_code = OP_NODE_OBJYOLOV5
    op_title = "Yolo V5"
    content_label_objname = "Yolo V5"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[3,5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.input_payload = {}
        self.pass_payload = {}
        self.copy_payload = {}

    def initInnerClasses(self):
        self.content = ObjectDetect(self)        # <----------- init UI with data and widget
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
        self.content.comboGPU.activated[str].connect(self.onChangedCPU)

        self.content.checkLog.stateChanged.connect(self.SelectShowLog)
        self.content.ResCombo.activated[str].connect(self.onTrainingResChanged)

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
                    if len(str(self.input_payload['img'])) > 100:
                        self.copy_payload['img'] = self.input_payload['img']

                        if 'centers' in self.input_payload:
                            self.pass_payload['centers'] = self.input_payload['centers']
                            self.copy_payload['centers'] = self.input_payload['centers']
                    
                        #print("val['img'] = ", val['img'])
                        if 'fps' in self.input_payload:
                            self.pass_payload['fps'] = self.input_payload['fps']
                            self.copy_payload['fps'] = self.input_payload['fps']

                        if 'clock' in self.input_payload:
                            self.pass_payload['clock'] = self.input_payload['clock']
                            self.copy_payload['clock'] = self.input_payload['clock']

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

                    
                        if self.content.StartProcessDetect_flag:
                            if self.content.YoloProcess == "Detect" or self.content.YoloProcess == "iSegment" or self.content.YoloProcess == "Track":
                                confident = self.content.editConF.text()
                                if float(confident) < 0.1:
                                    confident = '0.1'

                                self.pass_payload['obj_found'], self.pass_payload['yolo_boxes'], self.pass_payload['img'] = self.detect_yolov5(self.input_payload['img'], conf_thres= float(confident))
                        
                                self.copy_payload['obj_found'] = self.pass_payload['obj_found']
                                self.copy_payload['yolo_boxes'] = self.pass_payload['yolo_boxes']
                        else:
                            self.pass_payload['obj_found'] = 0
                            self.pass_payload['yolo_boxes'] = []
                            self.pass_payload['img'] = self.input_payload['img']
                        
                        self.sendFixOutputByIndex(self.pass_payload, 0)
                        # print("self.copy_payload : ", self.copy_payload)
                        self.sendFixOutputByIndex(self.copy_payload, 1)
                        
                    else:
                        self.content.lbl.setText("<font color='red'>Wrong Input !!!</font>")

                    
            # self.value = self.pass_payload
            # self.markDirty(False)
            # self.markInvalid(False)

            # self.markDescendantsInvalid(False)
            # self.markDescendantsDirty()

            # #self.grNode.setToolTip("")
            # self.evalChildren()

            # #return self.value

    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren(index)

    def StartDetecOBJ(self):
        self.content.StartProcessDetect_flag = not self.content.StartProcessDetect_flag

        if not self.content.StartProcessDetect_flag:

            self.content.model = None

            self.content.combo.setEnabled(True)
            self.content.comboPreWeight.setEnabled(True)
            self.content.checkPreWeight.setEnabled(True)
            self.content.checkCustom.setEnabled(True)
            self.content.comboGPU.setEnabled(True)

            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))

            self.content.labelAnimate.setVisible(False)
            self.content.movie.stop()

            self.content.AutoLoadYolo = False
            
        else:
            if self.content.YoloProcess == "Detect" or self.content.YoloProcess == "iSegment" or self.content.YoloProcess == "Track":
   
                #print("self.content.YoloWeightPath = ", self.content.YoloWeightPath)
                #print("self.content.dataset_name = ", self.content.dataset_name)

                sys.path.insert(0, self.content.re_path + "/AI_Module/yolov5")

                # Load model
                self.content.device_usage = select_device(self.content.device)

                if not self.content.segmentation:
                    YoloWeightPath = self.content.YoloWeightPath

                else:
                    YoloWeightPath = self.content.YoloiSegWeightPath
    
                # print("YoloWeightPath = ", YoloWeightPath)
                # print("self.content.dataset_name = ", self.content.dataset_name)

                self.content.model = DetectMultiBackend(YoloWeightPath, device=self.content.device_usage, dnn=False, data=self.content.dataset_name, fp16=False)
                self.content.stride, self.content.names, self.content.pt = self.content.model.stride, self.content.model.names, self.content.model.pt

                self.content.imgsz = check_img_size((self.content.ImageTrainZ, self.content.ImageTrainZ), s=self.content.stride)  # check image size
                self.content.imgsz = check_img_size((1280, 1280), s=self.content.stride)  # check image size

                # print("self.content.device = ", self.content.device)
                # print("self.content.model = ", self.content.model)
                # print("self.content.stride = ", self.content.stride)
                # print("self.content.names = ", self.content.names)
                # print("self.content.pt = ", self.content.pt)

                # print("===> StartDetecOBJ : New self.content.imgsz = ", self.content.imgsz)
                # print("self.content.segmentation = ", self.content.segmentation)

                cudnn.benchmark = True  # set True to speed up constant image size inference

                self.content.labelAnimate.setVisible(True)
                self.content.movie.start()

                self.content.combo.setEnabled(False)
                self.content.comboPreWeight.setEnabled(False)
                self.content.checkPreWeight.setEnabled(False)
                self.content.checkCustom.setEnabled(False)

                self.content.comboGPU.setEnabled(False)

                self.content.AutoLoadYolo = True
                self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))

            else:
                self.content.labelAnimate.setVisible(False)
                self.content.movie.stop()

                self.content.model = None

                torch.cuda.empty_cache()
            
    def onChangedProcess(self, text):
        print("onChangedProcess : ", text)
        if text == "Detect":
            self.content.YoloProcess = "Detect"
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.checkCustom.setVisible(True)
            self.content.checkCustom.setEnabled(True)
            self.content.ResCombo.setEnabled(True)

            self.content.comboGPU.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)

            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)

            self.content.iSegmentation_Train_Check.setVisible(False)

            self.content.comboPreWeight.clear()

            self.content.comboPreWeight.addItem("yolov5s.pt")
            self.content.comboPreWeight.addItem("yolov5m.pt")
            self.content.comboPreWeight.addItem("yolov5l.pt")
            self.content.comboPreWeight.addItem("yolov5x.pt")

            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128.yaml"
            self.content.segmentation = False

        elif text == "iSegment":
            self.content.YoloProcess = "iSegment"
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.checkCustom.setVisible(True)
            self.content.checkCustom.setEnabled(True)

            self.content.comboGPU.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)

            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)

            self.content.iSegmentation_Train_Check.setVisible(False)

            self.content.comboPreWeight.clear()
            self.content.comboPreWeight.addItem("yolov5n-seg.pt")
            self.content.comboPreWeight.addItem("yolov5s-seg.pt")
            self.content.comboPreWeight.addItem("yolov5m-seg.pt")
            self.content.comboPreWeight.addItem("yolov5l-seg.pt")
            self.content.comboPreWeight.addItem("yolov5x-seg.pt")

            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128-seg.yaml"
            self.content.segmentation = True

        elif text == "Track":
            self.content.YoloProcess = "Track"

            self.content.checkPreWeight.setChecked(True)
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(True)

            self.content.comboGPU.setVisible(True)
            self.content.editConF.setVisible(True) 
            self.content.lblProjectPath.setVisible(True)

            self.content.checkCustom.setVisible(True)
            self.content.ResCombo.setEnabled(True)

            self.content.lblEpoch.setVisible(False)
            self.content.Epoch_sizeEdit.setVisible(False)

            self.content.lblbatch_size.setVisible(False)
            self.content.batch_sizeEdit.setVisible(False)
            self.content.lblTrain.setVisible(False)
            self.content.ImageLabelEdit.setVisible(False)
            self.content.browsTargetFolder.setVisible(False)
            self.content.lblSelectImage.setVisible(False)
            self.content.TrainObjectBtn.setVisible(False)

            self.content.iSegmentation_Train_Check.setVisible(False)
            
        elif text == "Train":
            self.content.YoloProcess = "Train"

            self.content.checkPreWeight.setChecked(True)
            self.content.checkPreWeight.setVisible(True)
            self.content.checkPreWeight.setEnabled(False)

            self.content.checkCustom.setVisible(False)
            self.content.lblProjectPath.setVisible(False)

            self.content.browsFilesCustome.setEnabled(False)
            self.content.comboGPU.setVisible(False)
            self.content.editConF.setVisible(False) 

            self.content.lblEpoch.setVisible(True)
            self.content.Epoch_sizeEdit.setVisible(True)

            self.content.lblbatch_size.setVisible(True)
            self.content.batch_sizeEdit.setVisible(True)
            self.content.lblTrain.setVisible(True)
            self.content.ImageLabelEdit.setVisible(True)
            self.content.browsTargetFolder.setVisible(True)
            #self.content.lblSelectImage.setVisible(True)
            self.content.TrainObjectBtn.setVisible(True)
            self.content.ResCombo.setVisible(True)

            self.content.iSegmentation_Train_Check.setVisible(True)

            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))

            self.content.labelAnimate.setVisible(False)
            self.content.movie.stop()

            self.content.AutoLoadYolo = False

    def onChangedPreWeight(self, text):
        if not self.content.segmentation:
            self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/" + text
            print("onChangedPreWeight : self.content.YoloPreWeightPath = ", self.content.YoloWeightPath)
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128.yaml"

        else:
            self.content.YoloiSegWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/" + text
            print("onChangedPreWeight : self.content.YoloiSegWeightPath = ", self.content.YoloiSegWeightPath)    
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128-seg.yaml"
        
        if self.content.YoloProcess == "Train":
            if str(self.content.comboPreWeight.currentText()) == "yolov5s.pt" or str(self.content.comboPreWeight.currentText()) == "yolov5m.pt" \
                    or str(self.content.comboPreWeight.currentText()) == "yolov5s-seg.pt" or str(self.content.comboPreWeight.currentText()) == "yolov5m-seg.pt":
                self.content.ImageTrainZ = 640
                
            elif str(self.content.comboPreWeight.currentText()) == "yolov5l.pt" or str(self.content.comboPreWeight.currentText()) == "yolov5x.pt" \
                    or str(self.content.comboPreWeight.currentText()) == "yolov5l-seg.pt" or str(self.content.comboPreWeight.currentText()) == "yolov5x-seg.pt":
                self.content.ImageTrainZ = 1280

            self.content.ResCombo.setCurrentText(str(self.content.ImageTrainZ))
            print("Train with image size = ", self.content.ImageTrainZ)

    def SelectPreWieght(self, state):
        if state == QtCore.Qt.Checked:
            self.content.browsFilesCustome.setEnabled(False)
            self.content.checkCustom.setChecked(False)
            self.content.comboPreWeight.setEnabled(True)

            self.content.selectWeight = "preweight"
            self.content.YoloWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/" + str(self.content.comboPreWeight.currentText())
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128.yaml"

        else:
            self.content.checkCustom.setChecked(True)

    def SelectiSegPreweight(self, state):
        print("Select i-Segmentation Preweight for Training")
        self.content.comboPreWeight.clear()

        if state == QtCore.Qt.Checked:
            self.content.comboPreWeight.addItem("yolov5s-seg.pt")
            self.content.comboPreWeight.addItem("yolov5m-seg.pt")
            self.content.comboPreWeight.addItem("yolov5l-seg.pt")
            self.content.comboPreWeight.addItem("yolov5x-seg.pt")

            self.content.iSegmentation_Train = True
            self.content.comboPreWeight.setCurrentText("yolov5m-seg.pt")

            self.content.YoloiSegWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/yolov5m-seg.pt"
            print("onChangedPreWeight : self.content.YoloiSegWeightPath = ", self.content.YoloiSegWeightPath)    
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128-seg.yaml"

            # Force fix image size as 640
            self.content.ImageTrainZ = 640
            print("self.content.ImageTrainZ =", self.content.ImageTrainZ)

            self.content.ResCombo.setCurrentText(str(self.content.ImageTrainZ))
            self.content.ResCombo.setEnabled(False)

        else:
            self.content.ResCombo.setEnabled(True)

            self.content.comboPreWeight.addItem("yolov5s.pt")
            self.content.comboPreWeight.addItem("yolov5m.pt")
            self.content.comboPreWeight.addItem("yolov5l.pt")
            self.content.comboPreWeight.addItem("yolov5x.pt")

            self.content.iSegmentation_Train = False
            self.content.comboPreWeight.setCurrentText("yolov5m.pt")

            self.content.YoloiSegWeightPath = self.content.re_path + "/AI_Module/yolov5/model_data/yolov5m.pt"
            print("onChangedPreWeight : self.content.YoloiSegWeightPath = ", self.content.YoloiSegWeightPath)    
            self.content.dataset_name = self.content.re_path + "/AI_Module/yolov5/data/coco128-seg.yaml"

        print("self.content.iSegmentation_Train = ", self.content.iSegmentation_Train)

    def SelectCustom(self, state):
        if state == QtCore.Qt.Checked:
            self.content.browsFilesCustome.setEnabled(True)
            self.content.checkPreWeight.setChecked(False)
            self.content.comboPreWeight.setEnabled(False)

            self.content.selectWeight = "custom"

            print("self.content.ProjectLocation : ", self.content.ProjectLocation)
            print("self.content.dataset_name : ", self.content.dataset_name)

            if len(self.content.ProjectLocation) > 0:

                isegmet = {}
                with open(self.content.dataset_name , "r") as stream:
                    try:
                        isegmet = yaml.safe_load(stream)
                        if 'isegment' in isegmet:
                            print("isegment = ", isegmet['isegment'])
                    except yaml.YAMLError as exc:
                        print(exc)

                if 'isegment' in isegmet:
                    print("isegment['isegment'][0] = ", isegmet['isegment'][0])
                    if isegmet['isegment'][0] == 'true':
                        self.content.YoloiSegWeightPath = self.content.ProjectLocation + "/best.pt"
                        self.content.segmentation = True

                    else:
                        self.content.YoloWeightPath = self.content.ProjectLocation + "/best.pt"
                        self.content.segmentation = False

                self.content.dataset_name = self.content.ProjectLocation + "/custom_data.yaml"

                print("SelectCustom self.content.segmentation : ", self.content.segmentation)

        else:
            self.content.checkPreWeight.setChecked(True)

    def onChangedCPU(self, select):
        if select == "CPU":
            self.content.device = 'cpu' #select_device(0)
            
        for i in range(len(self.content.NOF_GPU)):
            if select == str(self.content.NOF_GPU[i]):
                self.content.device = int(select) #select_device(0)
    
        print("Select self.device = ", self.content.device)


    def onTrainingResChanged(self, select):
        self.content.ImageTrainZ = int(select)
        print("Check Trining Image Resolution : ", select)
            
    @torch.no_grad()
    def detect_yolov5(self, image, conf_thres=0.25):
        iou_thres=0.45  # NMS IOU threshold
        max_det=1000  # maximum detections per image
        classes=0  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False  # class-agnostic NMS
        augment=False  # augmented inference
        visualize=False  # visualize features

        line_thickness=1  # bounding box thickness (pixels)
        retina_masks=False

        obj_found = 0
        yolo_boxes = [] # 'yolo_boxes': [{'x1': 213, 'y1': 412, 'x2': 264, 'y2': 470, 'score': 97, 'obj': 'pallet_track'}

        img0 = image

        # Padded resize
        img = letterbox(img0, self.content.imgsz, stride=self.content.stride, auto=False)[0]

        # Convert
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)

        im = torch.from_numpy(img).to(self.content.device_usage)
        im = im.half() if self.content.model.fp16 else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        # Inference
        if self.content.segmentation:
            # Inference
            pred, proto = self.content.model(im, augment=augment, visualize=visualize)[:2]

            # NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det, nm=32)
            # print("segmentation pred: ", pred)

        else:
            pred = self.content.model(im, augment=augment, visualize=visualize)

            # NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions
        for i, det in enumerate(pred):  # per image

            im0 = img0.copy()   
            annotator = Annotator(im0, line_width=line_thickness, example=str(self.content.names))
            if len(det):

                if self.content.segmentation:
                    masks = process_mask(proto[i], det[:, 6:], det[:, :4], im.shape[2:], upsample=True)  # HWC

                    # Segments

                    # segments = reversed(masks2segments(masks))
                    # segments = [scale_segments(im.shape[2:], x, im0.shape).round() for x in segments]

                    # Mask plotting
                    annotator.masks(masks,
                                    colors=[colors(x, True) for x in det[:, 5]],
                                    im_gpu=None if retina_masks else im[i])

                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                if not self.content.segmentation:
                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)  # integer class
                        label = f'{self.content.names[c]} : {int(conf* 100)}%'
                        annotator.box_label(xyxy, label, color=colors(c, True))
                    
                        #print("x1 = ", int(xyxy[0]))
                        #print("y1 = ", int(xyxy[1]))
                        #print("x2 = ", int(xyxy[2]))
                        #print("y2 = ", int(xyxy[3]))

                        obj_found += 1
                        yolo_boxes.append({'x1':int(xyxy[0]), 'y1':int(xyxy[1]), 'x2':int(xyxy[2]), 'y2': int(xyxy[3]), 'score': int(conf* 100), 'obj': self.content.names[c]})
                    
                else:
                    for j, (*xyxy, conf, cls) in enumerate(reversed(det[:, :6])):
                        c = int(cls)  # integer class
                        label = f'{self.content.names[c]} : {int(conf* 100)}%'
                        # annotator.box_label(xyxy, label, color=colors(c, True))
                        # annotator.draw.polygon(segments[j], outline=colors(c, True), width=3)

                        obj_found += 1
                        yolo_boxes.append({'x1':int(xyxy[0]), 'y1':int(xyxy[1]), 'x2':int(xyxy[2]), 'y2': int(xyxy[3]), 'score': int(conf* 100), 'obj': self.content.names[c]})

                        im0 = cv2.putText(im0, label, (int(xyxy[0]), int(xyxy[1])-10), cv2.FONT_HERSHEY_PLAIN, 1, colors(c, True), 1)

                # Stream results
                im0 = annotator.result()

        return obj_found, yolo_boxes, im0

    #=========================================================================
    def SelectShowLog(self, state):
        if state == QtCore.Qt.Checked:
            self.content.showlog = True

            YoloPreWeightPath = self.content.YoloWeightPath
            if self.content.iSegmentation_Train:
                YoloPreWeightPath = self.content.YoloiSegWeightPath

            self.AI_TrainingYolo = TraingYolo(self.content, YoloPreWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()),
                                            int(self.content.Epoch_sizeEdit.text()), self.content.iSegmentation_Train, solution="Log")
            self.AI_TrainingYolo.show()
        else:
            self.content.showlog = False

    def trainingObject(self):
        self.content.TrainObjectBtn.setEnabled(False)
        self.content.ResCombo.setEnabled(False)

        YoloPreWeightPath = self.content.YoloWeightPath
        if self.content.iSegmentation_Train:
            YoloPreWeightPath = self.content.YoloiSegWeightPath

        self.AI_TrainingYolo = TraingYolo(self.content, YoloPreWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()),
                                            int(self.content.Epoch_sizeEdit.text()), self.content.iSegmentation_Train, solution="Train")
        self.AI_TrainingYolo.show()

        # CacheTraining = self.content.re_path + '/Database/'       #boxitems
        # print("Yolo V5 CacheTraining : ", CacheTraining)
        # with open(CacheTraining + "yolo_cache.txt", 'w') as f:
        #     f.writelines("True")

        #training_app = YoloV5Traing(self.content.YoloWeightPath, self.content.ProjectTrainingLocation, self.content.ProjectTrainingLocation, int(self.content.batch_sizeEdit.text()))
        #training_app.show()

        #training_app.exec_()

