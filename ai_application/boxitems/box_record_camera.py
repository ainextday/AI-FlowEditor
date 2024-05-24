from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import ai_application.AI_Tools.Upload_File as UploadFile

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time, sys
import datetime

import ftplib
import os

class REC_CAMAERAS(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
        
        self.videorec_icon = self.Path + "/icons/icons_rec_image.png"
        self.imagerec_icon = self.Path + "/icons/icons_save_image.png"
        self.browse_icon = self.Path + "/icons/icons_save_ib.png"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.uploadhost_icon = self.Path + "/icons/icons_upload_photo.png"
        self.uploadhost_gray_icon = self.Path + "/icons/icons_upload_photo_gray.png"
        self.remove_icon = self.Path + "/icons/icons_cancel_btn.png"
        
        self.lblInput = QLabel("No Input" , self)
        self.lblInput.setAlignment(Qt.AlignLeft)
        self.lblInput.setGeometry(10,5,100,20)
        self.lblInput.setStyleSheet("color: red; font-size:5pt;")

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(120,72,25,25)
        self.browsFiles.setIcon(QIcon(self.browse_icon))
        self.browsFiles.setIconSize(QtCore.QSize(35,25))
        self.browsFiles.setStyleSheet("background-color: transparent; border: 0px;")  

        #=======================================
        # LED 

        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(30,30)
        graphicsView.setGeometry(QtCore.QRect(117, 0, 35, 35))

        self.img = QPixmap(self.bgImagePath)
        self.pixmap.setPixmap(self.img)

        #=======================================

        #self.edit.setObjectName(self.node.content_label_objname)
        self.radioRecState = QRadioButton(self)
        self.radioRecState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : rgba(0, 124, 212, 50);"
                                   "}")
        self.radioRecState.setGeometry(15,25,100,22)
        self.radioRecState.setIcon(QIcon(self.videorec_icon))

        self.lblsavevdo = QLabel("Video" , self)
        self.lblsavevdo.setAlignment(Qt.AlignLeft)
        self.lblsavevdo.setGeometry(65,25,50,20)
        self.lblsavevdo.setStyleSheet("color: lightblue")

        #=======================================

        #self.edit.setObjectName(self.node.content_label_objname)
        self.radioImgState = QRadioButton(self)
        self.radioImgState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : rgba(0, 124, 212, 50);"
                                   "}")
        self.radioImgState.setGeometry(15,55,100,22)
        self.radioImgState.setIcon(QIcon(self.imagerec_icon))

        self.lblsaveImg = QLabel("Image" , self)
        self.lblsaveImg.setAlignment(Qt.AlignLeft)
        self.lblsaveImg.setGeometry(65,55,50,20)
        self.lblsaveImg.setStyleSheet("color: lightblue")

        self.lblLoacation = QLabel("L:" , self)
        self.lblLoacation.setAlignment(Qt.AlignLeft)
        self.lblLoacation.setGeometry(10,85,100,20)
        self.lblLoacation.setStyleSheet("color: lightblue; font-size:5pt;")

        self.cntImage = QLabel("0" , self)
        self.cntImage.setAlignment(Qt.AlignLeft)
        self.cntImage.setGeometry(125,58,30,20)
        self.cntImage.setStyleSheet("color: lightblue; font-size:5pt;")

        #=======================================

        """self.saveprocess = QCheckBox("S",self)
        self.saveprocess.setGeometry(75,5,30,20)
        self.saveprocess.setStyleSheet("color: lightblue")

        self.saveprocess.setChecked(True)"""

        self.SwitchStartRecord = QPushButton(self)
        self.SwitchStartRecord.setGeometry(82,5,37,20)
        self.SwitchStartRecord.setIcon(QIcon(self.off_icon))
        self.SwitchStartRecord.setIconSize(QtCore.QSize(37,20))
        self.SwitchStartRecord.setStyleSheet("background-color: transparent; border: 0px;")  

        self.startWriteFile = False
        self.processave_flag = False

        #====================================================
        # Popup Host Server
        #====================================================
        self.UploadHostBtn = QPushButton(self)
        self.UploadHostBtn.setGeometry(115,30,30,30)
        self.UploadHostBtn.setIcon(QIcon(self.uploadhost_gray_icon))
        self.UploadHostBtn.setIconSize(QtCore.QSize(30,30))
        self.UploadHostBtn.setStyleSheet("background-color: transparent; border: 0px;")  

        self.PopUplbl = QLabel(self)
        self.PopUplbl.setGeometry(5,5,140,90)
        self.PopUplbl.setAlignment(Qt.AlignLeft)
        self.PopUplbl.setAlignment(Qt.AlignTop)
        self.PopUplbl.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:9pt;color:orange; border: 1px solid white; border-radius: 5%")
        self.PopUplbl.setVisible(False)

        self.checkHost = QCheckBox("Host Setting",self)
        self.checkHost.setGeometry(8,8,110,20)
        self.checkHost.setStyleSheet("color: orange")
        self.checkHost.setChecked(False)
        self.checkHost.setVisible(False)

        self.ExitPopUp = QPushButton(self)
        self.ExitPopUp.setGeometry(120,7,20,20)
        self.ExitPopUp.setIcon(QIcon(self.remove_icon))
        self.ExitPopUp.setVisible(False)

        self.editHost = QLineEdit(self)
        self.editHost.setGeometry(10,28,130,20)
        self.editHost.setPlaceholderText("Host")
        self.editHost.setVisible(False)

        self.editPort = QLineEdit(self)
        self.editPort.setGeometry(10,48,50,20)
        self.editPort.setPlaceholderText("Port")
        self.editPort.setVisible(False)

        self.editFolder = QLineEdit(self)
        self.editFolder.setGeometry(55,48,85,20)
        self.editFolder.setPlaceholderText("Folder")
        self.editFolder.setVisible(False)

        self.editUsername = QLineEdit(self)
        self.editUsername.setGeometry(10,68,70,20)
        self.editUsername.setPlaceholderText("Username")
        self.editUsername.setVisible(False)

        self.editPassword = QLineEdit(self)
        self.editPassword.setGeometry(75,68,65,20)
        self.editPassword.setPlaceholderText("Password")
        self.editPassword.setEchoMode(QLineEdit.Password)
        self.editPassword.setVisible(False)

        self.HostSetup_flag = False  
        self.Upload_timer = QtCore.QTimer(self)

        self.StopAndDelete_timer = QtCore.QTimer(self)

        self.server_status_flag = ""
        self.login_status_flag = ""
        self.HostServer_ready = False
        self.upload_status = ""

        self.ftp = None
        self.Upload_Done = False

        #=======================================

        self.RecordVideo_flag = False
        self.RecordImage_flag = False

        self.SaveResult = None

        self.tricker_flag = False
        self.tricker = False

        self.First_Record_Request = False
        self.Stop_Record_Req = False

        # ==========================================================
        # For EvalChrildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['flag_recvideo'] = self.RecordVideo_flag
        res['flag_recimage'] = self.RecordImage_flag
        res['filelocation'] = self.lblLoacation.text()
        res['saveprocess'] = self.processave_flag

        res['flag_hostsetup'] = self.HostSetup_flag
        res['host'] = self.editHost.text()
        res['port'] = self.editPort.text()
        res['folder'] = self.editFolder.text()
        res['username'] = self.editUsername.text()
        res['password'] = self.editPassword.text()

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']

            if 'flag_recvideo' in data:
                if data['flag_recvideo']:
                    self.RecordVideo_flag = True
                    self.radioRecState.setChecked(True)

            if 'flag_recimage' in data:
                if data['flag_recimage']:
                    self.RecordImage_flag = True
                    self.radioImgState.setChecked(True)

            if 'filelocation' in data:
                self.lblLoacation.setText(data['filelocation'])

            if 'saveprocess' in data:
                if data['saveprocess']:
                    self.processave_flag = True
                    self.SwitchStartRecord.setIcon(QIcon(self.on_icon))

                else:
                    self.processave_flag = False
                    self.SwitchStartRecord.setIcon(QIcon(self.off_icon))

            if 'host' in data:
                self.editHost.setText(data['host'])

            if 'port' in data:
                self.editPort.setText(data['port'])

            if 'folder' in data:
                self.editFolder.setText(data['folder'])

            if 'username' in data:
                self.editUsername.setText(data['username'])

            if 'password' in data:
                self.editPassword.setText(data['password'])

            if 'flag_hostsetup' in data:
                self.HostSetup_flag = data['flag_hostsetup']
                if self.HostSetup_flag:
                    #self.HostServer_ready = self.LoginHost_Server()
                    #print("deserialize : self.HostServer_ready = ", self.HostServer_ready)
                    self.checkHost.setChecked(True)

                else:
                    self.checkHost.setChecked(False)

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def LoginHost_Server(self):
        print()
        # connect to host on default port i.e 21
        if len(str(self.editHost.text())) > 0 and len(str(self.editPort.text())) > 0:
            self.ftp = ftplib.FTP()
            self.ftp.set_pasv(False)
            
            self.ftp.connect(str(self.editHost.text()), int(str(self.editPort.text())))
            self.server_status_flag = self.ftp.getwelcome()
            print("self.server_status_flag = ", self.server_status_flag)

            try:
                print("Logging in...")
                self.login_status_flag = self.ftp.login(str(self.editUsername.text()), str(self.editPassword.text()))
                print("login_status = ", self.login_status_flag)

                # change directory to upload
                if len(str(self.editFolder.text())) > 0:

                    # directory to upload
                    print("str(self.editFolder.text()) : ", str(self.editFolder.text()))
                    self.ftp.cwd(str(self.editFolder.text()))

                login_respond = "230 User " + str(self.editUsername.text()) + " logged in"
                print("login_respond : ", login_respond)

                # self.UploadHostBtn.setIcon(QIcon(self.uploadhost_icon))
                return True
                    
            except:
                print("failed to login")
                return False

        else:
            return False

    #Select destinate Folder to Save file
    def browseSlot(self):
        """self.fileLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.fileLocation)"""

        self.lblLoacation.setText(str(QFileDialog.getExistingDirectory(self, "Select Directory")))

