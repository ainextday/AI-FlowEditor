from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
import ai_application.AI_Tools.scan_usb as usbscaning
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import win32com.client
import cv2
import os

import time
from datetime import datetime

# # pip install mss
# from mss import mss
# from PIL import Image

# importing the required packages
import pyautogui
import numpy as np

# import dbr
# from dbr import *

from pyzbar.pyzbar import decode

from win32api import GetSystemMetrics
import wmi
import sys

#CalcInputContent
class CameraID(QDMNodeContentWidget):
    def initUI(self):
        Path = os.path.dirname(os.path.abspath(__file__))
        self.capture_icon = Path + "/icons/icons_capture.png"
        self.video_icon = Path + "/icons/icons_video.png"

        self.setting_icon = Path + "/icons/icons_settings_icon.png"

        self.lbl = QLabel("N" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(2,7,10,20)
        self.lbl.setStyleSheet("color: orange; font-size:6pt;")

        self.lbl_cap = QLabel("C" , self)
        self.lbl_cap.setAlignment(Qt.AlignLeft)
        self.lbl_cap.setGeometry(2,32,10,20)
        self.lbl_cap.setStyleSheet("color: red; font-size:6pt;")

        self.lbl_Vdo = QLabel("V" , self)
        self.lbl_Vdo.setAlignment(Qt.AlignLeft)
        self.lbl_Vdo.setGeometry(2,77,10,20)
        self.lbl_Vdo.setStyleSheet("color: yellow; font-size:6pt;")

        self.Devicelbl = QLabel("Device:" , self)
        self.Devicelbl.setAlignment(Qt.AlignLeft)
        self.Devicelbl.setGeometry(82,7,35,20)
        self.Devicelbl.setStyleSheet("color: orange; font-size:5pt;")

        self.CamCH_Select = QComboBox(self)
        # self.CamCH_Select.setAlignment(Qt.AlignRight)
        # self.CamCH_Select.setFixedWidth(20)
        self.CamCH_Select.setGeometry(80,4,60,25)
        self.CamCH_Select.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #F1725D; font-size:6pt;"
                                   "}") 

        #self.edit.setObjectName(self.node.content_label_objname)
        self.radioState = QRadioButton(self)
        self.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                        "background-color : #33CCFF"
                                   "}")
        self.radioState.setGeometry(15,4,60,25)
        self.radioState.setIcon(QIcon(self.video_icon))

        """self.checkFlip = QCheckBox("F",self)
        self.checkFlip.setGeometry(15,27,30,20)
        self.checkFlip.setStyleSheet("color: orange")

        self.checkMirror = QCheckBox("M",self)
        self.checkMirror.setGeometry(50,27,33,20)
        self.checkMirror.setStyleSheet("color: orange")"""


        self.combo = QComboBox(self)
        self.combo.addItem("0 " + chr(176))
        self.combo.addItem("180 " + chr(176))
        self.combo.addItem("360 " + chr(176))
        self.combo.setGeometry(15,35,60,25)
        self.combo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 

        self.ResCombo = QComboBox(self)
        self.ResCombo.addItem("640")
        self.ResCombo.addItem("1280")
        self.ResCombo.addItem("1920")
        self.ResCombo.addItem("2560")
        self.ResCombo.setGeometry(80,35,60,25)
        self.ResCombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33DDFF; font-size:6pt;"
                                   "}") 

        self.Capture = QPushButton(self)
        self.Capture.setGeometry(15,65,100,27)
        self.Capture.setIcon(QIcon(self.capture_icon))

        # self.editName = QLineEdit(self)
        # self.editName.setGeometry(5,100,140,18)
        # self.editName.setPlaceholderText("Camera Name")
        # self.editName.setAlignment(QtCore.Qt.AlignCenter)
        # self.editName.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:8pt;color:white; border: 1px solid white; border-radius: 3%;")

        self.CameraIDCombo = QComboBox(self)
        self.CameraIDCombo.setGeometry(5,95,140,25)
        self.CameraIDCombo.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:7pt;color:white; border: 1px solid white; border-radius: 3%;")
        # self.CameraNameCombo.setEnabled(True)

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(120,70,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        # Lable ROI Chanel out
        self.lbl_ROI1 = QLabel("1" , self)
        self.lbl_ROI1.setAlignment(Qt.AlignLeft)
        self.lbl_ROI1.setGeometry(141,44,10,20)
        self.lbl_ROI1.setStyleSheet("color: red; font-size:5pt;")
        self.lbl_ROI1.setVisible(False)

        self.lbl_ROI2 = QLabel("2" , self)
        self.lbl_ROI2.setAlignment(Qt.AlignLeft)
        self.lbl_ROI2.setGeometry(141,67,10,20)
        self.lbl_ROI2.setStyleSheet("color: yellow; font-size:5pt;")
        self.lbl_ROI2.setVisible(False)

        self.lbl_ROI3 = QLabel("3" , self)
        self.lbl_ROI3.setAlignment(Qt.AlignLeft)
        self.lbl_ROI3.setGeometry(141,88,10,20)
        self.lbl_ROI3.setStyleSheet("color: gray; font-size:5pt;")
        self.lbl_ROI3.setVisible(False)

        # =============================================================================

        self.Camera_timer = QtCore.QTimer(self)
        self.USBScan_timer = QtCore.QTimer(self)
        self.Camera_autoRE_timer = QtCore.QTimer(self)

        self.Camera_find_recovery = QtCore.QTimer(self)

        self.GlobalTimer = GlobalVariable()
        if self.GlobalTimer.hasGlobal("GlobalTimerApplication"):
            ListGlobalTimer = []
            ListGlobalTimer = list(self.GlobalTimer.getGlobal("GlobalTimerApplication"))

            ListGlobalTimer.append(self.Camera_timer)
            ListGlobalTimer.append(self.USBScan_timer)
            ListGlobalTimer.append(self.Camera_autoRE_timer)
            self.GlobalTimer.setGlobal("GlobalTimerApplication", ListGlobalTimer)
            

        # self.camera_CH = int(self.edit.text())
        # self.camera_CH = self.CamCH_Select.currentText()

        self.ImgData = None
        self.camera_res = 640
        self.CamCapture = None
        # self.CamCapture = cv2.VideoCapture(0) #captureDevice = camera)
        # self.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.camera_res))
        # self.CamCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.CamCapture.set(cv2.CAP_PROP_FPS, 30)

        self.all_usb_cameras = self.find_usb_cameras()
        # self.CamCH_Select.clear()
        # self.CamCH_Select.addItem('screen cap')

        self.dbr_license = "DLS2eyJoYW5kc2hha2VDb2RlIjoiMjAwMDAxLTE2NDk4Mjk3OTI2MzUiLCJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSIsInNlc3Npb25QYXNzd29yZCI6IndTcGR6Vm05WDJrcEQ5YUoifQ=="

        # self.QR_CodeReader = cv2.QRCodeDetector()
        # BarcodeReader.init_license(self.dbr_license)
        # self.reader = BarcodeReader()

        self.fix_ch = ""
        self.new_update_ch = 0

        self.Nof_CameraBox = 0
        self.innit_camera_fps = False
        self.TotalOfCamInSystem = 1
        self.StartfromSave = False
        self.usb_cnt = 0

        self.submit_true_cnt = 0
        self.command_start = False

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.FlipCam = False
        self.MirrorCam = False

        self.autorun = ""

        print("Screen Width =", GetSystemMetrics(0))
        print("Screen Height =", GetSystemMetrics(1))


        self.ListAllCameraIndex = []

        # ---------------------------------------------
        self.camera_usb_keys = []
        self.camera_usb_names = []
        self.combine_cam_id = []
        self.save_combine_cam_id = []

        self.cam_id = ""

        self.camera_box_key = ""

        # self.record_combine_cam_id = []

        self.change_CamCH = False
        self.update_new_usb = ""

        self.skip_check_missing = False
        self.missing_USB_index_channels = []

        self.Camera_replaceMissing = False

        self.camera_usb_keys = self.scan_usb_cameras()
        # print("Onload Camera camera_usb_keys :", self.camera_usb_keys)

        self.ThisCH_Need_minusIndex = False
        self.missing_Cam_key = ""

        self.all_frezz = False

        # self.camera_discon = False
        # self.SaveChanel = False

        # ---------------------------------------------
        # Multiple Monitor
        # self.monitor_number = 2

        # self.sct = mss()
        # self.mon = self.sct.monitors[monitor_number]

        # The screen part to capture
        # self.monitor = {
        #     "top": self.mon["top"],
        #     "left": self.mon["left"],
        #     "width": self.mon["width"],
        #     "height": self.mon["height"],
        #     "mon": self.monitor_number,
        # }
        # output = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**self.monitor)

        # # Grab the data
        # self.sct_img = self.sct.grab(self.monitor)

        # ----------------------------------------------
        # Single Monitor
        # self.sct = mss()
        # self.monitor = {'top': 0, 'left':0, 'width':GetSystemMetrics(0), 'height':GetSystemMetrics(1)}

        self.camera_mode = ""

        self.cam_inc_bright_flag = False
        self.increase_brightness = 0

        self.cam_incCont_flag = False
        self.adjust_contrast = 1

        self.setting_image = None

        # ============================================
        # ROI 1
        self.setCameraROI = False
        self.setROIX1 = 50
        self.setROIY1 = 50

        self.setROIX2 = 150
        self.setROIY2 = 200

        self.rotateROI1 = "0"

        self.custom_angleROI1 = False
        self.angle_ROI1 = ""

        self.convert_angle_ROI1 = False
        self.color_refROI1 = ""

        # ============================================
        # ROI 2
        self.setCameraROI2 = False
        self.setROI2X1 = 50
        self.setROI2Y1 = 50

        self.setROI2X2 = 150
        self.setROI2Y2 = 200

        self.rotateROI2 = "0"

        self.custom_angleROI2 = False
        self.angle_ROI2 = ""

        self.convert_angle_ROI2 = False
        self.color_refROI2 = ""

        # ============================================
        # ROI 3
        self.setCameraROI3 = False
        self.setROI3X1 = 50
        self.setROI3Y1 = 50

        self.setROI3X2 = 150
        self.setROI3Y2 = 200

        self.rotateROI3 = "0"

        self.custom_angleROI3 = False
        self.angle_ROI3 = ""

        self.convert_angle_ROI3 = False
        self.color_refROI3 = ""

        #=============================================
        self.auto_reconnect = False
        self.interval_connect = 3

        self.show_fps_flag = True

        self.Cam_Alive = True
        self.Last_Frame = None

        self.img_width = 640
        self.img_height = 480

        self.CamUpdateGlobal = GlobalVariable()

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================


    def serialize(self):
        res = super().serialize()
        res['ch'] = self.CamCH_Select.currentText()
        res['autorun'] = self.lbl.text()
        res['MirrorCam'] = self.MirrorCam
        res['FlipCam'] = self.FlipCam
        res['img_res'] = self.ResCombo.currentText()
        res['camera_id'] = self.CameraIDCombo.currentText()

        if self.CamUpdateGlobal.hasGlobal("GlobalCameraBoxID"):
            self.ListUpdateGlobalCameraBox = list(self.CamUpdateGlobal.getGlobal("GlobalCameraBoxID"))
            self.TotalOfCamInSystem = len(self.ListUpdateGlobalCameraBox)
                
        res['tot_camsys'] = self.TotalOfCamInSystem
        res['cam_mode'] = self.camera_mode
        res['cam_bright_flag'] = self.cam_inc_bright_flag
        res['number_br_increas'] = self.increase_brightness

        res['incCont_flag'] = self.cam_incCont_flag
        res['number_contrast'] = self.adjust_contrast

        res['dbr_license'] = self.dbr_license
        res['combine_cam_id'] = self.save_combine_cam_id

        res['ListAllCameraIndex'] = self.ListAllCameraIndex

        # ============================================
        # ROI 1
        res['set_cam_roi'] = self.setCameraROI
        res['roi_x1'] = self.setROIX1
        res['roi_y1'] = self.setROIY1
        res['roi_x2'] = self.setROIX2
        res['roi_y2'] = self.setROIY2

        res['rotateROI1'] = self.rotateROI1
        
        res['custom_angleROI1'] = self.custom_angleROI1
        res['angle_ROI1'] = self.angle_ROI1

        res['convert_angle_ROI1'] = self.convert_angle_ROI1
        res['color_refROI1'] = self.color_refROI1

        # ============================================
        # ROI 2
        res['set_cam_roi2'] = self.setCameraROI2
        res['roi_2x1'] = self.setROI2X1
        res['roi_2y1'] = self.setROI2Y1
        res['roi_2x2'] = self.setROI2X2
        res['roi_2y2'] = self.setROI2Y2

        res['rotateROI2'] = self.rotateROI2

        res['custom_angleROI2'] = self.custom_angleROI2
        res['angle_ROI2'] = self.angle_ROI2

        res['convert_angle_ROI2'] = self.convert_angle_ROI2
        res['color_refROI2'] = self.color_refROI2

        # ============================================
        # ROI 3
        res['set_cam_roi3'] = self.setCameraROI3
        res['roi_3x1'] = self.setROI3X1
        res['roi_3y1'] = self.setROI3Y1
        res['roi_3x2'] = self.setROI3X2
        res['roi_3y2'] = self.setROI3Y2
        
        res['rotateROI3'] = self.rotateROI3

        res['custom_angleROI3'] = self.custom_angleROI3
        res['angle_ROI3'] = self.angle_ROI3

        res['convert_angle_ROI3'] = self.convert_angle_ROI3
        res['color_refROI3'] = self.color_refROI3

        # =============================================
        res['auto_reconnect'] = self.auto_reconnect
        res['interval_connect'] = self.interval_connect
        res['show_fps_flag'] = self.show_fps_flag

        res['img_width'] = self.img_width
        res['img_height'] = self.img_height

        # FPS = int(60/int(self.TotalOfCamInSystem))

        # print("\033[96m {}\033[00m".format("Detect Camera in system : " + str(self.TotalOfCamInSystem)))
        # print("\033[93m {}\033[00m".format("Camera Chanel : " + str(self.edit.text()) + " - FPS is : " + str(FPS)))

        # # self.CamCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.CamCapture.set(cv2.CAP_PROP_FPS, FPS)

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.fix_ch = data['ch']
            print("..........................................................................................................")
            print("..........................................................................................................")
            print("\033[93m {}\033[00m".format("Camera Chanel : " + str(self.fix_ch)))
            self.autorun = data['autorun']
            self.lbl.setText(self.autorun)

            self.MirrorCam = data['MirrorCam']
            self.FlipCam = data['FlipCam']
            
            if 'img_res' in data:
                self.camera_res = data['img_res']

                if self.fix_ch != 'screen cap' and self.fix_ch != 'X':
                    self.CamCapture = cv2.VideoCapture(int(self.fix_ch)) #captureDevice = camera)
                    self.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.camera_res))

                    FPS = 30

                    if 'tot_camsys' in data:
                        self.TotalOfCamInSystem = data['tot_camsys']
                        print("self.TotalOfCamInSystem :", self.TotalOfCamInSystem)
                        FPS = int(60/int(self.TotalOfCamInSystem))

                        print("\033[96m {}\033[00m".format("Detect Camera in system : " + str(self.TotalOfCamInSystem)))
                        print("\033[93m {}\033[00m".format("Camera Chanel : " + str(self.fix_ch) + " - FPS is : " + str(FPS)))

                    # self.CamCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.CamCapture.set(cv2.CAP_PROP_FPS, FPS)

                    # ListGlobalCamera = []
                    # if self.GlobalTimer.hasGlobal("GlobalCameraApplication"):
                    #     if type(self.GlobalTimer.getGlobal("GlobalCameraApplication")) is list:
                    #         ListGlobalCamera = list(self.GlobalTimer.getGlobal("GlobalCameraApplication"))
                       
                    # ListGlobalCamera.append(self.CamCapture)
                    # print("deserialize -> ListGlobalCamera : ", ListGlobalCamera)
                    # self.GlobalTimer.setGlobal("GlobalCameraApplication", ListGlobalCamera)

                else:
                    # if self.camera_res == '1280':
                    #     self.image_width = 1280
                    #     self.image_height = 720
                        
                    # elif self.camera_res == '1920':
                    #     self.image_width = 1920
                    #     self.image_height = 1080

                    # elif self.camera_res == '2560':
                    #     self.image_width = 2560
                    #     self.image_height = 1440

                    # else:
                    #     self.image_width = 640
                    #     self.image_height = 480

                    if 'image_width' in data:         
                        self.img_width = data['img_width']
                        print("self.img_width:", self.img_width)
       
                    if 'img_height' in data:
                        self.img_height = data['img_height']
                        print("self.img_height:", self.img_height)

                self.ResCombo.setCurrentText(self.camera_res)

            if 'camera_id' in data:
                self.CameraIDCombo.setCurrentText(data['camera_id'])

            if 'cam_mode' in data:
                self.camera_mode = data['cam_mode']

            if 'cam_bright_flag' in data:
                self.cam_inc_bright_flag = data['cam_bright_flag']

            if 'number_br_increas' in data:
                self.increase_brightness = data['number_br_increas']

            if 'incCont_flag' in data:
                self.cam_incCont_flag = data['incCont_flag']

            if 'number_contrast' in data:
                self.adjust_contrast = data['number_contrast']

            if 'dbr_license' in data:
                self.dbr_license = data['dbr_license']

            if 'combine_cam_id' in data:
                self.combine_cam_id = data['combine_cam_id']
            
                print("self.combine_cam_id =", self.combine_cam_id)
                # Extracting the text '1' from the list
                if len(self.combine_cam_id) > 0:
                    key = self.combine_cam_id[0].keys()
                    print(key)  # Output: dict_keys(['1'])
                    print(list(key)[0])  # Output: '1'

                    if self.fix_ch == "0" and self.fix_ch != str(list(key)[0]):
                        self.fix_ch = str(list(key)[0])

                    if len(self.combine_cam_id) > 0:
                        self.camera_box_key = self.combine_cam_id[0][str(self.fix_ch)]
                        print("\033[92m {}\033[00m".format("Onload Index Combine cam = " + str(self.combine_cam_id[0])))
                    else:
                        self.camera_box_key = ""

                print("self.camera_box_key =", self.camera_box_key)
                print("type(self.camera_box_key) :", type(self.camera_box_key))

                print("\033[92m {}\033[00m".format("Onload combine camera key = " + str(self.camera_box_key)))

                # self.camera_usb_keys = self.scan_usb_cameras()
                print("Onload Camera camera_usb_keys :", self.camera_usb_keys)

                # for usb_cam in range(len(self.camera_usb_keys)):
                #     if str(list(self.combine_cam_id[0][str(self.fix_ch)].values())[0]) == str(self.camera_usb_keys[usb_cam]):
                #         print("\033[95m {}\033[00m".format("Onload Detect Camera CH" + str(self.fix_ch)))
                #         # self.CamCH_Select.setCurrentText(self.fix_ch)
                #         self.skip_check_missing = True

                # Extracting the key from camera_key dictionary
                camera_usb_check = ""
                if isinstance(self.camera_box_key, str):
                    if len(self.combine_cam_id) > 0:
                        camera_usb_check = self.combine_cam_id[0][str(self.fix_ch)]
                        print("str --> camera_usb_check :", camera_usb_check)

                elif isinstance(self.camera_box_key, dict):
                    # Get the first value directly
                    camera_usb_check = next(iter(self.camera_box_key.values()), None) 
                    
                    print("dict --> camera_usb_check :", camera_usb_check)

                # Checking if the camera key is in camera_usb_keys list
                if camera_usb_check in self.camera_usb_keys:
                    print("\033[92m {}\033[00m".format("Camera key CH : " + self.fix_ch + " is present in camera_usb_keys list."))
                    print("\033[95m {}\033[00m".format("Onload Detect Camera CH : " + self.fix_ch))
                    self.CamCH_Select.setCurrentText(self.fix_ch)
                    self.skip_check_missing = True
                    
                else:
                    print("\033[91m {}\033[00m".format("Camera key is not present in camera_usb_keys list !!!\n Cannot load Camera CH :" + self.fix_ch))

                # if camera_key_to_check in self.camera_usb_keys:
                #     print("\033[95m {}\033[00m".format("Onload Detect Camera CH" + str(self.fix_ch)))
                #     self.CamCH_Select.setCurrentText(self.fix_ch)
                #     self.skip_check_missing = True
        
                if self.GlobalTimer.hasGlobal("MissingUSBCameraKey"):
                    self.missing_USB_index_channels = self.GlobalTimer.getGlobal("MissingUSBCameraKey")
                    print("missing_USB_index_channels :", self.missing_USB_index_channels)

                    if self.fix_ch != 'X':
                        self.new_update_ch = int(self.fix_ch)
                        for i in self.missing_USB_index_channels:
                            print("i :", i)
                            print("type(i) :", type(i))
                            if int(self.fix_ch) > int(i):
                                self.new_update_ch -= 1
                                self.ThisCH_Need_minusIndex = True

                if not self.skip_check_missing:
                    # Find the missing USB index channels
                    print("\033[91m {}\033[00m".format("Load Camera Missing CH : " + self.fix_ch + " ; self.missing_Cam_key : " + camera_usb_check))
                    self.missing_Cam_key = camera_usb_check
                    self.CamCH_Select.addItem("X")
                    self.CamCH_Select.setCurrentText("X")

                    self.CameraIDCombo.addItem("Missing Cam " + self.fix_ch)
                    self.CameraIDCombo.setCurrentText("Missing Cam " + self.fix_ch)
                    self.CameraIDCombo.setStyleSheet("font-size:7pt; color:red;")

                    self.missing_USB_index_channels.append(self.fix_ch)
                    self.GlobalTimer.setGlobal("MissingUSBCameraKey", self.missing_USB_index_channels)

                # else:
                #     # print("\033[94m {}\033[00m".format("missing_USB_index_channels :"+ self.missing_USB_index_channels))
                #     # print("len(self.missing_USB_index_channels) :", len(self.missing_USB_index_channels))
                    
                #     # if len(self.missing_USB_index_channels) > 0:
                #     # #     for i in range(len(self.missing_USB_index_channels)):
                #     #     self.fix_ch = str(int(self.fix_ch) - len(self.missing_USB_index_channels))
                #     #     # print("rotate_ch :", self.fix_ch)

                #     #     self.Camera_replaceMissing = True
                    
                #     self.CamCH_Select.setCurrentText(self.fix_ch)

                # ============================================
                # ROI 1 
                if 'set_cam_roi' in data:
                    self.setCameraROI = data['set_cam_roi']
                    if self.setCameraROI:
                        self.lbl_ROI1.setVisible(True)
                
                if 'roi_x1' in data:
                    self.setROIX1 = data['roi_x1']
                
                if 'roi_y1' in data:
                    self.setROIY1 = data['roi_y1']
                
                if 'roi_x2' in data:
                    self.setROIX2 = data['roi_x2']

                if 'roi_y2' in data:
                    self.setROIY2 = data['roi_y2']

                if 'rotateROI1' in data:
                    self.rotateROI1 = data['rotateROI1']

                if 'custom_angleROI1' in data:
                    self.custom_angleROI1 = data['custom_angleROI1']

                if 'angle_ROI1' in data:
                    self.angle_ROI1 = data['angle_ROI1']

                if 'convert_angle_ROI1' in data:
                    self.convert_angle_ROI1 = data['convert_angle_ROI1']

                if 'color_refROI1' in data:
                    self.color_refROI1 = data['color_refROI1']

                # ============================================
                # ROI 2
                if 'set_cam_roi2' in data:
                    self.setCameraROI2 = data['set_cam_roi2']
                    if self.setCameraROI2:
                        self.lbl_ROI2.setVisible(True)
                
                if 'roi_2x1' in data:
                    self.setROI2X1 = data['roi_2x1']
                
                if 'roi_2y1' in data:
                    self.setROI2Y1 = data['roi_2y1']
                
                if 'roi_2x2' in data:
                    self.setROI2X2 = data['roi_2x2']

                if 'roi_2y2' in data:
                    self.setROI2Y2 = data['roi_2y2']

                if 'rotateROI2' in data:
                    self.rotateROI2 = data['rotateROI2']

                if 'custom_angleROI2' in data:
                    self.custom_angleROI2 = data['custom_angleROI2']

                if 'angle_ROI2' in data:
                    self.angle_ROI2 = data['angle_ROI2']

                if 'convert_angle_ROI2' in data:
                    self.convert_angle_ROI2 = data['convert_angle_ROI2']

                if 'color_refROI2' in data:
                    self.color_refROI2 = data['color_refROI2']

                # ============================================
                # ROI 3
                if 'set_cam_roi3' in data:
                    self.setCameraROI3 = data['set_cam_roi3']
                    if self.setCameraROI3:
                        self.lbl_ROI3.setVisible(True)
                
                if 'roi_3x1' in data:
                    self.setROI3X1 = data['roi_3x1']
                
                if 'roi_3y1' in data:
                    self.setROI3Y1 = data['roi_3y1']
                
                if 'roi_3x2' in data:
                    self.setROI3X2 = data['roi_3x2']

                if 'roi_3y2' in data:
                    self.setROI3Y2 = data['roi_3y2']

                if 'rotateROI3' in data:
                    self.rotateROI3 = data['rotateROI3']

                if 'custom_angleROI3' in data:
                    self.custom_angleROI3 = data['custom_angleROI3']

                if 'angle_ROI3' in data:
                    self.angle_ROI3 = data['angle_ROI3']

                if 'convert_angle_ROI3' in data:
                    self.convert_angle_ROI3 = data['convert_angle_ROI3']

                if 'color_refROI3' in data:
                    self.color_refROI3 = data['color_refROI3']

                # ============================================
                    
            if 'auto_reconnect' in data:
                self.auto_reconnect = data['auto_reconnect']

            if 'interval_connect' in data:   
                self.interval_connect = data['interval_connect']

            if 'show_fps_flag' in data:
                self.show_fps_flag = data['show_fps_flag']

            if self.autorun == 'A':
                if self.skip_check_missing: 
                    if self.ThisCH_Need_minusIndex:
                        self.fix_ch = str(self.new_update_ch)

                    print("Camera Auto Start CH :", self.fix_ch)
                    self.save_combine_cam_id = self.combine_cam_id

                    self.StartfromSave = True
                    self.CameraIDCombo.setEnabled(False)

                    self.Capture.setEnabled(False)
                    self.radioState.setChecked(True)
                    self.BlinkingState = True

                    Cam_CH = int(self.fix_ch)
                    self.CamCH_Select.setCurrentText(str(Cam_CH))
                    self.CamCapture = cv2.VideoCapture(Cam_CH) #captureDevice = camera)
                    self.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.camera_res))
                    
                    self.Camera_timer.start()

                # else:
                #     self.Camera_find_recovery.start()

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
    def find_usb_cameras(self, max_cameras=10):
        usb_cameras = []
        self.CamCH_Select.clear()
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.camera_res))
            if cap.isOpened():
                usb_cameras.append(i)
                self.CamCH_Select.addItem(str(i))
                cap.release()

        # print("\033[93m {}\033[00m".format("Scan USB Camera in System --> : " + str(usb_cameras)))
        self.CamCH_Select.addItem('screen cap')
        return usb_cameras
    
    def scan_usb_cameras(self):
        camera_usb_keys = []
        self.CameraIDCombo.clear()

        # Connect to the WMI interface
        wmi_interface = wmi.WMI()

        # Query USB camera devices
        query = "SELECT * FROM Win32_PnPEntity WHERE ClassGuid = '{ca3e7ab9-b4c3-4ae6-8251-579ef933890f}'"
        camera_devices = wmi_interface.query(query)

        # Get the names of USB camera devices
        for device in camera_devices:
            if device.DeviceID:
                # print("device.DeviceID =", device.DeviceID)
                # print("type(device.DeviceID =)", type(device.DeviceID))

                camera_usb_keys.append(device.DeviceID)
                self.CameraIDCombo.addItem(device.DeviceID[-17:])

        return camera_usb_keys
    
    def scan_combine(self):
        # Combine CH with USB Devide
        # self.combine_cam_id.append({str(self.CamCH_Select.currentText()):{str(self.CameraNameCombo.currentText()):str(self.camera_usb_keys[self.CameraNameCombo.currentIndex()])}})
        # print("\033[93m {}\033[00m".format("Scan Camera --> Combine camID :" + str(self.combine_cam_id)))

        print("self.camera_usb_keys :", self.camera_usb_keys)
        self.cam_id = self.CameraIDCombo.currentText()
        print("cam_id :", self.cam_id)

        # Using a loop
        for index, key in enumerate(self.camera_usb_keys):
            if self.cam_id in key:
                print("Index:", index)
                print("Full data:", key)
                break
        else:
            print("cam_id not found in camera_usb_keys")

        # Using list comprehension
        correct_camera_usb = ""
        indices = [index for index, key in enumerate(self.camera_usb_keys) if self.cam_id in key]
        if indices:
            print("Index:", indices[0])
            correct_camera_usb = self.camera_usb_keys[indices[0]]
            print("Full data:", correct_camera_usb)

        else:
            print("cam_id not found in camera_usb_keys")

        if len(self.combine_cam_id) > 0:
            self.combine_cam_id[0] = ({str(self.CamCH_Select.currentText()):str(correct_camera_usb)})
        else:
            self.combine_cam_id.append({str(self.CamCH_Select.currentText()):str(correct_camera_usb)})

        self.save_combine_cam_id = self.combine_cam_id
        print("self.save_combine_cam_id :", self.save_combine_cam_id)

        # self.CamCH_Select.setCurrentText()

