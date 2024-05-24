from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import*
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import cv2
import numpy as np
import os

import requests
from io import BytesIO
from PIL import Image
import sys

import ai_application.AI_Tools.cv2.utlis as utlis

#On Linux Need to Install
# sudo apt update
# sudo apt install tesseract-ocr
# sudo apt install libtesseract-dev

# Library Requirment
# pip install pytesseract
import pytesseract

class OpenCVConfig(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.Path = os.path.dirname(os.path.abspath(__file__))
        logo_img = self.Path + "/icons/icons_opencv_30.png"
        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"

        self.browse_icon = self.Path + "/icons/icons_save_ib.png"

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        self.lbl = QLabel("No Image Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,2,100,25)
        self.lbl.setStyleSheet("font-size:6pt;")


        graphicsView.resize(35,35)
        graphicsView.setGeometry(QtCore.QRect(5, 18, 32, 32))

        img = QPixmap(logo_img)
        self.pixmap.setPixmap(img)
        #====================================================

        self.lblPayload = QLabel("Payload" , self)
        self.lblPayload.setAlignment(Qt.AlignLeft)
        self.lblPayload.setGeometry(105,21,35,20)
        self.lblPayload.setStyleSheet("color: #FFDD00; font-size:5pt;")

        self.lblImgResize = QLabel("func, Rez" , self)
        self.lblImgResize.setAlignment(Qt.AlignLeft)
        self.lblImgResize.setGeometry(105,42,40,20)
        self.lblImgResize.setStyleSheet("color: #EF8028; font-size:5pt;")

        self.lblImgYolo = QLabel("Yolo Obj" , self)
        self.lblImgYolo.setAlignment(Qt.AlignLeft)
        self.lblImgYolo.setGeometry(105,62,40,20)
        self.lblImgYolo.setStyleSheet("color: #FBC8B5; font-size:5pt;")

        # Setting
        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(10,52,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.Rotatecombo = QComboBox(self)
        self.Rotatecombo.addItem("0 " + chr(176))
        self.Rotatecombo.addItem("90 " + chr(176))
        self.Rotatecombo.addItem("180 " + chr(176))
        self.Rotatecombo.addItem("270 " + chr(176))
        self.Rotatecombo.setGeometry(40,20,60,25)
        self.Rotatecombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 

        self.ResCombo = QComboBox(self)
        self.ResCombo.addItem("640")
        self.ResCombo.addItem("1280")
        self.ResCombo.addItem("1920")
        self.ResCombo.addItem("2560")
        self.ResCombo.setGeometry(40,48,60,25)
        self.ResCombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33DDFF; font-size:6pt;"
                                   "}") 

        self.CV2FuntionName = QLabel(self)
        self.CV2FuntionName.setGeometry(5,77,140,18)
        self.CV2FuntionName.setText("CV2 Function")
        self.CV2FuntionName.setAlignment(QtCore.Qt.AlignCenter)
        self.CV2FuntionName.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:7pt;color:white; border: 1px solid white; border-radius: 3%;")
        
        self.opencv_mode = ""
        self.object_name = ""

        self.resize_h = 480
        self.resize_w = 640

        self.RotateImageAngle = 0

        self.setting_image = None
        self.score = 80

        #============================================
        # ROI 1
        self.setCameraROI = False
        self.setROIX1 = 50
        self.setROIY1 = 50

        self.setROIX2 = 150
        self.setROIY2 = 200

        # ==============================================

        self.cam_inc_bright_flag = False
        self.increase_brightness = 0

        self.cam_incCont_flag = False
        self.adjust_contrast = 1
        self.flipmode = 0

        # ==============================================
        # OpenCV Image Function
        self.image_gray = False
        self.image_threshold_flag = False
        self.image_threshold_mode = "THRESH_BINARY"
        self.mode_threshold_index = 0

        self.image_segmentation_flag = False
        self.edges_flage = False

        self.payload_obj = False
        self.bgr_rgb = False

        self.noise_removal_flag = False

        self.re_yolo_640 = False
        self.select_best_image = False
        self.WaitBestImage = 5

        self.resize_custom_flag = False
        self.resize_custom_height = 480
        self.resize_custom_width = 640

        self.thresh_bright = 255
        self.thesh_seta = 11
        self.thesh_setb = 2

        self.image_count = 0
        self.save_crop_yolo_flag = False
        self.save_filelocation = ""

        self.jump_image_cnt = 0

        # ==============================================

        self.baseline = 50   # Percent
        self.fornt_width = 30 # Percent
        self.center_line = 320

        #self.reader = easyocr.Reader(['th','en'] ,gpu=True) # this needs to run only once to load the model into memory


        self.perspective = False
        # Specify the points for eprspective transform
        self.x1, self.y1 = 100, 20  # top left
        self.x2, self.y2 = 500, 90  # top right
        self.x3, self.y3 = 100, 480  # bottom left
        self.x4, self.y4 = 500, 390  # bottom right

        # All points are in format [cols, rows]
        self.pt_A = [100, 20]       # top left
        self.pt_B = [100, 480]       # bottom left
        self.pt_C = [500, 390]      # bottom right
        self.pt_D = [500, 90]       # top right

        self.BestImg_timer = QtCore.QTimer()
                
        # Adding custom options
        self.custom_config = "--oem 3 --psm 6"

        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\Tesseract-OCR\\tesseract.exe'

        self.province_list = {
            "KBI":"กระบี่", "BKK":"กรุงเทพมหานคร", "KRI":"กาญจนบุรี", "KSN":"กาฬสินธุ์", "KPT":"กำแพงเพชร", "KKN":"ขอนแก่น", 
            "CTI":"จันทบุรี", "CCO":"ฉะเชิงเทรา", "CBI":"ชลบุรี", "CNT":"ชัยนาท", "CPM":"ชัยภูมิ", "CPN":"ชุมพร", "CRI":"เชียงราย",
            "CMI":"เชียงใหม่", "TRG":"ตรัง", "TRT":"ตราด", "TAK":"ตาก", "NYK":"นครนายก", "NPT":"นครปฐม", "NPM":"นครพนม",
            "NMA":"นครราชสีมา", "NST":"นครศรีธรรมราช", "NSN":"นครสวรรค์", "NBI":"นนทบุรี", "NWT":"นราธิวาส", "NAN":"น่าน",
            "BKN":"บึงกาฬ", "BRM":"บุรีรัมย์", "PTE":"ปทุมธานี", "PKN":"ประจวบคีรีขันธ์", "PRI":"ปราจีนบุรี", "PTN":"ปัตตานี", "PYO":"พะเยา",
            "AYA":"พระนครศรีอยุธยา", "PNA":"พังงา", "PLG":"พัทลุง", "PCT":"พิจิตร", "PLK":"พิษณุโลก", "PBI":"เพชรบุรี", "PNB":"เพชรบูรณ์",
            "PRE":"แพร่", "PKT":"ภูเก็ต", "MKM":"มหาสารคาม", "MDH":"มุกดาหาร", "MSN":"แม่ฮ่องสอน", "YST":"ยโสธร", "YLA":"ยะลา",
            "RET":"ร้อยเอ็ด", "RNG":"ระนอง", "RYG":"ระยอง", "RBR":"ราชบุรี", "LRI":"ลพบุรี", "LPG":"ลำปาง", "LPN":"ลำพูน",
            "LEI":"เลย", "SSK":"ศรีสะเกษ", "SNK":"สกลนคร", "SKA":"สงขลา", "STN":"สตูล", "SPK":"สมุทรปราการ", "SKM":"สมุทรสงคราม",
            "SKN":"สมุทรสาคร", "SKW":"สระแก้ว", "SRI":"สระบุรี", "SBR":"สิงห์บุรี", "STI":"สุโขทัย", "SPB":"สุพรรณบุรี", "SNI":"สุราษฎร์ธานี",
            "SRN":"สุรินทร์", "NKI":"หนองคาย", "NBP":"หนองบัวลำภู", "ATG":"อ่างทอง", "ACR":"อำนาจเจริญ",
            "UDN":"อุดรธานี", "UTT":"อุตรดิตถ์", "UTI":"อุทัยธานี", "UBN":"อุบลราชธานี"
        }

        # ==========================================================
        # For EvalChrildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['value'] = self.Data

        res['opencv_mode'] = self.opencv_mode
        res['object_name'] = self.object_name
        res['score'] = self.score
        res['baseline'] = self.baseline

        res['rotate_img'] = self.RotateImageAngle
        res['img_res'] = self.ResCombo.currentText()

        res['flip'] = self.flipmode

        # ============================================
        # ROI 1
        res['set_cam_roi'] = self.setCameraROI
        res['roi_x1'] = self.setROIX1
        res['roi_y1'] = self.setROIY1
        res['roi_x2'] = self.setROIX2
        res['roi_y2'] = self.setROIY2

        res['cam_bright_flag'] = self.cam_inc_bright_flag
        res['number_br_increas'] = self.increase_brightness

        res['incCont_flag'] = self.cam_incCont_flag
        res['number_contrast'] = self.adjust_contrast

        # =============================================
        res['image_gray'] = self.image_gray
        res['image_threshold_flag'] = self.image_threshold_flag
        res['threshold'] = self.image_threshold_mode
        res['segmentation'] = self.image_segmentation_flag
        res['edges'] = self.edges_flage

        res['perspective'] = self.perspective
        res['pt_A'] = self.pt_A
        res['pt_B'] = self.pt_B
        res['pt_C'] = self.pt_C
        res['pt_D'] = self.pt_D

        res['bgr_rgb'] = self.bgr_rgb
        res['mode_threshold_index'] = self.mode_threshold_index
        res['noise_removal'] = self.noise_removal_flag
        res['re_yolo_640'] = self.re_yolo_640

        res['resize_custom_flag'] = self.resize_custom_flag
        res['resize_custom_height'] = self.resize_custom_height
        res['resize_custom_width'] = self.resize_custom_width

        res['thresh_bright'] = self.thresh_bright
        res['thesh_seta'] = self.thesh_seta
        res['thesh_setb'] = self.thesh_setb

        res['select_best_image'] = self.select_best_image
        res['wait_bimg'] = self.WaitBestImage

        res['save_crop_yolo_flag'] = self.save_crop_yolo_flag
        res['save_filelocation'] = self.save_filelocation

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            if 'opencv_mode' in data:
                self.opencv_mode = data['opencv_mode']
                self.CV2FuntionName.setText(str(self.opencv_mode))

            if 'object_name' in data:
                self.object_name = data['object_name']

            if 'score' in data:
                self.score = data['score']

            if 'payload_obj' in data:
                self.payload_obj = data['payload_obj']

            if 'baseline' in data:
                self.baseline = data['baseline']

            if 'rotate_img' in data:
                self.RotateImageAngle = data['rotate_img']
                self.Rotatecombo.setCurrentText(str(self.RotateImageAngle) + " " + chr(176))

            if 'img_res' in data:
                self.camera_res = data['img_res']
                if self.camera_res == '1280':
                    self.resize_w = 1280
                    self.resize_h = 720
                        
                elif self.camera_res == '1920':
                    self.resize_w = 1920
                    self.resize_w = 1080

                elif self.camera_res == '2560':
                    self.resize_w = 2560
                    self.resize_h = 1440

                else:
                    self.resize_w = 640
                    self.resize_h = 480

                self.ResCombo.setCurrentText(self.camera_res)

            # ============================================
            # ROI 1 
            if 'set_cam_roi' in data:
                self.setCameraROI = data['set_cam_roi']
            
            if 'roi_x1' in data:
                self.setROIX1 = data['roi_x1']
            
            if 'roi_y1' in data:
                self.setROIY1 = data['roi_y1']
            
            if 'roi_x2' in data:
                self.setROIX2 = data['roi_x2']

            if 'roi_y2' in data:
                self.setROIY2 = data['roi_y2']

            if 'cam_bright_flag' in data:
                self.cam_inc_bright_flag = data['cam_bright_flag']

            if 'number_br_increas' in data:
                self.increase_brightness = data['number_br_increas']

            if 'incCont_flag' in data:
                self.cam_incCont_flag = data['incCont_flag']

            if 'number_contrast' in data:
                self.adjust_contrast = data['number_contrast']

            # ===============================================
            # Image Function
            if 'image_gray' in data:
                self.image_gray = data['image_gray']

            if 'flip' in data:
                self.flipmode = data['flip']

            if 'threshold' in data:
                self.image_threshold_mode = data['threshold']
            
            if 'image_threshold_flag' in data:
                self.image_threshold_flag = data['image_threshold_flag']
                if self.image_threshold_flag:
                    self.CV2FuntionName.setText(str(self.image_threshold_mode))

            if 'mode_threshold_index' in data:
                self.mode_threshold_index = data['mode_threshold_index']

            if 'segmentation' in data:
                self.image_segmentation_flag = data['segmentation']

            if 'edges' in data:
                self.edges_flage = data['edges']

            # Specify the points for perspective transform
            if 'perspective' in data:
                self.perspective = data['perspective']
                if self.perspective:
                    self.CV2FuntionName.setText('Perspective')

            if 'pt_A' in data:
                self.pt_A = data['pt_A']

            if 'pt_B' in data:
                self.pt_B = data['pt_B'] 

            if 'pt_C' in data:
                self.pt_C = data['pt_C']

            if 'pt_D' in data:
                self.pt_D = data['pt_D']

            if 'bgr_rgb'in data:
                self.bgr_rgb = data['bgr_rgb'] 
                if self.bgr_rgb:
                    self.CV2FuntionName.setText('BGR2RGB')

            if 'noise_removal' in data:
                self.noise_removal_flag = data['noise_removal']
                if self.noise_removal_flag:
                    self.CV2FuntionName.setText('Denoising')

            if 're_yolo_640' in data:
                self.re_yolo_640 = data['re_yolo_640']
                
            if 'resize_custom_flag' in data:
                self.resize_custom_flag = data['resize_custom_flag']
            
            if 'resize_custom_height' in data:
                self.resize_custom_height = data['resize_custom_height']

            if 'resize_custom_width' in data:
                self.resize_custom_width = data['resize_custom_width']

            if 'thresh_bright' in data:       
                self.thresh_bright = data['thresh_bright']

            if 'thesh_seta' in data:
                self.thesh_seta = data['thesh_seta']

            if 'thesh_setb' in data:
                self.thesh_setb = data['thesh_setb']

            if 'select_best_image' in data:
                self.select_best_image = data['select_best_image']

            if 'wait_bimg' in data:
                self.WaitBestImage = data['wait_bimg']

            if 'save_crop_yolo_flag' in data:
                self.save_crop_yolo_flag = data['save_crop_yolo_flag']

            if 'save_filelocation' in data:
                self.save_filelocation = data['save_filelocation']

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
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

        self.camera_res = camera_res
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


class OpenCV_Function(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class OpenCV_Function ---> OpenCV Function')

        self.content = content
        self.xml_dir = ""
        self.out_dir = ""
        self.class_file = ""

        self.file_number = 0
        self.draw_rectangle = False

        self.img = self.content.setting_image
        self.img_height = 640
        self.img_width = 480

        if type(self.content.setting_image) != type(None):
            self.img_height, self.img_width, img_colors = self.img.shape
        
        self.camera_res = self.img_width

        self.title = "OpenCV_Function"
        self.top    = 300
        self.left   = 600
        self.width  = 1200
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")
        #======================================================================
        # 
        self.lbl = QLabel("OpenCV Img_H : " + str(self.img_height) + ", Img_W : " + str(self.img_width), self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,5,1000,25)
        self.lbl.setStyleSheet("color: white; font-size:10pt;")

        self.lbl.setText("OpenCV Img_H : " + str(self.img_height) + ", Img_W : " + str(self.img_width) + " ; Mode : "  + self.content.opencv_mode)

        #=====================================================================
        # Content.Image ImageView
        self.lbl_setting_image = QLabel("" , self)
        self.lbl_setting_image.setAlignment(Qt.AlignLeft)
        self.lbl_setting_image.setGeometry(530,55,640,480)
        self.lbl_setting_image.setStyleSheet("background-color: rgba(0, 32, 130, 225); border: 1px solid white; border-radius: 3%")
        # self.update_setting_img(self.content.setting_image)
        self.display_timer = QtCore.QTimer(self)
        self.display_timer.timeout.connect(self.update_setting_img)
        self.display_timer.setInterval(10)
        self.display_timer.start()

        # Create and set the MovableRectLabel as a child of self.lbl_setting_image
        self.resizable_rect_label = ResizableRectLabel(self.lbl_setting_image)
        self.resizable_rect_label.setGeometry(0, 0, self.img_width, self.img_height)  # Set the size to match self.lbl_setting_image
        self.resizable_rect_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 1px solid white; border-radius: 3%")
        self.resizable_rect_label.coordinates_changed.connect(self.handle_coordinates_changed)


        self.conner_lt = QLabel("( 0 , 0 )" , self)
        self.conner_lt.setAlignment(Qt.AlignLeft)
        self.conner_lt.setGeometry(510,35,60,20)
        self.conner_lt.setStyleSheet("color: yellow; font-size:6pt;")

        self.conner_rt = QLabel("( 0 , 640 )" , self)
        self.conner_rt.setAlignment(Qt.AlignLeft)
        self.conner_rt.setGeometry(1120,35,70,20)
        self.conner_rt.setStyleSheet("color: yellow; font-size:6pt;")

        self.conner_rt.setText("( 0 , " + str(self.img_width) + " )")

        self.conner_hrt = QLabel("( 0 , 640 )" , self)
        self.conner_hrt.setAlignment(Qt.AlignLeft)
        self.conner_hrt.setGeometry(830,35,70,20)
        self.conner_hrt.setStyleSheet("color: yellow; font-size:6pt;")

        self.conner_hrt.setText("( 0 , " + str(int(self.img_width/2)) + " )")

        self.conner_lb = QLabel("( 480 , 0 )" , self)
        self.conner_lb.setAlignment(Qt.AlignLeft)
        self.conner_lb.setGeometry(510,540,70,20)
        self.conner_lb.setStyleSheet("color: yellow; font-size:6pt;")

        self.conner_lb.setText("( " + str(self.img_height)  + " , 0 )")

        self.conner_lb = QLabel("( 480 , 640 )" , self)
        self.conner_lb.setAlignment(Qt.AlignLeft)
        self.conner_lb.setGeometry(1100,540,70,20)
        self.conner_lb.setStyleSheet("color: yellow; font-size:6pt;")

        self.conner_lb.setText("( " + str(self.img_height)  + " , "  + str(self.img_width) + " )")

        # =====================================================================
        # CV2 Function get Imange Size
    
        self.cropImage = QCheckBox("Crop Img Payload",self)
        self.cropImage.setGeometry(10,40,200,20)
        self.cropImage.setStyleSheet("color: #FC03C7; font-size:8pt;")
        if self.content.opencv_mode == "Crop Image":
            self.cropImage.setChecked(True)
            self.content.CV2FuntionName.setText("Crop Image")

        else:
            self.cropImage.setChecked(False)

    # =============================================================
    # =============================================================
    # ROI 1 
        self.setROIX1_edit = QLineEdit("", self)
        self.setROIX1_edit.setAlignment(Qt.AlignCenter)
        self.setROIX1_edit.setGeometry(180,40,60,25)
        self.setROIX1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIX1_edit.setPlaceholderText("X1")

        self.setROIY1_edit = QLineEdit("", self)
        self.setROIY1_edit.setAlignment(Qt.AlignCenter)
        self.setROIY1_edit.setGeometry(250,40,60,25)
        self.setROIY1_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIY1_edit.setPlaceholderText("Y1")

        self.setROIX2_edit = QLineEdit("", self)
        self.setROIX2_edit.setAlignment(Qt.AlignCenter)
        self.setROIX2_edit.setGeometry(320,40,60,25)
        self.setROIX2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIX2_edit.setPlaceholderText("X2")

        self.setROIY2_edit = QLineEdit("", self)
        self.setROIY2_edit.setAlignment(Qt.AlignCenter)
        self.setROIY2_edit.setGeometry(390,40,60,25)
        self.setROIY2_edit.setStyleSheet("color: red; font-size:8pt;")
        self.setROIY2_edit.setPlaceholderText("Y2")

        if self.content.setCameraROI:
            self.cropImage.setChecked(True)
            self.setROIX1_edit.setText(str(self.content.setROIX1))
            self.setROIY1_edit.setText(str(self.content.setROIY1))
            self.setROIX2_edit.setText(str(self.content.setROIX2))
            self.setROIY2_edit.setText(str(self.content.setROIY2))
        else:
            self.cropImage.setChecked(False)

        self.cropImage.stateChanged.connect(self.add_red_rectangle)
        
        self.Update_ROI = QPushButton("Update", self)
        self.Update_ROI.setGeometry(460,40,60,25)
        self.Update_ROI.clicked.connect(self.onUpdateROI)
        
        #=====================================================================
        # CV2 Function Resize
        self.checkFlipImage = QCheckBox("Flip Image -> Payload",self)
        self.checkFlipImage.setGeometry(10,220,200,20)
        self.checkFlipImage.setStyleSheet("color: lightblue; font-size:8pt;")

        if self.content.opencv_mode == "Flip Image":
            self.checkFlipImage.setChecked(True)
            self.content.CV2FuntionName.setText("Flip Image")

        else:
            self.checkFlipImage.setChecked(False)

        self.Flipcombo = QComboBox(self)
        self.Flipcombo.addItem("0 " + chr(176))
        self.Flipcombo.addItem("180 " + chr(176))
        self.Flipcombo.addItem("360 " + chr(176))
        self.Flipcombo.setGeometry(250,220,200,20)
        self.Flipcombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 
        
        self.Flipcombo.setCurrentIndex(self.content.flipmode)
        self.Flipcombo.activated[str].connect(self.onFlipModeChanged)


        #======================================================================
    
        self.cropImage.stateChanged.connect(self.SelectCropImage)
        self.checkFlipImage.stateChanged.connect(self.SelectFlipImage)


        #======================================================================
        #=====================================================================
        # Camera Brightness
        self.checkBrightness = QCheckBox("Brightness -> func,resize : ",self)
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
        self.lbl_brn.setGeometry(250,70,35,20)
        self.lbl_brn.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_brn.setText(str(self.content.increase_brightness))

        #=====================================================================
        #=====================================================================
        # Camera Contrast
        self.checkContrast = QCheckBox("Contrast -> func,resize : ",self)
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
        self.lbl_contrast.setGeometry(250,150,35,20)
        self.lbl_contrast.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_contrast.setText(str(self.content.adjust_contrast))

        # ====================================================================
        # Select Best Image
        self.checkBestImg = QCheckBox("Best Image",self)
        self.checkBestImg.setGeometry(400,150,120,20)
        self.checkBestImg.setStyleSheet("color: #FC606E; font-size:8pt;")

        self.WaitBestImage_edit = QLineEdit("5", self)
        self.WaitBestImage_edit.setAlignment(Qt.AlignCenter)
        self.WaitBestImage_edit.setGeometry(400,180,120,25)
        self.WaitBestImage_edit.setStyleSheet("color: #FC606E;; font-size:8pt;")
        self.WaitBestImage_edit.setPlaceholderText("Second")

        if self.content.select_best_image:
            self.checkBestImg.setChecked(True)
            self.WaitBestImage_edit.setText(str(self.content.WaitBestImage))

        self.checkBestImg.stateChanged.connect(self.check_SelectBestImage)

        #=====================================================================
        # Crop Object Image
        #=====================================================================
        self.checkCropObjectImage = QCheckBox("Crop Yolo Object Payload:",self)
        self.checkCropObjectImage.setGeometry(10,250,220,20)
        self.checkCropObjectImage.setStyleSheet("color: lightblue; font-size:8pt;")

        self.editObjName = QLineEdit("", self)
        self.editObjName.setGeometry(240,250,150,20)
        self.editObjName.setPlaceholderText("Yolo Obj Name")
        self.editObjName.setStyleSheet("color: lightblue; font-size:8pt;")

        self.editObjScore = QLineEdit("", self)
        self.editObjScore.setGeometry(400,250,45,20)
        self.editObjScore.setPlaceholderText("Conf")
        self.editObjScore.setStyleSheet("color: lightblue; font-size:8pt;")

        if self.content.opencv_mode == "Crop Object Image":
            self.checkCropObjectImage.setChecked(True)
            if len(self.content.object_name) > 0:
                self.editObjName.setText(self.content.object_name)
            if len(str(self.content.score)) > 0:
                self.editObjScore.setText(str(self.content.score))

        else:
            self.checkCropObjectImage.setChecked(False)

        self.checkCropObjectImage.stateChanged.connect(self.SelectCheckCropImage)

        #self.re_yolo_640
        self.checkYoloNoBGImage = QCheckBox("Full",self)
        self.checkYoloNoBGImage.setGeometry(455,250,70,20)
        self.checkYoloNoBGImage.setStyleSheet("color: lightblue; font-size:8pt;")

        if self.content.re_yolo_640:
            self.checkYoloNoBGImage.setChecked(True)

        else:
            self.checkYoloNoBGImage.setChecked(False)

        self.checkYoloNoBGImage.stateChanged.connect(self.SelectCheckFullNoBG)

        # ===================================================================
        # Image Function
        # ===================================================================
        self.ImageFunction_lbl = QLabel("OpenCV Image Function", self)
        self.ImageFunction_lbl.setAlignment(Qt.AlignLeft)
        self.ImageFunction_lbl.setGeometry(10,290,500,25)
        self.ImageFunction_lbl.setStyleSheet("color: #F15A25; font-size:10pt;")

        self.checkGrayImage = QCheckBox("Gray Image -> func,resize : ",self)
        self.checkGrayImage.setGeometry(10,325,380,20)
        self.checkGrayImage.setStyleSheet("color: lightblue; font-size:8pt;")

        if self.content.image_gray:
            self.checkGrayImage.setChecked(True)

        self.checkGrayImage.stateChanged.connect(self.setcheckGrayImage)

        # -----------------------------------------------------------------
        # Adaptive Thresholding
        # In the previous section, we used a global value as threshold value. But it may not be good in all the conditions where image has different lighting conditions in different areas. In that case, we go for adaptive thresholding. In this, the algorithm calculate the threshold for a small regions of the image. So we get different thresholds for different regions of the same image and it gives us better results for images with varying illumination.

        # We use the function: cv.adaptiveThreshold (src, dst, maxValue, adaptiveMethod, thresholdType, blockSize, C)

        # Parameters
        # src = source 8-bit single-channel image.
        # dst = destination image of the same size and the same type as src.
        # maxValue = non-zero value assigned to the pixels for which the condition is satisfied
        # adaptiveMethod = adaptive thresholding algorithm to use.
        # thresholdType = thresholding type that must be either cv.THRESH_BINARY or cv.THRESH_BINARY_INV.
        # blockSize = size of a pixel neighborhood that is used to calculate a threshold value for the pixel: 3, 5, 7, and so on.
        # C	constant = subtracted from the mean or weighted mean (see the details below). Normally, it is positive but may be zero or negative as well.

        self.checkImageTHRESH = QCheckBox("Threshold --> func,resize : ",self)
        self.checkImageTHRESH.setGeometry(10,355,380,20)
        self.checkImageTHRESH.setStyleSheet("color: lightblue; font-size:8pt;")

        self.THRESHCombo = QComboBox(self)
        self.THRESHCombo.addItem("THRESH_BINARY")
        self.THRESHCombo.addItem("THRESH_BINARY_INV")
        self.THRESHCombo.addItem("THRESH_TRUNC")
        self.THRESHCombo.addItem("THRESH_TOZERO")
        self.THRESHCombo.addItem("THRESH_TOZERO_INV")
        self.THRESHCombo.addItem("THRESH_MEAN")
        self.THRESHCombo.addItem("THRESH_GAUSSIAN")
        self.THRESHCombo.setGeometry(250,355,200,20)
        self.THRESHCombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33DDFF; font-size:6pt;"
                                   "}")
        
        self.set_THRESHBright_edit = QLineEdit("255", self)
        self.set_THRESHBright_edit.setAlignment(Qt.AlignCenter)
        self.set_THRESHBright_edit.setGeometry(460,335,60,25)
        self.set_THRESHBright_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.set_THRESHBright_edit.setPlaceholderText("Bright")
        self.set_THRESHBright_edit.setValidator(QIntValidator(0, 255, self))

        self.set_THRESH_A_edit = QLineEdit("11", self)
        self.set_THRESH_A_edit.setAlignment(Qt.AlignCenter)
        self.set_THRESH_A_edit.setGeometry(460,370,60,25)
        self.set_THRESH_A_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.set_THRESH_A_edit.setPlaceholderText("3 - 19")
        self.set_THRESH_A_edit.setValidator(QIntValidator(3, 19, self))

        self.set_THRESH_B_edit = QLineEdit("2", self)
        self.set_THRESH_B_edit.setAlignment(Qt.AlignCenter)
        self.set_THRESH_B_edit.setGeometry(460,405,60,25)
        self.set_THRESH_B_edit.setStyleSheet("color: yellow; font-size:8pt;")
        self.set_THRESH_B_edit.setPlaceholderText("0")
        self.set_THRESH_B_edit.setValidator(QIntValidator(-30, 30, self))

        if self.content.image_threshold_flag:
            self.checkImageTHRESH.setChecked(True)
            self.THRESHCombo.setCurrentIndex(self.content.mode_threshold_index)

            self.set_THRESHBright_edit.setText(str(self.content.thresh_bright))
            self.set_THRESH_A_edit.setText(str(self.content.thesh_seta))
            self.set_THRESH_B_edit.setText(str(self.content.thesh_setb))
        
        self.checkImageTHRESH.stateChanged.connect(self.setcheckThresholding)
        self.THRESHCombo.activated[str].connect(self.onThresholdChanged)

        self.set_THRESHBright_edit.textChanged[str].connect(self.doUpdate_Property)
        self.set_THRESH_A_edit.textChanged[str].connect(self.doUpdate_Property)
        self.set_THRESH_B_edit.textChanged[str].connect(self.doUpdate_Property)

        # -----------------------------------------------------------------
        self.checkImageSegmentation = QCheckBox("Segmentation --> func,resize : ",self)
        self.checkImageSegmentation.setGeometry(10,380,380,20)
        self.checkImageSegmentation.setStyleSheet("color: lightblue; font-size:8pt;")

        if self.content.image_segmentation_flag:
            self.checkImageSegmentation.setChecked(True)

        self.checkImageSegmentation.stateChanged.connect(self.CheckSegmentation)

        # -----------------------------------------------------------------
        self.checkImageEdge = QCheckBox("Edge --> func,resize : ",self)
        self.checkImageEdge.setGeometry(10,410,380,20)
        self.checkImageEdge.setStyleSheet("color: lightblue; font-size:8pt;")
        
        if self.content.edges_flage:
            self.checkImageEdge.setChecked(True)

        self.checkImageEdge.stateChanged.connect(self.CheckEdgeDetection)

        # -----------------------------------------------------------------
        # Perspective Transformation
        self.Perspective_Image = QCheckBox("Perspective",self)
        self.Perspective_Image.setGeometry(10,440,200,20)
        self.Perspective_Image.setStyleSheet("color: yellow; font-size:8pt;")
            
        self.set_Perspective_A_edit = QLineEdit("", self)
        self.set_Perspective_A_edit.setAlignment(Qt.AlignCenter)
        self.set_Perspective_A_edit.setGeometry(180,440,60,25)
        self.set_Perspective_A_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Perspective_A_edit.setPlaceholderText("A")

        self.A_lbl = QLabel("A", self)
        self.A_lbl.setAlignment(Qt.AlignCenter)
        self.A_lbl.setGeometry(180,470,60,25)
        self.A_lbl.setStyleSheet("color: yellow; font-size:8pt;")
        self.A_lbl.setVisible(False)

        self.set_Perspective_B_edit = QLineEdit("", self)
        self.set_Perspective_B_edit.setAlignment(Qt.AlignCenter)
        self.set_Perspective_B_edit.setGeometry(250,440,60,25)
        self.set_Perspective_B_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Perspective_B_edit.setPlaceholderText("B")

        self.B_lbl = QLabel("B", self)
        self.B_lbl.setAlignment(Qt.AlignCenter)
        self.B_lbl.setGeometry(250,470,60,25)
        self.B_lbl.setStyleSheet("color: yellow; font-size:8pt;")
        self.B_lbl.setVisible(False)

        self.set_Perspective_C_edit = QLineEdit("", self)
        self.set_Perspective_C_edit.setAlignment(Qt.AlignCenter)
        self.set_Perspective_C_edit.setGeometry(320,440,60,25)
        self.set_Perspective_C_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Perspective_C_edit.setPlaceholderText("C")

        self.C_lbl = QLabel("C", self)
        self.C_lbl.setAlignment(Qt.AlignCenter)
        self.C_lbl.setGeometry(320,470,60,25)
        self.C_lbl.setStyleSheet("color: yellow; font-size:8pt;")
        self.C_lbl.setVisible(False)

        self.set_Perspective_D_edit = QLineEdit("", self)
        self.set_Perspective_D_edit.setAlignment(Qt.AlignCenter)
        self.set_Perspective_D_edit.setGeometry(390,440,60,25)
        self.set_Perspective_D_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Perspective_D_edit.setPlaceholderText("D")

        self.D_lbl = QLabel("D", self)
        self.D_lbl.setAlignment(Qt.AlignCenter)
        self.D_lbl.setGeometry(390,470,60,25)
        self.D_lbl.setStyleSheet("color: yellow; font-size:8pt;")
        self.D_lbl.setVisible(False)    

        if self.content.perspective:
            self.Perspective_Image.setChecked(True)
            self.display_timer.stop()

            self.set_Perspective_A_edit.setText(str(self.content.pt_A)[1:-1])
            self.set_Perspective_B_edit.setText(str(self.content.pt_B)[1:-1])
            self.set_Perspective_C_edit.setText(str(self.content.pt_C)[1:-1])
            self.set_Perspective_D_edit.setText(str(self.content.pt_D)[1:-1])

            self.A_lbl.setVisible(True) 
            self.B_lbl.setVisible(True) 
            self.C_lbl.setVisible(True) 
            self.D_lbl.setVisible(True) 

            self.content.setting_image = self.draw_perspective_line(self.content.setting_image)
            self.update_setting_img()

        else:
            self.Perspective_Image.setChecked(False)

        self.Perspective_Image.stateChanged.connect(self.Change_Perspective_Mode)
        
        self.Update_Perspective = QPushButton("Update", self)
        self.Update_Perspective.setGeometry(460,440,60,25)
        self.Update_Perspective.clicked.connect(self.onUpdate_perspective_point)

        self.Update_Perspective = QPushButton("help", self)
        self.Update_Perspective.setGeometry(460,470,60,25)
        self.Update_Perspective.clicked.connect(self.onHelp_perspective)

        # self.bgr_rgb
        # -----------------------------------------------------------------
        # RGB to BGR Transformation
        self.BGR2RGB_Image = QCheckBox("RGB to BGR",self)
        self.BGR2RGB_Image.setGeometry(10,510,150,20)
        self.BGR2RGB_Image.setStyleSheet("color: #2DD5AC; font-size:8pt;")
            
        if self.content.bgr_rgb:
            self.BGR2RGB_Image.setChecked(True)

        else:
            self.BGR2RGB_Image.setChecked(False)

        self.BGR2RGB_Image.stateChanged.connect(self.Change_Image_BGR_RGB)


        #self.noise_removal_flag
        # -----------------------------------------------------------------
        # RGB to BGR Transformation
        self.NoiseRem_Image = QCheckBox("Noise Removal",self)
        self.NoiseRem_Image.setGeometry(10,540,150,20)
        self.NoiseRem_Image.setStyleSheet("color: #2DD5AC; font-size:8pt;")
            
        if self.content.noise_removal_flag:
            self.NoiseRem_Image.setChecked(True)

        else:
            self.NoiseRem_Image.setChecked(False)

        self.NoiseRem_Image.stateChanged.connect(self.Change_NoiseRem_Image)

        # -----------------------------------------------------------------
        # Resize Custom
        self.ResizeCustom_Image = QCheckBox("Resize Custom",self)
        self.ResizeCustom_Image.setGeometry(10,570,150,20)
        self.ResizeCustom_Image.setStyleSheet("color: #2DD5AC; font-size:8pt;")

        self.set_Recustom_H_edit = QLineEdit("", self)
        self.set_Recustom_H_edit.setAlignment(Qt.AlignCenter)
        self.set_Recustom_H_edit.setGeometry(180,570,60,25)
        self.set_Recustom_H_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Recustom_H_edit.setPlaceholderText("height")
        self.set_Recustom_H_edit.setValidator(QIntValidator(1, 99999, self))

        self.set_Recustom_W_edit = QLineEdit("", self)
        self.set_Recustom_W_edit.setAlignment(Qt.AlignCenter)
        self.set_Recustom_W_edit.setGeometry(250,570,60,25)
        self.set_Recustom_W_edit.setStyleSheet("color: red; font-size:8pt;")
        self.set_Recustom_W_edit.setPlaceholderText("width")
        self.set_Recustom_W_edit.setValidator(QIntValidator(1, 99999, self))

        if self.content.resize_custom_flag:
            self.ResizeCustom_Image.setChecked(True)
            self.set_Recustom_H_edit.setText(str(self.content.resize_custom_height))
            self.set_Recustom_W_edit.setText(str(self.content.resize_custom_width))

        else:
            self.ResizeCustom_Image.setChecked(False)

        self.ResizeCustom_Image.stateChanged.connect(self.Change_HW_Resize)

        self.arrow_right = QLabel("==>", self)
        self.arrow_right.setAlignment(Qt.AlignLeft)
        self.arrow_right.setGeometry(330,570,50,25)
        self.arrow_right.setStyleSheet("color: yellow; font-size:10pt;")

        # Save yolo Crop image
        self.set_save_crop_yolo = QCheckBox("Save Yolo Crop Img",self)
        self.set_save_crop_yolo.setGeometry(390,570,220,20)
        self.set_save_crop_yolo.setStyleSheet("color: lightblue; font-size:10pt;")

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(620,570,30,30)
        self.browsFiles.setIcon(QIcon(self.content.browse_icon))
        self.browsFiles.setIconSize(QtCore.QSize(35,30))
        self.browsFiles.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lblPath = QLabel("Select Save Img Path" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(670,570,500,25)
        self.lblPath.setStyleSheet("color: white; font-size:9pt;")

        self.editImgInput = QLineEdit("0", self)
        self.editImgInput.setGeometry(1065,570,100,20)
        self.editImgInput.setPlaceholderText("Jump")
        self.editImgInput.setStyleSheet("color: white;font-size:9pt;")

        self.editImgInput.textChanged[str].connect(self.UpdateCurrentImage)

        # save_crop_yolo_flag
        # save_filelocation

        if self.content.save_crop_yolo_flag:
            self.set_save_crop_yolo.setChecked(True)
            self.lblPath.setText(self.content.save_filelocation)
        else:
            self.set_save_crop_yolo.setChecked(False)

        self.set_save_crop_yolo.stateChanged.connect(self.Save_CropImage)
        self.browsFiles.clicked.connect(self.browseSlot)

    # =======================================================================
    # End UI
    # =======================================================================
    #Select destinate Folder to Save file
    def browseSlot(self):
        """self.fileLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.fileLocation)"""

        self.content.save_filelocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.lblPath.setText(self.content.save_filelocation)

        if len(self.content.save_filelocation) > 0:
            self.content.save_crop_yolo_flag = True
            self.set_save_crop_yolo.setChecked(True)

    def Save_CropImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.save_crop_yolo_flag = True
        else:
            self.content.save_crop_yolo_flag = False

    def UpdateCurrentImage(self, text):
        if str(text).isnumeric():
            self.content.jump_image_cnt = int(text)

    def check_SelectBestImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.WaitBestImage = int(self.WaitBestImage_edit.text())
            self.content.select_best_image = True

        else:
            self.content.select_best_image = False
            self.content.BestImg_timer.stop()

    def doUpdate_Property(self, text):
        if len(self.set_THRESHBright_edit.text()) > 0 and len(self.set_THRESH_A_edit.text()) > 0 and len(self.set_THRESH_B_edit.text()) > 0:
            print("doUpdate_Property :", text)
            self.content.thresh_bright = int(self.set_THRESHBright_edit.text())
            self.content.thesh_seta = int(self.set_THRESH_A_edit.text())
            self.content.thesh_setb = int(self.set_THRESH_B_edit.text())

    def Change_HW_Resize(self, state):
        if state == QtCore.Qt.Checked:
            if len(self.set_Recustom_H_edit.text()) > 0 and len(self.set_Recustom_W_edit.text()) > 0:
                self.content.resize_custom_height = int(self.set_Recustom_H_edit.text())
                self.content.resize_custom_width = int(self.set_Recustom_W_edit.text())
            else:
                self.set_Recustom_H_edit.setText(str(self.content.resize_custom_height))
                self.set_Recustom_W_edit.setText(str(self.content.resize_custom_width))
            
            self.content.resize_custom_flag = True
        else:
            self.content.resize_custom_flag = False

    def SelectCheckFullNoBG(self, state):
        if state == QtCore.Qt.Checked:
            self.content.re_yolo_640 = True
        else:
            self.content.re_yolo_640 = False

    def Change_NoiseRem_Image(self, state):
        if state == QtCore.Qt.Checked:
            self.content.noise_removal_flag = True
        else:
            self.content.noise_removal_flag = False

    def Change_Image_BGR_RGB(self, state):
        if state == QtCore.Qt.Checked:
            self.content.bgr_rgb = True
        else:
            self.content.bgr_rgb = False

    def onUpdate_perspective_point(self):
        # Split the text by comma and convert each number to an integer

        if len(self.set_Perspective_A_edit.text()) > 0 and len(self.set_Perspective_B_edit.text()) > 0 and len(self.set_Perspective_C_edit.text()) > 0 and len(self.set_Perspective_D_edit.text()) > 0:
            self.content.pt_A = [int(num) for num in self.set_Perspective_A_edit.text().split(",")]
            self.content.pt_B = [int(num) for num in self.set_Perspective_B_edit.text().split(",")]
            self.content.pt_C = [int(num) for num in self.set_Perspective_C_edit.text().split(",")]
            self.content.pt_D = [int(num) for num in self.set_Perspective_D_edit.text().split(",")]

            self.content.setting_image = self.draw_perspective_line(self.content.setting_image)
            self.update_setting_img()
    
    def Change_Perspective_Mode(self, state):
        if state == QtCore.Qt.Checked:
            self.display_timer.stop()
            self.content.opencv_mode = "Image Perspective"
            self.content.CV2FuntionName.setText("Perspective")
            self.content.perspective = True

            # print("self.content.pt_A :", self.content.pt_A)
            # print("self.content.pt_B :", self.content.pt_B)
            # print("self.content.pt_C :", self.content.pt_C)
            # print("self.content.pt_D :", self.content.pt_D)

            self.A_lbl.setVisible(True) 
            self.B_lbl.setVisible(True) 
            self.C_lbl.setVisible(True) 
            self.D_lbl.setVisible(True) 

            self.set_Perspective_A_edit.setText(str(self.content.pt_A)[1:-1])
            self.set_Perspective_B_edit.setText(str(self.content.pt_B)[1:-1])
            self.set_Perspective_C_edit.setText(str(self.content.pt_C)[1:-1])
            self.set_Perspective_D_edit.setText(str(self.content.pt_D)[1:-1])

            self.content.setting_image = self.draw_perspective_line(self.content.setting_image)
            self.update_setting_img()

        else:
            self.display_timer.start()
            self.content.perspective = False

            self.A_lbl.setVisible(False) 
            self.B_lbl.setVisible(False) 
            self.C_lbl.setVisible(False) 
            self.D_lbl.setVisible(False) 
    
    def draw_perspective_line(self, image_roi):
        # Converting lists to tuples
        tuple_A = tuple(self.content.pt_A)
        tuple_B = tuple(self.content.pt_B)
        tuple_C = tuple(self.content.pt_C)
        tuple_D = tuple(self.content.pt_D)

        # print("tuple_A :", tuple_A)
        # print("tuple_B :", tuple_B)
        # print("tuple_C :", tuple_C)
        # print("tuple_D :", tuple_D)

        # Draw the rectangle with the provided points
        # Connect points A -> B -> C -> D -> A
        image_roi = cv2.line(image_roi, tuple_A, tuple_B, (255, 0, 0), thickness=2)
        image_roi = cv2.line(image_roi, tuple_B, tuple_C, (255, 0, 0), thickness=2)
        image_roi = cv2.line(image_roi, tuple_C, tuple_D, (255, 0, 0), thickness=2)
        image_roi = cv2.line(image_roi, tuple_D, tuple_A, (255, 0, 0), thickness=2)

        # # Put 'ROI' text in the center of the rectangle
        # # Calculate center of the rectangle
        # center_x = int((tuple_A[0] + tuple_C[0]) / 2)
        # center_y = int((tuple_A[1] + tuple_C[1]) / 2)
        # image_roi = cv2.putText(image_roi, 'ROI', (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 
        #             2, (0, 0, 255), 2)    
        
        
        # Label the corners with A, B, C, D
        # offset = 15  # offset for text from corner point
        # image_roi = cv2.putText(image_roi, 'A', (tuple_A[0] + offset, tuple_A[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 
        #             0.7, (0, 0, 255), 1)
        # image_roi = cv2.putText(image_roi, 'B', (tuple_B[0] + offset, tuple_B[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 
        #             0.7, (0, 0, 255), 1)
        # image_roi = cv2.putText(image_roi, 'C', (tuple_C[0] + offset, tuple_C[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 
        #             0.7, (0, 0, 255), 1)
        # image_roi = cv2.putText(image_roi, 'D', (tuple_D[0] + offset, tuple_D[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 
        #             0.7, (0, 0, 255), 1)
        
        # Label the corners with A, B, C, D inside the rectangle, near the corners
        inset = 15  # inset distance from the corner point
        cv2.putText(image_roi, 'A', (tuple_A[0] + inset, tuple_A[1] + (2 *inset)), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255), 1)
        cv2.putText(image_roi, 'B', (tuple_B[0] + inset, tuple_B[1] - inset), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255), 1)
        cv2.putText(image_roi, 'C', (tuple_C[0] - inset - int(inset/2), tuple_C[1] - inset), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255), 1)
        cv2.putText(image_roi, 'D', (tuple_D[0] - inset - int(inset/2), tuple_D[1] + inset + int(inset/2)), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255), 1)

        return image_roi
    
    def onHelp_perspective(self):
        # URL of the image
        image_url = "https://i0.wp.com/theailearner.com/wp-content/uploads/2020/11/perspective2-2.jpg?w=880&ssl=1"

        # Send a HTTP request to the URL of the image
        response = requests.get(image_url)
        # Check if the request was successful
        if response.status_code == 200:
            # Read the image data (bytes) from the response
            image_data = BytesIO(response.content)
            
            # Convert the bytes data to a numpy array
            image_array = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
            
            # Decode the numpy array into an image
            self.content.setting_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            self.update_setting_img()

    # ================================================================================================================

    def onFlipModeChanged(self, text):
        select = text[0:-2]
        print("Select Angle = ", select)
        if select == "0":
            self.content.flipmode = 0
        elif select == "180":
            self.content.flipmode = 1
        elif select == "360":
            self.content.flipmode = 2

    def setcheckGrayImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.image_gray = True
        else:
            self.content.image_gray = False

    def setcheckThresholding(self, state):
        if state == QtCore.Qt.Checked:
            self.content.image_threshold_flag = True
            self.content.image_gray = True
            self.checkGrayImage.setChecked(True)
            self.checkGrayImage.setEnabled(False)

            self.THRESHCombo.setCurrentIndex(self.content.mode_threshold_index)

            self.content.thresh_bright = int(self.set_THRESHBright_edit.text())
            self.content.thesh_seta = int(self.set_THRESH_A_edit.text())
            self.content.thesh_setb = int(self.set_THRESH_B_edit.text())

        else:
            self.content.image_threshold_flag = False
            self.checkGrayImage.setEnabled(True)

    def onThresholdChanged(self, text):
        self.content.image_threshold_mode = text
        self.content.mode_threshold_index = self.THRESHCombo.currentIndex()

    def CheckSegmentation(self, state):
        if state == QtCore.Qt.Checked:
            self.content.image_segmentation_flag = True
            self.content.image_gray = True
            self.checkGrayImage.setChecked(True)
            self.checkGrayImage.setEnabled(False)

        else:
            self.content.image_segmentation_flag = False
            self.checkGrayImage.setEnabled(True)

    def CheckEdgeDetection(self, state):
        if state == QtCore.Qt.Checked:
            self.content.edges_flage = True
        else:
            self.content.edges_flage = False

    # +++++++++++++++++++++++++++++++++++++
        
    def SelectCropImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.opencv_mode = "Crop Image"
            self.content.CV2FuntionName.setText("Crop Image")

            self.content.cam_inc_bright_flag = False
            self.checkBrightness.setChecked(False)
            self.checkBrightness.setEnabled(False)

            self.content.cam_incCont_flag = False
            self.checkContrast.setChecked(False)
            self.checkContrast.setEnabled(False)

            #ROI1
            if len(self.setROIX1_edit.text()) > 0 and self.setROIX1_edit.text().isnumeric(): self.content.setROIX1 = int(self.setROIX1_edit.text())
            if len(self.setROIY1_edit.text()) > 0 and self.setROIY1_edit.text().isnumeric(): self.content.setROIY1 = int(self.setROIY1_edit.text())
            if len(self.setROIX2_edit.text()) > 0 and self.setROIX2_edit.text().isnumeric(): self.content.setROIX2 = int(self.setROIX2_edit.text())
            if len(self.setROIY2_edit.text()) > 0 and self.setROIY2_edit.text().isnumeric(): self.content.setROIY2 = int(self.setROIY2_edit.text())

            if ( self.content.setROIX1 >= 0 ) and ( self.content.setROIX2 > self.content.setROIX1 ) and ( self.content.setROIY1 >= 0 ) and ( self.content.setROIY2 > self.content.setROIY1 ):
                self.content.setCameraROI = True

        else:
            self.content.opencv_mode = ""

    def SelectFlipImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.opencv_mode = "Flip Image"
            self.content.CV2FuntionName.setText("Flip Image")

        else:
            self.content.opencv_mode = ""

    def SelectCheckCropImage(self, state):
        if state == QtCore.Qt.Checked:
            self.content.opencv_mode = "Crop Object Image"

        else:
            self.content.opencv_mode = ""

    # # ==============================================================
    # #ROI1
    def onUpdateROI(self):
        self.content.setROIX1 = int(self.setROIX1_edit.text())
        self.content.setROIY1 = int(self.setROIY1_edit.text())
        self.content.setROIX2 = int(self.setROIX2_edit.text())
        self.content.setROIY2 = int(self.setROIY2_edit.text())

    def onChangedROI1(self, text):
        # print("onChangedROI1 ==> text:", text[:-2])
        self.content.rotateROI1 = str(text[:-2])

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
            # self.content.lbl_ROI1.setVisible(True)
        else:
            self.content.setCameraROI = False
            # self.content.lbl_ROI1.setVisible(False)

    def handle_coordinates_changed(self, color, x1, y1, x2, y2, action):
        # print("====================================================")
        # print(f'Color: {color}, x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}, Action: {action}')
        if str(color) == "#ff0000":
            # print("Select Red Rectangle")
            self.setROIX1_edit.setText(str(x1))
            self.setROIY1_edit.setText(str(y1))
            self.setROIX2_edit.setText(str(x2))
            self.setROIY2_edit.setText(str(y2))

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
            # Draw Rectangle
            # if self.content.setCameraROI:
            #     img = cv2.putText(img  , "scale : W{:.3f} , H{:.3f} ".format(scale_w, scale_h)  , ( 10, 20 ), cv2.FONT_HERSHEY_DUPLEX, 0.7, ( 0, 0, 255 ), 1)
            #     img = cv2.rectangle(img,(int(self.content.setROIX1 * scale_w) , int(self.content.setROIY1 * scale_w)), (int(self.content.setROIX2* scale_w), int(self.content.setROIY2* scale_w)), (0 , 0, 255), 1)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)

            self.lbl_setting_image.setPixmap(QtGui.QPixmap.fromImage(image))

    #=====================================================================
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

    # ==============================================================
    def closeEvent(self, event):
        self.content.SettingBtn.setEnabled(True)
        print("Open CV Setting is closed !!! by Sellect OpenCV Mode: ", self.content.opencv_mode)

        if len(self.set_Recustom_H_edit.text()) > 0 and len(self.set_Recustom_W_edit.text()) > 0:
            self.content.resize_custom_height = int(self.set_Recustom_H_edit.text())
            self.content.resize_custom_width = int(self.set_Recustom_W_edit.text())

        if len(self.set_THRESHBright_edit.text()) > 0 and len(self.set_THRESH_A_edit.text()) > 0 and len(self.set_THRESH_B_edit.text()) > 0:
            self.content.thresh_bright = int(self.set_THRESHBright_edit.text())
            self.content.thesh_seta = int(self.set_THRESH_A_edit.text())
            self.content.thesh_setb = int(self.set_THRESH_B_edit.text())

        self.content.object_name = self.editObjName.text()
        if len(self.editObjScore.text()) > 0 and self.editObjScore.text().isnumeric():
            self.content.score = int(self.editObjScore.text())

        if len(self.WaitBestImage_edit.text()) > 0 and self.WaitBestImage_edit.text().isnumeric():
            self.content.WaitBestImage = int(self.WaitBestImage_edit.text())

        self.display_timer.stop()