@register_node(OP_NODE_RECORD)
class Open_RecordCAM(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_rec_button.png"
    op_code = OP_NODE_RECORD
    op_title = "Rec - Ext/FTP"
    content_label_objname = "Rec - Ext/FTP"

    def __init__(self, scene):
        super().__init__(scene, inputs=[3,4], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        #self.eval()

        self.FirstInput = False
        self.timeString = ""

        self.start_record = None

        self.i = 0

        self.Upload_image_file = False

        self.filename = None
        self.video_filename = None
        self.upload_file = None

        self.waitingControl = False
        self.control_mode = "normal_payload"

        self.upload_img_one_time = False

        self.new_payload = {}
        self.rx_payload_1 = {}
        self.rx_payload_2 = {}

        self.file_type = "img"

    def initInnerClasses(self):
        self.content = REC_CAMAERAS(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.FTP_ID = str(self.id)

        self.content.radioRecState.toggled.connect(self.onClickedRecVideo)
        self.content.radioImgState.toggled.connect(self.onClickedRecImage)

        self.content.browsFiles.clicked.connect(self.content.browseSlot)
        self.content.SwitchStartRecord.clicked.connect(self.StartRecordFile)

        self.content.UploadHostBtn.clicked.connect(self.ServerHost_Setup)
        self.content.ExitPopUp.clicked.connect(self.CloseSetup)
        self.content.checkHost.stateChanged.connect(self.SelectHostSetup)

        self.content.Upload_timer.timeout.connect(self.Upload_file_to_server)
        self.content.Upload_timer.setInterval(100)

        self.content.StopAndDelete_timer.timeout.connect(self.StopAndDelet_Video)

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node_1 = self.getInput(0)
        if not input_node_1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()

        else:
            self.rx_payload_1 = input_node_1.eval()
            
        input_node_2 = self.getInput(1)
        if not input_node_2:
            self.waitingControl = False
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()

        else:
            self.waitingControl = True
            self.rx_payload_2 = input_node_2.eval()

        if self.rx_payload_1 is None and self.rx_payload_2 is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        else:
            if self.rx_payload_1 and self.rx_payload_2:
                self.new_payload = {**self.rx_payload_1, **self.rx_payload_2} 
            
            else:
                #self.rx_payload_2 is Empty
                self.new_payload = self.rx_payload_1

            if self.new_payload:
                if 'submit' in self.new_payload:
                    # print("self.new_payload['submit'] = ", self.new_payload['submit'])
                    
                    if self.new_payload['submit'] and not self.content.tricker_flag and not self.content.First_Record_Request:
                        self.content.tricker_flag = True

                    if not self.new_payload['submit'] and self.content.tricker_flag and not self.content.First_Record_Request:
                        self.content.First_Record_Request = True
                        # print("First Request Record File !!!")

                    if self.content.First_Record_Request and not self.content.tricker:
                        self.content.tricker =True
                        # print("Start tricker = ", self.content.tricker)

                        self.control_mode = "normal_payload"

                        self.content.First_Record_Request = True
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.on_icon))

                        self.content.processave_flag = True
                        # print("self.content.processave_flag: ", self.content.processave_flag)

                    if self.new_payload['submit'] and self.content.tricker and self.content.First_Record_Request:
                        self.content.First_Record_Request = False
                        self.content.Stop_Record_Req = True

                    if not self.new_payload['submit'] and self.content.tricker and self.content.Stop_Record_Req:
                        self.content.tricker = False
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

                if 'result' in self.new_payload:
                    if self.new_payload['result'] and not self.content.tricker:
                        self.content.tricker =True
                        # print("Start tricker from payload.result = ", self.content.tricker)

                        self.control_mode = "normal_payload"

                        self.content.First_Record_Request = True
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.on_icon))

                        self.content.processave_flag = True
                        self.content.StopAndDelete_timer.start()

                    if not self.new_payload['result'] and self.content.First_Record_Request:
                        self.content.First_Record_Request = False

                        self.content.tricker = False
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

                        # print("Stop record camera from payload.result= ", self.content.tricker)

                        self.content.processave_flag = False
                        self.content.StopAndDelete_timer.stop()

                if 'mqtt_payload' in self.new_payload:
                    if self.new_payload['mqtt_payload'] == "record" and not self.content.tricker:
                        self.content.tricker =True
                        print("Start tricker from mqtt_payload = ", self.content.tricker)

                        self.control_mode = "normal_payload"

                        self.content.First_Record_Request = True
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.on_icon))

                        self.content.processave_flag = True
                        self.content.StopAndDelete_timer.start()

                    if self.new_payload['mqtt_payload'] == "stop" and self.content.First_Record_Request:
                        self.content.First_Record_Request = False

                        self.content.tricker = False
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

                        print("Stop record camera from mqtt_payload = ", self.content.tricker)

                        self.content.processave_flag = False
                        self.content.StopAndDelete_timer.stop()

                if 'upload' in self.new_payload:
                    print("Find Video in Folder")

                # ========================================================================================================
                # schedule_process
                if 'schedule_process' in self.new_payload:
                    if self.new_payload['schedule_process'] == "Start":
                        self.control_mode = "schedule"

                        # print("Start Record Camera")
                        if 'img' in self.new_payload:
                            if len(str(self.new_payload['img'] )) > 100:
                                self.content.SwitchStartRecord.setIcon(QIcon(self.content.on_icon))

                                if 'blink' in self.new_payload:
                                    if self.new_payload['blink'] == True:
                                        self.content.lblInput.setText("<font color=#FF0000>Image Input</font>")
                                        #if self.content.processave_flag or self.content.tricker:
                                        if self.content.tricker:
                                            self.content.bgImagePath = self.content.Path + "/icons/icons_red_spot_30.png"

                                    else:
                                        self.content.lblInput.setText("")
                                        self.content.bgImagePath = None

                                if self.content.RecordVideo_flag or self.content.RecordImage_flag:
                                    self.content.img = QPixmap(self.content.bgImagePath)
                                    self.content.pixmap.setPixmap(self.content.img)

                                    if not self.FirstInput:
                                        self.start_record = datetime.datetime.now()
                                        self.timeString = self.start_record.strftime("%Y_%m_%d_%H%M%S")
                                        # print("self.timeString= ", self.timeString)

                                        if self.content.RecordVideo_flag:
                                            self.Upload_image_file = False
                                            self.filename = self.content.lblLoacation.text() + "/video_" + self.timeString + ".avi"
                                            self.video_filename = "video_" + self.timeString + ".avi"
                                            self.content.SaveResult = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc(*'XVID'), 10, (self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]))

                                        self.FirstInput = True

                                    #=========================================================================================================
                                    # Process Record Video from Camera
                                    if self.content.RecordVideo_flag:
                                        if 'run' in self.new_payload:
                                            if self.new_payload['run']:

                                                self.payload['result'] = "START"

                                                if self.start_record is not None:
                                                    current_time = datetime.datetime.now()
                                                    process_time  = current_time.replace(microsecond=0) - self.start_record.replace(microsecond=0)
                                                    self.payload['result'] = str(int(process_time.total_seconds())) + " SEC"

                                                #print("Process Data record to video ", self.rx_payload['run'], " ,Video File Name = ",self.filename)
                                                self.new_payload['img'] = cv2.putText(self.new_payload['img'] , str(current_time.strftime("%d-%m-%Y %H:%M:%S")), ( self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)    #Blue Green Red (Blue)
                                                self.payload['img'] = self.new_payload['img']
                                                self.payload['inputtype'] = "img"

                                                self.content.SaveResult.write(self.new_payload['img'])
                                                self.content.startWriteFile = True

                                            else:
                                                if self.content.SaveResult is not None:
                                                    self.content.SaveResult.release()
                                                    print("Run The video was successfully saved")
                                                    if self.content.HostSetup_flag:
                                                        self.file_type = "video"
                                                        self.content.Upload_timer.start()

                                                    self.FirstInput = False

                                    #=========================================================================================================
                                    # Process Schedule Extract
                                    if self.content.RecordImage_flag:
                                        self.i += 1

                                        if self.i%5 == 0: 
                                            # print("Extract image from video, self.i = ", self.i)

                                            cv2.imwrite(self.content.lblLoacation.text() + '/Image_' + str(self.timeString) + "_" + str(self.i)+ '.png', self.new_payload['img'])
                                            self.content.cntImage.setText(str(int(self.i/5)))

                                            self.payload['result'] = "EXTRACT"

                    elif self.new_payload['schedule_process'] == "Stop":
                        # print("Schedule process was Stop !!!")
                        self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))
                        if self.content.RecordVideo_flag or self.content.RecordImage_flag:
                            if self.content.SaveResult is not None and self.content.startWriteFile:
                                self.content.SaveResult.release()
                                print("The video in schedule record was successfully saved")
                                self.content.startWriteFile = False

                            self.FirstInput = False

                            self.i = 0
                            self.payload['result'] = "STOP"

                if 'img_upload' in self.new_payload:
                    if self.new_payload['img_upload'] and not self.upload_img_one_time:
                        current_datetime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                        print("\033[96m {}\033[00m".format("Start Upload Image !!!! ---> " + current_datetime))
                        if 'img' in self.new_payload and type(self.new_payload['img']) != type(None):
                            if self.content.HostSetup_flag:
                                self.upload_img_one_time = True
                                self.Upload_image_file = True
                                # self.content.HostServer_ready = self.content.LoginHost_Server()
                                # print("SelectHostSetup(self, state): self.content.HostServer_ready = ", self.content.HostServer_ready)
                                # if self.content.HostServer_ready:

                                self.filename = self.new_payload['img_name']
                                self.video_filename = os.path.basename(self.filename)
                                self.file_type = "img"
                                print("\033[93m {}\033[00m".format("Starting Upload Image !!!!"))

                                self.content.Upload_timer.start()
                                    
                        if not self.new_payload['img_upload']:
                            self.upload_img_one_time = False
                            print("\033[93m {}\033[00m".format("FTP Waiting ..."))

                # ====================================================================================================

                if self.control_mode == "normal_payload":
                    if self.content.processave_flag:

                        # print("self.waitingControl = ", self.waitingControl)

                        if 'img' in self.new_payload:
                            if len(str(self.new_payload['img'] )) > 100:
                                if 'blink' in self.new_payload:
                                    if self.new_payload['blink'] == True:
                                        self.content.lblInput.setText("<font color=#FF0000>Image Input</font>")
                                        #if self.content.processave_flag or self.content.tricker:
                                        if self.content.tricker:
                                            self.content.bgImagePath = self.content.Path + "/icons/icons_red_spot_30.png"

                                    else:
                                        self.content.lblInput.setText("")
                                        self.content.bgImagePath = None

                                #if self.content.processave_flag or self.content.tricker:
                                if self.content.tricker:
                                    if self.content.RecordVideo_flag or self.content.RecordImage_flag:
                                        self.content.img = QPixmap(self.content.bgImagePath)
                                        self.content.pixmap.setPixmap(self.content.img)

                                        if not self.FirstInput:
                                            self.start_record = datetime.datetime.now()
                                            self.timeString = self.start_record.strftime("%Y_%m_%d_%H%M%S")
                                            # print("self.timeString= ", self.timeString)

                                            if self.content.RecordVideo_flag:
                                                self.filename = self.content.lblLoacation.text() + "/video_" + self.timeString + ".avi"
                                                self.video_filename = "video_" + self.timeString + ".avi"
                                                self.content.SaveResult = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc(*'XVID'), 10, (self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]))

                                            self.FirstInput = True

                                        #=========================================================================================================
                                        # Process Record Video from Camera
                                        if self.content.RecordVideo_flag:
                                            if 'run' in self.new_payload:
                                                if self.new_payload['run']:

                                                    self.payload['result'] = "START"

                                                    if self.start_record is not None:
                                                        current_time = datetime.datetime.now()
                                                        process_time  = current_time.replace(microsecond=0) - self.start_record.replace(microsecond=0)
                                                        self.payload['result'] = str(int(process_time.total_seconds())) + " SEC"

                                                    #print("Process Data record to video ", self.rx_payload['run'], " ,Video File Name = ",self.filename)
                                                    self.new_payload['img'] = cv2.putText(self.new_payload['img'] , str(current_time.strftime("%d_%m_%Y_%H%M%S")), ( self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)    #Blue Green Red (Blue)
                                                    self.payload['img'] = self.new_payload['img']
                                                    self.payload['inputtype'] = "img"

                                                    if type(self.content.SaveResult) != type(None):
                                                        self.content.SaveResult.write(self.new_payload['img'])
                                                        self.content.startWriteFile = True

                                                    else:
                                                        self.start_record = datetime.datetime.now()
                                                        self.timeString = self.start_record.strftime("%Y_%m_%d_%H%M%S")
                                                        # print("self.timeString= ", self.timeString)

                                                        if self.content.RecordVideo_flag:
                                                            self.filename = self.content.lblLoacation.text() + "/video_" + self.timeString + ".avi"
                                                            self.video_filename = "video_" + self.timeString + ".avi"
                                                            self.content.SaveResult = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc(*'XVID'), 10, (self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]))

                                                else:
                                                    if self.content.SaveResult is not None:
                                                        self.content.SaveResult.release()
                                                        print("The video was successfully saved")
                                                        if self.content.HostSetup_flag:
                                                            self.file_type = "video"
                                                            self.content.Upload_timer.start()

                                                        self.FirstInput = False

                                            #=========================================================================================================
                                            # Process Record Video from Media Player
                                            if 'clock' in self.new_payload:
                                                if self.new_payload['clock']:

                                                    self.payload['result'] = "START"

                                                    if self.start_record is not None:
                                                        current_time = datetime.datetime.now()
                                                        process_time  = current_time.replace(microsecond=0) - self.start_record.replace(microsecond=0)
                                                        self.payload['result'] = str(int(process_time.total_seconds())) + " SEC"

                                                    #print("Process Data record to video ", self.rx_payload['run'], " ,Video File Name = ",self.filename)
                                                    self.new_payload['img'] = cv2.putText(self.new_payload['img'] , str(current_time.strftime("%d-%m-%Y %H:%M:%S")), ( self.new_payload['img'].shape[1], self.new_payload['img'].shape[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)    #Blue Green Red (Blue)
                                                    self.payload['img'] = self.new_payload['img']
                                                    self.payload['inputtype'] = "img"

                                                    self.content.SaveResult.write(self.new_payload['img'])
                                                    self.content.startWriteFile = True

                                                else:
                                                    if self.content.SaveResult is not None:
                                                        self.content.SaveResult.release()
                                                        # print("if 'clock' in self.new_payload: The video was successfully saved")

                                                        self.FirstInput = False

                                        #=========================================================================================================
                                        # Process cameraCapture and Extract
                                        if self.content.RecordImage_flag:
                                            if 'cameraCapture' in self.new_payload :
                                                # print("Process Data record to image ", self.new_payload['cameraCapture'])

                                                cv2.imwrite(self.content.lblLoacation.text() + '/Image_' + str(self.timeString) + '.png', self.new_payload['img'])

                                                self.payload['result'] = "CAPTURE"
                                                self.payload['img'] = self.new_payload['img']
                                                self.payload['inputtype'] = "img"
                                            
                                            if 'run' in self.new_payload:
                                                if self.new_payload['run']:

                                                    if not self.waitingControl:
                                            
                                                        self.i += 1

                                                        if self.i%5 == 0: 
                                                            # print("Extract image from video, self.i = ", self.i)

                                                            cv2.imwrite(self.content.lblLoacation.text() + '/Image_' + str(self.timeString) + "_" + str(self.i)+ '.png', self.new_payload['img'])
                                                            self.content.cntImage.setText(str(int(self.i/5))) 

                                                            self.payload['result'] = "EXTRACT"

                                                    else:

                                                        cv2.imwrite(self.content.lblLoacation.text() + '/Image_Capture' + str(self.timeString) + '.png', self.new_payload['img'])

                                                        self.payload['result'] = "CAPTURE"
                                                        self.payload['img'] = self.new_payload['img']
                                                        self.payload['inputtype'] = "img"

                                                else:
                                                    # print("Stop to Extract")
                                                    self.FirstInput = False

                                                    self.i = 0

                                                    self.payload['result'] = "STOP"

                                            if 'clock' in self.new_payload:
                                                if self.new_payload['clock']:

                                                    if not self.waitingControl:
                                                        self.i += 1

                                                        if self.i%5 == 0: 
                                                            # print("Extract image from video, self.i = ", self.i)

                                                            cv2.imwrite(self.content.lblLoacation.text() + '/Image_' + str(self.timeString) + "_" + str(self.i)+ '.png', self.new_payload['img'])
                                                            self.content.cntImage.setText(str(int(self.i/5))) 

                                                            self.payload['result'] = "EXTRACT"

                                                    else:
                                                        cv2.imwrite(self.content.lblLoacation.text() + '/Image_Capture' + str(self.timeString) + '.png', self.new_payload['img'])

                                                        self.payload['result'] = "CAPTURE"
                                                        self.payload['img'] = self.new_payload['img']
                                                        self.payload['inputtype'] = "img"

                                                else:
                                                    # print("Stop to Extract")
                                                    self.FirstInput = False

                                                    self.i = 0

                                                    self.payload['result'] = "STOP"
                                                    
                                else:
                                    if self.content.startWriteFile:
                                        # print("Stop Write File !!!")

                                        if self.content.SaveResult is not None:
                                            self.content.SaveResult.release()
                                            # print("self.content.startWriteFile: The video was successfully saved")
                                            self.FirstInput = False

                                            self.i = 0

                                            self.content.tricker_flag = False

                                            self.content.First_Record_Request = False
                                            self.content.Stop_Record_Req = False

                                            self.content.startWriteFile = False
                                            self.payload['result'] = "STOP"

                                            self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

                                            # self.content.HostServer_ready = self.content.LoginHost_Server()
                                            # # print("SelectHostSetup(self, state): self.content.HostServer_ready = ", self.content.HostServer_ready)
                                            # if self.content.HostServer_ready:

                                            self.file_type = "video"
                                            self.content.Upload_timer.start()

                    else:
                        if self.content.startWriteFile:
                            # print("Stop Write File !!!")

                            if self.content.SaveResult is not None:
                                self.content.SaveResult.release()
                                # print("else: if self.content.startWriteFile: The video was successfully saved")
                                self.FirstInput = False

                                self.i = 0

                                self.content.tricker_flag = False

                                self.content.First_Record_Request = False
                                self.content.Stop_Record_Req = False

                                self.content.startWriteFile = False
                                self.payload['result'] = "STOP"

                                self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

                                if self.content.HostSetup_flag:
                                    # self.content.HostServer_ready = self.content.LoginHost_Server()
                                    # # print("SelectHostSetup(self, state): self.content.HostServer_ready = ", self.content.HostServer_ready)
                                    # if self.content.HostServer_ready:
                                    
                                    self.file_type = "video"
                                    self.content.Upload_timer.start()

                    """
                    if self.Global.hasGlobal('delete_video'):
                        if self.Global.getGlobal('delete_video'):
                            self.content.SaveResult.release()
                            print("else: if self.content.startWriteFile: The video was successfully saved")

                            self.content.startWriteFile = False

                            #print("self.filename = ", self.filename)
                            if len(str(self.filename)) > 5: # self.filename is not None
                                if os.path.isfile(self.filename):
                                    print ("File exist")

                                    os.remove(self.filename)        
                                    print ("self.Global.hasGlobal('delete_video'): Removed self.filename = ", self.filename)
                            
                            self.Global.setGlobal('delete_video', None)
                            self.Global.removeGlobal('delete_video')   """

        self.sendOutputPayload(self.payload)                       # <----------- Push payload to value

        #return self.value

    def ServerHost_Setup(self):
        self.content.PopUplbl.setVisible(True)
        self.content.ExitPopUp.setVisible(True)
        self.content.checkHost.setVisible(True)

        self.content.editHost.setVisible(True)
        self.content.editPort.setVisible(True)
        self.content.editFolder.setVisible(True)
        self.content.editUsername.setVisible(True)
        self.content.editPassword.setVisible(True)

    def CloseSetup(self):
        self.content.PopUplbl.setVisible(False)
        self.content.ExitPopUp.setVisible(False)
        self.content.checkHost.setVisible(False)

        self.content.editHost.setVisible(False)
        self.content.editPort.setVisible(False)
        self.content.editFolder.setVisible(False)
        self.content.editUsername.setVisible(False)
        self.content.editPassword.setVisible(False)

    def StopAndDelet_Video(self):
        if self.Global.hasGlobal('delete_video'):
            self.content.StopAndDelete_timer.stop()

            self.content.SaveResult.release()
            # print("StopAndDelet_Video : The video was successfully saved")
            
            self.FirstInput = False
            self.content.startWriteFile = False

            if self.Global.getGlobal('delete_video'):

                #print("self.filename = ", self.filename)
                if len(str(self.filename)) > 5 and not self.Upload_image_file: # self.filename is not None
                    if os.path.isfile(self.filename):
                        print ("File exist")

                        os.remove(self.filename)        
                        print ("StopAndDelet_Video(self): Removed self.filename = ", self.filename) 
            
            self.Global.removeGlobal('delete_video')
            # print("self.Global.removeGlobal('delete_video')")
            
            self.content.processave_flag = False
            self.content.First_Record_Request = False
            self.content.tricker = False
            self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

    def Upload_file_to_server(self):
        if self.content.HostServer_ready and not self.content.Upload_Done:
            self.content.Upload_Done = True

            self.content.UploadHostBtn.setIcon(QIcon(self.content.uploadhost_icon))

            # upload file
            print("def Upload_video(self): self.filename = ", self.filename)
            print("def Upload_video(self): self.video_filename = ", self.video_filename)
            # self.upload_file = open(self.filename, 'rb')
            # self.content.upload_status = self.content.ftp.storbinary('STOR %s' % os.path.basename(self.video_filename), self.upload_file, 1024)

            # Upload Video

            # if 'host' in data:
            #     self.editHost.setText(data['host'])

            # if 'port' in data:
            #     self.editPort.setText(data['port'])

            # if 'folder' in data:
            #     self.editFolder.setText(data['folder'])

            # if 'username' in data:
            #     self.editUsername.setText(data['username'])

            # if 'password' in data:
            #     self.editPassword.setText(data['password'])

            try:
                UploadFile_app = UploadFile.app
                UploadFile.UploadFileThread(self.content.editHost.text(), int(self.content.editPort.text()), 
                                            self.content.editUsername.text(), self.content.editPassword.text(),
                                            self.filename, self.video_filename, self.FTP_ID, self.file_type).start()
                UploadFile_app.exec_()

            except:
                print("Upload Duplicate !!!")

                self.content.Upload_timer.stop()
                self.content.Upload_Done = False

                self.content.UploadHostBtn.setIcon(QIcon(self.content.uploadhost_gray_icon))
                
                # self.upload_img_one_time = False

        if self.Global.hasGlobal("FTP_Process" + self.FTP_ID):
            if self.Global.getGlobal("FTP_Process" + self.FTP_ID):
                if os.path.isfile(self.filename) and not self.Upload_image_file:
                    print ("File exist")

                    os.remove(self.filename)        
                    print ("Removed self.filename = ", self.filename) 

                self.content.Upload_timer.stop()
                self.content.Upload_Done = False


                self.Global.setGlobal("FTP_Process" + self.FTP_ID, False)
                self.Global.removeGlobal("FTP_Process" + self.FTP_ID)

                self.content.UploadHostBtn.setIcon(QIcon(self.content.uploadhost_gray_icon))

                self.upload_img_one_time = False
                
                result = "FTP Upload OK : " + str(datetime.datetime.now().strftime("%H:%M:%S"))
                print("\033[92m {}\033[00m".format(result))
                
                self.payload['result'] = result
                self.sendOutputPayload(self.payload)                       # <----------- Push payload to value


    def SelectHostSetup(self, state):
        print()
        print("SelectHostSetup:")
        if state == QtCore.Qt.Checked:
            self.content.HostSetup_flag = True
            self.content.HostServer_ready = self.content.LoginHost_Server()
            print("SelectHostSetup(self, state): self.content.HostServer_ready = ", self.content.HostServer_ready)

        else:
            self.content.HostSetup_flag = False
            self.content.UploadHostBtn.setIcon(QIcon(self.content.uploadhost_gray_icon))

            self.upload_img_one_time = False
      
        print("def SelectHostSetup(self, state): self.content.HostSetup_flag = ", self.content.HostSetup_flag)

    def onClickedRecVideo(self):
        print("Select Record Video")

        self.content.RecordVideo_flag = True
        self.content.RecordImage_flag = False

        if self.content.SaveResult is not None:
            self.content.SaveResult.release()
            print("onClickedRecVideo(self); The video was successfully saved")
            self.FirstInput = False

            self.i = 0

            self.content.tricker_flag = False
            self.content.tricker = False

            self.content.startWriteFile = False
            self.payload['result'] = "STOP"

    def onClickedRecImage(self):
        print("Select Record Image")

        self.content.RecordVideo_flag = False
        self.content.RecordImage_flag = True

        if self.content.SaveResult is not None:
            self.content.SaveResult.release()
            print("onClickedRecImage(self); The video was successfully saved")
            self.FirstInput = False

            self.i = 0

            self.content.tricker_flag = False

            self.content.First_Record_Request = False
            self.content.Stop_Record_Req = False

            self.content.startWriteFile = False
            self.payload['result'] = "STOP"

    def StartRecordFile(self):
        if not self.content.processave_flag:
            self.content.SwitchStartRecord.setIcon(QIcon(self.content.on_icon))
            self.content.processave_flag = True

            self.content.tricker = True

        else:
            self.content.SwitchStartRecord.setIcon(QIcon(self.content.off_icon))

            self.content.bgImagePath = None
            self.content.img = QPixmap(self.content.bgImagePath)
            self.content.pixmap.setPixmap(self.content.img)

            self.upload_img_one_time = False
            self.content.UploadHostBtn.setIcon(QIcon(self.content.uploadhost_gray_icon))

            if self.content.tricker:
                if self.content.SaveResult is not None:
                    self.content.SaveResult.release()
                    print("StartRecordFile(self); The video was successfully saved")

                    self.FirstInput = False
                    self.content.tricker = False

                    self.payload['result'] = "STOP"
                    self.sendOutputPayload(self.payload)                       # <----------- Push payload to value

            self.content.tricker_flag = False

            self.content.First_Record_Request = False
            self.content.Stop_Record_Req = False

            self.content.processave_flag = False

            
    def sendOutputPayload(self, value):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(self.op_code)
        else:
            self.evalChildren()

            