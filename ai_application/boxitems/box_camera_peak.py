# https://en.ids-imaging.com/files/downloads/ids-peak/readme/ids-peak-windows-readme-1.2_EN.html#first-start
# install library
# C:\Program Files\IDS\ids_peak\generic_sdk\api\binding\python\wheel\x86_64
# C:\Program Files\IDS\ids_peak\generic_sdk\ipl\binding\python\wheel\x86_64

# pip install ids_peak-1.6.1.0-cp310-cp310-win_amd64.whl
# pip install ids_peak_ipl-1.8.0.0-cp310-cp310-win_amd64.whl

# import sys
from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak import ids_peak_ipl_extension

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import*
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

VERSION = "1.2.0"
FPS_LIMIT = 30

import os
import time

import numpy as np
import cv2

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId

#CalcInputContent
class idsPeakCamera(QDMNodeContentWidget):
    def initUI(self):
        path = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.normpath(os.path.join(path, ".."))
        # print(fpath)
        self.fpath = fpath
        # self.capture_icon = path + "/icons/icons_capture.png"
        # Create a QIcon with the pixmap
        # icon = QIcon(QtGui.QPixmap(path + "/icons/icons_capture.png"))
        # self.video_icon = path + "/icons/icons_peak_20.png"
        # peak_img = QtGui.QPixmap(path + "/icons/icons_peak_45.png")

        self.setting_icon = path + "/icons/icons_settings_icon.png"

        self.lbIcon = QtWidgets.QLabel(self)
        self.lbIcon.setGeometry(QtCore.QRect(1, 2, 40, 40))
        self.lbIcon.setText("")
        self.lbIcon.setPixmap(QtGui.QPixmap(path + "/icons/icons_ids_peak_48.png"))
        # self.lbIcon.setPixmap(peak_img)
        self.lbIcon.setObjectName("lbIcon")

        self.lbComment = QtWidgets.QLabel(self)
        self.lbComment.setGeometry(QtCore.QRect(50, 5, 111, 20))
        self.lbComment.setStyleSheet("font: 75 7pt \"Consolas\";")
        self.lbComment.setAlignment(QtCore.Qt.AlignCenter)
        self.lbComment.setObjectName("lbComment")
        
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(5, 47, 131, 22))
        self.comboBox.setStyleSheet("font: 75 7pt \"Consolas\";")
        self.comboBox.setObjectName("comboBox")

        self.bCamState = QtWidgets.QPushButton(self)
        self.bCamState.setGeometry(QtCore.QRect(80, 98, 70, 23))
        # Set the icon on the QPushButton
        self.bCamState.setIcon(QIcon(QtGui.QPixmap(path + "/icons/icons_capture.png")))
        self.bCamState.setIconSize(QtCore.QSize(75, 23))
        self.bCamState.setStyleSheet("font: 75 7pt \"Consolas\";")
        self.bCamState.setObjectName("bCamState")

        #====================================================
        # Label
        self.lblPayload = QLabel("Payload" , self)
        self.lblPayload.setAlignment(Qt.AlignLeft)
        self.lblPayload.setGeometry(135,33,35,20)
        self.lblPayload.setStyleSheet("color: #FFDD00; font-size:5pt;")

        self.lblImgHW = QLabel("H : W" , self)
        self.lblImgHW.setAlignment(Qt.AlignLeft)
        self.lblImgHW.setGeometry(145,55,35,20)
        self.lblImgHW.setStyleSheet("color: #FBC8B5; font-size:5pt;")

        self.lblImgResize = QLabel("Image 640 x 480" , self)
        self.lblImgResize.setAlignment(Qt.AlignLeft)
        self.lblImgResize.setGeometry(100,77,80,20)
        self.lblImgResize.setStyleSheet("color: #EF8028; font-size:5pt;")

        self.Rotatecombo = QComboBox(self)
        self.Rotatecombo.addItem("0 " + chr(176))
        self.Rotatecombo.addItem("90 " + chr(176))
        self.Rotatecombo.addItem("180 " + chr(176))
        self.Rotatecombo.addItem("270 " + chr(176))
        self.Rotatecombo.setGeometry(5,70,70,25)
        self.Rotatecombo.setStyleSheet("QComboBox"
                                   "{"
                                        "background-color : #33CCFF; font-size:6pt;"
                                   "}") 

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(155,100,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.RotateImageAngle = 0
        self.resize_h = 480
        self.resize_w = 640

        self.cam_inc_bright_flag = False
        self.increase_brightness = 0

        self.cam_incCont_flag = False
        self.adjust_contrast = 1

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

        self.setting_image = None

        # ============================================
        # List to store device information
        self.devices_info = []

        # self.find_Camera()

        self.camid = 0
        self.retranslateUi()

        self.USBScan_timer = QtCore.QTimer(self)
        self.GlobalTimer = GlobalVariable()
        if self.GlobalTimer.hasGlobal("GlobalTimerApplication"):
            ListGlobalTimer = []
            ListGlobalTimer = list(self.GlobalTimer.getGlobal("GlobalTimerApplication"))

            ListGlobalTimer.append(self.USBScan_timer)
            self.GlobalTimer.setGlobal("GlobalTimerApplication", ListGlobalTimer)

    def retranslateUi(self):
        if len(self.devices_info) > 0:
            self.lbComment.setText(self.devices_info[0]["Model"])
        else:
            self.lbComment.setText("U3-3560XCP-HQ")
        
        self.bCamState.setText("Start")

    def serialize(self):
        res = super().serialize()
        res['CamId'] = self.comboBox.currentText()
        res['CamState'] = self.bCamState.text()

        res['rotate_img'] = self.RotateImageAngle

        res['cam_bright_flag'] = self.cam_inc_bright_flag
        res['number_br_increas'] = self.increase_brightness

        res['incCont_flag'] = self.cam_incCont_flag
        res['number_contrast'] = self.adjust_contrast

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

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            text = data['CamId']
            camstate = data['CamState']
            
            index = self.comboBox.findText(text)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)
                if camstate == "Stop":
                    self.bCamState.click()
            # time.sleep(0.1)
                    
            if 'rotate_img' in data:
                self.RotateImageAngle = data['rotate_img']
                self.Rotatecombo.setCurrentText(str(self.RotateImageAngle) + " " + chr(176))

            if 'cam_bright_flag' in data:
                self.cam_inc_bright_flag = data['cam_bright_flag']

            if 'number_br_increas' in data:
                self.increase_brightness = data['number_br_increas']

            if 'incCont_flag' in data:
                self.cam_incCont_flag = data['incCont_flag']

            if 'number_contrast' in data:
                self.adjust_contrast = data['number_contrast']

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

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
    def find_Camera(self):
                # initialize peak library
        ids_peak.Library.Initialize()

        # Create instance of the device manager
        device_manager = ids_peak.DeviceManager.Instance()

        # Update the device manager
        device_manager.Update()

        # Check if any device was found
        if not device_manager.Devices().empty():
            # Iterate over each device and store information
            for i, device in enumerate(device_manager.Devices()):
                device_obj = {
                    "ID": i,
                    "Serial": device.SerialNumber(),
                    "Model": device.ModelName()
                }
                print(device_obj)
                self.comboBox.addItem(device.SerialNumber())
                self.devices_info.append(device_obj)

            self.USBScan_timer.stop()
            return True

        else:
            # Handle the case when no devices are found
            # Example: Print an error message or log it
            print("initUI : No device found!")
            self.USBScan_timer.start()
            return False
        
        # Close device and peak library
        ids_peak.Library.Close()

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

        self.camera_res = 4200
        
        self.ids_h = 3120
        self.ids_w = 4200

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
        self.resizable_rect_label.setGeometry(0, 0, self.ids_w, self.ids_h)  # Set the size to match self.lbl_setting_image
        self.resizable_rect_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 1px solid white; border-radius: 3%")
        self.resizable_rect_label.coordinates_changed.connect(self.handle_coordinates_changed)

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


        self.Install_Btn = QPushButton("Install ids_peak", self)
        self.Install_Btn.setGeometry(990,680,200,30)
        self.Install_Btn.clicked.connect(self.exe_command)

    # ==============================================================
    # End UI Interface
    # ==============================================================================
    def exe_command(self):

        shell = client.Dispatch("WScript.Shell")
        run_cmdScript = Exec_cmdScript()
        run_cmdScript.open_cmd(shell)
        # run_cmdScript.activate_venv(shell, root_part, self.Training_File_Path)
        run_cmdScript.run_cmd_script(shell, "cd C:\Program Files\IDS\ids_peak\generic_sdk\\api\\binding\python\wheel\\x86_64")
        time.sleep(0.5)

        run_cmdScript.run_cmd_script(shell, "pip install ids_peak-1.6.1.0-cp310-cp310-win_amd64.whl")
        time.sleep(0.5)

        run_cmdScript.run_cmd_script(shell, "C:\Program Files\IDS\ids_peak\generic_sdk\ipl\\binding\python\wheel\\x86_64")
        time.sleep(0.5)

        run_cmdScript.run_cmd_script(shell, "pip install ids_peak_ipl-1.8.0.0-cp310-cp310-win_amd64.whl")
        time.sleep(1)

        run_cmdScript.run_cmd_script(shell, "  exit")

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

    def onChangedROI1(self, text):
        # print("onChangedROI1 ==> text:", text[:-2])
        self.content.rotateROI1 = str(text[:-2])

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

    def checkConvertROI1(self, state):
        if state == QtCore.Qt.Checked:
            self.content.convert_angle_ROI1 = True
            if len(self.setRefColorROI1_edit.text()) > 0 and self.setRefColorROI1_edit.text().isnumeric():
                self.content.color_refROI1 = self.setRefColorROI1_edit.text()
        else:
            self.content.convert_angle_ROI1 = False

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

    def closeEvent(self, event):
        self.content.SettingBtn.setEnabled(True)

        #ROI1
        if len(self.setROIX1_edit.text()) > 0 and self.setROIX1_edit.text().isnumeric(): self.content.setROIX1 = int(self.setROIX1_edit.text())
        if len(self.setROIY1_edit.text()) > 0 and self.setROIY1_edit.text().isnumeric(): self.content.setROIY1 = int(self.setROIY1_edit.text())
        if len(self.setROIX2_edit.text()) > 0 and self.setROIX2_edit.text().isnumeric(): self.content.setROIX2 = int(self.setROIX2_edit.text())
        if len(self.setROIY2_edit.text()) > 0 and self.setROIY2_edit.text().isnumeric(): self.content.setROIY2 = int(self.setROIY2_edit.text())

        if len(self.CustomA_ROI1_edit.text()) > 0 and len(self.CustomA_ROI1_edit.text()) <= 3 and self.CustomA_ROI1_edit.text().isnumeric(): self.content.angle_ROI1 = self.CustomA_ROI1_edit.text()
        if len(self.setRefColorROI1_edit.text()) > 0 and self.setRefColorROI1_edit.text().isnumeric(): self.content.color_refROI1 = self.setRefColorROI1_edit.text()

        self.display_timer.stop()

