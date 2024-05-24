from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time
import os

import numpy as np
import datetime

class Ui_MediaPlayer_MainWindow(object):
    def setupUi(self, MainWindow):
        #=======================================

        self.top    = 25
        self.left   = 5
        self.width  = 320
        self.height = 70
        self.MainWindow = MainWindow
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 

        self.fix_pos_h = 1

        self.playBtn = QPushButton(self.MainWindow)
        self.playBtn.setGeometry(25,self.fix_pos_h,50,20)

        self.browsFiles = QPushButton(self.MainWindow)
        self.browsFiles.setGeometry(0,self.fix_pos_h,20,20)

        self.slider = QSlider(Qt.Horizontal, self.MainWindow)
        self.slider.setGeometry(140,self.fix_pos_h,105,20)

        self.slbl = QLineEdit('00:00:00', self.MainWindow)
        self.slbl.setGeometry(80,self.fix_pos_h,55,20)

        self.elbl = QLineEdit('00:00:00', self.MainWindow)
        self.elbl.setGeometry(250,self.fix_pos_h,55,20)

        #====================================================
        self.check_loop = QCheckBox("loop",self.MainWindow)
        self.check_loop.setGeometry(10,25,50,10)

        self.ResizeBtn = QPushButton(self.MainWindow)
        self.ResizeBtn.setGeometry(300, 26,10,10)

        self.BackBtn = QPushButton("<",self.MainWindow)
        self.BackBtn.setGeometry(80,self.fix_pos_h + 22,20,14)

        self.FFBtn = QPushButton(">",self.MainWindow)
        self.FFBtn.setGeometry(115,self.fix_pos_h + 22,20,14)

class MEDIAPLAYER_BAR(QDMNodeContentWidget):
    resized = pyqtSignal()

    def initUI(self):
        Path = os.path.dirname(os.path.abspath(__file__))
        self.refresh_icon = Path + "/icons/icons_refresh.png"
        self.play_icon = Path + "/icons/icons_play.png"
        self.pause_icon = Path + "/icons/icons_pause.png"
        self.save_icon = Path + "/icons/icons_save.png"

        self.icon_round_btn = Path + "/icons/icons_btn_round10x10.png"
        self.icon_round_green = Path + "/icons/icons_btn_round10x10_green.png"

        self.Data = None
        self.Frame_w = 320
        self.Frame_h = 240 

        self.fix_pos = 1

        self.ui = Ui_MediaPlayer_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.ui.playBtn.setIcon(QIcon(self.play_icon))
        self.ui.playBtn.setEnabled(False)

        self.ui.browsFiles.setIcon(QIcon(self.save_icon))

        #========================================

        self.ui.slider.setRange(0,100)
        self.ui.slider.setSingleStep(2)
        self.ui.slider.setPageStep(20)
        self.ui.slider.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.slider.setStyleSheet("background-color: rgba(0, 32, 130, 20);")
        self.ui.slider.setEnabled(False)

        self.ui.slbl.setText('00:00:00')
        self.ui.slbl.setAlignment(Qt.AlignCenter)
        self.ui.slbl.setReadOnly(True)
        self.ui.slbl.setUpdatesEnabled(True)
        self.ui.slbl.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:5pt;")

        self.ui.elbl.setText('00:00:00')
        self.ui.elbl.setAlignment(Qt.AlignCenter)
        self.ui.elbl.setReadOnly(True)
        self.ui.elbl.setUpdatesEnabled(True)
        self.ui.elbl.setStyleSheet("background-color: rgba(0, 32, 130, 100); font-size:5pt;")

        # ========================================
        self.ui.check_loop.setStyleSheet("color: lightblue; font-size:5pt;")

        self.ui.BackBtn.setStyleSheet("color: lightblue; font-size:5pt;")
        self.ui.FFBtn.setStyleSheet("color: lightblue; font-size:5pt;")

        self.videowidget = QVideoWidget()

        self.grabber = VideoFrameGrabber(self.videowidget, self)
        self.mediaPlayer.setVideoOutput(self.grabber)

        self.ui.ResizeBtn.setIcon(QIcon(self.icon_round_btn))
        self.ui.ResizeBtn.setStyleSheet("background-color: transparent; border: 0px;")   

        self.slid_position = 0
        self.fileLocation = ""

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.mplayer_status = False
        self.filename = ""

        self.play_loop = False

        self.SendFrame_Timer = QtCore.QTimer(self)

        self.ResizeFrame_timer = QtCore.QTimer(self)
        self.resize_terminal = False
        self.resized.connect(self.ReDrawGeometry)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        #GlobaTimer.setGlobal("MediaBarTimer", self.SendFrame_Timer)

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))
            
            self.ListGlobalTimer.append(self.SendFrame_Timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", ListGlobalTimer)

    def serialize(self):
        res = super().serialize()
        res['fileLocate'] = self.fileLocation
        res['mpstatus'] = self.mplayer_status
        res['filename'] = self.filename
        res['loop'] = self.play_loop

        res['resize'] = self.resize_terminal
        res['new_width'] = self.Frame_w
        res['new_height'] = self.Frame_h
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'fileLocate' in data:
                self.fileLocation = data['fileLocate']

            if 'mpstatus' in data:    
                self.mplayer_status = data['mpstatus']
                
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(str(self.fileLocation))))

            if 'filename' in data:
                self.filename = data['filename']

            if os.path.isfile(self.fileLocation):
                self.ui.playBtn.setEnabled(True)
                print ("File exist")

            if self.mplayer_status == True:
                self.mediaPlayer.play()
                self.SendFrame_Timer.start()
            else:
                self.mediaPlayer.pause()
                self.SendFrame_Timer.stop()

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

    def browseSlot(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Video Files (*.mp4)", options=options)
        
        if files:
            self.fileLocation = files[0]
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(str(self.fileLocation))))
            self.ui.playBtn.setEnabled(True)

            File_Name = self.fileLocation.split("/")
            self.filename = File_Name[len(File_Name) - 1]

    def stylesheet(self):
        return

    def ReDrawGeometry(self):
        #print("ReDrawGeometry Frame_w = ", self.Frame_w, " ; self.Frame_h = ", self.Frame_h)
        self.ui.MainWindow.setGeometry(2, 27, int(self.Frame_w - 7), int(self.Frame_h - 30)) 
        self.ui.slider.setGeometry(140, self.fix_pos, int(self.Frame_w - 215), 20)
        self.ui.elbl.setGeometry(int(self.Frame_w - 70), self.fix_pos, 55, 20)
        self.ui.ResizeBtn.setGeometry(int(self.Frame_w - 19), 26,10,10)

