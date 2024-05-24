from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import cv2 
import datetime

from PIL import Image
import os, sys

class ExtractImage(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.refresh_icon = self.Path + "/icons/icons_refresh.png"
        self.play_icon = self.Path + "/icons/icons_play.png"
        self.pause_icon = self.Path + "/icons/icons_pause.png"
        self.save_icon = self.Path + "/icons/icons_save.png"

        # Start Video to Extract
        self.lbl = QLabel("Video Sorce: " , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,0,100,20)
        self.lbl.setStyleSheet("color: orange")

        self.edit = QLineEdit("", self)
        self.edit.setGeometry(10,15,105,20)
        self.edit.setPlaceholderText("Source Folder :")
        
        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(120,15,20,20)
        self.browsFiles.setIcon(QIcon(self.save_icon))

        #==============================================
        # Destination Image
        self.lbl2 = QLabel("Destination : " , self)
        self.lbl2.setAlignment(Qt.AlignLeft)
        self.lbl2.setGeometry(10,40,100,20)
        self.lbl2.setStyleSheet("color: pink")

        self.editDest = QLineEdit("", self)
        self.editDest.setGeometry(10,55,105,20)
        self.editDest.setPlaceholderText("Destination Folder :")

        self.browsDestFiles = QPushButton(self)
        self.browsDestFiles.setGeometry(120,55,20,20)
        self.browsDestFiles.setIcon(QIcon(self.save_icon))

        #==============================================

        self.lblResult = QLabel("" , self)
        self.lblResult.setAlignment(Qt.AlignLeft)
        self.lblResult.setGeometry(13,82,80,20)
        self.lblResult.setStyleSheet("color: white")

        self.extractbtn = QPushButton(self)
        self.extractbtn.setGeometry(90,78,50,20)
        self.extractbtn.setIcon(QIcon(self.play_icon))

        self.fileLocation = ""
        self.BtnToggle = False

        self.Extract_timer = QtCore.QTimer(self)
        

    def serialize(self):
        res = super().serialize()
        res['value'] = self.Data
        res['startFolder'] = self.edit.text()
        res['endFolder'] = self.editDest.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.fileLocation = data['startFolder']
            self.edit.setText(data['startFolder'])
            self.editDest.setText(data['endFolder'])
            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def browseSlot(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Video Files (*.mp4)", options=options)
        if files:
            self.fileLocation = files[0]
            self.edit.setText(str(self.fileLocation))

    def browseFolder(self):
        print("self.Path = ", self.Path[0:-9] )
        path = self.Path[0:-9] + "/AI_Module/yolo_training/custom_dataset"
        os.startfile(path)

@register_node(OP_NODE_EXTRACT)
class Open_ExtractImage(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_extract_icon.png"
    op_code = OP_NODE_EXTRACT
    op_title = "Extract Image"
    content_label_objname = "Extract Image"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.payload['prepdataset'] = None

        self.cam = None

        # frame 
        self.currentframe = 0

    def initInnerClasses(self):
        self.content = ExtractImage(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.browsFiles.clicked.connect(self.content.browseSlot)
        self.content.browsDestFiles.clicked.connect(self.content.browseFolder)

        self.content.editDest.setText(self.content.Path[0:-9] + "/AI_Tools/Extract_Image")
        self.content.extractbtn.clicked.connect(self.StartExtractImage)

        self.content.Extract_timer.timeout.connect(self.extract_frame)

    def evalImplementation(self):                 # <

        self.value = self.payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        return self.value

    def StartExtractImage(self):
        print("self.content.fileLocation = " , self.content.fileLocation)
        print("len(self.content.fileLocation) = ", len(self.content.fileLocation))

        if len(self.content.fileLocation) > 1:
            # Read the video from specified path 
            self.cam = cv2.VideoCapture(self.content.fileLocation) 
            self.content.Extract_timer.start()

            if self.content.BtnToggle:
                self.content.Extract_timer.stop()
                self.content.BtnToggle = False
                self.content.extractbtn.setIcon(QIcon(self.content.play_icon))

            else: 
                self.content.BtnToggle = True
                self.content.extractbtn.setIcon(QIcon(self.content.pause_iconplay_icon))

    def resize(self):
        #source_path = self.content.Path[0:-9] + "/AI_Tools/Extract_Image/"
        source_path = r"D:\\PoseEval  Image\\New Exhuast Dataset\\"
        dirs = os.listdir(source_path)
        print("Start Resize at dirs = ", dirs)

        #dest_path = self.content.Path[0:-9] + "/AI_Module/yolo_training/custom_dataset/"
        dest_path = r"D:\\PoseEval  Image\\New Exhuast Dataset\\custom_dataset\\"

        now = datetime.datetime.now()
        timeString = now.strftime("%H%M%S")

        i = 0 
        for item in dirs:
            if os.path.isfile(source_path+item):
                im = Image.open(source_path+item)
                f, e = os.path.splitext(source_path+item)
                imResize = im.resize((640,480), Image.ANTIALIAS)
                imResize.save(dest_path + 'Image_' + str(int(timeString)/5) + str(i)+ '.jpg', 'JPEG', quality=90)
                i=i+1
                debug = "done to resize image " + str(i)
                print(debug)
                self.payload['destfolder'] = debug
                self.evalImplementation()

        self.content.lblResult.setText("Rescale Done")
        self.operation_delete()

    def extract_frame(self):

        if self.content.BtnToggle:
            # reading from frame 
            ret,frame = self.cam.read() 
        
            if ret: 
                # if video is still left continue creating images 
                
                # writing the extracted images with even number
                if self.currentframe%2 == 0:
                    #name = self.content.Path[0:-9] + '/AI_Tools/Extract_Image/img' + str(self.currentframe) + '.jpg'
                    name = r"D:\\PoseEval  Image\\New Exhuast Dataset\\" + str(self.currentframe) + '.jpg'
                    print ('Creating... ' + name) 
                    cv2.imwrite(name, frame) 

                    self.payload['destfolder'] = name
                    self.evalImplementation()
        
                # increasing counter so that it will 
                # show how many frames are created 
                self.content.lblResult.setText(str(self.currentframe))
                self.currentframe += 1
            else: 
                self.content.lblResult.setText("Extract Done")
                self.content.Extract_timer.stop()
                self.content.BtnToggle = False
                self.resize()

    def operation_delete(self):
        print("Delete All file in folder")

        #src = self.content.Path[0:-9] + "/AI_Tools/Extract_Image"
        src = r"D:\\PoseEval  Image\\New Exhuast Dataset\\"

        fileImagelist = [ f for f in os.listdir(src) if f.endswith(".jpg") ]
        for f in fileImagelist:
            os.remove(os.path.join(src, f))

        self.content.lblResult.setText("Process Done")
        
        self.payload['prepdataset'] = 'done'