# ========================================================================================================
# ========================================================================================================        

@register_node(OP_NODE_PEAK)
class Open_CAM(FlowNode):
    path = os.path.dirname(os.path.abspath(__file__))
    icon = path + "/icons/icons_ids_peak_48.png"
    op_code = OP_NODE_PEAK
    op_title = "iDS Peak Cam 3.0"
    content_label_objname = "Cam Process"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[5,3,4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.ids_payload = {}
        self.ids_payload['fps'] = 1
        self.ids_payload['img'] = None
        self.ids_payload['inputtype'] = "img"

        self.ids_640_payload = {}
        self.ids_640_payload['img'] = None
        self.ids_640_payload['inputtype'] = "img"

        self.ids_imgSize_paylaod = {}

        self.__device = None
        self.__nodemap_remote_device = None
        self.__datastream = None

        self.__display = False
        self.__acquisition_timer = QTimer()
        self.__frame_counter = 0
        self.__error_counter = 0
        self.__acquisition_running = False

        # initialize peak library
        ids_peak.Library.Initialize()

        self.device_loss = False
        self.wait__sec = 0

    def initInnerClasses(self):
        self.content = idsPeakCamera(self)
        self.grNode = FlowGraphicsCholeProcess(self)               # <----------- Box Image Draw in Flow_Node_Base

        self.grNode.width = 180
        self.grNode.height = 150

        self.content.bCamState.clicked.connect(self.onClicked)
        # self.content.txCamId.textChanged.connect(self.ChangedChanel)
        # self.content.comboBox.currentIndexChanged.connect(self.ChangedDevice)
        self.content.Rotatecombo.activated[str].connect(self.onRotateChanged)

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

        self.content.USBScan_timer.timeout.connect(self.update_USB)
        self.content.USBScan_timer.setInterval(1000)
        self.content.USBScan_timer.stop()

        self.content.find_Camera()

    def update_USB(self):
        self.wait__sec += 1
        # print("update_USB wait__sec :", self.wait__sec)
        if self.wait__sec >= 5:
            self.wait__sec = 0
            if self.content.find_Camera():
                self.onClicked()

    def onClicked(self):
        if self.content.bCamState.text() == "Start":
            self.content.comboBox.setEnabled(False)
            self.content.bCamState.setText("Stop")
            
            self.__initial_device()
            
            self.__start_acquisition()
            
        else:
            self.content.comboBox.setEnabled(True)
            self.content.bCamState.setText("Start")
            # Stop acquisition timer
            self.__acquisition_timer.stop()
            self.__acquisition_running = False
            self.__destroy_all()
            
    def ChangedDevice(self):
        # Get the current index
        current_index = self.content.comboBox.currentIndex()
        # Print the current index
        print(f"Changed device to index: {current_index}")
    
    def __initial_device(self):
        # Get the current index
        current_index = self.content.comboBox.currentIndex()
        
        try:
            # initial new camera device
            self.__device = None
            self.__nodemap_remote_device = None
            self.__datastream = None

            self.__display = False
            self.__acquisition_timer = QTimer()
            self.__frame_counter = 0
            self.__error_counter = 0
            self.__acquisition_running = False

            # initialize peak library
            ids_peak.Library.Initialize()

            self.content.bCamState.setEnabled(True)

        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            return
        
        if self.__open_device(source=current_index):
            try:
                print("Open device: ", current_index)

            except Exception as e:
                # QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)
                # Optionally, log the exception to a file or logging system
                print("Exception occurred:", e)

        else:
            self.content.bCamState.setEnabled(False)
            self.content.lbComment.setText("Camera is opened")
            self.__destroy_all()
            

    # ========================================================================================
    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        # Stop acquisition
        self.__stop_acquisition()

        # Close device and peak library
        self.__close_device()
        ids_peak.Library.Close()

    def __open_device(self, source=0):
        try:
            # Create instance of the device manager
            device_manager = ids_peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                # QMessageBox.critical(self, "Error", "No device found!", QMessageBox.Ok)
                print("__open_device : No device found!")
                return False

            # # # Open the first openable device in the managers device list
            # # for device in device_manager.Devices():
            # #     if device.IsOpenable():
            # #         self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
            # #         break
            # for i, _ in enumerate(device_manager.Devices()):
            #     if source > i:
            #         return False

            # self.__device = device_manager.Devices()[source].OpenDevice(ids_peak.DeviceAccessType_Control)
            self.__device = device_manager.Devices()[source].OpenDevice(ids_peak.DeviceAccessType_Control)

            # Return if no device could be opened
            if self.__device is None:
                # QMessageBox.critical(self, "Error", "Device could not be opened!", QMessageBox.Ok)
                print("Device could not be opened!")
                return False

            # Open standard data stream
            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                # QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.Ok)
                print("Device has no DataStream!")
                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()

            # Get nodemap of the remote device for all accesses to the genicam nodemap tree
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            # To prepare for untriggered continuous image acquisition, load the default user set if available and
            # wait until execution is finished
            try:
                ####--## Load from file
                # file = "para1.cset"
                # self.__nodemap_remote_device.LoadFromFile(file)

                source = int(source)  # Ensure 'source' is an integer (if it's not already)
    
                # Construct the file path using string formatting
                # file = f"{self.content.fpath}/para{source + 1}.cset"
                file = f"{self.content.fpath}/{self.content.comboBox.currentText()}.cset"
                
                # Check if the file exists before loading it
                if os.path.isfile(file):
                    self.__nodemap_remote_device.LoadFromFile(file)
                    # time.sleep(0.5)
                else:
                    self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
                    self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
                    self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            except ids_peak.Exception:
                # Userset is not available
                pass

            # Get the payload size for correct buffer allocation
            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()

            # Get minimum number of buffers that must be announced
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            # Allocate and announce image buffers and queue them
            for i in range(buffer_count_max):
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception as e:
            # QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)
            print("__open_device :", str(e))

        return False
    
    def __close_device(self):
        """
        Stop acquisition if still running and close datastream and nodemap of the device
        """
        # Stop Acquisition in case it is still running
        self.__stop_acquisition()

        # If a datastream has been opened, try to revoke its image buffers
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception as e:
                # QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)
                print("__close_device :", str(e))
    
    def __start_acquisition(self):
        """
        Start Acquisition on camera and start the acquisition timer to receive and display images

        :return: True/False if acquisition start was successful
        """
        # Check that a device is opened and that the acquisition is NOT running. If not, return.

        if self.__display is True:
            self.__acquisition_timer.start()
            self.__acquisition_running = True
            return

        if self.__device is None:
            return False

        if self.__acquisition_running is True:
            return True

        # Get the maximum framerate possible, limit it to the configured FPS_LIMIT. If the limit can't be reached, set
        # acquisition interval to the maximum possible framerate
        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            # # AcquisitionFrameRate is not available. Unable to limit fps. Print warning and continue on.
            # QMessageBox.warning(self, "Warning",
            #                     "Unable to limit fps, since the AcquisitionFrameRate Node is"
            #                     " not supported by the connected camera. Program will continue without limit.")
            print("Unable to limit fps, since the AcquisitionFrameRate Node is not supported by the connected camera. Program will continue without limit.")

        # Setup acquisition timer accordingly
        # Convert the calculated interval to an integer
        interval_ms = int((1 / target_fps) * 1000)
        # self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        self.__acquisition_timer.setInterval(interval_ms)
        self.__acquisition_timer.setSingleShot(False)
        self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            # Lock critical features to prevent them from changing during acquisition
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition on camera
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception as e:
            print("Exception; __start_acquisition: " + str(e))

            return False

        # Start acquisition timer
        self.__acquisition_timer.start()
        self.__acquisition_running = True
        self.__display = True
        # return True
    
    def __stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        :return:
        """
        # Check that a device is opened and that the acquisition is running. If not, return.
        if self.__device is None or self.__acquisition_running is False:
            return

        # Otherwise try to stop acquisition
        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush datastream
            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self.__acquisition_running = False

            # Unlock parameters after acquisition stop
            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    # QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)
                    print(str(e))

        except Exception as e:
            # QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)
            print("__stop_acquisition :", str(e))
    
    # @Slot()
    def on_acquisition_timer(self):
        """
        This function gets called on every timeout of the acquisition timer
        """
        try:
            # Get buffer from device's datastream
            buffer = self.__datastream.WaitForFinishedBuffer(5000)

            # Create IDS peak IPL image for debayering and convert it to RGBa8 format
            ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
            # converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8)
            converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
            # Queue buffer so that it can be used again
            self.__datastream.QueueBuffer(buffer)

            # # Get raw image data from converted image and construct a QImage from it
            # image_np_array = converted_ipl_image.get_numpy_1D()
            # image = QImage(image_np_array,
            #                converted_ipl_image.Width(), converted_ipl_image.Height(),
            #                QImage.Format_RGB32)

            # # Make an extra copy of the QImage to make sure that memory is copied and can't get overwritten later on
            # image_cpy = image.copy()

            # # Emit signal that the image is ready to be displayed
            # self.__display.on_image_received(image_cpy)
            # self.__display.update()

            # if self.__acquisition_running is True:
            # Convert the IPL image to a NumPy array
            image_np_array = converted_ipl_image.get_numpy_3D()

            image_np_array = image_np_array[:, :, :3].astype(np.uint8)
            # image_np_array = cv2.resize(image_np_array, (640, 480))
            Payload_img = image_np_array
            # self.payload['fps'] = time.time()
            # self.payload['inputtype'] = "img"

            if type(image_np_array) != type(None):
                self.content.setting_image = image_np_array

            if self.content.setCameraROI:
                ROI_Img = image_np_array.copy()

                scale_w = 6.5625
                scale_h = 6.5

                # Crop the image
                # cropped_image = image[y1:y2, x1:x2]
                y1 = int(self.content.setROIY1 * scale_h) 
                y2 = int(self.content.setROIY2* scale_h) 
                
                x1 = int(self.content.setROIX1 * scale_w) 
                x2 = int(self.content.setROIX2 * scale_w) 
                # print("y1 :", y1, " , y2:", y2, " , x1 :", x1, " ,x2:", x2)
                Payload_img = ROI_Img[y1:y2, x1:x2]

            self.ids_payload['img'] = Payload_img

            # Increase frame counter
            # self.__frame_counter += 1
            # self.ids_payload['img'] = image_np_array
            self.ids_payload['fps'] = time.time()
            self.ids_640_payload['fps'] = self.ids_payload['fps']

            heightImg , widthImg , _ = image_np_array.shape
            self.ids_imgSize_paylaod['result'] = "img_h:" + str(heightImg) + ", img_w:" + str(widthImg)

            image_np_array = cv2.resize(image_np_array, (640, 480))
            self.res_img = cv2.resize(image_np_array, (self.content.resize_w, self.content.resize_h))
            if self.content.cam_inc_bright_flag:
                self.res_img = self.Increase_cam_brightness(self.res_img)

            if self.content.cam_incCont_flag:
                self.res_img = self.Adjust_cam_contrast(self.res_img)

            if self.content.RotateImageAngle == 90:
                image_rotated_90 = cv2.rotate(self.res_img, cv2.ROTATE_90_CLOCKWISE)
                if image_rotated_90.shape[1] > image_rotated_90.shape[0]:
                    # Calculate the scaling factor to fit the width to 640 pixels
                    scale_factor = self.content.resize_w / image_rotated_90.shape[1]

                elif image_rotated_90.shape[0] > image_rotated_90.shape[1]:
                    # Calculate the scaling factor to fit the height to 480 pixels
                    scale_factor = self.content.resize_h / image_rotated_90.shape[0]

                self.res_img = self.cropped_image_rotate_standard(image_rotated_90, scale_factor)

            elif self.content.RotateImageAngle == 180:
                image_rotated_180 = cv2.rotate(self.res_img, cv2.ROTATE_180)
                if image_rotated_180.shape[1] > image_rotated_180.shape[0]:
                    # Calculate the scaling factor to fit the width to 640 pixels
                    scale_factor = self.content.resize_w / image_rotated_180.shape[1]

                elif image_rotated_180.shape[0] > image_rotated_180.shape[1]:
                    # Calculate the scaling factor to fit the height to 480 pixels
                    scale_factor = self.content.resize_h / image_rotated_180.shape[0]

                self.res_img = self.cropped_image_rotate_standard(image_rotated_180, scale_factor)

            elif self.content.RotateImageAngle == 270:
                image_rotated_270 = cv2.rotate(self.res_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                if image_rotated_270.shape[1] > image_rotated_270.shape[0]:
                    # Calculate the scaling factor to fit the width to 640 pixels
                    scale_factor = self.content.resize_w / image_rotated_270.shape[1]

                elif image_rotated_270.shape[0] > image_rotated_270.shape[1]:
                    # Calculate the scaling factor to fit the height to 480 pixels
                    scale_factor = self.content.resize_h / image_rotated_270.shape[0]

                self.res_img = self.cropped_image_rotate_standard(image_rotated_270, scale_factor)

            self.ids_640_payload['img'] = self.res_img

        except ids_peak.Exception as e:
            self.__error_counter += 1
            # print("Exception; on_acquisition_timer: " + str(e))
            self.scan_usb_cam()
            # self.__stop_acquisition()
        
        self.sendFixOutputByIndex(self.ids_payload, 0)
        self.sendFixOutputByIndex(self.ids_imgSize_paylaod, 1)
        self.sendFixOutputByIndex(self.ids_640_payload, 2)

    def scan_usb_cam(self):
        # initialize peak library
        ids_peak.Library.Initialize()

        # Create instance of the device manager
        device_manager = ids_peak.DeviceManager.Instance()

        # Update the device manager
        device_manager.Update()

        # List to store device information
        self.devices_info = []

        # Check if any device was found
        if not device_manager.Devices().empty():
            # Iterate over each device and store information
            for i, device in enumerate(device_manager.Devices()):
                device_obj = {
                    "ID": i,
                    "Serial": device.SerialNumber(),
                    "Model": device.ModelName()
                }
                print(device_obj)
                if self.content.comboBox.currentText() == device.SerialNumber():
                    self.onClicked()
                    self.device_loss = False

                # self.devices_info.append(device_obj)
        else:
            # Handle the case when no devices are found
            # Example: Print an error message or log it
            if not self.device_loss:
                self.device_loss = True

                print("scan_usb_cam : No device found!")

                self.content.comboBox.setEnabled(True)
                self.content.bCamState.setText("Start")
                # Stop acquisition timer
                # self.__acquisition_timer.stop()
                self.__acquisition_running = False
                self.__destroy_all()

                text = "Camera Disconnected !!!"
                img_height, img_width, img_colors = self.res_img.shape

                start_x = int(int(img_width)/10)
                end_x = int(img_width) - int(int(img_width)/10)
                end_y = int(img_height) - int(int(img_height)/10)

                start_y = end_y - 50

                blk = np.zeros((int(img_height), int(img_width), 3), np.uint8)

                image = cv2.resize(self.res_img, (int(img_width), int(img_height)), interpolation = cv2.INTER_AREA)
                image = cv2.rectangle(image, (0, 0), (int(int(img_width)/2), int(int(img_height)/10) - 15), (0 , 0, 255), -1)
                blk   = cv2.line(blk, (0,0), (int(img_width), int(img_height)), ( 0, 0, 255 ), 3) 
                blk   = cv2.line(blk, (0, int(img_height)), (int(img_width) ,0), ( 0, 0, 255 ), 3) 
                blk   = cv2.rectangle(blk, (0, 0), (int(img_width) - 10, int(img_height)), (0 , 0, 255), 65)
                image = cv2.putText(image  , text , ( start_x + 10, end_y - 5 ), cv2.FONT_HERSHEY_DUPLEX, 1, ( 0, 0, 255 ), 2)
                blk   = cv2.rectangle(blk, (start_x, start_y), (end_x + 10, end_y + 10), (224 , 255, 2), -1)

                image = cv2.addWeighted(image, 1.0, blk, 0.20, 1)

                self.ids_payload['img'] = image
                self.ids_640_payload['img'] = image
        
        # Close device and peak library
        ids_peak.Library.Close()

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

    def onRotateChanged(self, text):
        select = text[0:-2]
    
        self.content.RotateImageAngle = int(select)
        print("Select Rotate Angle = ", self.content.RotateImageAngle)

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

        #self.grNode.setToolTip("")
        self.evalChildren(index)

  