#===========================================================================================

class VideoFrameGrabber(QAbstractVideoSurface):
    frameAvailable = pyqtSignal(QImage)

    def __init__(self, widget: QWidget, parent: QObject):
        super().__init__(parent)

        self.widget = widget

    def supportedPixelFormats(self, handleType):
        return [QVideoFrame.Format_ARGB32, QVideoFrame.Format_ARGB32_Premultiplied,
                QVideoFrame.Format_RGB32, QVideoFrame.Format_RGB24, QVideoFrame.Format_RGB565,
                QVideoFrame.Format_RGB555, QVideoFrame.Format_ARGB8565_Premultiplied,
                QVideoFrame.Format_BGRA32, QVideoFrame.Format_BGRA32_Premultiplied, QVideoFrame.Format_BGR32,
                QVideoFrame.Format_BGR24, QVideoFrame.Format_BGR565, QVideoFrame.Format_BGR555,
                QVideoFrame.Format_BGRA5658_Premultiplied, QVideoFrame.Format_AYUV444,
                QVideoFrame.Format_AYUV444_Premultiplied, QVideoFrame.Format_YUV444,
                QVideoFrame.Format_YUV420P, QVideoFrame.Format_YV12, QVideoFrame.Format_UYVY,
                QVideoFrame.Format_YUYV, QVideoFrame.Format_NV12, QVideoFrame.Format_NV21,
                QVideoFrame.Format_IMC1, QVideoFrame.Format_IMC2, QVideoFrame.Format_IMC3,
                QVideoFrame.Format_IMC4, QVideoFrame.Format_Y8, QVideoFrame.Format_Y16,
                QVideoFrame.Format_Jpeg, QVideoFrame.Format_CameraRaw, QVideoFrame.Format_AdobeDng]

    def isFormatSupported(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()

        return imageFormat != QImage.Format_Invalid and not size.isEmpty() and \
               format.handleType() == QAbstractVideoBuffer.NoHandle

    def start(self, format: QVideoSurfaceFormat):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()

        if imageFormat != QImage.Format_Invalid and not size.isEmpty():
            self.imageFormat = imageFormat
            self.imageSize = size
            self.sourceRect = format.viewport()

            super().start(format)

            self.widget.updateGeometry()
            self.updateVideoRect()

            return True
        else:
            return False

    def stop(self):
        self.currentFrame = QVideoFrame()
        self.targetRect = QRect()

        super().stop()

        self.widget.update()

    def present(self, frame):
        if frame.isValid():
            cloneFrame = QVideoFrame(frame)
            cloneFrame.map(QAbstractVideoBuffer.ReadOnly)
            image = QImage(cloneFrame.bits(), cloneFrame.width(), cloneFrame.height(),
                           QVideoFrame.imageFormatFromPixelFormat(cloneFrame.pixelFormat()))
            self.frameAvailable.emit(image)  # this is very important
            cloneFrame.unmap()

        if self.surfaceFormat().pixelFormat() != frame.pixelFormat() or \
                self.surfaceFormat().frameSize() != frame.size():
            self.setError(QAbstractVideoSurface.IncorrectFormatError)
            self.stop()

            return False
        else:
            self.currentFrame = frame

            self.widget.repaint(self.targetRect)

            return True

    def updateVideoRect(self):
        size = self.surfaceFormat().sizeHint()
        size.scale(self.widget.size().boundedTo(size), Qt.KeepAspectRatio)

        self.targetRect = QRect(QPoint(0, 0), size)
        self.targetRect.moveCenter(self.widget.rect().center())

    def paint(self, painter):
        if self.currentFrame.map(QAbstractVideoBuffer.ReadOnly):
            oldTransform = self.painter.transform()

        if self.surfaceFormat().scanLineDirection() == QVideoSurfaceFormat.BottomToTop:
            self.painter.scale(1, -1)
            self.painter.translate(0, -self.widget.height())

        image = QImage(self.currentFrame.bits(), self.currentFrame.width(), self.currentFrame.height(),
                       self.currentFrame.bytesPerLine(), self.imageFormat)

        self.painter.drawImage(self.targetRect, image, self.sourceRect)

        self.painter.setTransform(oldTransform)

        self.currentFrame.unmap()
        
@register_node(OP_NODE_MEDIAPLAYER_BAR)
class Open_MEDIAPLAYER_BAR(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_bar_control.png"
    op_code = OP_NODE_MEDIAPLAYER_BAR
    op_title = "Media Player Bar"
    content_label_objname = "Media Player Bar"

    def __init__(self, scene):
        super().__init__(scene, inputs=[3], outputs=[2]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

        self.payload['inputtype'] = "img"
        self.payload['centers'] = {15: (0, 0), 16: (0, 0)}

        self.reset_payload = {}

        self.payload_out1 = {}
        self.img_h = 480
        self.img_w = 640
        
        self.frame = None

        self.QTimeClock = None

    def initInnerClasses(self):
        self.content = MEDIAPLAYER_BAR(self)                       # <----------- init UI with data and widget
        self.grNode = FlowGraphicsMediaBar(self)          # <----------- Box Image Draw in Flow_Node_Base

        #=============================================================
        # Resizeable
        self.grNode_addr = str(self.grNode)[-13:-1]
        self.BoxKey = "ChangeItemFrame:" + self.grNode_addr

        self.content.ui.playBtn.clicked.connect(self.play_video)
        self.content.ui.browsFiles.clicked.connect(self.content.browseSlot)
        self.content.ui.slider.sliderMoved.connect(self.set_position)

        self.content.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.content.mediaPlayer.positionChanged.connect(self.position_changed)
        self.content.mediaPlayer.durationChanged.connect(self.duration_changed)

        self.content.grabber.frameAvailable.connect(self.process_frame)
        self.content.SendFrame_Timer.timeout.connect(self.Update_Frame)
        self.content.SendFrame_Timer.setInterval(100)

        self.content.ui.ResizeBtn.clicked.connect(self.StartResize_ItemFram)
        self.content.ResizeFrame_timer.timeout.connect(self.update_ItemFrame)

        self.content.ui.BackBtn.clicked.connect(self.back_video)
        self.content.ui.FFBtn.clicked.connect(self.forward_video)

        self.Global = GlobalVariable()
        self.Global.setGlobal("ReadyChangeItemFrame", False)

    def evalImplementation(self):                       # <----------- Create Socket range Index
        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.reset_payload = input_node.eval()

            if self.reset_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                # return

            elif self.reset_payload is not None:
                #print("val Len = ", len(str(self.payload['img'])))
                if "submit" in self.reset_payload: 
                    if self.reset_payload["submit"]: 
                        print("\033[93m {}\033[00m".format("Reset Media Player !!!"))
                        self.content.mediaPlayer.setPosition(0)

        # self.value = self.payload                       # <----------- Push payload to value
        # self.markDirty(False)
        # self.markInvalid(False)

        # self.markDescendantsInvalid(False)
        # self.markDescendantsDirty()

        # #self.grNode.setToolTip("")
        # self.evalChildren()

        #return self.value

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

    def process_frame(self, image):
        self.payload['fps'] = time.time()

        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                self.payload['blink'] = True
            else:
                self.payload['blink'] = False

            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

        #Converts a QImage into an opencv MAT format
        OpenCVImage = image.convertToFormat(4)

        width = OpenCVImage.width()
        height = OpenCVImage.height()

        ptr = OpenCVImage.bits()
        ptr.setsize(OpenCVImage.byteCount())
        Img_arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        self.img_h, self.img_w = Img_arr.shape[:2]
        # Img_arr = cv2.resize(Img_arr, dsize=(640, 480), interpolation=cv2.INTER_AREA)

        self.frame = cv2.cvtColor(Img_arr, cv2.COLOR_BGR2RGB)
        height, width, bpc = self.frame.shape
        bpl = bpc * width
        img = QtGui.QImage(self.frame.data, width, height, bpl, QtGui.QImage.Format_RGB888)

        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath() + "/Videos", "Media (*.webm *.mp4 *.ts *.avi *.mpeg *.mpg *.mkv *.VOB *.m4v *.3gp *.mp3 *.m4a *.wav *.ogg *.flac *.m3u *.m3u8)")

        if fileName != '':
            self.loadFilm(fileName)
            print("File loaded")
        
    def play_video(self):
        if self.content.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.content.mediaPlayer.pause()
            self.content.ui.slider.setEnabled(True)
            #self.content.playBtn.setIcon(QIcon(self.content.pause_icon))

            self.content.SendFrame_Timer.stop()
            self.content.mplayer_status = False

        else:
            self.content.mediaPlayer.play()
            #self.content.playBtn.setIcon(QIcon(self.content.play_icon))
            self.content.SendFrame_Timer.start()
            self.content.mplayer_status = True

            if self.Global.hasGlobal("StopMediaPlayer"):
                self.Global.removeGlobal("StopMediaPlayer")

    def mediastate_changed(self, state):
        if self.content.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.content.ui.playBtn.setIcon(QIcon(self.content.pause_icon))

        else:
            self.content.ui.playBtn.setIcon(QIcon(self.content.play_icon))

    def position_changed(self, position):
        self.content.ui.slider.setValue(position)
        #print("position_changed = ", position)
        self.content.slid_position = position
        mtime = QTime(0,0,0,0)
        mtime = mtime.addMSecs(self.content.mediaPlayer.position())
        self.QTimeClock = mtime
        # print("self.QTimeClock :", self.QTimeClock.toString())
        self.content.ui.slbl.setText(mtime.toString())

    def duration_changed(self, duration):
        self.content.ui.slider.setRange(0, duration)
        #print("duration_changed = ", duration)

        mtime = QTime(0,0,0,0)
        mtime = mtime.addMSecs(self.content.mediaPlayer.duration())
        self.content.ui.elbl.setText(mtime.toString())

    def forward_video(self):
        # Increase the time by 5 seconds
        self.QTimeClock = self.QTimeClock.addSecs(5)
        self.update_media_player_position()
        self.update_time_display()

    def back_video(self):
        # Decrease the time by 5 seconds
        self.QTimeClock = self.QTimeClock.addSecs(-5)
        self.update_media_player_position()
        self.update_time_display()

    def update_time_display(self):
        # Update the label
        self.content.ui.slbl.setText(self.QTimeClock.toString())

        # Convert QTime to milliseconds
        time_in_msecs = QTime(0, 0).msecsTo(self.QTimeClock)

        # Update the slider in the content
        self.content.ui.slider.setValue(time_in_msecs)

        # Update the external slider
        self.content.ui.slider.setValue(time_in_msecs)

    def update_media_player_position(self):
        # Convert QTime to milliseconds
        new_position = QTime(0, 0).msecsTo(self.QTimeClock)
        # Set the new position to the media player
        self.content.mediaPlayer.setPosition(new_position)


    def set_position(self, position):
        self.content.mediaPlayer.setPosition(position)

    def handle_errors(self):
        self.content.ui.playBtn.setEnabled(False)
        #self.label.setText("Error: " + self.content.mediaPlayer.errorString())

    def Update_Frame(self):
        self.payload['video_filename'] = self.content.filename
        self.payload['clock'] = self.content.ui.slbl.text()
        self.payload['img_h'] = self.img_h
        self.payload['img_w'] = self.img_w
        self.payload['img'] = self.frame

        # self.evalImplementation()                   #<--------- Send Payload to output socket

        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        if self.Global.hasGlobal("StopMediaPlayer"):
            if self.Global.getGlobal("StopMediaPlayer"):
                self.content.mediaPlayer.pause()
                self.content.SendFrame_Timer.stop()
                self.content.mplayer_status = False


