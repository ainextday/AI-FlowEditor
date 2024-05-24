from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
import GPUtil

import numpy as np
import tensorflow as tf

#from ai_application.AI_Module.yolo.yolov3 import Create_Yolov3
from ai_application.AI_Module.yolo.yolov4 import Create_Yolo
from ai_application.AI_Module.yolo.utils import detect_video, Load_Yolo_model
import ai_application.AI_Module.yolo.configs as YoloConfig

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

from os import listdir
from os.path import isfile, join

import cv2

class ObjectDetectCustom(QDMNodeContentWidget):
    def initUI(self):

        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.save_icon = self.Path + "/icons/icons_save.png"
        self.animate_movie = self.Path + "/icons/icons_dane_re.gif"
        self.reload_icon = self.Path + "/icons/icons_refresh.png"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.Data = None

        """#====================================================
        # Database Image
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(75,75)
        self.graphicsView.setGeometry(QtCore.QRect(18, 15, 105, 75))

        img = QPixmap(self.animate_movie)
        self.pixmap.setPixmap(img)"""

        #====================================================
        # Loading the GIF
        self.labelAnimate = QLabel(self)
        self.labelAnimate.setGeometry(QtCore.QRect(35, 15, 105, 75))
        self.labelAnimate.setMinimumSize(QtCore.QSize(75, 75))
        self.labelAnimate.setMaximumSize(QtCore.QSize(75, 75))

        self.movie = QMovie(self.animate_movie)
        self.labelAnimate.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        self.labelAnimate.setVisible(False)

        #====================================================

        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,2,105,45)
        self.lbl.setStyleSheet("font-size:6pt;")

        self.SwitchDetect = QPushButton(self)
        self.SwitchDetect.setGeometry(108,5,37,20)
        self.SwitchDetect.setIcon(QIcon(self.off_icon))
        self.SwitchDetect.setIconSize(QtCore.QSize(37,20))
        self.SwitchDetect.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lblYoloType = QLabel("" , self)
        self.lblYoloType.setAlignment(Qt.AlignLeft)
        self.lblYoloType.setGeometry(110,30,40,20)
        self.lblYoloType.setStyleSheet("font-size:6pt;")

        self.lblYoloTiny = QLabel("" , self)
        self.lblYoloTiny.setAlignment(Qt.AlignLeft)
        self.lblYoloTiny.setGeometry(110,50,40,20)
        self.lblYoloTiny.setStyleSheet("font-size:6pt;")

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(5,75,20,20)
        self.browsFiles.setIcon(QIcon(self.save_icon))
        self.browsFiles.setEnabled(False)

        self.lblPath = QLabel("Path:" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(30,80,45,20)
        self.lblPath.setStyleSheet("font-size:5pt;")


        self.radioPreWeight = QRadioButton("PreWeight",self)
        self.radioPreWeight.setGeometry(10,25,90,20)
        self.radioPreWeight.setStyleSheet("color: lightblue; font-size:6pt;")
        self.radioPreWeight.setChecked(True)

        self.radioCustom = QRadioButton("Custom",self)
        self.radioCustom.setGeometry(10,50,90,20)
        self.radioCustom.setStyleSheet("color: orange; font-size:6pt;")

        self.selectWightFile = "preweight"

        self.NOF_GPU = GPUtil.getAvailable()

        self.combo = QComboBox(self)
        self.combo.addItem("-1")

        for i in range(len(self.NOF_GPU)):
            self.combo.addItem(str(self.NOF_GPU[i]))

        self.combo.setGeometry(120,75,25,20)
        self.combo.move(120, 75)
        self.combo.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : #33CCFF"
                                   "}") 

        self.lblCPU = QLabel("CPU" , self)
        self.lblCPU.setAlignment(Qt.AlignLeft)
        self.lblCPU.setGeometry(85,80,30,20)
        self.lblCPU.setStyleSheet("font-size:6pt;")

        self.StartProcessDetect_flag = False

        self.custom_path = None
        self.GPUselect = "-1"

        self.fileLocation = ""

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msg.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msg.setStandardButtons(QMessageBox.Ok)

        self.YOLO_TYPE = "yolov4"
        self.TRAIN_YOLO_TINY = True

        self.AutoLoadYolo = False

        self.gpus = tf.config.experimental.list_physical_devices('GPU')
        print(f'\nGPUs = {self.gpus}')
        if len(self.gpus) > 0:
            try: tf.config.experimental.set_memory_growth(self.gpus[0], True)
            except RuntimeError: pass

        self.YOLO_STRIDES = [8, 16, 32]
        self.YOLO_ANCHORS = []

        self.STRIDES = []
        self.ANCHORS = []

        self.yolo = None
        self.TRAIN_CLASSES = None
        self.weightFile_valid_1 = False
        self.weightFile_valid_2 = False

        #==============================================================
        #Detect YoloV4-Tiny PreWeight

        self.Conf_threshold = 0.4
        self.NMS_threshold = 0.4
        self.COLORS = [(255, 255, 0), (255, 0, 255), (0, 255, 255), (124, 252, 0), (0, 255, 255), 
                (255, 51, 102), (204, 51, 255), (51, 153, 255), (51, 255, 255), (51, 255, 51), (204, 255, 51),
                (255, 204, 51), (255, 153, 51), (255, 102, 51), (102, 51, 255), (51, 102, 255)]

        self.class_name = []
        with open(self.Path[0:-9] + '/AI_Module/yolo/model_data/classes.txt', 'r') as f:
            self.class_name = [cname.strip() for cname in f.readlines()]

        net = cv2.dnn.readNet(self.Path[0:-9] + '/AI_Module/yolo/model_data/yolov4-tiny.weights', self.Path[0:-9] + '/AI_Module/yolo/model_data/yolov4-tiny.cfg')
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)


    def serialize(self):
        res = super().serialize()
        res['customepath'] = self.lblPath.text()
        res['selectgpu'] = self.GPUselect

        res['yolotype'] = self.YOLO_TYPE
        res['yolotiny'] = self.TRAIN_YOLO_TINY

        res['autoloadyolo'] = self.AutoLoadYolo
        res['select_weight'] = self.selectWightFile 

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'select_weight' in data:
                self.selectWightFile = data['select_weight']
                print("self.selectWightFile = ", self.selectWightFile)
                if self.selectWightFile == "custom":
                    self.browsFiles.setEnabled(True) 

                    if 'customepath' in data:
                        self.custom_path = data['customepath']
                        print("self.custom_path = ", self.custom_path)
                        self.lblPath.setText(self.custom_path)
                        self.radioCustom.setChecked(True)
                        self.radioPreWeight.setEnabled(False)

                        if self.Load_YoloWeight_file(self.custom_path):
                            if 'autoloadyolo' in data:
                                self.AutoLoadYolo = data['autoloadyolo']
                                print('autoloadyolo = ', self.AutoLoadYolo)

                                if self.AutoLoadYolo:

                                    self.YOLO_TYPE = data['yolotype']
                                    self.lblYoloType.setText(str(self.YOLO_TYPE))

                                    self.TRAIN_YOLO_TINY = data['yolotiny']
                                    if self.TRAIN_YOLO_TINY:
                                        self.lblYoloTiny.setText("Tiny")
                                    else:
                                        self.lblYoloTiny.setText("")

                                    if self.YOLO_TYPE == "yolov4":
                                        self.YOLO_ANCHORS = [[[12,  16], [19,   36], [40,   28]], [[36,  75], [76,   55], [72,  146]], [[142,110], [192, 243], [459, 401]]]
                                    if self.YOLO_TYPE == "yolov3":
                                        self.YOLO_ANCHORS = [[[10,  13], [16,   30], [33,   23]], [[30,  61], [62,   45], [59,  119]], [[116, 90], [156, 198], [373, 326]]]

                                    #YOLOv3-TINY and YOLOv4-TINY WORKAROUND
                                    if self.TRAIN_YOLO_TINY:
                                        self.YOLO_STRIDES = [16, 32, 64]    
                                        self.YOLO_ANCHORS = [[[10,  14], [23,   27], [37,   58]], [[81,  82], [135, 169], [344, 319]], [[0,    0], [0,     0], [0,     0]]]

                                    self.STRIDES = np.array(self.YOLO_STRIDES)
                                    self.ANCHORS = (np.array(self.YOLO_ANCHORS).T/self.STRIDES).T

                                    if YoloConfig.YOLO_FRAMEWORK == "tf":
                                        #weight_path = self.lblPath.text() + "/checkpoints/"+ self.YOLO_TYPE + "_custom_Tiny"
                                        weight_path = self.lblPath.text() + "/"+ self.YOLO_TYPE + "_custom_Tiny"
                                        print("Custom Weight_path = ", weight_path)

                                        #self.TRAIN_CLASSES = self.lblPath.text() + "/checkpoints/dataset_names.txt"
                                        self.TRAIN_CLASSES = self.lblPath.text() + "/dataset_names.txt"
                                        print("TRAIN_CLASSES = ", self.TRAIN_CLASSES)
                                        
                                        self.yolo = Create_Yolo(input_size=YoloConfig.YOLO_INPUT_SIZE, CLASSES=self.TRAIN_CLASSES, 
                                            YOLO_TYPE=self.YOLO_TYPE, TRAIN_YOLO_TINY=self.TRAIN_YOLO_TINY, CY_STRIDES=self.STRIDES, CY_ANCHORS=self.ANCHORS)
                                        self.yolo.load_weights(weight_path)
                                        #yolo = Load_Yolo_model()

                                    print("Start Auto yolo.load_weights = ", self.yolo)

                                    self.SwitchDetect.setIcon(QIcon(self.on_icon))
                                    #self.graphicsView.setVisible(False)

                                    self.labelAnimate.setVisible(True)
                                    self.movie.start()

                                    self.StartProcessDetect_flag = True

                                    self.radioPreWeight.setEnabled(False)
                                    self.radioCustom.setEnabled(False)
                                    self.browsFiles.setEnabled(False)

                                else:
                                    self.SwitchDetect.setIcon(QIcon(self.off_icon))
                                    #self.graphicsView.setVisible(True)

                                    self.labelAnimate.setVisible(False)
                                    self.movie.stop()

                                    self.StartProcessDetect_flag = False

                                    self.radioPreWeight.setEnabled(True)
                                    self.radioCustom.setEnabled(True)
                                    self.browsFiles.setEnabled(True)
            
                else:
                    self.radioPreWeight.setEnabled(True)
                    self.browsFiles.setEnabled(False) 
                    print("Use YoloV4 Tiny Demo PreWeight")
                    
            else:
                self.radioPreWeight.setEnabled(True)
                self.browsFiles.setEnabled(False) 
                print("Use YoloV4 Tiny Demo PreWeight")

            if 'selectgpu' in data:
                self.GPUselect = data['selectgpu']
                if self.GPUselect == "-1":
                    self.lblCPU.setText("CPU")
                else:
                    self.lblCPU.setText("GPU" + self.GPUselect)
            
            return True & res
        except Exception as e:
            dumpException(e)
        return res

    #Select destinate Folder to Save file
    def browseSlot(self):
        self.fileLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.fileLocation)

        self.lblPath.setText(self.fileLocation)
        self.radioCustom.setChecked(True)
        self.selectWightFile = "custom"

    def Load_YoloWeight_file(self, location_path):
        #if os.path.isfile(location_path + "/checkpoints/dataset_names.txt"):
        """if os.path.isfile(location_path + "/dataset_names.txt"):
            self.weightFile_valid_1 = True"""

        """if os.path.exists(location_path + "/checkpoints"):
            self.weightFile_valid_2 = True """
    
        #if self.weightFile_valid_1 and self.weightFile_valid_2:
        if os.path.isfile(location_path + "/dataset_names.txt"):
            #onlyfiles = [f for f in listdir(location_path + "/checkpoints") if isfile(join(location_path + "/checkpoints", f))]
            onlyfiles = [f for f in listdir(location_path) if isfile(join(location_path, f))]
            print("File in folder[2] = ", onlyfiles[2])
            if onlyfiles[2] == "yolov3_custom_Tiny.index":
                self.YOLO_TYPE = "yolov3"
                self.TRAIN_YOLO_TINY = True

            elif onlyfiles[2] == "yolov3_custom.index":
                self.YOLO_TYPE = "yolov3"
                self.TRAIN_YOLO_TINY = False

            elif onlyfiles[2] == "yolov4_custom_Tiny.index":
                self.YOLO_TYPE = "yolov4"
                self.TRAIN_YOLO_TINY = True

            elif onlyfiles[2] == "yolov4_custom.index":
                self.YOLO_TYPE = "yolov4"
                self.TRAIN_YOLO_TINY = False

            print("self.YOLO_TYPE = ", self.YOLO_TYPE)
            self.lblYoloType.setText(str(self.YOLO_TYPE))

            print("self.TRAIN_YOLO_TINY = ", self.TRAIN_YOLO_TINY)
            if self.TRAIN_YOLO_TINY:
                self.lblYoloTiny.setText("Tiny")
            else:
                self.lblYoloTiny.setText("")

            return True

        else:
            print("No weight file in folder")
            self.msg.setText("No weight file in folder")
            retval = self.msg.exec_()

            return False