# ======================================================================================
# ======================================================================================

class ResizableRectLabel(QtWidgets.QLabel):
    resized = QtCore.pyqtSignal()
    coordinates_changed = QtCore.pyqtSignal(str, int, int, int, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rectangles = {}
        self.circle_colors = {}  # Store circle colors separately
        # self.current_color = QtGui.QColor(255, 0, 0)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.dragging_index = None
        self.offset = None
        self.rect = None
        self.hovered_handle = None
        self.current_resize_handle = None
        self.resize_handle_radius = 10
        self.selected_rect = None

        # self.camera_res = 640
        self.ratio_w = 1
        self.ratio_h = 1

        self.image_width = 640
        self.image_height = 480

        self.text_positions = {}  # Initialize the text_positions dictionary

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        for color_name, (rect, color) in self.rectangles.items():
            if self.dragging_index == color_name:
                painter.setPen(QtGui.QPen(color, 2))  # Set the pen color and width for both the rectangle and circle
                painter.setBrush(QtCore.Qt.NoBrush)  # Set no brush (transparent fill)
                for handle in self.get_resize_handles(rect):
                    painter.drawEllipse(handle, self.resize_handle_radius, self.resize_handle_radius)

                # Draw only the border when dragging
                painter.drawRect(rect)

            else:
                if rect.contains(self.mapFromGlobal(QtGui.QCursor.pos())):
                    painter.setPen(QtGui.QPen(color, 2))  # Set the pen color and width for both the rectangle and circle
                    right_bottom = rect.bottomRight()
                    circle_center = QtCore.QPoint(int(right_bottom.x()), int(right_bottom.y()))  # Convert to integers

                    # Change circle color to match rectangle border color
                    circle_color = self.circle_colors.get(color_name, color)
                    painter.setBrush(QtGui.QColor(circle_color))  # Set brush color matching rectangle border
                    painter.drawEllipse(circle_center, self.resize_handle_radius, self.resize_handle_radius)

                    x, y = int(right_bottom.x()), int(right_bottom.y())
                    text = f"({x}, {y})"
                    text_rect = QtCore.QRect(int(right_bottom.x()) - 25, int(right_bottom.y()) + 10, 60, 30)  # Doubled text area size
                    text_color = QtGui.QColor(0, 255, 0)

                    font = QtGui.QFont()
                    font.setPointSize(6)
                    painter.setFont(font)

                    painter.setPen(text_color)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, text)

                    # Add text at the top-left corner (closer to the border)
                    top_left = rect.topLeft()
                    x1, y1 = int(top_left.x()), int(top_left.y())
                    text_top_left = f"({x1}, {y1})"
                    text_top_left_rect = QtCore.QRect(int(top_left.x()) - 30, int(top_left.y()) - 25, 60, 30)  # Adjusted text position
                    painter.drawText(text_top_left_rect, QtCore.Qt.AlignCenter, text_top_left)

                # Draw only the border when not dragging
                painter.setPen(QtGui.QPen(color, 2))  # Set the pen color and width for both the rectangle and circle
                painter.setBrush(QtCore.Qt.NoBrush)  # Set no brush (transparent fill)
                painter.drawRect(rect)

        if self.rect:
            if self.rect.contains(self.mapFromGlobal(QtGui.QCursor.pos())):
                if self.hovered_handle:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))  # Set the pen color and width for both the rectangle and circle
                    painter.setBrush(QtCore.Qt.NoBrush)  # Set no brush (transparent fill)
                    painter.drawEllipse(self.hovered_handle, self.resize_handle_radius, self.resize_handle_radius)

    def get_resize_handles(self, rect):
        handles = []
        if rect:
            x1, y1, x2, y2 = rect.getCoords()
            handles.append(QtCore.QPoint(int(x2), int(y2)))  # Bottom-right handle
        return handles

    def create_rectangle(self, color_name, camera_res, x1, y1, x2, y2, ):
        # print("type(camera_res):", type(camera_res))
        if camera_res == 640:
            self.image_width = 640
            self.image_height = 480
        elif camera_res == 1280:
            self.image_width = 1280
            self.image_height = 960
        elif camera_res == 1920:
            self.image_width = 1920
            self.image_height = 1440
        elif camera_res == 2560:
            self.image_width = 2560
            self.image_height = 1920

        self.ratio_w = 640/self.image_width
        self.ratio_h = 480/self.image_height

        # print("camera_res:", camera_res , " , self.ratio_w:", self.ratio_w, " , self.ratio_h:", self.ratio_h)
        # print("create_rectangle ==> x1:", x1, " ,y1:",y1, " ,x2:",x2 , " ,y2:",y2 , " ,color_name:", color_name)

        if color_name.name() not in self.rectangles:
            if x2 > x1 and y2 > y1:
                x1_scaled = x1 * self.ratio_w
                y1_scaled = y1 * self.ratio_h
                width_scaled = (x2 - x1) * self.ratio_w
                height_scaled = (y2 - y1) * self.ratio_h

                self.rect = QtCore.QRectF(x1_scaled, y1_scaled, width_scaled, height_scaled)
                self.rectangles[color_name.name()] = (self.rect, color_name)
                self.circle_colors[color_name.name()] = color_name.name()
                self.update()

    def mousePressEvent(self, event):
        for color_name, (rect, color) in self.rectangles.items():
            if rect.contains(event.pos()):
                self.dragging_index = color_name
                self.offset = event.pos() - rect.topLeft()
                self.current_resize_handle = self.get_resize_handle(event.pos(), rect)
                self.resize_direction = self.get_resize_direction(event.pos())

                if self.current_resize_handle:
                    self.selected_rect = rect
                    self.update()
                    break

        if not self.current_resize_handle:
            for color_name, (rect, color) in self.rectangles.items():
                if rect.contains(event.pos()):
                    self.dragging_index = color_name
                    self.offset = event.pos() - rect.topLeft()
                    self.selected_rect = rect
                    # print("The mouse click is inside an existing rectangle for dragging")
                    break

    def mouseReleaseEvent(self, event):
        self.dragging_index = None
        self.current_resize_handle = None
        self.selected_rect = None
        self.update()

    def mouseMoveEvent(self, event):
        if self.selected_rect is not None:
            if self.current_resize_handle:
                self.resize_rect(event.pos())
            else:
                rect, color = self.rectangles[self.dragging_index]
                new_top_left = event.pos() - self.offset
                rect.moveTopLeft(new_top_left)
                self.rect = rect  # Update self.rect with the resized rectangle
                self.rectangles[self.dragging_index] = (rect, color)
                self.circle_colors[self.dragging_index] = color.name()  # Update circle color to match the rectangle's color
                self.update()
                self.emit_coordinates(color, rect, "move")

    def get_resize_handle(self, pos, rect):
        for handle in self.get_resize_handles(rect):
            if QtCore.QRectF(handle.x() - self.resize_handle_radius, handle.y() - self.resize_handle_radius,
                            2 * self.resize_handle_radius, 2 * self.resize_handle_radius).contains(pos):
                return handle
        return None

    def get_resize_direction(self, pos):
        handle = self.get_resize_handle(pos, self.rect)
        if handle:
            if handle == self.rect.bottomRight():
                return "bottom_right"
        return None

    # def resize_rect(self, pos):
    #     if self.selected_rect is not None:
    #         old_rect, color = self.rectangles[self.dragging_index]
    #         print("resize_rect ==> old_rect:", old_rect)

    #         new_rect = QtCore.QRectF(old_rect)
    #         print("resize_rect ==> new_rect:", new_rect)

    #         if self.resize_direction == "bottom_right":
    #             new_rect.setBottomRight(pos)

    #         if new_rect.width() >= 1 and new_rect.height() >= 1:
    #             self.rectangles[self.dragging_index] = (new_rect, color)
    #             self.circle_color = color  # Update the circle color to match the rectangle's color
    #             self.selected_rect = new_rect
    #             self.emit_coordinates(color, new_rect, "resize")
    #             self.update()

    def resize_rect(self, pos):
        if self.selected_rect is not None:
            old_rect, color = self.rectangles[self.dragging_index]

            new_rect = QtCore.QRectF(old_rect)
            if self.resize_direction == "bottom_right":
                # Calculate the change in x2 and y2 based on the step size (640x480 label size)
                step_x = 640 / self.image_width
                step_y = 480 / self.image_height
                new_x2 = old_rect.left() + (pos.x() - old_rect.left()) // step_x * step_x
                new_y2 = old_rect.top() + (pos.y() - old_rect.top()) // step_y * step_y

                # Update the new_rect dimensions
                new_rect.setBottomRight(QtCore.QPointF(new_x2, new_y2))

            # Adjust the dimensions of the new_rect using the scaling factors
            new_rect.setWidth(new_rect.width() * self.ratio_w)
            new_rect.setHeight(new_rect.height() * self.ratio_h)

            if new_rect.width() >= 1 and new_rect.height() >= 1:
                self.rectangles[self.dragging_index] = (new_rect, color)
                self.circle_colors[self.dragging_index] = color.name()
                self.selected_rect = new_rect
                self.emit_coordinates(color, new_rect, "resize")
                self.update()


    def update_hovered_handle(self, pos):
        if self.selected_rect is not None:
            self.hovered_handle = self.get_resize_handle(pos, self.rect)
        else:
            self.hovered_handle = None

    # def emit_coordinates(self, color, rect, action):
    #     x1 = int(rect.left()/self.ratio_w)
    #     y1 = int(rect.top()/self.ratio_h)
    #     x2 = int(rect.right()/self.ratio_w)
    #     y2 = int(rect.bottom()/self.ratio_h)

    #     if x2 > x1 and y2 > y1 and (x2 < self.image_width) and (y2 < self.image_height):
    #         color_name = color.name()
    #         self.coordinates_changed.emit(color_name, x1, y1, x2, y2, action)

    def emit_coordinates(self, color, rect, action):
        step_x = 640 / self.image_width
        step_y = 480 / self.image_height

        x1 = int(rect.left() / self.ratio_w // step_x * step_x)
        y1 = int(rect.top() / self.ratio_h // step_y * step_y)
        x2 = int(rect.right() / self.ratio_w)
        y2 = int(rect.bottom() / self.ratio_h)

        if x2 > x1 and y2 > y1 and (x2 < self.image_width) and (y2 < self.image_height):
            color_name = color.name()
            self.coordinates_changed.emit(color_name, x1, y1, x2, y2, action)


# ====================================================================================================
# ====================================================================================================
class CAMSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content
        # print("self.content :", self.content)
        
        self.camera_res = self.content.camera_res

        self.title = "Camera Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 1200
        self.height = 720
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        #======================================================================
        # 
        self.lbl = QLabel("Function : " , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,5,380,25)
        self.lbl.setStyleSheet("color: white; font-size:10pt;")

        self.lbl.setText("Camera Mode : "  + self.content.camera_mode)

        #=====================================================================
        # Content.Image ImageView
        self.lbl_setting_image = QLabel("" , self)
        self.lbl_setting_image.setAlignment(Qt.AlignLeft)
        self.lbl_setting_image.setGeometry(530,5,640,480)
        self.lbl_setting_image.setStyleSheet("background-color: rgba(0, 32, 130, 225); border: 1px solid white; border-radius: 3%")
        # self.update_setting_img(self.content.setting_image)
        self.display_timer = QtCore.QTimer(self)
        self.display_timer.timeout.connect(self.update_setting_img)
        self.display_timer.setInterval(10)
        self.display_timer.start()

        # Create and set the MovableRectLabel as a child of self.lbl_setting_image
        self.resizable_rect_label = ResizableRectLabel(self.lbl_setting_image)
        self.resizable_rect_label.setGeometry(0, 0, 640, 480)  # Set the size to match self.lbl_setting_image
        self.resizable_rect_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 1px solid white; border-radius: 3%")
        self.resizable_rect_label.coordinates_changed.connect(self.handle_coordinates_changed)

        #=====================================================================
        # Barcode Reader
        self.checkBarcodeCode = QCheckBox("QR and BarCode Reader",self)
        self.checkBarcodeCode.setGeometry(10,35,380,20)
        self.checkBarcodeCode.setStyleSheet("color: lightgreen; font-size:8pt;")
        if self.content.camera_mode == "Code Reader":
            self.checkBarcodeCode.setChecked(True)

        else:
            self.checkBarcodeCode.setChecked(False)

        self.checkBarcodeCode.stateChanged.connect(self.checkBarCodeModeChange)

        # self.dbr_license_edittext = QLineEdit(self)
        # self.dbr_license_edittext.setAlignment(Qt.AlignLeft)
        # self.dbr_license_edittext.setGeometry(220,35,280,20)
        # self.dbr_license_edittext.setPlaceholderText("DBR License")
        # self.dbr_license_edittext.setStyleSheet("color: orange; font-size:8pt;")
        # self.dbr_license_edittext.setText(self.content.dbr_license)

        # self.SetBtn = QPushButton("SET", self)
        # self.SetBtn.setGeometry(510,35,30,20)

        # self.SetBtn.clicked.connect(self.setProcess)

        # Auto Connect
        self.checkAuton_Recon = QCheckBox("Auto Reconnect",self)
        self.checkAuton_Recon.setGeometry(400,35,120,20)
        self.checkAuton_Recon.setStyleSheet("color: yellow; font-size:8pt;")

        self.Interval_edit = QLineEdit("3", self)
        self.Interval_edit.setAlignment(Qt.AlignCenter)
        self.Interval_edit.setGeometry(400,70,120,25)
        self.Interval_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.Interval_edit.setPlaceholderText("Interval Minute")

        if self.content.auto_reconnect:
            self.checkAuton_Recon.setChecked(True)
            self.Interval_edit.setText(str(self.content.interval_connect))

        else:
            self.checkAuton_Recon.setChecked(False)

        self.checkAuton_Recon.stateChanged.connect(self.checkAutoReconnect)

        # Show FPS
        self.show_FPS = QCheckBox("Show FPS",self)
        self.show_FPS.setGeometry(400,105,120,20)
        self.show_FPS.setStyleSheet("color: lightgreen; font-size:8pt;")

        print("show_fps_flag :", self.content.show_fps_flag)
        if self.content.show_fps_flag:
            self.show_FPS.setChecked(True)

        else:
            self.show_FPS.setChecked(False)

        self.show_FPS.stateChanged.connect(self.check_Show_FPS)

        #=====================================================================
        # Camera Brightness
        self.checkBrightness = QCheckBox("Camera Brightness : ",self)
        self.checkBrightness.setGeometry(10,70,380,20)
        self.checkBrightness.setStyleSheet("color: lightblue; font-size:8pt;")

        self.sl = QSlider(Qt.Horizontal, self)
        self.sl.setMinimum(0)
        self.sl.setMaximum(255)
        self.sl.setValue(self.content.increase_brightness)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(1)
        self.sl.setGeometry(40,100,350,30)

        self.sl.valueChanged.connect(self.valuechange)

        if self.content.cam_inc_bright_flag:
            self.checkBrightness.setChecked(True)

        self.checkBrightness.stateChanged.connect(self.checkBrightnessChange)

        self.lbl_brn = QLabel(self)
        self.lbl_brn.setAlignment(Qt.AlignLeft)
        self.lbl_brn.setGeometry(210,70,35,20)
        self.lbl_brn.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_brn.setText(str(self.content.increase_brightness))

        #=====================================================================
        # Camera Contrast
        self.checkContrast = QCheckBox("Camera Contrast : ",self)
        self.checkContrast.setGeometry(10,150,380,20)
        self.checkContrast.setStyleSheet("color: lightblue; font-size:8pt;")

        self.slcon = QSlider(Qt.Horizontal, self)
        self.slcon.setMinimum(0)
        self.slcon.setMaximum(20)
        self.slcon.setValue(int(self.content.adjust_contrast*10))
        self.slcon.setTickPosition(QSlider.TicksBelow)
        self.slcon.setTickInterval(1)
        self.slcon.setGeometry(40,180,350,30)

        self.slcon.valueChanged.connect(self.con_valuechange)

        if self.content.cam_incCont_flag:
            self.checkContrast.setChecked(True)

        self.checkContrast.stateChanged.connect(self.checkContrastChange)

        self.lbl_contrast = QLabel(self)
        self.lbl_contrast.setAlignment(Qt.AlignLeft)
        self.lbl_contrast.setGeometry(210,150,35,20)
        self.lbl_contrast.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_contrast.setText(str(self.content.adjust_contrast))

        # ==============================================================

        self.lbl_combineID = QLabel(self)
        self.lbl_combineID.setAlignment(Qt.AlignLeft)
        self.lbl_combineID.setGeometry(40,210,350,20)
        self.lbl_combineID.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_combineID.setText("Update Combine USB Key on CH: " + str(self.content.fix_ch))


        print("CAMSetting : self.content.camera_usb_keys :", self.content.camera_usb_keys)
        self.combineID_edit = QComboBox(self)
        # self.combineID_edit.setAlignment(Qt.AlignLeft)
        self.combineID_edit.setGeometry(40,240,480,35)
        self.combineID_edit.setStyleSheet("color: red; font-size:8pt;")
        self.combineID_edit.addItems(self.content.camera_usb_keys) 

        # print("self.content.camera_box_key :", self.content.camera_box_key)
        # print("type(self.content.camera_box_key) :", type(self.content.camera_box_key))
        # if type(self.content.camera_box_key) == type(str):
        #     self.combineID_edit.setCurrentText(self.content.camera_box_key)

        # elif type(self.content.camera_box_key) == type(dict):
        #     self.content.camera_box_key = dict(self.content.camera_box_key).values()
        #     print("dict(self.content.camera_box_key).values() =", self.content.camera_box_key)

        # print("self.camera_usb_keys :", self.camera_usb_keys)
        # cam_id = self.CameraIDCombo.currentText()
        print("cam_id :", self.content.cam_id)

        # Using a loop
        for index, key in enumerate(self.content.camera_usb_keys):
            if self.content.cam_id in key:
                print("Index:", index)
                print("Full data:", key)
                break
        else:
            print("cam_id not found in camera_usb_keys")

        # Using list comprehension
        correct_camera_usb = ""
        indices = [index for index, key in enumerate(self.content.camera_usb_keys) if self.content.cam_id in key]
        if indices:
            print("Index:", indices[0])
            correct_camera_usb = self.content.camera_usb_keys[indices[0]]
            print("Full data:", correct_camera_usb)

        else:
            print("cam_id not found in camera_usb_keys")

        self.combineID_edit.setCurrentText(correct_camera_usb)

        # self.combine_cam_id.append({str(self.CamCH_Select.currentText()):str(correct_camera_usb)})
        # self.save_combine_cam_id = self.combine_cam_id

    # =============================================================
    # =============================================================
    # ROI 1 
        self.checkCameraROI = QCheckBox("Set Camera ROI",self)
        self.checkCameraROI.setGeometry(10,290,170,25)
        self.checkCameraROI.setStyleSheet("color: pink; font-size:8pt;")

        self.setROIX1_edit = QLineEdit("", self)
        self.setROIX1_edit.setAlignment(Qt.AlignCenter)
        self.setROIX1_edit.setGeometry(180,290,60,25)
        self.setROIX1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIX1_edit.setPlaceholderText("X1")

        self.setROIY1_edit = QLineEdit("", self)
        self.setROIY1_edit.setAlignment(Qt.AlignCenter)
        self.setROIY1_edit.setGeometry(250,290,60,25)
        self.setROIY1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIY1_edit.setPlaceholderText("Y1")

        self.setROIX2_edit = QLineEdit("", self)
        self.setROIX2_edit.setAlignment(Qt.AlignCenter)
        self.setROIX2_edit.setGeometry(320,290,60,25)
        self.setROIX2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIX2_edit.setPlaceholderText("X2")

        self.setROIY2_edit = QLineEdit("", self)
        self.setROIY2_edit.setAlignment(Qt.AlignCenter)
        self.setROIY2_edit.setGeometry(390,290,60,25)
        self.setROIY2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIY2_edit.setPlaceholderText("Y2")

        if self.content.setCameraROI:
            self.checkCameraROI.setChecked(True)
            self.setROIX1_edit.setText(str(self.content.setROIX1))
            self.setROIY1_edit.setText(str(self.content.setROIY1))
            self.setROIX2_edit.setText(str(self.content.setROIX2))
            self.setROIY2_edit.setText(str(self.content.setROIY2))
        else:
            self.checkCameraROI.setChecked(False)

        self.checkCameraROI.stateChanged.connect(self.add_red_rectangle)

        self.Update_ROI = QPushButton("Update", self)
        self.Update_ROI.setGeometry(460,290,60,25)
        self.Update_ROI.clicked.connect(self.onUpdateROI)

        self.comboROI1 = QComboBox(self)
        self.comboROI1.addItem("0 " + chr(176))
        self.comboROI1.addItem("90 " + chr(176))
        self.comboROI1.addItem("180 " + chr(176))
        self.comboROI1.addItem("270 " + chr(176))
        self.comboROI1.setGeometry(40,325,100,25)
        self.comboROI1.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 
        # print("self.content.rotateROI1:", self.content.rotateROI1)
        if len(self.content.rotateROI1) > 0:
            self.comboROI1.setCurrentText(self.content.rotateROI1 + " " + chr(176))
        
        self.comboROI1.activated[str].connect(self.onChangedROI1)

        self.CustomA_ROI1_edit = QLineEdit("", self)
        self.CustomA_ROI1_edit.setAlignment(Qt.AlignCenter)
        self.CustomA_ROI1_edit.setGeometry(160,325,60,25)
        self.CustomA_ROI1_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.CustomA_ROI1_edit.setPlaceholderText("Angle")

        # print("self.content.custom_angleROI1:", self.content.custom_angleROI1 , " ,self.content.angle_ROI1:", self.content.angle_ROI1)
        if self.content.custom_angleROI1:
            if len(str(self.content.angle_ROI1)) > 0:
                self.CustomA_ROI1_edit.setText(str(self.content.angle_ROI1))
                self.comboROI1.setEnabled(False)

        self.CustomA_ROI1_edit.textChanged.connect(self.ChangedCustomAnglROI1)

        self.ReverseCameraROI1 = QCheckBox("Revert Angle",self)
        self.ReverseCameraROI1.setGeometry(240,325,120,25)
        self.ReverseCameraROI1.setStyleSheet("color: lightblue; font-size:7pt;")
        self.ReverseCameraROI1.stateChanged.connect(self.checkConvertROI1)

        self.setRefColorROI1_edit = QLineEdit("", self)
        self.setRefColorROI1_edit.setAlignment(Qt.AlignCenter)
        self.setRefColorROI1_edit.setGeometry(370,325,150,25)
        self.setRefColorROI1_edit.setStyleSheet("color: lightblue; font-size:7pt;")
        self.setRefColorROI1_edit.setPlaceholderText("Referent Color")

        print("self.content.convert_angle_ROI1:", self.content.convert_angle_ROI1, " , self.content.color_refROI1:", self.content.color_refROI1)
        if self.content.convert_angle_ROI1:
            self.ReverseCameraROI1.setChecked(True)
            if len(self.content.color_refROI1) > 0:
                self.setRefColorROI1_edit.setText(str(self.content.color_refROI1))

    # ==============================================================
    # ==============================================================
    # ROI 2
        self.checkCameraROI2 = QCheckBox("Set Camera ROI2",self)
        self.checkCameraROI2.setGeometry(10,360,170,25)
        self.checkCameraROI2.setStyleSheet("color: pink; font-size:8pt;")

        self.setROI2X1_edit = QLineEdit("", self)
        self.setROI2X1_edit.setAlignment(Qt.AlignCenter)
        self.setROI2X1_edit.setGeometry(180,360,60,25)
        self.setROI2X1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI2X1_edit.setPlaceholderText("X1")

        self.setROI2Y1_edit = QLineEdit("", self)
        self.setROI2Y1_edit.setAlignment(Qt.AlignCenter)
        self.setROI2Y1_edit.setGeometry(250,360,60,25)
        self.setROI2Y1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI2Y1_edit.setPlaceholderText("Y1")

        self.setROI2X2_edit = QLineEdit("", self)
        self.setROI2X2_edit.setAlignment(Qt.AlignCenter)
        self.setROI2X2_edit.setGeometry(320,360,60,25)
        self.setROI2X2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI2X2_edit.setPlaceholderText("X2")

        self.setROI2Y2_edit = QLineEdit("", self)
        self.setROI2Y2_edit.setAlignment(Qt.AlignCenter)
        self.setROI2Y2_edit.setGeometry(390,360,60,25)
        self.setROI2Y2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI2Y2_edit.setPlaceholderText("Y2")

        if self.content.setCameraROI2:
            self.checkCameraROI2.setChecked(True)
            self.setROI2X1_edit.setText(str(self.content.setROI2X1))
            self.setROI2Y1_edit.setText(str(self.content.setROI2Y1))
            self.setROI2X2_edit.setText(str(self.content.setROI2X2))
            self.setROI2Y2_edit.setText(str(self.content.setROI2Y2))
        else:
            self.checkCameraROI2.setChecked(False)

        self.checkCameraROI2.stateChanged.connect(self.add_yellow_rectangle)

        self.Update_ROI2 = QPushButton("Update", self)
        self.Update_ROI2.setGeometry(460,360,60,25)
        self.Update_ROI2.clicked.connect(self.onUpdateROI2)

        self.comboROI2 = QComboBox(self)
        self.comboROI2.addItem("0 " + chr(176))
        self.comboROI2.addItem("90 " + chr(176))
        self.comboROI2.addItem("180 " + chr(176))
        self.comboROI2.addItem("270 " + chr(176))
        self.comboROI2.setGeometry(40,395,100,25)
        self.comboROI2.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 
        if len(self.content.rotateROI2) > 0:
            self.comboROI2.setCurrentText(self.content.rotateROI2 + " " + chr(176))
        
        self.comboROI2.activated[str].connect(self.onChangedROI2)

        self.CustomA_ROI2_edit = QLineEdit("", self)
        self.CustomA_ROI2_edit.setAlignment(Qt.AlignCenter)
        self.CustomA_ROI2_edit.setGeometry(160,395,60,25)
        self.CustomA_ROI2_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.CustomA_ROI2_edit.setPlaceholderText("Angle")

        # print("self.content.custom_angleROI2:", self.content.custom_angleROI2 , " ,self.content.angle_ROI2:", self.content.angle_ROI2)
        if self.content.custom_angleROI2:
            if len(str(self.content.angle_ROI2)) > 0:
                self.CustomA_ROI2_edit.setText(str(self.content.angle_ROI2))
                self.comboROI2.setEnabled(False)

        self.CustomA_ROI2_edit.textChanged.connect(self.ChangedCustomAnglROI2)

        self.ReverseCameraROI2 = QCheckBox("Revert Angle",self)
        self.ReverseCameraROI2.setGeometry(240,395,120,25)
        self.ReverseCameraROI2.setStyleSheet("color: lightblue; font-size:7pt;")
        self.ReverseCameraROI2.stateChanged.connect(self.checkConvertROI2)

        self.setRefColorROI2_edit = QLineEdit("", self)
        self.setRefColorROI2_edit.setAlignment(Qt.AlignCenter)
        self.setRefColorROI2_edit.setGeometry(370,395,150,25)
        self.setRefColorROI2_edit.setStyleSheet("color: lightblue; font-size:7pt;")
        self.setRefColorROI2_edit.setPlaceholderText("Referent Color")

        print("self.content.convert_angle_ROI2:", self.content.convert_angle_ROI2, " , self.content.color_refROI2:", self.content.color_refROI2)
        if self.content.convert_angle_ROI2:
            self.ReverseCameraROI2.setChecked(True)
            if len(self.content.color_refROI2) > 0:
                self.setRefColorROI2_edit.setText(str(self.content.color_refROI2))

    # ==============================================================
    # ==============================================================
    # ROI 3
        self.checkCameraROI3 = QCheckBox("Set Camera ROI3",self)
        self.checkCameraROI3.setGeometry(10,430,170,25)
        self.checkCameraROI3.setStyleSheet("color: pink; font-size:8pt;")

        self.setROI3X1_edit = QLineEdit("", self)
        self.setROI3X1_edit.setAlignment(Qt.AlignCenter)
        self.setROI3X1_edit.setGeometry(180,430,60,25)
        self.setROI3X1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI3X1_edit.setPlaceholderText("X1")

        self.setROI3Y1_edit = QLineEdit("", self)
        self.setROI3Y1_edit.setAlignment(Qt.AlignCenter)
        self.setROI3Y1_edit.setGeometry(250,430,60,25)
        self.setROI3Y1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI3Y1_edit.setPlaceholderText("Y1")

        self.setROI3X2_edit = QLineEdit("", self)
        self.setROI3X2_edit.setAlignment(Qt.AlignCenter)
        self.setROI3X2_edit.setGeometry(320,430,60,25)
        self.setROI3X2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI3X2_edit.setPlaceholderText("X2")

        self.setROI3Y2_edit = QLineEdit("", self)
        self.setROI3Y2_edit.setAlignment(Qt.AlignCenter)
        self.setROI3Y2_edit.setGeometry(390,430,60,25)
        self.setROI3Y2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROI3Y2_edit.setPlaceholderText("Y2")

        if self.content.setCameraROI3:
            self.checkCameraROI3.setChecked(True)
            self.setROI3X1_edit.setText(str(self.content.setROI3X1))
            self.setROI3Y1_edit.setText(str(self.content.setROI3Y1))
            self.setROI3X2_edit.setText(str(self.content.setROI3X2))
            self.setROI3Y2_edit.setText(str(self.content.setROI3Y2))
        else:
            self.checkCameraROI3.setChecked(False)

        self.checkCameraROI3.stateChanged.connect(self.add_blue_rectangle)

        self.Update_ROI3 = QPushButton("Update", self)
        self.Update_ROI3.setGeometry(460,430,60,25)
        self.Update_ROI3.clicked.connect(self.onUpdateROI3)

        self.comboROI3 = QComboBox(self)
        self.comboROI3.addItem("0 " + chr(176))
        self.comboROI3.addItem("90 " + chr(176))
        self.comboROI3.addItem("180 " + chr(176))
        self.comboROI3.addItem("270 " + chr(176))
        self.comboROI3.setGeometry(40,465,100,25)
        self.comboROI3.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 
        
        if len(self.content.rotateROI3) > 0:
            self.comboROI3.setCurrentText(self.content.rotateROI3 + " " + chr(176))
    
        self.comboROI3.activated[str].connect(self.onChangedROI3)

        self.CustomA_ROI3_edit = QLineEdit("", self)
        self.CustomA_ROI3_edit.setAlignment(Qt.AlignCenter)
        self.CustomA_ROI3_edit.setGeometry(160,465,60,25)
        self.CustomA_ROI3_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.CustomA_ROI3_edit.setPlaceholderText("Angle")

        # print("self.content.custom_angleROI3:", self.content.custom_angleROI3 , " ,self.content.angle_ROI3:", self.content.angle_ROI3)
        if self.content.custom_angleROI3:
            if len(str(self.content.angle_ROI3)) > 0:
                self.CustomA_ROI3_edit.setText(str(self.content.angle_ROI3))
                self.comboROI3.setEnabled(False)

        self.CustomA_ROI3_edit.textChanged.connect(self.ChangedCustomAnglROI3)

        self.ReverseCameraROI3 = QCheckBox("Revert Angle",self)
        self.ReverseCameraROI3.setGeometry(240,465,120,25)
        self.ReverseCameraROI3.setStyleSheet("color: lightblue; font-size:7pt;")
        self.ReverseCameraROI3.stateChanged.connect(self.checkConvertROI3)

        self.setRefColorROI3_edit = QLineEdit("", self)
        self.setRefColorROI3_edit.setAlignment(Qt.AlignCenter)
        self.setRefColorROI3_edit.setGeometry(370,465,150,25)
        self.setRefColorROI3_edit.setStyleSheet("color: lightblue; font-size:7pt;")
        self.setRefColorROI3_edit.setPlaceholderText("Referent Color")

        print("self.content.convert_angle_ROI3:", self.content.convert_angle_ROI3, " , self.content.color_refROI3:", self.content.color_refROI3)
        if self.content.convert_angle_ROI3:
            self.ReverseCameraROI3.setChecked(True)
            if len(self.content.color_refROI3) > 0:
                self.setRefColorROI3_edit.setText(str(self.content.color_refROI3))

        self.Update_New_Camera = QPushButton("Scan New Camera", self)
        self.Update_New_Camera.setGeometry(40,510,480,40)
        self.Update_New_Camera.clicked.connect(self.onUpdateNew_Camera)

        self.lbl_usb_connect = QLabel(self)
        self.lbl_usb_connect.setAlignment(Qt.AlignLeft)
        self.lbl_usb_connect.setGeometry(530,510,640,40)
        self.lbl_usb_connect.setStyleSheet("color: yellow; font-size:12pt;")
        self.lbl_usb_connect.setText("USB Camera in System : " + str(self.content.all_usb_cameras))

        # self.Test_Camera = QPushButton("test Camera", self)
        # self.Test_Camera.setGeometry(40,560,100,40)
        # self.Test_Camera.clicked.connect(self.onTest_Camera)

    # End UI Interface
    # ==============================================================================
    def onTest_Camera(self):
        ...
  
    def checkAutoReconnect(self, state):
        if state == QtCore.Qt.Checked:
            self.content.auto_reconnect = True
            self.Interval_edit.setText(str(self.content.interval_connect))
        else:
            self.content.auto_reconnect = False

    def check_Show_FPS(self, state):
        if state == QtCore.Qt.Checked:
            self.content.show_fps_flag = True
        else:
            self.content.show_fps_flag = False
        
    def onUpdateNew_Camera(self):
        self.content.CamCH_Select.clear()
        self.content.CameraIDCombo.clear()

        # self.content.combine_cam_id[0] = ""
        self.content.all_usb_cameras = self.content.find_usb_cameras()
        self.content.camera_usb_keys = self.content.scan_usb_cameras()

        self.combineID_edit.clear()
        self.combineID_edit.addItems(self.content.camera_usb_keys) 

        # self.content.CamCH_Select.addItem('screen cap')
        self.lbl_usb_connect.setText("USB Camera in System : " + str(self.content.all_usb_cameras))

    def add_red_rectangle(self, state):
        if state == QtCore.Qt.Checked:
            self.content.setCameraROI = True
            # self.resizable_rect_label.set_current_color(QtGui.QColor(255, 0, 0))
            self.resizable_rect_label.create_rectangle(QtGui.QColor(255, 0, 0), int(self.camera_res), self.content.setROIX1, self.content.setROIY1, self.content.setROIX2, self.content.setROIY2)
            self.resizable_rect_label.update()

            self.setROIX1_edit.setText(str(self.content.setROIX1))
            self.setROIY1_edit.setText(str(self.content.setROIY1))
            self.setROIX2_edit.setText(str(self.content.setROIX2))
            self.setROIY2_edit.setText(str(self.content.setROIY2))
            self.content.lbl_ROI1.setVisible(True)
        else:
            self.content.setCameraROI = False
            self.content.lbl_ROI1.setVisible(False)

    def add_yellow_rectangle(self, state):
        if state == QtCore.Qt.Checked:
            self.content.setCameraROI2 = True
            # self.resizable_rect_label.set_current_color(QtGui.QColor(255, 255, 0))
            self.resizable_rect_label.create_rectangle(QtGui.QColor(255, 255, 0), int(self.camera_res), self.content.setROI2X1, self.content.setROI2Y1, self.content.setROI2X2, self.content.setROI2Y2)
            self.resizable_rect_label.update()

            self.setROI2X1_edit.setText(str(self.content.setROI2X1))
            self.setROI2Y1_edit.setText(str(self.content.setROI2Y1))
            self.setROI2X2_edit.setText(str(self.content.setROI2X2))
            self.setROI2Y2_edit.setText(str(self.content.setROI2Y2))
            self.content.lbl_ROI2.setVisible(True)
        else:
            self.content.setCameraROI2 = False
            self.content.lbl_ROI2.setVisible(False)

    def add_blue_rectangle(self, state):
        if state == QtCore.Qt.Checked:
            self.content.setCameraROI3 = True
            # self.resizable_rect_label.set_current_color(QtGui.QColor(0, 0, 255))
            self.resizable_rect_label.create_rectangle(QtGui.QColor(0, 0, 255), int(self.camera_res), self.content.setROI3X1, self.content.setROI3Y1, self.content.setROI3X2, self.content.setROI3Y2)
            self.resizable_rect_label.update()

            self.setROI3X1_edit.setText(str(self.content.setROI3X1))
            self.setROI3Y1_edit.setText(str(self.content.setROI3Y1))
            self.setROI3X2_edit.setText(str(self.content.setROI3X2))
            self.setROI3Y2_edit.setText(str(self.content.setROI3Y2))
            self.content.lbl_ROI3.setVisible(True)
        else:
            self.content.setCameraROI3 = False
            self.content.lbl_ROI3.setVisible(False)

    def handle_coordinates_changed(self, color, x1, y1, x2, y2, action):
        # print("====================================================")
        # print(f'Color: {color}, x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}, Action: {action}')
        if str(color) == "#ff0000":
            # print("Select Red Rectangle")
            self.setROIX1_edit.setText(str(x1))
            self.setROIY1_edit.setText(str(y1))
            self.setROIX2_edit.setText(str(x2))
            self.setROIY2_edit.setText(str(y2))

        elif str(color) == "#ffff00":
            # print("Select Yellow Rectangle")
            self.setROI2X1_edit.setText(str(x1))
            self.setROI2Y1_edit.setText(str(y1))
            self.setROI2X2_edit.setText(str(x2))
            self.setROI2Y2_edit.setText(str(y2))

        elif str(color) == "#0000ff":
            # print("Select Blue Rectangle")
            self.setROI3X1_edit.setText(str(x1))
            self.setROI3Y1_edit.setText(str(y1))
            self.setROI3X2_edit.setText(str(x2))
            self.setROI3Y2_edit.setText(str(y2))

        # Find the color rectangle based on the color
        for color_name, (rect, rect_color) in self.resizable_rect_label.rectangles.items():
            if rect_color.name() == color:
                # print(f'Found matching color: {color_name}')
                if action == "resize":
                    # print('Performing resize operation')
                    # Calculate the new rectangle
                    new_rect = QtCore.QRectF(x1, y1, x2 - x1, y2 - y1)
                    # print(f'Old Rectangle: {rect}')
                    # print(f'New Rectangle: {new_rect}')
                    
                    # Update the color rectangle's size and position
                    self.resizable_rect_label.rectangles[color_name] = (new_rect, rect_color)
                    # print(f'Updated Rectangle: {self.resizable_rect_label.rectangles[color_name][0]}')

                    # Update the UI
                    self.resizable_rect_label.update()
                    # break


    # # ==============================================================
    # #ROI1
    def onUpdateROI(self):
        self.content.setROIX1 = int(self.setROIX1_edit.text())
        self.content.setROIY1 = int(self.setROIY1_edit.text())
        self.content.setROIX2 = int(self.setROIX2_edit.text())
        self.content.setROIY2 = int(self.setROIY2_edit.text())
        if len(self.setRefColorROI1_edit.text()) > 0 and self.setRefColorROI1_edit.text().isnumeric(): self.content.color_refROI1 = self.setRefColorROI1_edit.text()

    # #ROI2
    def onUpdateROI2(self):
        self.content.setROI2X1 = int(self.setROI2X1_edit.text())
        self.content.setROI2Y1 = int(self.setROI2Y1_edit.text())
        self.content.setROI2X2 = int(self.setROI2X2_edit.text())
        self.content.setROI2Y2 = int(self.setROI2Y2_edit.text())
        if len(self.setRefColorROI2_edit.text()) > 0 and self.setRefColorROI2_edit.text().isnumeric(): self.content.color_refROI2 = self.setRefColorROI2_edit.text()

    # #ROI3

    def onUpdateROI3(self):
        self.content.setROI3X1 = int(self.setROI3X1_edit.text())
        self.content.setROI3Y1 = int(self.setROI3Y1_edit.text())
        self.content.setROI3X2 = int(self.setROI3X2_edit.text())
        self.content.setROI3Y2 = int(self.setROI3Y2_edit.text())
        if len(self.setRefColorROI3_edit.text()) > 0 and self.setRefColorROI3_edit.text().isnumeric(): self.content.color_refROI3 = self.setRefColorROI3_edit.text()

    def onChangedROI1(self, text):
        # print("onChangedROI1 ==> text:", text[:-2])
        self.content.rotateROI1 = str(text[:-2])

    def onChangedROI2(self, text):
        # print("onChangedROI2 ==> text:", text[:-2])
        self.content.rotateROI2 = str(text[:-2])

    def onChangedROI3(self, text):
        # print("onChangedROI3 ==> text:", text[:-2])
        self.content.rotateROI3 = str(text[:-2])
    
    # ==============================================================
    # ==============================================================
    def checkBarCodeModeChange(self, state):
        if state == QtCore.Qt.Checked:
            self.content.camera_mode = "Code Reader"
        else:
            self.content.camera_mode = ""

        self.lbl.setText("Camera Mode : "  + self.content.camera_mode)

    # ===========================================================
    def checkBrightnessChange(self, state):
        if state == QtCore.Qt.Checked:
            self.content.cam_inc_bright_flag = True
        else:
            self.content.cam_inc_bright_flag = False

    def valuechange(self):
        self.content.increase_brightness = self.sl.value()
        self.lbl_brn.setText(str(self.content.increase_brightness))

    # ===========================================================
    def checkContrastChange(self, state):
        if state == QtCore.Qt.Checked:
            self.content.cam_incCont_flag = True
        else:
            self.content.cam_incCont_flag = False

    def con_valuechange(self):
        value  = self.slcon.value()
        self.content.adjust_contrast = float(value/10)
        self.lbl_contrast.setText(str(self.content.adjust_contrast))


    # def setProcess(self):
    #     # BarcodeReader.init_license(self.content.dbr_license)
    #     ...

    # ===========================================================
    def update_setting_img(self):
        if type(self.content.setting_image) != type(None):
            img = self.content.setting_image
            img_height, img_width, img_colors = img.shape
            scale_w = float(640) / float(img_width)
            scale_h = float(480) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1
            
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)

            self.lbl_setting_image.setPixmap(QtGui.QPixmap.fromImage(image))

    # ============================================================
    def ChangedCustomAnglROI1(self):
        if len(self.CustomA_ROI1_edit.text()) > 0 and len(self.CustomA_ROI1_edit.text()) <= 3:
            if self.CustomA_ROI1_edit.text().isnumeric():
                self.content.angle_ROI1 = self.CustomA_ROI1_edit.text()
                self.content.custom_angleROI1 = True
                self.comboROI1.setEnabled(False)

        elif len(self.CustomA_ROI1_edit.text()) == 0:
            self.content.custom_angleROI1 = False
            self.comboROI1.setEnabled(True)

    def ChangedCustomAnglROI2(self):
        if len(self.CustomA_ROI2_edit.text()) > 0 and len(self.CustomA_ROI2_edit.text()) <= 3:
            if self.CustomA_ROI2_edit.text().isnumeric():
                self.content.angle_ROI2 = self.CustomA_ROI2_edit.text()
                self.content.custom_angleROI2 = True
                self.comboROI2.setEnabled(False)

        elif len(self.CustomA_ROI2_edit.text()) == 0:
            self.content.custom_angleROI2 = False
            self.comboROI2.setEnabled(True)


    def ChangedCustomAnglROI3(self):
        if len(self.CustomA_ROI3_edit.text()) > 0 and len(self.CustomA_ROI3_edit.text()) <= 3:
            if self.CustomA_ROI3_edit.text().isnumeric():
                self.content.angle_ROI3 = self.CustomA_ROI3_edit.text()
                self.content.custom_angleROI3 = True
                self.comboROI1.setEnabled(False)

        elif len(self.CustomA_ROI3_edit.text()) == 0:
            self.content.custom_angleROI3 = False
            self.comboROI3.setEnabled(True)

    # ============================================================
    def checkConvertROI1(self, state):
        if state == QtCore.Qt.Checked:
            self.content.convert_angle_ROI1 = True
            if len(self.setRefColorROI1_edit.text()) > 0 and self.setRefColorROI1_edit.text().isnumeric():
                self.content.color_refROI1 = self.setRefColorROI1_edit.text()
        else:
            self.content.convert_angle_ROI1 = False

    def checkConvertROI2(self, state):
        if state == QtCore.Qt.Checked:
            self.content.convert_angle_ROI2 = True
            if len(self.setRefColorROI2_edit.text()) > 0 and self.setRefColorROI2_edit.text().isnumeric():
                self.content.color_refROI2 = self.setRefColorROI2_edit.text()
        else:
            self.content.convert_angle_ROI2 = False

    def checkConvertROI3(self, state):
        if state == QtCore.Qt.Checked:
            self.content.convert_angle_ROI3 = True
            if len(self.setRefColorROI3_edit.text()) > 0 and self.setRefColorROI3_edit.text().isnumeric():
                self.content.color_refROI3 = self.setRefColorROI3_edit.text()
        else:
            self.content.convert_angle_ROI3 = False

    # ============================================================

    def closeEvent(self, event):
        print("Camera Mode :", self.content.camera_mode)
        print("increase_brightness : ", self.content.increase_brightness)

        if len(self.content.combine_cam_id) > 0:
            self.content.combine_cam_id[0] = ({str(self.content.fix_ch):str(self.combineID_edit.currentText())})
        else:
            self.content.combine_cam_id.append({str(self.content.fix_ch):str(self.combineID_edit.currentText())})

        #self.content.scan_combine()
        print("\033[94m {}\033[00m".format("closeEvent; Keep New --> combine_cam_id :" + str(self.content.combine_cam_id)))
        self.content.CameraIDCombo.setCurrentText(str(self.combineID_edit.currentText()[-17:]))
        self.content.CameraIDCombo.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:7pt;color:white; border: 1px solid white; border-radius: 3%;")

        self.content.CamCH_Select.setCurrentText(self.content.fix_ch) 
        self.content.save_combine_cam_id = self.content.combine_cam_id

        # if len(self.combineID_edit.text()) > 0:
        #     # record_combine_cam_id
        #     self.content.record_combine_cam_id[0][str(self.content.edit.text())] = self.combineID_edit.text()

        # if len(self.content.update_new_usb) > 0:
        #     self.content.combine_cam_id[0][str(self.content.fix_ch)] =  self.content.update_new_usb

        # self.content.dbr_license = self.dbr_license_edittext.text()
        self.content.SettingBtn.setEnabled(True)
        self.content.interval_connect = int(self.Interval_edit.text())

        #ROI1
        if len(self.setROIX1_edit.text()) > 0 and self.setROIX1_edit.text().isnumeric(): self.content.setROIX1 = int(self.setROIX1_edit.text())
        if len(self.setROIY1_edit.text()) > 0 and self.setROIY1_edit.text().isnumeric(): self.content.setROIY1 = int(self.setROIY1_edit.text())
        if len(self.setROIX2_edit.text()) > 0 and self.setROIX2_edit.text().isnumeric(): self.content.setROIX2 = int(self.setROIX2_edit.text())
        if len(self.setROIY2_edit.text()) > 0 and self.setROIY2_edit.text().isnumeric(): self.content.setROIY2 = int(self.setROIY2_edit.text())

        #ROI2
        if len(self.setROI2X1_edit.text()) > 0 and self.setROI2X1_edit.text().isnumeric(): self.content.setROI2X1 = int(self.setROI2X1_edit.text())
        if len(self.setROI2Y1_edit.text()) > 0 and self.setROI2Y1_edit.text().isnumeric(): self.content.setROI2Y1 = int(self.setROI2Y1_edit.text())
        if len(self.setROI2X2_edit.text()) > 0 and self.setROI2X2_edit.text().isnumeric(): self.content.setROI2X2 = int(self.setROI2X2_edit.text())
        if len(self.setROI2Y2_edit.text()) > 0 and self.setROI2Y2_edit.text().isnumeric(): self.content.setROI2Y2 = int(self.setROI2Y2_edit.text())

        #ROI3
        if len(self.setROI3X1_edit.text()) > 0 and self.setROI3X1_edit.text().isnumeric(): self.content.setROI3X1 = int(self.setROI3X1_edit.text())
        if len(self.setROI3Y1_edit.text()) > 0 and self.setROI3Y1_edit.text().isnumeric(): self.content.setROI3Y1 = int(self.setROI3Y1_edit.text())
        if len(self.setROI3X2_edit.text()) > 0 and self.setROI3X2_edit.text().isnumeric(): self.content.setROI3X2 = int(self.setROI3X2_edit.text())
        if len(self.setROI3Y2_edit.text()) > 0 and self.setROI3Y2_edit.text().isnumeric(): self.content.setROI3Y2 = int(self.setROI3Y2_edit.text())

        if len(self.CustomA_ROI1_edit.text()) > 0 and len(self.CustomA_ROI1_edit.text()) <= 3 and self.CustomA_ROI1_edit.text().isnumeric(): self.content.angle_ROI1 = self.CustomA_ROI1_edit.text()
        if len(self.CustomA_ROI2_edit.text()) > 0 and len(self.CustomA_ROI2_edit.text()) <= 3 and self.CustomA_ROI2_edit.text().isnumeric(): self.content.angle_ROI2 = self.CustomA_ROI2_edit.text()
        if len(self.CustomA_ROI3_edit.text()) > 0 and len(self.CustomA_ROI3_edit.text()) <= 3 and self.CustomA_ROI3_edit.text().isnumeric(): self.content.angle_ROI3 = self.CustomA_ROI3_edit.text()

        if len(self.setRefColorROI1_edit.text()) > 0 and self.setRefColorROI1_edit.text().isnumeric(): self.content.color_refROI1 = self.setRefColorROI1_edit.text()
        if len(self.setRefColorROI2_edit.text()) > 0 and self.setRefColorROI2_edit.text().isnumeric(): self.content.color_refROI2 = self.setRefColorROI2_edit.text()
        if len(self.setRefColorROI3_edit.text()) > 0 and self.setRefColorROI3_edit.text().isnumeric(): self.content.color_refROI3 = self.setRefColorROI3_edit.text()

        self.display_timer.stop()

# ========================================================================================================
# ========================================================================================================

@register_node(OP_NODE_CAMINPUT)
class Open_CAM(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_cam3.png"
    #print("icon cam2.png = " , icon)
    op_code = OP_NODE_CAMINPUT
    op_title = "Camera"
    content_label_objname = "Cam Process"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4,5], outputs=[3,4,5,6])
        self.payload = {}
        self.payload['fps'] = 1
        self.payload['blink'] = True

        self.payload['run'] = False
        self.payload['stop'] = False
        self.payload['inputtype'] = "img"
        self.payload['centers'] = {15: (0, 0), 16: (0, 0)}
        self.payload['img_h'] = 480
        self.payload['img_w'] = 640

        self.payload['img'] = None

        self.payload_roi = {}
        self.payload_roi['inputtype'] = "img"
        self.payload_roi['blink'] = True
        self.payload_roi['run'] = False

        self.payload_roi['img_h'] = 480
        self.payload_roi['img_w'] = 640

        self.payload_roi['fps'] = 1

        # h, w, c = image.shape
        self.process_capture = False
        self.process_video = False
        self.Add_Camera_List = False

        self.Start_Video = False

        self.input_sanp_payload = {}
        self.input_vdo_payload = {}

        # self.cam_ch = 0
        self.Sigle_SnapInput = False

        self.confirm_submit_true = False
        self.start_command = False
        self.start_MQTTCommand = False

        # self.cnt_frame = 0
        # self.prev_frame = None
        # self.current_frame = None

        # self.first_read = False

        self.ack_onetime = False
        self.camera_frezz = False
        self.missing_ch = []

        self.show_disconnect = False
        self.discon_image = None

        self.do_one_round = False
        self.Interval_recon = 60

        self.from_freeze = False
        self.freez_cnt = 0
        self.first_freezing_cam = False

    def initInnerClasses(self):
        self.content = CameraID(self)
        self.grNode = FlowGraphics150x150Process(self)

        self.content.Camera_timer.timeout.connect(self.update_frame)
        self.content.Camera_timer.setInterval(50)

        self.content.USBScan_timer.timeout.connect(self.update_USB)
        self.content.USBScan_timer.setInterval(50)

        self.content.radioState.toggled.connect(self.onClicked)
        self.content.combo.activated[str].connect(self.onChanged)
        """self.content.checkFlip.stateChanged.connect(self.setFlipCam)
        self.content.checkMirror.stateChanged.connect(self.setMirrorCam)"""

        self.content.ResCombo.activated[str].connect(self.onResolutionChanged)

        self.content.CamCH_Select.activated[str].connect(self.ChangedChanel)
        self.content.Capture.clicked.connect(self.cameraCapture)

        self.content.CameraIDCombo.activated[str].connect(self.onChangeCam_ID)

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

        self.content.Camera_find_recovery.timeout.connect(self.update_recovery_cam)
        self.content.Camera_find_recovery.setInterval(10000)

        self.content.Camera_autoRE_timer.timeout.connect(self.auto_recon_cam)

        self.Interval_recon = int(self.content.interval_connect * 60000)
        print("initInnerClasses -> self.Interval_recon :", self.Interval_recon)
        self.content.Camera_autoRE_timer.setInterval(self.Interval_recon)

        """self.camera_CH = self.content.edit.text()
        print("Camera Capture CH = " , self.camera_CH)"""

        # usb_cnt = 0
        
        # wmi = win32com.client.GetObject ("winmgmts:")
        # for usb in wmi.InstancesOf ("Win32_USBHub"):
        #     usb_cnt += 1
        #     print(usb.DeviceID)

        # all_camera_idx_available = []

        # for camera_idx in range(usb_cnt):
        #     self.content.CamCapture = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW) #captureDevice = camera)
        #     if not self.CamCapture.isOpened():
        #         camera_idx += 1
            
        #     if self.CamCapture.isOpened():
        #         print(f'Camera index available: {camera_idx}')
        #         self.camera_CH = camera_idx
        #         all_camera_idx_available.append(camera_idx)
        #         #self.content.CamCapture.release()
        #         break

        # #self.content.CamCapture = cv2.VideoCapture(int(self.camera_CH))

        # self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))
        # # self.content.CamCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.content.CamCapture.set(cv2.CAP_PROP_FPS, 30)

        # self.content.edit.setText(str(self.camera_CH))

        self.Global = GlobalVariable()

        # self.grNode_addr = str(self.grNode)[-13:-1]
        # self.Camera_ID = "CameraBox_ID" + self.grNode_addr
        # print("self.Camera_ID : ", self.Camera_ID)

        # print("Node ID:", str(self.id))
        self.Camera_ID = str(self.id)

        self.ListGlobalCameraBox = []
        self.ListGlobalUSBDevice = []

        self.ListGlobalCamera = []

        if not self.content.StartfromSave:
            if self.Global.hasGlobal("GlobalCameraBoxID"):
                self.ListGlobalCameraBox = list(self.Global.getGlobal("GlobalCameraBoxID"))

                self.ListGlobalCameraBox.append(self.Camera_ID)
                self.Global.setGlobal("GlobalCameraBoxID", self.ListGlobalCameraBox)

                print("New Append Camera :", self.ListGlobalCameraBox)

            else:
                self.ListGlobalCameraBox.append(self.Camera_ID)
                self.Global.setGlobal("GlobalCameraBoxID", self.ListGlobalCameraBox)

                print("Update Camera List :", self.ListGlobalCameraBox)
                print("Scan All USB List in System")

                wmi = win32com.client.GetObject ("winmgmts:")
                for usb in wmi.InstancesOf ("Win32_USBHub"):
                    self.content.usb_cnt += 1
                    # print(usb.DeviceID)
                    self.ListGlobalUSBDevice.append(usb.DeviceID)

                    print("\033[93m {}\033[00m".format(str(usb.DeviceID)))

                self.ListGlobalUSBDevice = list(dict.fromkeys(self.ListGlobalUSBDevice))
                self.Global.setGlobal("ListGlobalUSBDevice", self.ListGlobalUSBDevice)
                print("self.ListGlobalUSBDevice :", self.ListGlobalUSBDevice)

            # self.content.camera_usb_keys = self.content.scan_usb_cameras()
            self.content.camera_usb_keys = list(dict.fromkeys(self.content.camera_usb_keys))
            # self.Global.setGlobal("Scan_USB_CameraSys :", self.content.camera_usb_keys)

            print("self.content.camera_usb_keys :", self.content.camera_usb_keys)

            # Clear combine_cam_id[0]
            # self.content.combine_cam_id[0] = ""
            # self.content.scan_combine()

    def update_recovery_cam(self):
        self.content.all_usb_cameras = self.content.find_usb_cameras()
        # print("self.content.camera_usb_keys :", self.content.camera_usb_keys)
        if len(self.content.all_usb_cameras) > len(self.content.camera_usb_keys):
            self.content.camera_usb_keys = self.content.scan_usb_cameras()
            if self.content.missing_Cam_key in self.content.camera_usb_keys:
                print("\033[91m {}\033[00m".format(f"Found New Recovery Camera which is record id ---> Force Restart Program"))
                self.restart_program()

    def restart_program(self):
        python = sys.executable
        # os.execl(python, python, *sys.argv)
        os.execl(python, python, '"' + sys.argv[0] + '"', *sys.argv[1:])

    def auto_recon_cam(self):
        self.Add_Camera_List = True
        self.StartRuuningCam()

        self.do_one_round = False
        self.content.Camera_autoRE_timer.stop()

        # print("Auto Reconnect !!", str(datetime.now().strftime("%Y-%m-%d %H:%M%S")))

    def evalImplementation(self):
        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.Sigle_SnapInput = False

        else:
            self.input_sanp_payload = input_node.eval()

            if self.input_sanp_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.Sigle_SnapInput = False

            elif type(self.input_sanp_payload) != type(None):
                if 'submit' in self.input_sanp_payload:
                    if self.input_sanp_payload['submit'] and not self.Sigle_SnapInput:
                        self.Sigle_SnapInput = True
                        self.cameraCapture()

                    else:
                        self.Sigle_SnapInput = False

        # Input CH2
        #===================================================
        input_node1 = self.getInput(1)
        if not input_node1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.Start_Video = False

        else:
            self.input_vdo_payload = input_node1.eval()

            if self.input_vdo_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.Start_Video = False

            elif type(self.input_vdo_payload) != type(None):
                if 'mqtt_payload' in self.input_vdo_payload:
                    self.start_MQTTCommand = self.input_vdo_payload['mqtt_payload']

                if 'submit' in self.input_vdo_payload:
                    self.start_command = self.input_vdo_payload['submit']
                    print("self.start_command : ", self.start_command)

                if 'submit' in self.input_vdo_payload and not self.Start_Video:
                    print("Process Count Submit")
                    if self.start_command:
                        self.content.submit_true_cnt += 1
                        # print("self.content.submit_true_cnt = ", self.content.submit_true_cnt)

                        if self.content.submit_true_cnt >= 1:
                            self.confirm_submit_true = True

                    elif not self.start_command and self.confirm_submit_true:
                        self.confirm_submit_true = False

                        self.content.command_start = not self.content.command_start

                        #Start Camera in Video Mode
                        if self.content.command_start:
                            self.StartRuuningCam()
                            self.payload['run'] = True
                            self.payload_roi['run'] = True
                            print("Input Button Checked !!!!")

                            if self.content.fix_ch != 'screen cap':
                                self.content.CamCapture = cv2.VideoCapture(int(self.content.CamCH_Select)) #captureDevice = camera
                                self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                            self.start_MQTTCommand = False

                        #Stop Camera Video Mode
                        else:
                            self.StopRunningCam()
                            self.payload['run'] = False
                            self.payload_roi['run'] = False
                            self.sendFixOutputByIndex(self.payload, 0)                   #<--------- Send Payload to output socket
                            #print("Redic Button UnChecked !!!!")
                            self.content.CamCapture.release()

                        self.content.submit_true_cnt = 0

                elif self.start_MQTTCommand and not self.confirm_submit_true: 
                    self.confirm_submit_true = True
                    
                    self.StartRuuningCam()
                    self.payload['run'] = True
                    self.payload_roi['run'] = True
                    print("MQTT Button Checked !!!!")

                    if self.content.fix_ch != 'screen cap':
                        self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
                        self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                elif not self.start_MQTTCommand and self.confirm_submit_true: 
                    self.confirm_submit_true = False
                    
                    self.StopRunningCam()
                    self.payload['run'] = False
                    self.payload_roi['run'] = False
                    self.sendFixOutputByIndex(self.payload, 0)                   #<--------- Send Payload to output socket
                    #print("Redic Button UnChecked !!!!")
                    self.content.CamCapture.release()

        #===================================================

    def cameraCapture(self):
        self.content.CamCH_Select.setEnabled(False)
        # i = 0

        # while i < 10:
        #     return_value, image = self.content.CamCapture.read()

        #     if return_value == False:
        #         image = "No Camera Detect !!!"

        #     i += 1
        if self.process_video:
            self.content.CamCapture.release()
            self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
            self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

        return_value, image = self.content.CamCapture.read()
        print("return_value :", return_value)
        if return_value:
                
            #print("Img = ", image)
            self.payload['fps'] = 1
            self.payload['blink'] = True
            self.payload['cameraCapture'] = True
            self.payload['img_h'], self.payload['img_w'], self.payload['img_c'] = image.shape
            self.payload['img'] = image

            self.payload_roi['blink'] = True

            if self.content.show_fps_flag:
                self.payload_roi['fps'] = self.payload['fps']

            else:
                self.payload_roi['fps'] = "Not Display"

        self.content.CamCH_Select.setEnabled(True)
        self.sendFixOutputByIndex(self.payload, 0)               #<--------- Send Payload to output socket

        self.process_capture = True
        self.process_video = False

    def update_frame(self):
        if self.content.show_fps_flag:
            self.payload['fps'] = time.time()
            self.payload_roi['fps'] = self.payload['fps']

        else:
            self.payload['fps'] = "Not Display"
            self.payload_roi['fps'] = "Not Display"

        # self.content.Cam_Alive = True
        # self.content.Last_Frame = None

        if self.content.auto_reconnect and not self.do_one_round:
            self.do_one_round = True

            self.Interval_recon = int(self.content.interval_connect * 60000)
            print("update_frame -> self.Interval_recon :", self.Interval_recon)
            self.content.Camera_autoRE_timer.setInterval(self.Interval_recon)

            self.content.Camera_autoRE_timer.start()    

        if self.content.fix_ch == 'screen cap':
            # Use mss() ===> Solution but a bit slower than pyautogui
            
            # sct_img = self.content.sct.grab(self.content.monitor)
            # img = Image.frombytes('RGB', (sct_img.size.width, sct_img.size.height), sct_img.rgb)
            # img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            # screen_image = np.array(img_bgr)

            # Take screenshot using PyAutoGUI
            img = pyautogui.screenshot()
        
            # Convert the screenshot to a numpy array
            screen_image = np.array(img)
        
            # Convert it from BGR(Blue, Green, Red) to
            # RGB(Red, Green, Blue)
            screen_image = cv2.cvtColor(screen_image, cv2.COLOR_BGR2RGB)

            self.payload['img'] =  cv2.resize(screen_image, dsize=(self.content.img_width, self.content.img_height), interpolation=cv2.INTER_AREA)
            self.payload['img_h'], self.payload['img_w'], self.payload['img_c'] = self.payload['img'].shape

        else:
            if self.Global.hasGlobal("GlobalCameraBoxID") and not self.content.innit_camera_fps:
                self.content.innit_camera_fps = True

                self.ListGlobalCameraBox = list(self.Global.getGlobal("GlobalCameraBoxID"))
                self.content.TotalOfCamInSystem = len(self.ListGlobalCameraBox)

                if type(self.content.CamCapture) != type(None):
                    self.content.CamCapture.set(cv2.CAP_PROP_FPS, int(60/int(self.content.TotalOfCamInSystem)))

            if self.content.TimerBlinkCnt >= 5:
                self.content.TimerBlinkCnt = 0
                if self.content.BlinkingState:
                    self.payload['blink'] = True
                    self.payload_roi['blink'] = True
                    self.content.radioState.setStyleSheet("QRadioButton"
                                    "{"
                                        "background-color : rgba(0, 0, 28, 50);"
                                    "}") 
                else:
                    self.payload['blink'] = False
                    self.payload_roi['blink'] = False
                    self.content.radioState.setStyleSheet("QRadioButton"
                                    "{"
                                    "background-color : #33CCFF"
                                    "}") 
                self.content.BlinkingState = not self.content.BlinkingState

            self.content.TimerBlinkCnt += 1
        
            if type(self.content.CamCapture) != type(None):
                return_value, image = self.content.CamCapture.read()

                if type(image) != type(None):
                    self.content.setting_image = image
                    self.content.img_height, self.content.img_width, _ = image.shape

                # if not self.first_read:
                #     self.first_read = True
                #     self.prev_frame = image

                # print(image)
                
                    if self.content.FlipCam and self.content.MirrorCam:
                        image = cv2.flip(image, -1)  # Flip Both
                    else:
                        if self.content.FlipCam:
                            image = cv2.flip(image, 0) # Flip vertically Upside Down
                        if self.content.MirrorCam:
                            image = cv2.flip(image, 1)  # Flip Left/Right

                    if self.content.cam_inc_bright_flag:
                        image = self.Increase_cam_brightness(image)

                    if self.content.cam_incCont_flag:
                        image = self.Adjust_cam_contrast(image)

                # =========================================================================
                # Select Region of Interest (ROI1)
                if self.content.setCameraROI:
                    cropped_image = None
                    if type(image) != type(None):
                        ROI_Img = image.copy()
                        cropped_image = ROI_Img[self.content.setROIY1:self.content.setROIY2, self.content.setROIX1:self.content.setROIX2]
                        
                        image = cv2.putText(image  , "ROI 1" , (self.content.setROIX2 - 35, self.content.setROIY1 - 5 ), cv2.FONT_HERSHEY_DUPLEX, 0.4, ( 0, 100, 255 ), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROIX1) + " , " + str(self.content.setROIY1) + ")" , (self.content.setROIX1 - 30, self.content.setROIY1 - 10 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROIX2) + " , " + str(self.content.setROIY2) + ")" , (self.content.setROIX2 - 30 , self.content.setROIY2 + 15 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50 ), 1)
                        image = cv2.rectangle(image, (self.content.setROIX1, self.content.setROIY1), (int(self.content.setROIX2), int(self.content.setROIY2)), (0 , 0, 255), 1)

                        self.bg_image = None
                        scale_factor = 1
                        ave_ref_color = self.checkAveragImage_Color(cropped_image)

                        if self.content.setROIX2 > self.content.setROIX1 and self.content.setROIY2 > self.content.setROIY1:
                            if not self.content.custom_angleROI1:
                                if self.content.rotateROI1 == "0":
                                    if cropped_image.shape[1] > cropped_image.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / cropped_image.shape[1]

                                    elif cropped_image.shape[0] > cropped_image.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / cropped_image.shape[0]

                                    self.bg_image = self.cropped_image_rotate_standard(cropped_image, scale_factor)

                                if self.content.rotateROI1 == "90":
                                    # Rotate the image by 90 degrees clockwise
                                    image_rotated_90 = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                                    if image_rotated_90.shape[1] > image_rotated_90.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_90.shape[1]

                                    elif image_rotated_90.shape[0] > image_rotated_90.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_90.shape[0]

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_90, scale_factor)

                                if self.content.rotateROI1 == "180":
                                    # Rotate the image by 180 degrees
                                    image_rotated_180 = cv2.rotate(cropped_image, cv2.ROTATE_180)
                                    if image_rotated_180.shape[1] > image_rotated_180.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_180.shape[1]

                                    elif image_rotated_180.shape[0] > image_rotated_180.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_180.shape[0]

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_180, scale_factor)

                                if self.content.rotateROI1 == "270":
                                    # Rotate the image by 270 degrees clockwise
                                    image_rotated_270 = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                                    if image_rotated_270.shape[1] > image_rotated_270.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_270.shape[1]

                                    elif image_rotated_270.shape[0] > image_rotated_270.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_270.shape[0]

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_270, scale_factor)


                                if self.content.convert_angle_ROI1:
                                    self.bg_image = cv2.putText(self.bg_image, f"Average color: {ave_ref_color:.2f}", (15, 480 - 15 ), cv2.FONT_HERSHEY_DUPLEX, 1, ( 196, 228, 17 ), 1)

                                    # Check if cropped color is not empty and > or < self.content.angle_ROI1
                                    if len(self.content.color_refROI1) > 0 and int(self.content.color_refROI1) > int(ave_ref_color):
                                        # Flip the image horizontally
                                        self.bg_image = cv2.rotate(self.bg_image, cv2.ROTATE_180)
                            else:
                                self.bg_image = self.cropped_image_rotate_custom(cropped_image, self.content.setROIX1,self.content.setROIY1,self.content.setROIX2,self.content.setROIY2, int(self.content.angle_ROI1))
                            
                            self.payload_roi['img'] = self.bg_image
                            self.sendFixOutputByIndex( self.payload_roi, 1)

                # =========================================================================
                # =========================================================================
                # Select Region of Interest (ROI2)
                if self.content.setCameraROI2:
                    cropped_image = None
                    if type(image) != type(None):
                        ROI_Img = image.copy()
                        cropped_image = ROI_Img[self.content.setROI2Y1:self.content.setROI2Y2, self.content.setROI2X1:self.content.setROI2X2]
                        
                        image = cv2.putText(image  , "ROI 2" , (self.content.setROI2X2 - 35, self.content.setROI2Y1 - 5 ), cv2.FONT_HERSHEY_DUPLEX, 0.4, ( 0, 255, 100 ), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROI2X1) + " , " + str(self.content.setROI2Y1) + ")" , (self.content.setROI2X1 - 30, self.content.setROI2Y1 - 10 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROI2X2) + " , " + str(self.content.setROI2Y2) + ")" , (self.content.setROI2X2 - 30 , self.content.setROI2Y2 + 15 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50 ), 1)
                        image = cv2.rectangle(image, (self.content.setROI2X1, self.content.setROI2Y1), (int(self.content.setROI2X2), int(self.content.setROI2Y2)), (0 , 225, 255), 1)

                        self.bg_image = None
                        scale_factor = 1
                        ave_ref_color = self.checkAveragImage_Color(cropped_image)

                        if self.content.setROI2X2 > self.content.setROI2X1 and self.content.setROI2Y2 > self.content.setROI2Y1:
                            if not self.content.custom_angleROI2:
                                if self.content.rotateROI2 == "0":
                                    if cropped_image.shape[1] > cropped_image.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / cropped_image.shape[1]

                                    elif cropped_image.shape[0] > cropped_image.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / cropped_image.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(cropped_image, scale_factor)

                                if self.content.rotateROI2 == "90":
                                    # Rotate the image by 90 degrees clockwise
                                    image_rotated_90 = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                                    if image_rotated_90.shape[1] > image_rotated_90.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_90.shape[1]

                                    elif image_rotated_90.shape[0] > image_rotated_90.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_90.shape[0]

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_90, scale_factor)

                                if self.content.rotateROI2 == "180":
                                    # Rotate the image by 180 degrees
                                    image_rotated_180 = cv2.rotate(cropped_image, cv2.ROTATE_180)
                                    if image_rotated_180.shape[1] > image_rotated_180.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_180.shape[1]

                                    elif image_rotated_180.shape[0] > image_rotated_180.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_180.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_180, scale_factor)

                                if self.content.rotateROI2 == "270":
                                    # Rotate the image by 270 degrees clockwise
                                    image_rotated_270 = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                                    if image_rotated_270.shape[1] > image_rotated_270.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_270.shape[1]

                                    elif image_rotated_270.shape[0] > image_rotated_270.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_270.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_270, scale_factor)

                                if self.content.convert_angle_ROI2:
                                    self.bg_image = cv2.putText(self.bg_image, f"Average color: {ave_ref_color:.2f}", (15, 480 - 15 ), cv2.FONT_HERSHEY_DUPLEX, 1, ( 196, 228, 17 ), 1)

                                    # Check if cropped color is not empty and > or < self.content.angle_ROI2
                                    if len(self.content.color_refROI2) > 0 and int(self.content.color_refROI2) > int(ave_ref_color):
                                        # Flip the image horizontally
                                        self.bg_image = cv2.rotate(self.bg_image, cv2.ROTATE_180)

                            else:
                                self.bg_image = self.cropped_image_rotate_custom(cropped_image, self.content.setROI2X1,self.content.setROI2Y1,self.content.setROI2X2,self.content.setROI2Y2, int(self.content.angle_ROI2))

                            self.payload_roi['img'] = self.bg_image
                            self.sendFixOutputByIndex( self.payload_roi, 2)

                # =========================================================================
                # Select Region of Interest (ROI3)
                if self.content.setCameraROI3:
                    cropped_image = None
                    if type(image) != type(None):
                        ROI_Img = image.copy()
                        cropped_image = ROI_Img[self.content.setROI3Y1:self.content.setROI3Y2, self.content.setROI3X1:self.content.setROI3X2]
                        
                        image = cv2.putText(image  , "ROI 3" , (self.content.setROI3X2 - 35, self.content.setROI3Y1 - 5 ), cv2.FONT_HERSHEY_DUPLEX, 0.4, ( 225, 100, 50 ), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROI3X1) + " , " + str(self.content.setROI3Y1) + ")" , (self.content.setROI3X1 - 30, self.content.setROI3Y1 - 10 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50), 1)
                        image = cv2.putText(image  , "("+str(self.content.setROI3X2) + " , " + str(self.content.setROI3Y2) + ")" , (self.content.setROI3X2 - 30 , self.content.setROI3Y2 + 15 ), cv2.FONT_HERSHEY_DUPLEX, 0.3, ( 0, 255, 50 ), 1)
                        image = cv2.rectangle(image, (self.content.setROI3X1, self.content.setROI3Y1), (int(self.content.setROI3X2), int(self.content.setROI3Y2)), (255 , 100, 100), 1)
                        
                        self.bg_image = None
                        scale_factor = 1
                        ave_ref_color = self.checkAveragImage_Color(cropped_image)

                        if self.content.setROI3X2 > self.content.setROI3X1 and self.content.setROI3Y2 > self.content.setROI3Y1:
                            if not self.content.custom_angleROI3:
                                if self.content.rotateROI3 == "0":
                                    if cropped_image.shape[1] > cropped_image.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / cropped_image.shape[1]

                                    elif cropped_image.shape[0] > cropped_image.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / cropped_image.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(cropped_image, scale_factor)

                                if self.content.rotateROI3 == "90":
                                    # Rotate the image by 90 degrees clockwise
                                    image_rotated_90 = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                                    if image_rotated_90.shape[1] > image_rotated_90.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_90.shape[1]

                                    elif image_rotated_90.shape[0] > image_rotated_90.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_90.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_90, scale_factor)

                                if self.content.rotateROI3 == "180":
                                    # Rotate the image by 180 degrees
                                    image_rotated_180 = cv2.rotate(cropped_image, cv2.ROTATE_180)
                                    if image_rotated_180.shape[1] > image_rotated_180.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_180.shape[1]

                                    elif image_rotated_180.shape[0] > image_rotated_180.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_180.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_180, scale_factor)

                                if self.content.rotateROI3 == "270":
                                    # Rotate the image by 270 degrees clockwise
                                    image_rotated_270 = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                                    if image_rotated_270.shape[1] > image_rotated_270.shape[0]:
                                        # Calculate the scaling factor to fit the width to 640 pixels
                                        scale_factor = self.content.img_width / image_rotated_270.shape[1]

                                    elif image_rotated_270.shape[0] > image_rotated_270.shape[1]:
                                        # Calculate the scaling factor to fit the height to 480 pixels
                                        scale_factor = self.content.img_height / image_rotated_270.shape[0]

                                    else:
                                        scale_factor = 1

                                    self.bg_image = self.cropped_image_rotate_standard(image_rotated_270, scale_factor)

                                if self.content.convert_angle_ROI3:
                                    self.bg_image = cv2.putText(self.bg_image, f"Average color: {ave_ref_color:.2f}", (15, 480 - 15 ), cv2.FONT_HERSHEY_DUPLEX, 1, ( 196, 228, 17 ), 1)

                                    # Check if cropped color is not empty and > or < self.content.angle_ROI1
                                    if len(self.content.color_refROI3) > 0 and int(self.content.color_refROI3) < int(ave_ref_color):
                                        # Flip the image horizontally
                                        self.bg_image = cv2.rotate(self.bg_image, cv2.ROTATE_180)

                            else:
                                self.bg_image = self.cropped_image_rotate_custom(cropped_image, self.content.setROI3X1,self.content.setROI3Y1,self.content.setROI3X2,self.content.setROI3Y2, int(self.content.angle_ROI3))

                            self.payload_roi['img'] = self.bg_image
                            self.sendFixOutputByIndex( self.payload_roi, 3)

                # =========================================================================
                # Detect QR Code and Barcode Reader
                if self.content.camera_mode == "Code Reader" and type(image) != type(None):
                    # results = self.content.reader.decode_buffer(image)
                    # if type(results) != type(None):
                        # # print('results :', results)
                        # for result in results:
                        #     points = result.localization_result.localization_points
                        #     cv2.line(image, points[0], points[1], (0,255,0), 2)
                        #     cv2.line(image, points[1], points[2], (0,255,0), 2)
                        #     cv2.line(image, points[2], points[3], (0,255,0), 2)
                        #     cv2.line(image, points[3], points[0], (0,255,0), 2)

                        #     x, y = points[0]
                        #     cv2.putText(image, result.barcode_text,(x, y -10) , 0, 0.6, (0,0,255),2)
                            # self.payload['code'] = str(result.barcode_text)

                            # print("result: ", result)
                            # print(len(result.barcode_text))

                            # if len(result.barcode_text) > 30:
                            #     BarcodeReader.init_license(self.content.dbr_license)
                            #     self.content.reader = BarcodeReader()

                    image, bdata, btype = self.BarcodeReader(image)
                    self.payload['code'] = bdata
                    self.payload['type'] = btype

                # pyzbar Solution
                    image, bfound, bdata = self.BarcodeReader(image)
                    self.payload['barcode_found'] = bfound
                    self.payload['barcode_data'] = bdata

                if return_value == False:
                    # image = "No Camera Detect !!!"

                    self.freez_cnt += 1
                    # print("self.freez_cnt :", self.freez_cnt)
                    if self.freez_cnt > 100:
                        self.payload['freezing'] = True
                        self.freez_cnt = 0

                        print("Camera ",str(self.content.fix_ch), " is Freezing detected!")
                        # self.content.all_usb_cameras = self.content.find_usb_cameras()
                        # print("Update new active Camera :", self.content.all_usb_cameras)

                        # self.content.Camera_timer.stop()
                        self.content.CamCapture.release()

                        self.content.Camera_timer.stop()
                        self.content.USBScan_timer.start()

                        # if len(self.content.all_usb_cameras) < self.content.TotalOfCamInSystem:
                        self.discon_image = self.payload['img']  

                        self.camera_frezz = True

                        self.Global.setGlobal(self.id, True)
                        self.from_freeze = True

                        if not self.first_freezing_cam:
                            self.first_freezing_cam = True
                            usbscaning_app = usbscaning.app
                            usbscaning.ScanThread(self.id, self.content.camera_usb_keys, self.content.fix_ch).start()
                            usbscaning_app.exec_()
                
                    # self.missing_ch = []
                    # if len(self.content.edit.text()) > 0:
                    #     self.missing_ch.append(int(self.content.edit.text()))
                    #     self.missing_ch = list(dict.fromkeys(self.missing_ch))
                    #     self.Global.setGlobal("Camera_MissingCH", self.missing_ch)

                    # self.content.edit.setText("")
                    # self.content.camera_discon = True

                    # if self.content.edit.text() != 's' and len(self.content.edit.text()) > 0:
                    #     self.StartRuuningCam()
                    #     self.payload['run'] = True
                    #     #print("Redic Button Checked !!!!")

                    #     if str(self.content.camera_CH).isnumeric():
                    #         self.content.CamCapture = cv2.VideoCapture(int(self.content.camera_CH)) #captureDevice = camera
                    #         self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                    #     else:
                    #         # Yellow
                    #         print("\033[93m {}\033[00m".format("Number of Camera is wrong !!!"))

                    # elif self.content.edit.text() == 's' and len(self.content.edit.text()) > 0:
                    #     print("\033[96m {}\033[00m".format("Screen Capture Process"))
                    # else:
                    #     print("\033[91m {}\033[00m".format("Not select a Camera !!!"))

                    # self.first_read = False

                    if self.content.auto_reconnect:
                        self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
                        self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                        self.StartRuuningCam()
                        self.content.Camera_autoRE_timer.start()    

                else:
                    #print("Img = ", image)
                    # Verify Which Chanel Connected
                    if self.from_freeze:
                        self.from_freeze = False
                        self.Global.setGlobal(self.id, False)

                    self.camera_frezz = False
                    self.freez_cnt = 0

                    self.payload['img_h'], self.payload['img_w'], self.payload['img_c'] = image.shape

                    if self.content.StartfromSave:
                        ...

                    # Compare_Last_Frame

                    # self.current_frame = self.payload['img']
                    # # Check if frames are freezing
                    # # self.freezing = self.is_frame_freezing()

                    # # Print freezing status
                    # if not self.freezing:
                    #     self.payload['freezing'] = False
                    #     # print("No freezing detected!")

                    # # # Set current frame as previous frame for next iteration
                    # self.prev_frame = self.current_frame

                # if self.content.camera_discon:
                #     # Check for USB camera connections
                #     # print("self.camera_discon CH :",self.content.fix_ch, " --> ",self.camera_discon)      

                #     new_usb_camera_keys = self.content.scan_usb_cameras()
                #     # print("new_usb_camera_keys :", new_usb_camera_keys)

                #     if new_usb_camera_keys != self.content.camera_usb_keys:
                #         self.handle_usb_events(self.content.camera_usb_keys, new_usb_camera_keys)
                #         self.content.camera_usb_keys = new_usb_camera_keys
                    if not self.content.show_fps_flag:
                        if self.content.BlinkingState:
                            # image = cv2.putText(image  , "R" , (25, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (236, 231, 0), 2)
                            # Draw a solid circle on the image
                            image = cv2.circle(image, (40,20), 10, (236, 231, 0), -1)

                    self.payload['img'] = image

            else:
                print("len(self.content.fix_ch) =", len(self.content.fix_ch))
                if len(self.content.fix_ch) == 0:
                    self.content.fix_ch = "0"

                # In Case self.content.CamCapture is None Type will set Innit self.content.CamCapture again
                self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
                self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

        self.payload['clock'] = datetime.now().strftime("%H:%M:%S")
        self.sendFixOutputByIndex(self.payload, 0)                   #<--------- Send Payload to output socket


    def cropped_image_rotate_standard(self, cropped_image, scale_factor):
        # print("self.content.image_height:", self.content.img_height, " , self.content.image_width:", self.content.img_width)
        background = np.zeros((self.content.img_height, self.content.img_width, 3), np.uint8)

        # Resize the cropped image while maintaining the aspect ratio
        if scale_factor != 1:
            cropped_image = cv2.resize(cropped_image, None, fx=scale_factor, fy=scale_factor)

        else:
            cropped_image = cv2.resize(cropped_image, (640, 480))

        h, w = background.shape[:2]
        # print("Background Dimensions:", h, w)

        h1, w1 = cropped_image.shape[:2]
        # print("Cropped Image Dimensions:", h1, w1)

        # Calculate the center coordinates to place the cropped image in the center of the background
        cx, cy = (w - w1) // 2, (h - h1) // 2

        # Ensure that the cropped image dimensions match the region where you want to place it
        cropped_image = cropped_image[:min(h1, h - cy), :min(w1, w - cx)]

        # Place the resized image in the center of the background image
        background[cy:cy + cropped_image.shape[0], cx:cx + cropped_image.shape[1]] = cropped_image

        return background

    # Function to reconnect the camera

    def cropped_image_rotate_custom(self, cropped_image, x1,y1,x2,y2,angle):
        # Create a 640x480 canvas
        canvas = np.zeros((480, 640, 3), dtype=np.uint8)

        # Calculate the center of the cropped region
        cropped_width = x2 - x1
        cropped_height = y2 - y1

        # Calculate the position to place the cropped image in the canvas to center it
        canvas_center = (canvas.shape[1] // 2, canvas.shape[0] // 2)

        # Place the cropped image in the canvas
        canvas[y1:y2, x1:x2] = cropped_image  # Assuming cropped_image is properly loaded elsewhere in your code

        # Rotate the canvas with the centered cropped image
        rotation_matrix = cv2.getRotationMatrix2D(canvas_center, angle, 1.0)
        rotated_canvas = cv2.warpAffine(canvas, rotation_matrix, (canvas.shape[1], canvas.shape[0]))

        # Define the corner points as an array
        corners = np.array([[x1, y1], [x1, y2], [x2, y1], [x2, y2]], dtype=np.float32)

        # Rotate all corners simultaneously
        rotated_corners = cv2.transform(np.array([corners]), rotation_matrix).reshape(-1, 2)

        # Find xmin, ymin, xmax, ymax from rotated corners
        xmin = int(min(rotated_corners[:, 0]))
        ymin = int(min(rotated_corners[:, 1]))
        xmax = int(max(rotated_corners[:, 0]))
        ymax = int(max(rotated_corners[:, 1]))

        # Resize the rotated image to fit within 640x480
        rotated_canvas_resized = cv2.resize(rotated_canvas, (640, 480))

        # Crop the rotated canvas using the calculated xmin, ymin, xmax, and ymax values
        cropped_rotated_image = rotated_canvas_resized[ymin:ymax, xmin:xmax]

        # Calculate the dimensions of the cropped region
        cropped_height, cropped_width, _ = cropped_rotated_image.shape

        # Calculate the scaling factors for width and height to fit within 640x480
        scale_width = 640 / cropped_width
        scale_height = 480 / cropped_height

        # Choose the minimum scaling factor to maintain the aspect ratio
        scaling_factor = min(scale_width, scale_height)

        # Resize the cropped region to fit within 640x480 while maintaining aspect ratio
        resized_cropped_image = cv2.resize(cropped_rotated_image, None, fx=scaling_factor, fy=scaling_factor)

        # Calculate the new dimensions after resizing
        new_height, new_width, _ = resized_cropped_image.shape

        # Calculate the padding needed to center the resized image in a 640x480 frame
        pad_x = (640 - new_width) // 2
        pad_y = (480 - new_height) // 2

        # Create a 640x480 canvas and place the resized image in the center
        final_image = np.zeros((480, 640, 3), dtype=np.uint8)
        final_image[pad_y:pad_y + new_height, pad_x:pad_x + new_width] = resized_cropped_image

        return final_image
    
    def checkAveragImage_Color(self, cropped_image):
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

        # Calculate the average grayscale value
        average_value = np.average(gray_image)

        # Normalize the average value to the scale from 0 to 100
        normalized_value = (average_value / 255) * 100

        return normalized_value

    def update_USB(self):
        # new_usb_camera_keys = self.content.scan_usb_cameras()
        # print("new_usb_camera_keys :", new_usb_camera_keys)

        # if new_usb_camera_keys != self.content.camera_usb_keys:
        #     self.handle_usb_events(self.content.camera_usb_keys, new_usb_camera_keys)
        #     self.content.camera_usb_keys = new_usb_camera_keys

        if self.Global.hasGlobal(str("USBConnet") + str(self.id)):
            # print(str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[0])
            # print(str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[1])
            USB_KeyConnect = str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[0]
            # print("USB_KeyConnect :", USB_KeyConnect)

            if str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[1] == "disconnected" and not self.ack_onetime:
                self.ack_onetime = True 
                print("\033[91m {}\033[00m".format(f"XXX USB camera disconnected: {USB_KeyConnect} ; CH: {self.content.fix_ch}"))
                
                self.content.camera_box_key = USB_KeyConnect.strip()

                # self.content.update_new_usb = USB_KeyConnect.strip()
                print("self.content.update_new_usb = ", self.content.camera_box_key)

                self.content.CamCapture.release()
                self.show_disconnect = True

                # Check If Frezzing More than 1 Chanel
                cam_frezz_ch = []
                if self.Global.hasGlobal("CameraFrezzChanel"):
                    cam_frezz_ch = self.Global.getGlobal("CameraFrezzChanel")
                    cam_frezz_ch.append(self.content.fix_ch)
                else:
                    cam_frezz_ch.append(self.content.fix_ch)
                
                cam_frezz_ch = list(set(cam_frezz_ch))
                self.Global.setGlobal("CameraFrezzChanel", cam_frezz_ch)
                if len(cam_frezz_ch) > 2:
                    self.content.all_frezz = True

            if str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[1] == "connected" and self.camera_frezz:
                # print("\033[96m {}\033[00m".format(f"--> USB camera connected: {USB_KeyConnect.strip()}" + " ; CH :" + str(self.content.fix_ch)))
                # print("self.content.combine_cam_id:", self.content.combine_cam_id)

                # if not self.content.Camera_replaceMissing:
                #     result = self.content.combine_cam_id[0][str(self.content.fix_ch)]
                #     print("\033[93m {}\033[00m".format("handle_usb_events on record : " + str(result) + " ; On CH:" + self.content.fix_ch))

                # else:
                #     # In case connect form Rotate Missing Camaera
                #     result = self.content.combine_cam_id[0][str(int(self.content.fix_ch) + 1)]
                
                # if self.content.edit.text() == "":
                #     self.content.camera_usb_keys = self.content.scan_usb_cameras()
                #     print("\033[93m {}\033[00m".format("Reconnect after load missing camera_usb_keys :" + self.content.camera_usb_keys))

                #     self.content.edit.setText(str(self.content.edit.text())) 
                
                # print("str(self.content.combine_cam_id[0][str(self.content.fix_ch)].values()) = ", str(self.content.combine_cam_id[0][str(self.content.fix_ch)].values()))
                # if str(self.Global.getGlobal(str("USBConnet") + str(self.id))).split(":")[0].strip() == str(self.content.combine_cam_id[0][str(self.content.fix_ch)].values()):
                if USB_KeyConnect.strip() == self.content.camera_box_key:    
                    self.StopRunningCam()
                    time.sleep(0.5)

                    self.StartRuuningCam()
                    self.payload['run'] = True
                    self.payload_roi['run'] = True
                    print("Camera Reconnect CH :", self.content.fix_ch)

                    cam_frezz_ch = []
                    if self.Global.hasGlobal("CameraFrezzChanel"):
                        cam_frezz_ch = self.Global.getGlobal("CameraFrezzChanel")

                        for item in cam_frezz_ch:
                            if item == str(self.content.fix_ch):
                                cam_frezz_ch.remove(item)
                                self.Global.setGlobal("CameraFrezzChanel", cam_frezz_ch)

                    if self.content.all_frezz:
                        for cam in range(len(self.content.camera_usb_keys)):
                            self.content.CamCapture = cv2.VideoCapture(int(cam)) #captureDevice = camera
                            self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))
                            self.content.all_frezz = False
                    else:
                        self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
                        self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                    # self.content.camera_discon = False
                    # self.content.Camera_timer.start()

                    self.ack_onetime = False
                    self.camera_frezz = False

                    if self.from_freeze:
                        self.Global.setGlobal(self.id, False)

                    self.content.USBScan_timer.stop()

                    self.Global.removeGlobal(str("USBConnet") + str(self.id))

                    self.show_disconnect = False

                    # Update Correct Combine ID
                    self.content.combine_cam_id[0][str(self.content.fix_ch)] = str(USB_KeyConnect.strip())
                    self.content.CameraIDCombo.setCurrentText(USB_KeyConnect[-17:])

                    self.first_freezing_cam = False


        if self.show_disconnect:
            text = "Camera CH: " + str(self.content.fix_ch) + " Disconnected !!!"
            
            start_x = int(int(self.payload['img_w'])/10)
            end_x = int(self.payload['img_w']) - int(int(self.payload['img_w'])/10)
            end_y = int(self.payload['img_h']) - int(int(self.payload['img_h'])/10)

            start_y = end_y - 50

            blk = np.zeros((int(self.payload['img_h']), int(self.payload['img_w']), 3), np.uint8)

            image = cv2.resize(self.discon_image, (int(self.payload['img_w']), int(self.payload['img_h'])), interpolation = cv2.INTER_AREA)
            image = cv2.rectangle(image, (0, 0), (int(int(self.payload['img_w'])/2), int(int(self.payload['img_h'])/10) - 15), (0 , 0, 255), -1)
            blk   = cv2.line(blk, (0,0), (int(self.payload['img_w']), int(self.payload['img_h'])), ( 0, 0, 255 ), 3) 
            blk   = cv2.line(blk, (0, int(self.payload['img_h'])), (int(self.payload['img_w']) ,0), ( 0, 0, 255 ), 3) 
            blk   = cv2.rectangle(blk, (0, 0), (int(self.payload['img_w']) - 10, int(self.payload['img_h'])), (0 , 0, 255), 65)
            image = cv2.putText(image  , text , ( start_x + 10, end_y - 5 ), cv2.FONT_HERSHEY_DUPLEX, 1, ( 0, 0, 255 ), 2)
            blk   = cv2.rectangle(blk, (start_x, start_y), (end_x + 10, end_y + 10), (224 , 255, 2), -1)

            image = cv2.addWeighted(image, 1.0, blk, 0.20, 1)
            
            self.payload['img'] = image
            self.sendFixOutputByIndex(self.payload, 0)                   #<--------- Send Payload to output socket

    # ==================================================================================================
    # def handle_usb_events(self, previous_keys, current_keys):
    #     # print("previous_keys :", previous_keys)
    #     # print("current_keys :", current_keys)

    #     disconnected_keys = set(previous_keys) - set(current_keys)
    #     connected_keys = set(current_keys) - set(previous_keys)

    #     for key in disconnected_keys:
    #         print("\033[91m {}\033[00m".format(f"XXX USB camera disconnected: {key} ; CH: {self.content.edit.text()}"))

    #         self.content.CamCapture.release()
            
    #     for key in connected_keys:
    #         try:
    #             print("\033[96m {}\033[00m".format(f"--> USB camera connected: {key}"))
    #             print("self.content.combine_cam_id:", self.content.combine_cam_id)
    #             result = self.content.combine_cam_id[0]
    #             print("\033[93m {}\033[00m".format("handle_usb_events on record : " + result[self.content.edit.text()] + " ; On CH:" + self.content.edit.text()))
    #             # self.content.combine_cam_id[int(self.content.edit.text())][str(self.content.edit.text())] = key

    #             if self.content.edit.text() == "":
    #                 self.content.camera_usb_keys = self.content.scan_usb_cameras()
    #                 print("\033[93m {}\033[00m".format("Reconnect after load missing camera_usb_keys :" + self.content.camera_usb_keys))

    #                 self.content.edit.setText(str(self.content.edit.text())) 
                
    #             if key == result[str(self.content.edit.text())]:
    #                 self.StopRunningCam()
    #                 time.sleep(0.5)

    #                 self.StartRuuningCam()
    #                 self.payload['run'] = True
    #                 print("Camera Reconnect CH :", self.content.edit.text())

    #                 self.content.CamCapture = cv2.VideoCapture(int(self.content.edit.text())) #captureDevice = camera
    #                 self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

    #                 # self.content.camera_discon = False
    #                 # self.content.Camera_timer.start()
    #                 self.content.USBScan_timer.stop()

    #         except:
    #             ...

    def find_key_by_value(self, dictionary, value):
        for key, val in dictionary.items():
            if val == value:
                return key

    # # Function to compare two frames for freezing
    # def is_frame_freezing(self, threshold=0.9):
    #     # Convert frames to grayscale
    #     if type(self.prev_frame) != type(None) and type(self.current_frame) != type(None):
    #         gray1 = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
    #         gray2 = cv2.cvtColor(self.current_frame , cv2.COLOR_BGR2GRAY)
            
    #         # Calculate absolute difference between frames
    #         diff = cv2.absdiff(gray1, gray2)
            
    #         # Apply threshold to obtain binary image
    #         _, thresholded = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            
    #         # Calculate percentage of white pixels
    #         pixel_count = np.sum(thresholded == 255)
    #         total_pixels = thresholded.shape[0] * thresholded.shape[1]
    #         percentage = pixel_count / total_pixels
            
    #         # Check if percentage exceeds the threshold
    #         if percentage > threshold:
    #             self.payload['freezing'] = True
    #             return True  # Freezing detected
    #         else:
    #             self.payload['freezing'] = False
    #             return False  # No freezing detected

    def onClicked(self):
        radioButton = self.content.sender()
        if radioButton.isChecked():
            if self.content.auto_reconnect and not self.do_one_round:
                self.do_one_round = True
                self.Interval_recon = int(self.content.interval_connect * 60000)
                print("onClicked -> self.Interval_recon :", self.Interval_recon)
                self.content.Camera_autoRE_timer.setInterval(self.Interval_recon)
                self.content.Camera_autoRE_timer.start()    

            self.StartRuuningCam()
            self.payload['run'] = True
            self.payload_roi['run'] = True
            #print("Redic Button Checked !!!!")

            if self.content.fix_ch != 'screen cap':
                    if len(self.content.fix_ch) == 0:
                        self.content.fix_ch = "0"

                    self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
                    self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

                    if not self.content.StartfromSave:
                        self.content.change_CamCH = True

                        # Clear combine_cam_id[0]
                        # if type(self.content.combine_cam_id) != type(None):
                        #     self.content.combine_cam_id.clear()
                        
                        # else:
                        #     self.content.combine_cam_id = []

                        self.content.scan_combine()
                        # print('self.content.combine_cam_id[int(self.content.camera_CH)]:', self.content.combine_cam_id[int(self.content.camera_CH)])
                        # self.content.record_combine_cam_id.append(self.content.combine_cam_id[int(self.content.fix_ch)])
                        print("\033[94m {}\033[00m".format("onClicked; Keep New --> combine_cam_id :" + str(self.content.combine_cam_id)))

                        self.content.CameraIDCombo.setEnabled(False)

            elif self.content.fix_ch == 'screen cap':
                print("\033[96m {}\033[00m".format("onClicked --> Screen Capture Process"))
            else:
                print("\033[91m {}\033[00m".format("onClicked --> Not select a Camera !!!"))

        else:
            self.do_one_round = False
            self.content.Camera_autoRE_timer.stop()

            self.StopRunningCam()
            self.payload['run'] = False
            self.payload_roi['run'] = False
            self.sendFixOutputByIndex(self.payload, 0)                   #<--------- Send Payload to output socket
            #print("Redic Button UnChecked !!!!")

            if type(self.content.CamCapture) != type(None):
                self.content.CamCapture.release()

            self.content.innit_camera_fps = False

            if self.content.StartfromSave:
                self.content.StartfromSave = False

            # Clear combine_cam_id[0]
            # self.content.combine_cam_id[0] = ""
            # self.content.scan_combine()

            self.content.CameraIDCombo.setEnabled(True)

        # if not self.content.SaveChanel:
        #     self.content.SaveChanel = True

        #     # Auto Save When Close IDE
        #     pyautogui.hotkey('ctrl', 's')

    # ===============================================================================
    # Make one method to decode the barcode pyzbar 
    def BarcodeReader(self, image):

        barcode_data = None
        barcode_type = None
        
        # Decode the barcode image
        detectedBarcodes = decode(image)
        
        # If not detected then print the message
        if not detectedBarcodes:
            barcode_data = "Barcode Not Detected or your barcode is blank/corrupted!"
            # print("Barcode Not Detected or your barcode is blank/corrupted!")
        else:
        
            # Traverse through all the detected barcodes in image
            for barcode in detectedBarcodes: 
            
                # Locate the barcode position in image
                (x, y, w, h) = barcode.rect
                
                # Put the rectangle in image using
                # cv2 to highlight the barcode
                cv2.rectangle(image, (x-10, y-10),
                            (x + w+10, y + h+10),
                            (0, 255, 0), 2)
                
                if barcode.data!="":
                    barcode_data = barcode.data
                    barcode_type = barcode.type

                    cv2.putText(image, str(barcode_data),(x -10, y -20) , 0, 0.6, (0,0,255),2)
                    
                    # Print the barcode data
                    print(barcode.data)
                    print(barcode.type)

        return image, barcode_data, barcode_type

    def BarcodeReader(self, frame):
        barcode_info = ""
        barcode_type = ""
        barcode_found = 0

        barcode_data = []

        barcodes = decode(frame)
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            barcode_info = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # print("Barcode data: " + barcode_info)

            barcode_found += 1
            barcode_data.append({'data':str(barcode_info), 'info': str(barcode_type)})

        return frame, barcode_found, barcode_data

    def Increase_cam_brightness(self, input_img):
        # Increase Camera Brightness
        img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)

        # v = img[:, :, 2]
        # v = np.where(v <= 255 - self.content.increase_brightness, v + self.content.increase_brightness, 255)
        # img[:, :, 2] = v

        # From ChatGPT
        v = img[:,:,2]
        v = cv2.add(v, self.content.increase_brightness)
        v[v > 255] = 255
        v[v < 0] = 0

        # Update the V channel in the HSV color space
        img[:,:,2] = v

        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

        return img
    
    def Adjust_cam_contrast(self, input_img):

        # Convert the frame to LAB color space
        lab = cv2.cvtColor(input_img, cv2.COLOR_BGR2LAB)

        # Split the LAB channels
        l, a, b = cv2.split(lab)

        # Apply the contrast adjustment to the L channel
        l = cv2.multiply(l, self.content.adjust_contrast)

        # Merge the LAB channels
        lab = cv2.merge((l, a, b))

        # Convert the frame back to BGR color space
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return img

    def ChangedChanel(self, text):
        self.content.Camera_timer.stop()
        self.content.fix_ch = text
        print("self.content.fix_ch = ", self.content.fix_ch)

        if text != 'screen cap':
            self.content.change_CamCH = True
            self.content.ThisCH_Need_minusIndex = False
            self.content.GlobalTimer.removeGlobal("MissingUSBCameraKey")

            self.content.CamCH_Select.setCurrentText(self.content.fix_ch)

            self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
            self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

            if self.content.CamCapture is None or not self.content.CamCapture.isOpened():
                print('Warning: unable to open video source: ', self.content.fix_ch)
                self.payload['img'] = 'Warning: unable to open video source: ', self.content.fix_ch
                self.content.CamCH_Select.setEnabled(True)
            # else:
            #     self.content.CamCH_Select.setEnabled(False)
            
            if not self.content.StartfromSave and not self.content.skip_check_missing:
                # Clear combine_cam_id[0]
                self.content.CameraIDCombo.setCurrentIndex(int(self.content.fix_ch))
                # self.content.combine_cam_id = [""]
                self.content.scan_combine()

                print("\033[94m {}\033[00m".format("ChangedChanel; Keep New --> combine_cam_id :" + str(self.content.combine_cam_id)))
            else:
                self.content.camera_usb_keys.clear()
                self.content.camera_usb_keys = self.content.scan_usb_cameras()

                # Clear combine_cam_id[0]
                self.content.combine_cam_id = [""]
                self.content.scan_combine()
                print("\033[91m {}\033[00m".format("Camera Index Out of range"))

        elif text == 'screen cap':
            print("\033[96m {}\033[00m".format("Screen Capture Process"))

    def onChanged(self, text):
        select = text[0:-2]
        print("Select Angle = ", select)
        if select == "0":
            self.content.MirrorCam = False
            self.content.FlipCam = False
        elif select == "180":
            self.content.MirrorCam = True
        elif select == "360":
            self.content.FlipCam = True

    """def setFlipCam(self , state):
        if state == QtCore.Qt.Checked:
            self.content.FlipCam = True
        else:
            self.content.FlipCam = False

    def setMirrorCam(self, state):
        if state == QtCore.Qt.Checked:
            self.content.MirrorCam = True
        else:
            self.content.MirrorCam = False"""
    
    def onChangeCam_ID(self, text):
        self.content.CamCH_Select.setEnabled(True)

    def onResolutionChanged(self, text):
        self.content.camera_res = text
        self.content.CamCapture.release()

        print("onResChanged ==> New Image Res:", self.content.camera_res)

        if self.content.fix_ch != 'screen cap':
            self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch))  # captureDevice = camera
            self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))
            # self.content.CamCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.content.camera_res))


    def StartRuuningCam(self):
        self.content.CamCH_Select.setEnabled(False)
        self.content.Capture.setEnabled(False)
        self.content.BlinkingState = True
        self.content.Camera_timer.start()
        self.content.lbl.setText("A")

        self.ListGlobalCamera = []

        if self.process_capture:
            self.content.CamCapture.release()
            self.content.CamCapture = cv2.VideoCapture(int(self.content.fix_ch)) #captureDevice = camera
            self.content.CamCapture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.content.camera_res))

        if not self.Add_Camera_List:     
            self.Add_Camera_List = True
            if self.content.GlobalTimer.hasGlobal("GlobalCameraApplication"):
                # print("self.content.GlobalTimer.getGlobal(\"GlobalCameraApplication\") : ", self.content.GlobalTimer.getGlobal("GlobalCameraApplication"))
                if type(self.content.GlobalTimer.getGlobal("GlobalCameraApplication")) is list:
                    self.ListGlobalCamera = list(self.content.GlobalTimer.getGlobal("GlobalCameraApplication"))

            self.ListGlobalCamera.append(self.content.CamCapture)
            print("List GlobalCameraApplication : ", self.ListGlobalCamera)
            self.content.GlobalTimer.setGlobal("GlobalCameraApplication", self.ListGlobalCamera)

            for i in range(len(self.ListGlobalCamera)):
                self.content.ListAllCameraIndex.append(i)
            print("ListAllCameraIndex : ", self.content.ListAllCameraIndex)
            self.content.GlobalTimer.setGlobal("GlobalCameraIndex", self.content.ListAllCameraIndex)

        self.process_video = True
        self.process_capture = False

    def StopRunningCam(self):
        self.content.CamCH_Select.setEnabled(True)
        self.content.Capture.setEnabled(True)
        self.content.BlinkingState = False
        self.content.Camera_timer.stop()
        self.content.radioState.setStyleSheet("QRadioButton"
                                "{"
                                "background-color : #33CCFF"
                                "}") 
        self.content.lbl.setText("N")

        self.Sigle_SnapInput = False
        # self.first_read = False

    def OnOpen_Setting(self):
        self.CAM_Setting = CAMSetting(self.content)
        self.CAM_Setting.show()
        self.content.SettingBtn.setEnabled(False)

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

  