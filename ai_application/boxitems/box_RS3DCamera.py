from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time

import math
import numpy as np

import pyrealsense2 as rs
import cv2

import os

class Realsense3DCAM(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.video_icon = self.Path + "/icons/icons_video.png"
        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        self.realsense_logo = self.Path + "/icons/icons_intel_realsense.png"

        self.lbl = QLabel("N" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(2,7,10,20)
        self.lbl.setStyleSheet("color: orange; font-size:6pt;")

        self.lbl_cap = QLabel("Capture" , self)
        self.lbl_cap.setAlignment(Qt.AlignLeft)
        self.lbl_cap.setGeometry(10,55,50,20)
        self.lbl_cap.setStyleSheet("color: red; font-size:6pt;")

        self.lbl_nocam = QLabel("No Camera !!" , self)
        self.lbl_nocam.setAlignment(Qt.AlignLeft)
        self.lbl_nocam.setGeometry(15,70,100,20)
        self.lbl_nocam.setStyleSheet("color: red; font-size:8pt;")
        self.lbl_nocam.setVisible(False)

        self.radioState = QRadioButton(self)
        self.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                        "background-color : #33CCFF"
                                   "}")
        self.radioState.setGeometry(15,4,60,25)
        self.radioState.setIcon(QIcon(self.video_icon))

        # ==========================================================
        # Label for output
        self.lbl_out1 = QLabel("Raw Img" , self)
        self.lbl_out1.setAlignment(Qt.AlignLeft)
        self.lbl_out1.setGeometry(100,20,50,20)
        self.lbl_out1.setStyleSheet("color: lightblue; font-size:5pt;")

        self.lbl_out2 = QLabel("ColorMap" , self)
        self.lbl_out2.setAlignment(Qt.AlignLeft)
        self.lbl_out2.setGeometry(95,42,50,20)
        self.lbl_out2.setStyleSheet("color: pink; font-size:5pt;")

        self.lbl_out3 = QLabel("Distance" , self)
        self.lbl_out3.setAlignment(Qt.AlignLeft)
        self.lbl_out3.setGeometry(105,65,50,20)
        self.lbl_out3.setStyleSheet("color: orange; font-size:5pt;")

        self.lbl_out4 = QLabel("All" , self)
        self.lbl_out4.setAlignment(Qt.AlignLeft)
        self.lbl_out4.setGeometry(125,87,50,20)
        self.lbl_out4.setStyleSheet("color: green; font-size:5pt;")

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(125,102,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.Select2DBtn = QPushButton("2D", self)
        self.Select2DBtn.setGeometry(100,2,20,20)
        self.Select2DBtn.setStyleSheet("color: lightgreen; font-size:6pt;")
        self.Select2DBtn.setVisible(False)
        self.Select2DBtn_flag = True

        self.lbl_2D = QLabel("2D" , self)
        self.lbl_2D.setAlignment(Qt.AlignLeft)
        self.lbl_2D.setGeometry(100,2,20,20)
        self.lbl_2D.setStyleSheet("color: white; font-size:7pt;")
        # self.lbl_2D.setVisible(False)

        self.Select3DBtn = QPushButton("3D", self)
        self.Select3DBtn.setGeometry(125,2,20,20)
        self.Select3DBtn.setStyleSheet("color: blue; font-size:6pt;")
        self.Select3DBtn_flag = False

        self.lbl_3D = QLabel("3D" , self)
        self.lbl_3D.setAlignment(Qt.AlignLeft)
        self.lbl_3D.setGeometry(125,2,20,20)
        self.lbl_3D.setStyleSheet("color: white; font-size:7pt;")
        self.lbl_3D.setVisible(False)

        self.CameraSelect_Mode = "2D"

        #====================================================
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(120,30)
        self.graphicsView.setGeometry(QtCore.QRect(2, 88, 120, 30))

        img = QPixmap(self.realsense_logo)
        self.pixmap.setPixmap(img)

        # ==========================================================
        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.No_Camera_timer = QtCore.QTimer(self)
        self.No_Camera_timer.timeout.connect(self.show_camerror)

        self.Camera_timer = QtCore.QTimer(self)

        self.GlobalTimer = GlobalVariable()
        if self.GlobalTimer.hasGlobal("GlobalTimerApplication"):
            ListGlobalTimer = []
            ListGlobalTimer = list(self.GlobalTimer.getGlobal("GlobalTimerApplication"))

            ListGlobalTimer.append(self.Camera_timer)
            self.GlobalTimer.setGlobal("GlobalTimerApplication", ListGlobalTimer)

        # ==========================================================
        # Config pyrealsense2 Camera

        # Configure depth and color streams
        # ==========================================================
        self.window = None
        self.pc = None
        self.colorizer = None
        self.filters = None
        self.other_stream = None
        self.other_format = None
        self.decimate = None

        self.image_data = None
        self.width = 0
        self.height = 0

        self.vertex_list = None

        self.camera_link_flag = False
        self.relink_camera_cnt = 0

        self.depth_intrinsics = None
        self.out = None

        self.state = AppState()

        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Get device product line for setting a supporting resolution
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.Check_Camera_Link()

        # ==========================================================

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.autorun = ""
        self.Global_Object = ""
        self.GlobalObject_key = ""

        self.color_alpha = 0.2
        self.colorList = [(0,255,255) , (255,255,0)]

        self.select_top = False

    def serialize(self):
        res = super().serialize()
        # res['command'] = self.command
        res['autorun'] = self.lbl.text()
        res['global_object'] = self.Global_Object
        res['GObject_key'] = self.GlobalObject_key
        res['alpha'] = self.color_alpha
        res['select_top'] = self.select_top
        res['CameraSelect_Mode'] = self.CameraSelect_Mode
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'CameraSelect_Mode' in data:
                self.CameraSelect_Mode = data['CameraSelect_Mode']
                if self.CameraSelect_Mode == "2D":
                    self.Select2DBtn.setEnabled(False)
                    self.Select2DBtn_flag = True
                    self.Select3DBtn_flag = False

                else:
                    self.Select3DBtn.setEnabled(False)
                    self.Select3DBtn_flag = True
                    self.Select2DBtn_flag = False

            if 'autorun' in data:
                self.autorun = data['autorun']
                self.lbl.setText(self.autorun)

                if self.autorun == 'A':
                    self.StartfromSave = True

                    # if self.Check_Camera_Link():

                    self.radioState.setChecked(True)
                    self.BlinkingState = True
                    self.Camera_timer.start()

                    # else:
                    #     print("\033[91m {}\033[00m".format("No 3D Camera device connected"))
                    #     self.No_Camera_timer.start()

            if 'global_object' in data:
                self.Global_Object = data['global_object']

            if 'GObject_key' in data:
                self.GlobalObject_key = data['GObject_key']

            if 'alpha' in data:
                self.color_alpha = data['alpha']

            if 'select_top' in data:
                self.select_top = data['select_top']

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
    def Check_Camera_Link(self):
        try:
        #     if self.Select2DBtn_flag:

            device = self.pipeline_profile.get_device()
            # device_product_line = str(device.get_info(rs.camera_info.product_line))

            # ====================================================
            # Config 2D Camera View
            # self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            # self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

            # # Start streaming
            # # self.pipeline.start(self.config)

            # # Create an align object
            # # rs.align allows us to perform alignment of depth frames to others frames
            # # The "align_to" is the stream type to which we plan to align depth frames.
            # align_to = rs.stream.color
            # self.align = rs.align(align_to)

            # ====================================================
            # Config 3D Camera Veiw
        
            found_rgb = False
            for s in device.sensors:
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    found_rgb = True
                    break
            if not found_rgb:
                print("The demo requires Depth camera with Color sensor")
                exit(0)

            self.config.enable_stream(rs.stream.depth, rs.format.z16, 30)
            self.other_stream, self.other_format = rs.stream.color, rs.format.bgr8
            self.config.enable_stream(self.other_stream, self.other_format, 30)

            # Create an align object
            # rs.align allows us to perform alignment of depth frames to others frames
            # The "align_to" is the stream type to which we plan to align depth frames.
            # align_to = rs.stream.color
            # self.align = rs.align(self.other_stream)

            self.lbl_nocam.setVisible(False)
            self.No_Camera_timer.stop()

            return True

        except:
            print("\033[91m {}\033[00m".format("No 3D Camera device connected"))
            self.No_Camera_timer.start()

            return False

    
    def show_camerror(self):
        if self.TimerBlinkCnt >= 10000:
            self.TimerBlinkCnt = 0
            if self.BlinkingState:
                self.lbl_nocam.setVisible(True)
            else:
                self.lbl_nocam.setVisible(False)
                self.relink_camera_cnt += 1
                if self.relink_camera_cnt > 10:
                    self.relink_camera_cnt = 0
                    self.Check_Camera_Link()

            self.BlinkingState = not self.BlinkingState

        self.TimerBlinkCnt += 1

# ===========================================================
class AppState:
    def __init__(self, *args, **kwargs):
        self.WIN_NAME = 'RealSense Panel Pad'
        self.pitch, self.yaw = math.radians(-10), math.radians(-15)
        self.translation = np.array([0, 0, -1], dtype=np.float32)
        self.distance = 2
        self.prev_mouse = 0, 0
        self.mouse_btns = [False, False, False]
        self.paused = False
        self.decimate = 1
        self.scale = True
        self.color = True
        self.postprocessing = False

    def reset(self):
        self.pitch, self.yaw, self.distance = 0, 0, 2
        self.translation[:] = 0, 0, -1

    @property
    def rotation(self):
        Rx, _ = cv2.Rodrigues((self.pitch, 0, 0))
        Ry, _ = cv2.Rodrigues((0, self.yaw, 0))
        return np.dot(Ry, Rx).astype(np.float32)

    @property
    def pivot(self):
        return self.translation + np.array((0, 0, self.distance), dtype=np.float32)
    
# ===========================================================
class C3DSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content

        self.title = "3D Camera Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 800
        self.height = 470
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.lbl = QLabel("Check Global Object Distance : ", self)
        self.lbl.setGeometry(QtCore.QRect(10, 5, 250, 20))
        self.lbl.setStyleSheet("color: #42E3C8;")

        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignLeft)
        self.edit.setGeometry(280,4,200,25)
        self.edit.setPlaceholderText("Global Object Key")
        self.edit.setText(self.content.GlobalObject_key)

        self.editGlobalObject = QPlainTextEdit("",self)
        # self.editGlobalObject.setFixedWidth(380)
        self.editGlobalObject.setGeometry(10,35,780,150)
        self.editGlobalObject.setStyleSheet("background-color: rgba(19, 21, 91, 225);font-size:12pt;color:#42E3C8;")
        self.editGlobalObject.setPlaceholderText("Global Object")

        self.editGlobalObject.setPlainText(str(self.content.Global_Object))
        
        self.checkSelectTopObject = QCheckBox("Select Top Object",self)
        self.checkSelectTopObject.setGeometry(10,195,200,20)
        self.checkSelectTopObject.setStyleSheet("color: lightgreen; font-size:8pt;")
        if self.content.select_top:
            self.checkSelectTopObject.setChecked(True)

        else:
            self.checkSelectTopObject.setChecked(False)

        self.checkSelectTopObject.stateChanged.connect(self.checkSelectTopObject_Function)

        self.lbl2 = QLabel("Color Alpha : ", self)
        self.lbl2.setGeometry(QtCore.QRect(10, 250, 250, 20))
        self.lbl2.setStyleSheet("color: #42E3C8;")

        self.editAlpha = QLineEdit("", self)
        self.editAlpha.setAlignment(Qt.AlignLeft)
        self.editAlpha.setGeometry(280,250,200,25)
        self.editAlpha.setPlaceholderText("Color Alpha")
        self.editAlpha.setText(str(self.content.color_alpha))

    def checkSelectTopObject_Function(self, state):
        if state == QtCore.Qt.Checked:
            self.content.select_top = True
        else:
            self.content.select_top = False

    def closeEvent(self, event):
        self.content.Global_Object = self.editGlobalObject.toPlainText()
        self.content.GlobalObject_key = self.edit.text()
        self.content.color_alpha = float(self.editAlpha.text())

        self.content.SettingBtn.setEnabled(True)

# ==================================================================

@register_node(OP_NODE_3DCAMERA)
class Open_CMD(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_3dcam.png"
    op_code = OP_NODE_3DCAMERA
    op_title = "3D CAM"
    content_label_objname = "3D CAM"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[4,3,2,1]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.color3d_payload = {}
        self.color3d_payload['inputtype'] = "img"
        self.color3d_payload['fps'] = 1
        self.color3d_payload['run'] = False

        self.depth3d_paylaod = {}
        self.depth3d_paylaod['inputtype'] = "img"

        self.distance_payload = {}

        self.all_imagePayload = {}
        self.all_imagePayload['inputtype'] = "img"

        self.yolo_payload = {}

        self.process_capture = False
        self.process_video = False

        self.Start_Video = False
        self.Add_Camera_List = False

        self.input_sanp_payload = {}
        self.input_vdo_payload = {}

        self.Sigle_SnapInput = False

        self.confirm_submit_true = False
        self.start_command = False
        self.start_MQTTCommand = False

        self.yolo_distance = []

    def initInnerClasses(self):
        self.content = Realsense3DCAM(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphics150x150Process(self)               # <----------- Box Image Draw in Flow_Node_Base

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

        self.content.Select2DBtn.clicked.connect(self.On_Process2D_veiwer)
        self.content.Select3DBtn.clicked.connect(self.On_Process3D_pointcloud)

        self.content.radioState.toggled.connect(self.onStartVideo)
        self.content.Camera_timer.timeout.connect(self.update_frame)
        self.content.Camera_timer.setInterval(50)

        self.Global = GlobalVariable()


    def evalImplementation(self):                           # <----------- Create Socket range Index

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
                    if self.input_sanp_payload['submit']: #and not self.Sigle_SnapInput:
                        self.Sigle_SnapInput = True
                        self.StartRuuningCam()

                    else:
                        if self.Sigle_SnapInput:
                            self.StopRunningCam()
                            self.Sigle_SnapInput = False


    def StartRuuningCam(self):
        # try:
        self.color3d_payload['run'] = True

        # Start streaming
        self.content.pipeline.start(self.content.config)

        # Get stream profile and camera intrinsics
        profile = self.content.pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        self.content.width, self.content.height = depth_intrinsics.width, depth_intrinsics.height

        self.content.out = np.empty((self.content.height, self.content.width, 3), dtype=np.uint8)

        # Processing blocks
        self.content.pc = rs.pointcloud()
        self.content.decimate = rs.decimation_filter()
        self.content.decimate.set_option(rs.option.filter_magnitude, 2 ** self.content.state.decimate)
        self.content.colorizer = rs.colorizer()

        self.content.BlinkingState = True
        self.content.Camera_timer.start()
        self.content.lbl.setText("A")

        self.process_video = True
        self.process_capture = False

        # except Exception as e:
        #     print("Error :", e)

    def StopRunningCam(self):
        try:
            self.color3d_payload['run'] = False
            
            self.content.BlinkingState = False
            self.content.Camera_timer.stop()
            self.content.radioState.setStyleSheet("QRadioButton"
                                    "{"
                                    "background-color : #33CCFF"
                                    "}") 
            self.content.lbl.setText("N")

            self.Sigle_SnapInput = False

            # Stop streaming
            self.content.pipeline.stop()
        except Exception as e:
            ...

    def OnOpen_Setting(self):
        if self.content.Check_Camera_Link():
            self.C3D_Setting = C3DSetting(self.content)
            self.C3D_Setting.show()
            self.content.SettingBtn.setEnabled(False)

    def onStartVideo(self):
        radioButton = self.content.sender()
        if radioButton.isChecked():
            self.StartRuuningCam()
            self.color3d_payload['run'] = True

        else:
            self.StopRunningCam()
            self.color3d_payload['run'] = False

    # ==============================================================================
    # Process 2D Camera View
    def On_Process2D_veiwer(self):
        cv2.destroyAllWindows()

        self.content.Select2DBtn.setVisible(False)
        self.content.Select3DBtn.setVisible(True)
        self.content.Select3DBtn.setEnabled(True)

        self.content.Select2DBtn_flag = True
        self.content.Select3DBtn_flag = False

        self.content.lbl_2D.setVisible(True)
        self.content.lbl_3D.setVisible(False)

        self.content.lbl_out2.setText("ColorMap")

        self.content.Check_Camera_Link()

    # ==============================================================================
    # Process 3D Camera View

    def mouse_cb(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.content.state.mouse_btns[0] = True

        if event == cv2.EVENT_LBUTTONUP:
           self.content.state.mouse_btns[0] = False

        if event == cv2.EVENT_RBUTTONDOWN:
            self.content.state.mouse_btns[1] = True

        if event == cv2.EVENT_RBUTTONUP:
            self.content.state.mouse_btns[1] = False

        if event == cv2.EVENT_MBUTTONDOWN:
            self.content.state.mouse_btns[2] = True

        if event == cv2.EVENT_MBUTTONUP:
            self.content.state.mouse_btns[2] = False

        if event == cv2.EVENT_MOUSEMOVE:

            h, w = self.content.out.shape[:2]
            dx, dy = x - self.content.state.prev_mouse[0], y - self.content.state.prev_mouse[1]

            if self.content.state.mouse_btns[0]:
                self.content.state.yaw += float(dx) / w * 2
                self.content.state.pitch -= float(dy) / h * 2

            elif self.content.state.mouse_btns[1]:
                dp = np.array((dx / w, dy / h, 0), dtype=np.float32)
                self.content.state.translation -= np.dot(self.content.state.rotation, dp)

            elif self.content.state.mouse_btns[2]:
                dz = math.sqrt(dx**2 + dy**2) * math.copysign(0.01, -dy)
                self.content.state.translation[2] += dz
                self.content.state.distance -= dz

        if event == cv2.EVENT_MOUSEWHEEL:
            dz = math.copysign(0.1, flags)
            self.content.state.translation[2] += dz
            self.content.state.distance -= dz

        self.content.state.prev_mouse = (x, y)


    def On_Process3D_pointcloud(self):
        self.content.Select2DBtn.setVisible(True)
        self.content.Select2DBtn.setEnabled(True)
        
        self.content.Select3DBtn.setVisible(False)
        self.content.Select2DBtn_flag = False
        self.content.Select3DBtn_flag = True

        self.content.lbl_2D.setVisible(False)
        self.content.lbl_3D.setVisible(True)


        self.content.lbl_out2.setText("3D Map")

        cv2.namedWindow(self.content.state.WIN_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(self.content.state.WIN_NAME, self.content.width, self.content.height)
        cv2.setMouseCallback(self.content.state.WIN_NAME, self.mouse_cb)


        self.content.Check_Camera_Link()

    def project(self, v):
        """project 3d vector array to 2d"""
        h, w = self.content.out.shape[:2]
        view_aspect = float(h)/w

        # ignore divide by zero for invalid depth
        with np.errstate(divide='ignore', invalid='ignore'):
            proj = v[:, :-1] / v[:, -1, np.newaxis] * \
                (w*view_aspect, h) + (w/2.0, h/2.0)

        # near clipping
        znear = 0.03
        proj[v[:, 2] < znear] = np.nan
        return proj

    def view(self, v):
        """apply view transformation on vector array"""
        return np.dot(v - self.content.state.pivot, self.content.state.rotation) + self.content.state.pivot - self.content.state.translation

    def line3d(self, out, pt1, pt2, color=(0x80, 0x80, 0x80), thickness=1):
        """draw a 3d line from pt1 to pt2"""
        p0 = self.project(pt1.reshape(-1, 3))[0]
        p1 = self.project(pt2.reshape(-1, 3))[0]
        if np.isnan(p0).any() or np.isnan(p1).any():
            return
        p0 = tuple(p0.astype(int))
        p1 = tuple(p1.astype(int))
        rect = (0, 0, out.shape[1], out.shape[0])
        inside, p0, p1 = cv2.clipLine(rect, p0, p1)
        if inside:
            cv2.line(out, p0, p1, color, thickness, cv2.LINE_AA)

    def grid(self, out, pos, rotation=np.eye(3), size=1, n=10, color=(0x80, 0x80, 0x80)):
        """draw a grid on xz plane"""
        pos = np.array(pos)
        s = size / float(n)
        s2 = 0.5 * size
        for i in range(0, n+1):
            x = -s2 + i*s
            self.line3d(out, self.view(pos + np.dot((x, 0, -s2), rotation)),
                self.view(pos + np.dot((x, 0, s2), rotation)), color)
        for i in range(0, n+1):
            z = -s2 + i*s
            self.line3d(out, self.view(pos + np.dot((-s2, 0, z), rotation)),
                self.view(pos + np.dot((s2, 0, z), rotation)), color)
            
    def axes(self, out, pos, rotation=np.eye(3), size=0.075, thickness=2):
        """draw 3d axes"""
        self.line3d(out, pos, pos +
            np.dot((0, 0, size), rotation), (0xff, 0, 0), thickness)
        self.line3d(out, pos, pos +
            np.dot((0, size, 0), rotation), (0, 0xff, 0), thickness)
        self.line3d(out, pos, pos +
            np.dot((size, 0, 0), rotation), (0, 0, 0xff), thickness)
        
    def frustum(self, out, intrinsics, color=(0x40, 0x40, 0x40)):
        """draw camera's frustum"""
        orig = self.view([0, 0, 0])
        w, h = intrinsics.width, intrinsics.height

        for d in range(1, 6, 2):
            def get_point(x, y):
                p = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], d)
                self.line3d(out, orig, self.view(p), color)
                return p

            top_left = get_point(0, 0)
            top_right = get_point(w, 0)
            bottom_right = get_point(w, h)
            bottom_left = get_point(0, h)

            self.line3d(out, self.view(top_left), self.view(top_right), color)
            self.line3d(out, self.view(top_right), self.view(bottom_right), color)
            self.line3d(out, self.view(bottom_right), self.view(bottom_left), color)
            self.line3d(out, self.view(bottom_left), self.view(top_left), color)

    def pointcloud(self, out, verts, texcoords, color, painter=True):
        """draw point cloud with optional painter's algorithm"""
        if painter:
            # Painter's algo, sort points from back to front

            # get reverse sorted indices by z (in view-space)
            # https://gist.github.com/stevenvo/e3dad127598842459b68
            v = self.view(verts)
            s = v[:, 2].argsort()[::-1]
            proj = self.project(v[s])
        else:
            proj = self.project(self.view(verts))

        if self.content.state.scale:
            proj *= 0.5**self.content.state.decimate

        h, w = out.shape[:2]

        # proj now contains 2d image coordinates
        j, i = proj.astype(np.uint32).T

        # create a mask to ignore out-of-bound indices
        im = (i >= 0) & (i < h)
        jm = (j >= 0) & (j < w)
        m = im & jm

        cw, ch = color.shape[:2][::-1]
        if painter:
            # sort texcoord with same indices as above
            # texcoords are [0..1] and relative to top-left pixel corner,
            # multiply by size and add 0.5 to center
            v, u = (texcoords[s] * (cw, ch) + 0.5).astype(np.uint32).T
        else:
            v, u = (texcoords * (cw, ch) + 0.5).astype(np.uint32).T
        # clip texcoords to image
        np.clip(u, 0, ch-1, out=u)
        np.clip(v, 0, cw-1, out=v)

        # perform uv-mapping
        out[i[m], j[m]] = color[u[m], v[m]]

    # =================================================================================================
    # =================================================================================================
    def update_frame(self):
        # try:
        
        self.color3d_payload['fps'] = time.time()

        # Grab camera data
        if not self.content.state.paused:
            if self.content.Select2DBtn_flag:
                frames = self.content.pipeline.wait_for_frames()
                # print("frames:", frames)

                # Align the depth frame to color frame
                align = rs.align(rs.stream.color)
                aligned_frames = align.process(frames)

                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                # # Validate that both frames are valid
                # if not depth_frame or not color_frame:
                #     self.StopRunningCam()
                #     time.sleep(1)
                #     self.StartRuuningCam()

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=self.content.color_alpha), cv2.COLORMAP_JET)

                self.color3d_payload['img'] = color_image
                self.depth3d_paylaod['img'] = depth_colormap

                if len(self.content.Global_Object) > 0 and len(self.content.GlobalObject_key) > 0:
                    if self.Global.hasGlobal(str(self.content.GlobalObject_key)):
                        self.yolo_payload = self.Global.getGlobal(str(self.content.GlobalObject_key))
                        # print("self.yolo_payload :", self.yolo_payload)

                        list_GlobalObject = str(self.content.Global_Object).split("\n")
                        # print("list_GlobalObject :", list_GlobalObject)
                        # print("len(list_GlobalObject):", len(list_GlobalObject))

                        ObjectArea = []
                        ObjectLayer = []
                        PosX_sorted = []

                        self.yolo_distance = []
                        if 'obj_found' in self.yolo_payload:
                            if self.yolo_payload['obj_found'] > 0:
                                if 'yolo_boxes' in self.yolo_payload:
                                    # print(self.yolo_payload['yolo_boxes'])
                                    # print("self.yolo_payload['img'].shape:", self.yolo_payload['img'].shape)
                                    for i in range(len(self.yolo_payload['yolo_boxes'])):
                                        for l in range(len(list_GlobalObject)):
                                            if self.yolo_payload['yolo_boxes'][i]['obj'] == str(list_GlobalObject[l]):
                                                # print(self.yolo_payload['yolo_boxes'][i]['x1'])
                                                # print(self.yolo_payload['yolo_boxes'][i]['x2'])

                                                cx = int((int(self.yolo_payload['yolo_boxes'][i]['x2']) - int(self.yolo_payload['yolo_boxes'][i]['x1']))/2) + int(self.yolo_payload['yolo_boxes'][i]['x1'])
                                                cy = int((int(self.yolo_payload['yolo_boxes'][i]['y2']) - int(self.yolo_payload['yolo_boxes'][i]['y1']))/2) + int(self.yolo_payload['yolo_boxes'][i]['y1'])

                                                if l == 0:
                                                    ObjectArea.append({'x1':self.yolo_payload['yolo_boxes'][i]['x1'], 'x2':self.yolo_payload['yolo_boxes'][i]['x2'], 'y1':self.yolo_payload['yolo_boxes'][i]['y1'], 'y2':self.yolo_payload['yolo_boxes'][i]['y2']})
                                                    
                                                if l == 1:
                                                    for m in range(len(ObjectArea)):
                                                        if cx >= ObjectArea[m]['x1'] and cx <= ObjectArea[m]['x2'] and cy >= ObjectArea[m]['y1'] and cy <= ObjectArea[m]['y2']:
                                                            cx_box = int((int(ObjectArea[m]['x2']) - int(ObjectArea[m]['x1']))/2) + int(ObjectArea[m]['x1'])
                                                            cy_box = int((int(ObjectArea[m]['y2']) - int(ObjectArea[m]['y1']))/2) + int(ObjectArea[m]['y1'])

                                                            self.all_imagePayload['img'] = cv2.line(self.all_imagePayload['img'], (cx_box, cy_box), (cx, cy), (0,255,0), thickness=2)

                                                            # calculate the length and angle of the existing line
                                                            dx, dy = cx_box - cx, cy_box - cy
                                                            # line_length = math.sqrt(dx**2 + dy**2)
                                                            line_angle = math.atan2(dy, dx)

                                                            # define the length of the new line
                                                            new_line_length = math.sqrt((dx)**2 + (dy)**2)

                                                            # calculate the angle of the new line (90 degrees from the existing line)
                                                            new_line_angle = line_angle - math.pi/2
                                                            # print("new_line_angle:", new_line_angle)

                                                            # calculate the end point of the new line
                                                            x2_new = int(cx_box + new_line_length * math.cos(new_line_angle))
                                                            y2_new = int(cy_box + new_line_length * math.sin(new_line_angle))

                                                            # draw the new line
                                                            self.all_imagePayload['img'] = cv2.line(self.all_imagePayload['img'], (cx_box, cy_box), (x2_new, y2_new), (0, 0, 255), thickness=2)
                                                            
                                                            # new_line180_angle = new_line_angle + math.pi/2
                                                            # # calculate the end point of the new line
                                                            # x3_new = int(cx_box + new_line_length * math.cos(new_line180_angle))
                                                            # y3_new = int(cy_box + new_line_length * math.sin(new_line180_angle))

                                                            # self.all_imagePayload['img'] = cv2.line(self.all_imagePayload['img'], (cx_box, cy_box), (x3_new, y3_new), (0, 255, 0), thickness=2)

                                                            # new_line1802_angle = new_line180_angle + math.pi/2
                                                            # # calculate the end point of the new line
                                                            # x4_new = int(cx_box + new_line_length * math.cos(new_line1802_angle))
                                                            # y4_new = int(cy_box + new_line_length * math.sin(new_line1802_angle))

                                                            # self.all_imagePayload['img'] = cv2.line(self.all_imagePayload['img'], (cx_box, cy_box), (x4_new, y4_new), (0, 0, 255), thickness=2)


                                                distance = depth_image[cy, cx]

                                                if distance > 0:
                                                    self.all_imagePayload['img'] = cv2.circle(self.yolo_payload['img'], (cx, cy), 4, self.content.colorList[l])
                                                    self.all_imagePayload['img'] = cv2.putText(self.all_imagePayload['img'], "{}mm".format(distance), (cx - 25, cy - 20), 0, 0.5, self.content.colorList[l], thickness=1, lineType=cv2.LINE_AA)

                                                    if self.content.select_top:
                                                        self.yolo_distance.append({ 'cx':int(cx), 'cy':int(cy), 
                                                                                    'score': self.yolo_payload['yolo_boxes'][i]['score'],
                                                                                    'obj': self.yolo_payload['yolo_boxes'][i]['obj'],
                                                                                    'distance': distance})
                                                        
                                                        if len(self.yolo_distance) > 0:
                                                            for m in range(len(self.yolo_distance)):
                                                                ObjectLayer.append(self.yolo_distance[m]['distance'])

                                                            while ObjectLayer:
                                                                minimum = ObjectLayer[0]
                                                                for item in ObjectLayer:
                                                                    if item < minimum:
                                                                        minimum = item
                                                                PosX_sorted.append(minimum)
                                                                ObjectLayer.remove(minimum)

                                                            for data_x in range(len(self.yolo_distance)):
                                                                if self.yolo_distance[data_x]['distance'] == PosX_sorted[0] and self.yolo_distance[data_x]['obj'] == str(list_GlobalObject[0]):
                                                                    # print("PosX_sorted :", PosX_sorted)

                                                                    self.distance_payload['depth'] = { 'cx':int(self.yolo_distance[data_x]['cx']), 'cy':int(self.yolo_distance[data_x]['cy']), 
                                                                                    'score': self.yolo_distance[data_x]['score'],
                                                                                    'obj': self.yolo_distance[data_x]['obj'],
                                                                                    'distance': self.yolo_distance[data_x]['distance']}
                                                            PosX_sorted = []

                                                    else:
                                                        self.yolo_distance.append({ 'cx':int(cx), 'cy':int(cy), 
                                                                                    'score': self.yolo_payload['yolo_boxes'][i]['score'],
                                                                                    'obj': self.yolo_payload['yolo_boxes'][i]['obj'],
                                                                                    'distance': distance})

                                                        # print("ObjectLayer :", ObjectLayer)

                                                        self.distance_payload['depth'] = self.yolo_distance

        if self.content.Select3DBtn_flag:
            frames = self.content.pipeline.wait_for_frames()
            # print("frames:", frames)

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            depth_frame = self.content.decimate.process(depth_frame)

            # Grab new intrinsics (may be changed by decimation)
            self.content.depth_intrinsics = rs.video_stream_profile(
                depth_frame.profile).get_intrinsics()
            self.content.width, self.content.height = self.content.depth_intrinsics.width,self.content.depth_intrinsics.height

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            self.color3d_payload['img'] = color_image

            depth_colormap = np.asanyarray(
                self.content.colorizer.colorize(depth_frame).get_data())
                        
            if self.content.state.color:
                mapped_frame, color_source = color_frame, color_image
            else:
                mapped_frame, color_source = depth_frame, depth_colormap

            points = self.content.pc.calculate(depth_frame)
            self.content.pc.map_to(mapped_frame)

            # Pointcloud data to arrays
            v, t = points.get_vertices(), points.get_texture_coordinates()
            verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
            texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv

            self.content.out.fill(0)
            self.grid(self.content.out, (0, 0.5, 1), size=1, n=10)
            self.frustum(self.content.out, self.content.depth_intrinsics)
            self.axes(self.content.out, self.view([0, 0, 0]), self.content.state.rotation, size=0.1, thickness=1)

            if not self.content.state.scale or self.content.out.shape[:2] == (self.content.height, self.content.width):
                self.pointcloud(self.content.out, verts, texcoords, color_source)
            else:
                tmp = np.zeros((self.content.height, self.content.width, 3), dtype=np.uint8)
                self.pointcloud(tmp, verts, texcoords, color_source)
                tmp = cv2.resize(
                    tmp, self.content.out.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
                np.putmask(self.content.out, tmp > 0, tmp)

            if any(self.content.state.mouse_btns):
                self.axes(self.content.out, self.view(self.content.state.pivot), self.content.state.rotation, thickness=4)

            cv2.imshow(self.content.state.WIN_NAME, self.content.out)
            self.depth3d_paylaod['img'] = self.content.out
                                    
        self.sendFixOutputByIndex(self.color3d_payload, 0)
        self.sendFixOutputByIndex(self.depth3d_paylaod, 1)
        self.sendFixOutputByIndex(self.distance_payload, 2)
        self.sendFixOutputByIndex(self.all_imagePayload, 3)
        
        # except Exception as e:
        #     print("Error:", e)

        if self.content.TimerBlinkCnt >= 5:
                self.content.TimerBlinkCnt = 0
                if self.content.BlinkingState:
                    self.color3d_payload['blink'] = True
                    self.content.radioState.setStyleSheet("QRadioButton"
                                    "{"
                                        "background-color : rgba(0, 0, 28, 50);"
                                    "}") 
                else:
                    self.color3d_payload['blink'] = False
                    self.content.radioState.setStyleSheet("QRadioButton"
                                    "{"
                                    "background-color : #33CCFF"
                                    "}") 
                self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren(index)