@register_node(OP_NODE_OBJDETECT_CUSTOM)
class Open_ObjectDetect_Custom(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_object_yolo_icon.png"
    op_code = OP_NODE_OBJDETECT_CUSTOM
    op_title = "YoloV3_V4"
    content_label_objname = "YoloV3_V4"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.reciev_datazero = {}

    def initInnerClasses(self):
        self.content = ObjectDetectCustom(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.SwitchDetect.clicked.connect(self.StartDetecOBJ)
        self.content.combo.activated[str].connect(self.onChangedCPU)

        self.content.browsFiles.clicked.connect(self.content.browseSlot)

        self.content.radioPreWeight.toggled.connect(self.selectPreweight)
        self.content.radioCustom.toggled.connect(self.SelectCustom)

    def evalImplementation(self):                 # <
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.reciev_datazero = input_node.eval()

        if self.reciev_datazero is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return

        else:
            # Operate Process Here !!!!!
            if 'img' in self.reciev_datazero:
                if len(str(self.reciev_datazero['img'])) > 100:
                    
                    if 'inputtype' in self.reciev_datazero:
                        self.payload['inputtype'] = self.reciev_datazero['inputtype']

                    if 'centers' in self.reciev_datazero:
                        self.payload['centers'] = self.reciev_datazero['centers']
                
                    #print("val['img'] = ", val['img'])
                    if 'fps' in self.reciev_datazero:
                        self.payload['fps'] = self.reciev_datazero['fps']

                    if 'clock' in self.reciev_datazero:
                        self.payload['clock'] = self.reciev_datazero['clock']

                    if 'blink' in self.reciev_datazero:
                        if self.reciev_datazero['blink'] == True:
                            self.content.lbl.setText("<font color=#00FF00>-> Image Input</font>")
                        else:
                            self.content.lbl.setText("")
                    
                    if self.content.StartProcessDetect_flag:
                        if self.content.selectWightFile == "custom":
                            if self.content.yolo is not None:
                                self.payload['obj_found'], self.payload['yolo_boxes'], self.payload['img'] = detect_video(self.content.yolo, self.reciev_datazero['img'], '',
                                    input_size=YoloConfig.YOLO_INPUT_SIZE, show=True, CLASSES=self.content.TRAIN_CLASSES, rectangle_colors='')

                        else:
                            self.payload['obj_found'], self.payload['yolo_boxes'], self.payload['img'] = self.detect_yolov4_tiny(self.reciev_datazero['img'])

                    else:
                        self.payload['obj_found'] = 0
                        self.payload['yolo_boxes'] = []
                        self.payload['img'] = self.reciev_datazero['img']
                        
                    
                else:
                    self.content.lbl.setText("<font color='red'>Wrong Input !!!</font>")

        self.value = self.payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value

    def StartDetecOBJ(self):
        self.content.StartProcessDetect_flag = not self.content.StartProcessDetect_flag

        if not self.content.StartProcessDetect_flag:
            self.content.SwitchDetect.setIcon(QIcon(self.content.off_icon))
            #self.content.graphicsView.setVisible(True)

            self.content.labelAnimate.setVisible(False)
            self.content.movie.stop()

            self.content.AutoLoadYolo = False

            self.content.radioPreWeight.setEnabled(True)
            self.content.radioCustom.setEnabled(True)
            self.content.browsFiles.setEnabled(True)

            self.content.yolo = None
            
        else:
            self.content.AutoLoadYolo = True

            print("self.content.GPUselect = ", self.content.GPUselect)
            os.environ['CUDA_VISIBLE_DEVICES'] = self.content.GPUselect

            if self.content.selectWightFile == "custom":

                if self.content.YOLO_TYPE == "yolov4":
                    self.content.YOLO_ANCHORS = [[[12,  16], [19,   36], [40,   28]], [[36,  75], [76,   55], [72,  146]], [[142,110], [192, 243], [459, 401]]]
                if self.content.YOLO_TYPE == "yolov3":
                    self.content.YOLO_ANCHORS = [[[10,  13], [16,   30], [33,   23]], [[30,  61], [62,   45], [59,  119]], [[116, 90], [156, 198], [373, 326]]]

                #YOLOv3-TINY and YOLOv4-TINY WORKAROUND
                if self.content.TRAIN_YOLO_TINY:
                    self.content.YOLO_STRIDES = [16, 32, 64]    
                    self.content.YOLO_ANCHORS = [[[10,  14], [23,   27], [37,   58]], [[81,  82], [135, 169], [344, 319]], [[0,    0], [0,     0], [0,     0]]]

                self.content.STRIDES = np.array(self.content.YOLO_STRIDES)
                self.content.ANCHORS = (np.array(self.content.YOLO_ANCHORS).T/self.content.STRIDES).T
            
                if self.content.Load_YoloWeight_file(self.content.lblPath.text()):
                    self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))
                    #self.content.graphicsView.setVisible(False)

                    self.content.labelAnimate.setVisible(True)
                    self.content.movie.start()

                    if YoloConfig.YOLO_FRAMEWORK == "tf":
                        
                        if self.content.selectWightFile == "custom":
                            #weight_path = self.content.lblPath.text() + "/checkpoints/"+ self.content.YOLO_TYPE + "_custom_Tiny"
                            weight_path = self.content.lblPath.text() + "/"+ self.content.YOLO_TYPE + "_custom_Tiny"
                            print("Custom Weight_path = ", weight_path)

                            #self.content.TRAIN_CLASSES = self.content.lblPath.text() + "/checkpoints/dataset_names.txt"
                            self.content.TRAIN_CLASSES = self.content.lblPath.text() + "/dataset_names.txt"
                            print("TRAIN_CLASSES = ", self.content.TRAIN_CLASSES)
                            
                            self.content.yolo = Create_Yolo(input_size=YoloConfig.YOLO_INPUT_SIZE, CLASSES=self.content.TRAIN_CLASSES, 
                                YOLO_TYPE=self.content.YOLO_TYPE, TRAIN_YOLO_TINY=self.content.TRAIN_YOLO_TINY, CY_STRIDES=self.content.STRIDES, CY_ANCHORS=self.content.ANCHORS)
                            self.content.yolo.load_weights(weight_path)
                            #yolo = Load_Yolo_model()

                        else:
                            print("Click Start Detect by using YoloV4 Tiny Weight")

                    elif YoloConfig.YOLO_FRAMEWORK == "trt":
                        saved_model_loaded = tf.saved_model.load(YoloConfig.YOLO_CUSTOM_WEIGHTS, tags=[YoloConfig.tag_constants.SERVING])
                        print("saved_model_loaded = ", saved_model_loaded)
                        #signature_keys = list(saved_model_loaded.signatures.key())
                        self.content.yolo = saved_model_loaded.signatures['serving_default']

                    else:
                        if self.content.YOLO_TYPE == "yolov4":
                            if self.content.TRAIN_YOLO_TINY:
                                Darknet_weights = YoloConfig.YOLO_V4_TINY_WEIGHTS  
                            else:
                                Darknet_weights = YoloConfig.YOLO_V4_WEIGHTS

                        if self.content.YOLO_TYPE == "yolov3":
                            if self.content.TRAIN_YOLO_TINY:
                                Darknet_weights = YoloConfig.YOLO_V3_TINY_WEIGHTS  
                            else:
                                Darknet_weights = YoloConfig.YOLO_V3_WEIGHTS

                    self.content.radioPreWeight.setEnabled(False)
                    self.content.radioCustom.setEnabled(False)
                    self.content.browsFiles.setEnabled(False)

                else:
                    print("No weight file in folder")
                    self.content.msg.setText("No weight file in folder")
                    retval = self.content.msg.exec_()

                    self.content.radioPreWeight.setEnabled(True)
                    self.content.radioCustom.setEnabled(True)
                    self.content.browsFiles.setEnabled(True)

            else:
                print("Select Yolo V4-Tiny PreWeight")


                self.content.radioPreWeight.setEnabled(False)
                self.content.radioCustom.setEnabled(False)
                self.content.browsFiles.setEnabled(False)

                self.content.SwitchDetect.setIcon(QIcon(self.content.on_icon))
                self.content.labelAnimate.setVisible(True)
                self.content.movie.start()

            print()
            print("Start yolo.load_weights = ", self.content.yolo)

    def onChangedCPU(self, select):
        if select == "-1":
            self.content.lblCPU.setText("CPU")
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            
        for i in range(len(self.content.NOF_GPU)):
            if select == str(self.content.NOF_GPU[i]):
                self.content.lblCPU.setText("GPU" + str(self.content.NOF_GPU[i]))
                
                os.environ['CUDA_VISIBLE_DEVICES'] = str(self.content.NOF_GPU[i])
                from tensorflow.python.client import device_lib
                print("device_list = ", device_lib.list_local_devices())

                gpus = tf.config.experimental.list_physical_devices('GPU')
                print(f'\nGPUs = {gpus}')
                if len(gpus) > 0:
                    try: tf.config.experimental.set_memory_growth(gpus[0], True)
                    except RuntimeError: pass
    
        self.content.GPUselect = str(select)

    def selectPreweight(self, enabled):
        if enabled:
            print("Select YoloV4 Tiny PreWeight")
            self.content.selectWightFile = "preweight"
            self.content.browsFiles.setEnabled(False)

    def SelectCustom(self, enabled):
        if enabled:
            print("SelectCustom Weight")
            self.content.selectWightFile = "custom"
            self.content.browsFiles.setEnabled(True)

    def detect_yolov4_tiny(self, img):
        # Initialize black image of same dimensions for drawing the rectangles
        bgblk = np.zeros(img.shape, np.uint8)

        object_found = 0
        box_address = []

        classes, scores, boxes = self.content.model.detect(img, self.content.Conf_threshold, self.content.NMS_threshold)
        for (classid, score, box) in zip(classes, scores, boxes):
            color = self.content.COLORS[int(classid) % len(self.content.COLORS)]
            label = str(self.content.class_name[classid]) + " : " +str(int(score*100)) + "%"

            # get text size
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                                0.5, thickness=1)
            bgblk = cv2.rectangle(bgblk, box, color, 1)
            img = cv2.addWeighted(img, 1.0, bgblk, 0.5, 1.0)

            # put filled text rectangle
            img = cv2.rectangle(img, (box[0], box[1]), (box[0] + text_width, box[1] - text_height - baseline - 2), color, thickness=cv2.FILLED)
            # put text above rectangle
            img = cv2.putText(img, label, (box[0], box[1]-4), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        0.5, (255, 0, 0), 1, lineType=cv2.LINE_AA)

            object_found += 1

            box_address.append({'x1':box[0], 'y1':box[1], 'x2':box[2], 'y2':box[3], 'score': int(score*100), 'obj':str(self.content.class_name[classid])})
            
        return object_found, box_address, img