# ===================================================================================================
# ===================================================================================================
@register_node(OP_NODE_OPENCV)
class Open_OpenCV(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_opencv_icon.png"
    op_code = OP_NODE_OPENCV
    op_title = "Open CV2"
    content_label_objname = "Open CV2"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[5,3,4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.cv2_Outpayload = {}
        self.CV2_resizePayload = {}
        self.CV2_ObjetPayload = {}

        self.reciev_dataImg = {}
        self.cnt = 0

        self.img = None
        self.PosX_sorted = []

        self.Plaet_Number_PosX = []
        self.Plaet_Number_OCR = []

        self.yolo_img_height, self.yolo_img_width = 480, 640

        self.content.BestImg_timer.timeout.connect(self.update_select_img)
        # self.content.BestImg_timer.setInterval(20)

        self.BestImg_Cnt = 0
        self.OBJ_not_found = 0
        self.start_process = False

        self.hold_img = None
        self.force_crop_image = False

    def initInnerClasses(self):
        self.content = OpenCVConfig(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)               # <----------- Box Image Draw in Flow_Node_Base

        self.grNode.width = 150
        self.grNode.height = 125

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)
        self.content.Rotatecombo.activated[str].connect(self.onRotateChanged)
        self.content.ResCombo.activated[str].connect(self.onResolutionChanged)

    def evalImplementation(self):                 # <
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.reciev_dataImg = input_node.eval()

            if self.reciev_dataImg is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                # return

            else:
                if 'img' in self.reciev_dataImg:
                    if len(str(self.reciev_dataImg['img'])) > 100:
                        self.content.lbl.setText("-> Image Input")
                        self.content.lbl.setStyleSheet("color: #EC6F2F; font-size:5pt;")

                        if 'inputtype' in self.reciev_dataImg:
                            self.cv2_Outpayload['inputtype'] = self.reciev_dataImg['inputtype']
                            self.CV2_resizePayload['inputtype'] = self.reciev_dataImg['inputtype']

                        if 'centers' in self.reciev_dataImg:
                            self.cv2_Outpayload['centers'] = self.reciev_dataImg['centers']
                            self.CV2_resizePayload['centers'] = self.reciev_dataImg['centers']
                    
                        #print("val['img'] = ", val['img'])

                        if 'clock' in self.reciev_dataImg:
                            self.cv2_Outpayload['clock'] = self.reciev_dataImg['clock']
                            self.CV2_resizePayload['clock'] = self.reciev_dataImg['clock']

                        if 'run' in self.reciev_dataImg:
                            self.cv2_Outpayload['run'] = self.reciev_dataImg['run']
                            self.CV2_resizePayload['run'] = self.reciev_dataImg['run']

                        if 'img_feed' in self.reciev_dataImg:
                            self.cv2_Outpayload['img_feed'] = self.reciev_dataImg['img_feed']
                            self.CV2_resizePayload['img_feed'] = self.reciev_dataImg['img_feed']

                        if 'crop_output' in self.reciev_dataImg:
                            self.cv2_Outpayload['crop_output'] = self.reciev_dataImg['crop_output']
                            self.CV2_resizePayload['crop_output'] = self.reciev_dataImg['crop_output']

                        else:
                            if 'fps' in self.reciev_dataImg:
                                self.cv2_Outpayload['fps'] = self.reciev_dataImg['fps']

                        img = self.reciev_dataImg['img']
                        heightImg , widthImg , _ = img.shape
                        # print("heightImg :", heightImg , " x " , widthImg)
                        # self.CV2_resultPayload['result'] = "img_h:" + str(heightImg) + ", img_w:" + str(widthImg)

                        # Operate Process Here !!!!!
                        # if self.content.opencv_mode == "get Image Size":
                        #     img = self.reciev_dataImg['img']
                        #     heightImg , widthImg , _ = img.shape

                        #     self.content.lblPayload.setText("result")
                        #     self.cv2_Outpayload['result'] = "img_h:" + str(heightImg) + ", img_w:" + str(widthImg)

                        # elif self.content.opencv_mode == "Resize Image":
                        #     img = self.reciev_dataImg['img']
                        #     resized_image = cv2.resize(img, (self.content.resize_w, self.content.resize_h))
                        #     self.cv2_Outpayload['img'] = resized_image
                    
                        # payload_img = self.reciev_dataImg['img']

                        self.force_crop_image = False

                        self.content.setting_image = img
                        Payload_img = self.content.setting_image

                        if self.content.setCameraROI:
                            ROI_Img = img.copy()

                            if widthImg == 1280 or widthImg == 1920:
                                scale_w = widthImg/640
                                scale_h = heightImg/480

                            elif widthImg == 640:
                                scale_w = 1

                            #print("scale_h :", scale_h ," , scale_w :", scale_w)

                            # Crop the image
                            # cropped_image = image[y1:y2, x1:x2]
                            y1 = int(self.content.setROIY1 * scale_w) 
                            y2 = int(self.content.setROIY2* scale_w) 
                            
                            x1 = int(self.content.setROIX1 * scale_w) 
                            x2 = int(self.content.setROIX2 * scale_w) 
                            #print("y1 :", y1, " , y2:", y2, " , x1 :", x1, " ,x2:", x2)
                            Payload_img = ROI_Img[y1:y2, x1:x2]

                        h, w, _ = Payload_img.shape
                        self.cv2_Outpayload['img'] = Payload_img
                        self.cv2_Outpayload['inputtype'] = "img"
                        self.cv2_Outpayload['img_h'] = h
                        self.cv2_Outpayload['img_w']= w
                        self.cv2_Outpayload['centers'] = {15: (0, 0), 16: (0, 0)}

                        self.cv2_Outpayload['result'] = str(h) + " x " + str(w)

                        img = Payload_img
                        
                        # if 'fps' in self.reciev_dataImg:
                        #     self.cv2_Outpayload['fps'] = self.reciev_dataImg['fps']
                        # =============================================================
                        if self.content.RotateImageAngle == 90:
                            image_rotated_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                            if image_rotated_90.shape[1] > image_rotated_90.shape[0]:
                                # Calculate the scaling factor to fit the width to 640 pixels
                                scale_factor = self.content.resize_w / image_rotated_90.shape[1]

                            elif image_rotated_90.shape[0] > image_rotated_90.shape[1]:
                                # Calculate the scaling factor to fit the height to 480 pixels
                                scale_factor = self.content.resize_h / image_rotated_90.shape[0]

                            img = self.cropped_image_rotate_standard(image_rotated_90, scale_factor)

                        elif self.content.RotateImageAngle == 180:
                            image_rotated_180 = cv2.rotate(img, cv2.ROTATE_180)
                            if image_rotated_180.shape[1] > image_rotated_180.shape[0]:
                                # Calculate the scaling factor to fit the width to 640 pixels
                                scale_factor = self.content.resize_w / image_rotated_180.shape[1]

                            elif image_rotated_180.shape[0] > image_rotated_180.shape[1]:
                                # Calculate the scaling factor to fit the height to 480 pixels
                                scale_factor = self.content.resize_h / image_rotated_180.shape[0]

                            img = self.cropped_image_rotate_standard(image_rotated_180, scale_factor)

                        elif self.content.RotateImageAngle == 270:
                            image_rotated_270 = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                            if image_rotated_270.shape[1] > image_rotated_270.shape[0]:
                                # Calculate the scaling factor to fit the width to 640 pixels
                                scale_factor = self.content.resize_w / image_rotated_270.shape[1]

                            elif image_rotated_270.shape[0] > image_rotated_270.shape[1]:
                                # Calculate the scaling factor to fit the height to 480 pixels
                                scale_factor = self.content.resize_h / image_rotated_270.shape[0]

                            img = self.cropped_image_rotate_standard(image_rotated_270, scale_factor)

                        if self.content.opencv_mode == "Flip Image":
                            if self.content.flipmode == 0:
                                img = cv2.flip(img, -1)  # Flip Both
                            elif self.content.flipmode == 1:
                                img = cv2.flip(img, 0) # Flip vertically Upside Down
                            elif self.content.flipmode == 2:
                                img = cv2.flip(img, 1)  # Flip Left/Right

                            self.content.payload_obj = False

                        # if 'fps' in self.reciev_dataImg:
                        #     self.CV2_resizePayload['fps'] = self.reciev_dataImg['fps']

                        elif self.content.opencv_mode == "Crop Object Image":
                            # Cropping an image
                            yolo_img = self.reciev_dataImg['img'].copy()
                            img = np.zeros((480, 640, 3), dtype=np.uint8)
                            #self.reciev_dataImg.pop('img')
                            cropped_image = None
                            crop_output = False

                            self.hold_img = None

                            if 'yolo_boxes' in self.reciev_dataImg:
                                if len(self.reciev_dataImg['yolo_boxes']) > 0:
                                    for i in range(len(self.reciev_dataImg['yolo_boxes'])):
                                        if self.reciev_dataImg['yolo_boxes'][i]['obj'] == self.content.object_name and self.reciev_dataImg['yolo_boxes'][i]['score'] >= self.content.score:
                                            #crop_img = img[y:y+h, x:x+w]
                                            self.OBJ_not_found = 0

                                            if not self.start_process:
                                                self.content.BestImg_timer.start()
                                                self.start_process = True

                                            x = self.reciev_dataImg['yolo_boxes'][i]['x1']
                                            y = self.reciev_dataImg['yolo_boxes'][i]['y1']

                                            h = self.reciev_dataImg['yolo_boxes'][i]['y2'] - self.reciev_dataImg['yolo_boxes'][i]['y1']
                                            w = self.reciev_dataImg['yolo_boxes'][i]['x2'] - self.reciev_dataImg['yolo_boxes'][i]['x1']

                                            cropped_image = yolo_img[y:y+h, x:x+w]

                                            if not self.content.re_yolo_640:
                                                self.yolo_img_height, self.yolo_img_width, _ =  cropped_image.shape

                                                # Define the size of the yolo cropped image
                                                yolo_img_height = h
                                                yolo_img_width = w

                                                # Define the desired size of the canvas
                                                canvas_height = 480
                                                canvas_width = 640

                                                # Calculate the scaling factors to fit the yolo cropped image into the canvas
                                                scale_factor = min(canvas_width / yolo_img_width, canvas_height / yolo_img_height)

                                                # Calculate the new dimensions of the resized image
                                                new_width = int(yolo_img_width * scale_factor)
                                                new_height = int(yolo_img_height * scale_factor)

                                                # Resize the yolo cropped image
                                                resized_yolo_img = cv2.resize(cropped_image, (new_width, new_height))

                                                # Create the canvas with the desired size
                                                canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

                                                # Calculate the position to paste the resized image onto the canvas
                                                start_x = (canvas_width - new_width) // 2
                                                start_y = (canvas_height - new_height) // 2

                                                # Paste the resized image onto the canvas
                                                canvas[start_y:start_y + new_height, start_x:start_x + new_width] = resized_yolo_img
                                                cropped_image = canvas

                                            if self.content.select_best_image:
                                                if self.BestImg_Cnt > 0 and self.BestImg_Cnt < int(self.content.WaitBestImage):
                                                    cropped_image = cv2.putText(cropped_image  , str(self.BestImg_Cnt) , (580, 55), cv2.FONT_HERSHEY_DUPLEX, 2, (110, 96, 252), 1)
                                                    img = cv2.resize(cropped_image, dsize=(640 , 480), interpolation=cv2.INTER_AREA)

                                                    self.CV2_ObjetPayload['img'] = img
                                                    self.CV2_ObjetPayload['inputtype'] = 'img'
                                                    self.CV2_ObjetPayload['crop_output'] = True

                                                    # self.sendFixOutputByIndex(self.CV2_ObjetPayload, 2)

                                                    self.CV2_resizePayload['img_h'] = heightImg
                                                    self.CV2_resizePayload['img_w']= widthImg
                                                    self.CV2_resizePayload['img'] = img
                                                    self.CV2_resizePayload['inputtype'] = 'img'

                                                    if not (np.all(img == 0) or np.all(img == 255)):
                                                        self.sendFixOutputByIndex(self.CV2_resizePayload, 1)

                                                else:
                                                    # Send Black Image
                                                    self.content.lbl.setText("<font color: black>Put Blk Img</font>")
                                                    black_image = np.zeros((480, 640, 3), dtype=np.uint8)

                                                    self.CV2_ObjetPayload['img'] = black_image
                                                    self.CV2_ObjetPayload['inputtype'] = 'img'
                                                    self.CV2_ObjetPayload['crop_output'] = False

                                                    self.sendFixOutputByIndex(self.CV2_ObjetPayload, 2)

                                            else:
                                                img = cv2.resize(cropped_image, dsize=(640 , 480), interpolation=cv2.INTER_AREA)

                                                self.CV2_resizePayload['img_h'] = heightImg
                                                self.CV2_resizePayload['img_w']= widthImg
                                                self.CV2_resizePayload['img'] = img
                                                self.CV2_resizePayload['inputtype'] = 'img'

                                                if not (np.all(img == 0) or np.all(img == 255)):
                                                    self.sendFixOutputByIndex(self.CV2_resizePayload, 1)

                                            self.content.payload_obj = True
                                            crop_output = True

                                # No Object Found
                                else:
                                    self.OBJ_not_found += 1
                                    # print("self.OBJ_not_found :", self.OBJ_not_found)
                                    if self.content.select_best_image and self.OBJ_not_found > 3:
                                        if self.BestImg_Cnt > 1:
                                            self.BestImg_Cnt = 0
                                            self.start_process = False

                                            self.content.BestImg_timer.stop()

                                    self.content.lbl.setText("<font color: black>Put Blk Img</font>")
                                    black_image = np.zeros((480, 640, 3), dtype=np.uint8)

                                    self.CV2_ObjetPayload['img'] = black_image
                                    self.CV2_ObjetPayload['inputtype'] = 'img'
                                    self.CV2_ObjetPayload['crop_output'] = False

                                    # self.sendFixOutputByIndex(self.CV2_ObjetPayload, 2)

                                self.CV2_ObjetPayload['crop_output'] = crop_output
                                self.force_crop_image = True
                                # self.lblImgResize = QLabel("func, Rez" , self)
                                self.content.lblImgResize.setText("Crop")

                        else:
                            img = self.reciev_dataImg['img'].copy()
                            self.content.payload_obj = False
                            img = cv2.resize(img, (self.content.resize_w, self.content.resize_h))

                        if self.content.cam_inc_bright_flag:
                            img = self.Increase_cam_brightness(img)

                        if self.content.cam_incCont_flag:
                            img = self.Adjust_cam_contrast(img)

                        # =============================================================
                        # Image Function
                        if self.content.noise_removal_flag:
                            # denoising of image saving it into dst image 
                            # img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15) 
                            # Apply Gaussian Blur
                            img = cv2.GaussianBlur(img, (5, 5), 0)

                            # Apply Median Blur
                            img = cv2.medianBlur(img, 5)

                        if self.content.bgr_rgb:
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                            # Here we show bgr-image in RGB-color-space
                            # rgb_data = np.array(rgb_img)
                            # bgr_data = rgb_data[:, :, ::-1]  # (red,green,blue) --> (blue,green,red)
                            # bgr_img = Image.fromarray(bgr_data)

                        if self.content.image_gray:
                            # Convert the image to grayscale
                            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                            # Create a new 3 channel image with the same size as the original
                            img = cv2.merge([gray_image, gray_image, gray_image])

                        # ==================================================================================
                        # self.thresh_bright = 255
                        # self.thesh_seta = 11
                        # self.thesh_setb = 2

                        if self.content.image_threshold_flag:
                            # print("self.content.image_threshold_mode =", self.content.image_threshold_mode)
                            if self.content.image_threshold_mode == "THRESH_BINARY":
                                ret,image_threshold_img = cv2.threshold(gray_image,127,self.content.thresh_bright,cv2.THRESH_BINARY)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_BINARY_INV":
                                ret,image_threshold_img = cv2.threshold(gray_image,127,self.content.thresh_bright,cv2.THRESH_BINARY_INV)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_TRUNC":
                                ret,image_threshold_img = cv2.threshold(gray_image,127,self.content.thresh_bright,cv2.THRESH_TRUNC)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_TOZERO":
                                ret,image_threshold_img = cv2.threshold(gray_image,127,self.content.thresh_bright,cv2.THRESH_TOZERO)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_TOZERO_INV":
                                ret,image_threshold_img = cv2.threshold(gray_image,127,self.content.thresh_bright,cv2.THRESH_TOZERO_INV)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_MEAN":
                                # Assuming you have already loaded your gray_image and defined the other parameters
                                blockSize = max(3, self.content.thesh_seta)  # Ensuring blockSize is odd and greater than 1

                                # Ensure blockSize is odd
                                if blockSize % 2 == 0:
                                    blockSize += 1

                                image_threshold_img = cv2.adaptiveThreshold(gray_image, self.content.thresh_bright, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize, self.content.thesh_setb)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])

                            elif self.content.image_threshold_mode == "THRESH_GAUSSIAN":
                                image_threshold_img = cv2.adaptiveThreshold(gray_image,self.content.thresh_bright,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,self.content.thesh_seta,self.content.thesh_setb)
                                img = cv2.merge([image_threshold_img, image_threshold_img, image_threshold_img])


                        if self.content.image_segmentation_flag:
                            ret,thresh = cv2.threshold(gray_image,0,self.content.thresh_bright,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
                            #get a kernel
                            kernel = np.ones((3,3),np.uint8)
                            opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel,iterations = 2)
                            #extract the background from image
                            sure_bg = cv2.dilate(opening,kernel,iterations = 3)

                            dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
                            ret,sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
                            
                            sure_fg = np.uint8(sure_fg)
                            img = cv2.merge([sure_fg, sure_fg, sure_fg])

                        if self.content.edges_flage:
                            #calculate the edges using Canny edge algorithm
                            edges = cv2.Canny(img,100,200) 
                            img = cv2.merge([edges, edges, edges])

                        if self.content.perspective:
                            # Here, I have used L2 norm. You can use L1 also.
                            width_AD = np.sqrt(((self.content.pt_A[0] - self.content.pt_D[0]) ** 2) + ((self.content.pt_A[1] - self.content.pt_D[1]) ** 2))
                            width_BC = np.sqrt(((self.content.pt_B[0] - self.content.pt_C[0]) ** 2) + ((self.content.pt_B[1] - self.content.pt_C[1]) ** 2))
                            maxWidth = max(int(width_AD), int(width_BC))


                            height_AB = np.sqrt(((self.content.pt_A[0] - self.content.pt_B[0]) ** 2) + ((self.content.pt_A[1] - self.content.pt_B[1]) ** 2))
                            height_CD = np.sqrt(((self.content.pt_C[0] - self.content.pt_D[0]) ** 2) + ((self.content.pt_C[1] - self.content.pt_D[1]) ** 2))
                            maxHeight = max(int(height_AB), int(height_CD))

                            
                            input_pts = np.float32([self.content.pt_A, self.content.pt_B, self.content.pt_C, self.content.pt_D])
                            output_pts = np.float32([[0, 0],
                                                    [0, maxHeight - 1],
                                                    [maxWidth - 1, maxHeight - 1],
                                                    [maxWidth - 1, 0]])
                            input_pts = np.float32([self.content.pt_A, self.content.pt_B, self.content.pt_C, self.content.pt_D])
                            output_pts = np.float32([[0, 0],
                                                    [0, maxHeight - 1],
                                                    [maxWidth - 1, maxHeight - 1],
                                                    [maxWidth - 1, 0]])
                            
                            # Compute the perspective transform M
                            M = cv2.getPerspectiveTransform(input_pts,output_pts)
                            
                            img = cv2.warpPerspective(img,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)

                        self.CV2_resizePayload['img_h'] = heightImg
                        self.CV2_resizePayload['img_w']= widthImg
                        self.CV2_resizePayload['img'] = img
                        self.CV2_resizePayload['inputtype'] = "img"
                        self.CV2_resizePayload['centers'] = {15: (0, 0), 16: (0, 0)}

                        self.CV2_ObjetPayload['img'] = img
                        self.CV2_ObjetPayload['inputtype'] = 'img'
                        self.CV2_ObjetPayload['img_h'] = self.yolo_img_height
                        self.CV2_ObjetPayload['img_w'] = self.yolo_img_width

                        if 'yolo_boxes' in self.reciev_dataImg:
                            self.CV2_ObjetPayload['yolo_boxes'] = self.reciev_dataImg['yolo_boxes']

                        if self.content.resize_custom_flag:
                            # self.resize_custom_height = 480
                            # self.resize_custom_width = 640

                            img = cv2.resize(img, (self.content.resize_custom_width, self.content.resize_custom_height))

                            self.cv2_Outpayload['img'] = img
                            self.cv2_Outpayload['inputtype'] = 'img'
                            self.cv2_Outpayload['img_h'] = self.content.resize_custom_height
                            self.cv2_Outpayload['img_w']= self.content.resize_custom_width

                            self.CV2_resizePayload['img'] = img
                            self.CV2_resizePayload['inputtype'] = 'img'
                            self.CV2_resizePayload['img_h'] = self.content.resize_custom_height
                            self.CV2_resizePayload['img_w']= self.content.resize_custom_width

                            self.CV2_ObjetPayload['img'] = img
                            self.CV2_ObjetPayload['inputtype'] = 'img'
                            self.CV2_ObjetPayload['img_h'] = self.content.resize_custom_height
                            self.CV2_ObjetPayload['img_w'] = self.content.resize_custom_width

                        self.sendFixOutputByIndex(self.cv2_Outpayload, 0)

                        if not self.force_crop_image and not (np.all(img == 0) or np.all(img == 255)):
                            # self.lblImgResize = QLabel("func, Rez" , self)
                            self.content.lblImgResize.setText("func, Rez")
                            self.sendFixOutputByIndex(self.CV2_resizePayload, 1)

                        self.sendFixOutputByIndex(self.CV2_ObjetPayload, 2)

                        if self.content.save_crop_yolo_flag:
                            cv2.imwrite(self.content.save_filelocation + '/Image_' + str(self.content.image_count)+ '.png', self.CV2_ObjetPayload['img'])
                            if self.content.jump_image_cnt != 0:
                                self.content.image_count = self.content.jump_image_cnt
                                print("save_crop_yolo_flag :", self.content.save_crop_yolo_flag, " ;current image_count :", self.content.image_count)

                            self.content.image_count += 1

                else:
                    self.content.lbl.setText("<font color: white>No Image Input</font>")
                    black_image = np.zeros((480, 640, 3), dtype=np.uint8)

                    self.CV2_ObjetPayload['img'] = black_image
                    self.CV2_ObjetPayload['inputtype'] = 'img'
                    self.sendFixOutputByIndex(self.CV2_ObjetPayload, 2)

    def update_select_img(self):
        self.BestImg_Cnt += 1
        # print("self.BestImg_Cnt :", self.BestImg_Cnt)
        # if self.BestImg_Cnt > 10:
        #     self.BestImg_timer.stop()
        #     self.BestImg_Cnt = 0
                
    def valTrackbars(self):
        Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
        Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
        src = Threshold1,Threshold2
        return src
    
    def cropped_image_rotate_standard(self, cropped_image, scale_factor):
        # print("self.content.image_height:", self.content.img_height, " , self.content.image_width:", self.content.img_width)
        background = np.zeros((self.content.resize_h, self.content.resize_w, 3), np.uint8)

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
    
    # =========================================================================
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
    
    # =========================================================================
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
    
    # =========================================================================
    def onRotateChanged(self, text):
        select = text[0:-2]
    
        self.content.RotateImageAngle = int(select)
        print("Select Rotate Angle = ", self.content.RotateImageAngle)
    
    def onResolutionChanged(self, text):
        self.content.camera_res = text
        if self.content.camera_res == '1280':
            self.content.resize_w = 1280
            self.content.resize_h = 720
            
        elif self.content.camera_res == '1920':
            self.content.resize_w = 1920
            self.content.resize_h = 1080

        elif self.content.camera_res == '2560':
            self.content.resize_w = 2560
            self.content.resize_h = 1440

        else:
            self.content.resize_w = 640
            self.content.resize_h = 480

    def OnOpen_Setting(self):

        self.content.SettingBtn.setEnabled(False)
        self.OpenCV_Function = OpenCV_Function(self.content)
        self.OpenCV_Function.show()

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

#===============================================================================================================
"""elif self.content.opencv_mode == "Easy OCR":
    if 'org_cropped_image' in self.reciev_dataImg:
        print("len(self.reciev_dataImg['org_cropped_image']) = ", len(self.reciev_dataImg['org_cropped_image']))
        if len(self.reciev_dataImg['org_cropped_image']) > 30:

            imgH , imgW , _ = self.reciev_dataImg['org_cropped_image'].shape
            print("imgH = ", imgH)
            print("imgW = ", imgW)

            self.img = self.reciev_dataImg['org_cropped_image'].copy()

    else:
        self.img = self.reciev_dataImg['img']

    #print("img = ", self.img)
    result = self.content.reader.readtext(self.img)
    print("Easy OCR Result = ", result)
    text = ""
    for res in result:
        text = res[1]

    print("Easy OCR = ", text)

    self.payload['resul"""

