from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import datetime

import sys
import logging
import declxml as xml

import shutil
import cv2

import time

class ObjectDataset(QDMNodeContentWidget):
    def initUI(self):
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.save_icon = self.Path + "/icons/icons_save.png"
        self.dataset_image = self.Path + "/icons/icons_dataset_conv"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"

        self.Data = None
    
        #====================================================
        # Database Image
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(80,80)
        self.graphicsView.setGeometry(QtCore.QRect(40, 15, 80, 80))

        img = QPixmap(self.dataset_image)
        self.pixmap.setPixmap(img)

        #=====================================================
        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,2,105,20)
        self.lbl.setStyleSheet("font-size:6pt;")

        self.SwitchAnnotation = QPushButton(self)
        self.SwitchAnnotation.setGeometry(108,5,37,20)
        self.SwitchAnnotation.setIcon(QIcon(self.off_icon))
        self.SwitchAnnotation.setIconSize(QtCore.QSize(37,20))
        self.SwitchAnnotation.setStyleSheet("background-color: transparent; border: 0px; font-size:6pt;")  
        
        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(5,75,20,20)
        self.browsFiles.setIcon(QIcon(self.save_icon))
        self.browsFiles.setVisible(False)

        self.lblPath = QLabel("Path:" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(10,80,120,20)
        self.lblPath.setStyleSheet("color: white; font-size:5pt;")

        self.cntImage = QLabel("0" , self)
        self.cntImage.setAlignment(Qt.AlignLeft)
        self.cntImage.setGeometry(110,62,40,20)
        self.cntImage.setStyleSheet("color: lightblue; font-size:6pt;")

        self.lblIn1 = QLabel("Yolo" , self)
        self.lblIn1.setAlignment(Qt.AlignLeft)
        self.lblIn1.setGeometry(10,30,35,20)
        self.lblIn1.setStyleSheet("font-size:6pt;")

        self.lblIn2 = QLabel("Img" , self)
        self.lblIn2.setAlignment(Qt.AlignLeft)
        self.lblIn2.setGeometry(10,52,65,20)
        self.lblIn2.setStyleSheet("font-size:6pt;")

        self.lblfrom = QLabel("Conf" , self)
        self.lblfrom.setAlignment(Qt.AlignLeft)
        self.lblfrom.setGeometry(110,25,35,20)
        self.lblfrom.setStyleSheet("font-size:6pt;")

        self.ConFedit = QLineEdit("60", self)
        self.ConFedit.setGeometry(110,42,30,20)
        self.ConFedit.setPlaceholderText("60%")

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(125,78,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.StartProcessDetect_flag = False
        self.custom_path = None

        self.folderName = "Annotation_dataset"
        self.fileLocation = ""

        self.YoloFormat = "yolov5"
        self.Yolo_obj_found = 0
        self.Yolo_boxes = []
        self.autolabel_folder = ""
        self.autolabel_class_location = ""
        self.classes_data = None

        self.classes_data_dict = {}

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        # setting Message box window title
        self.msg.setWindowTitle("No Dataset Folder !!!")
        
        # declaring buttons on Message Box
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def serialize(self):
        res = super().serialize()
        res['datasetpath'] = self.lblPath.text()
        res['autoannotate'] = self.StartProcessDetect_flag
        res['foldername'] = self.folderName
        res['yoloformat'] = self.YoloFormat
        res['autolabel_folder'] = self.autolabel_folder
        res['autolabel_class_location'] = self.autolabel_class_location
        res['conf'] = self.ConFedit.text()

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            #self.allowtrain = data['allowtrain']
            if 'datasetpath' in data:
                self.lblPath.setText(str(data['datasetpath']))

            if 'foldername' in data:
                self.folderName = data['foldername']

            if 'yoloformat' in data:
                self.YoloFormat = data['yoloformat']

            if 'conf' in data:
                self.ConFedit.setText(data['conf'])

            if 'autolabel_folder' in data:
                self.autolabel_folder = data['autolabel_folder']
                self.lblPath.setStyleSheet("color: lightgreen; font-size:5pt;")
                self.lblPath.setText("Path: " + self.autolabel_folder)

            if 'autolabel_class_location' in data:
                self.autolabel_class_location = data['autolabel_class_location']

                if len(self.autolabel_folder) > 0 and len(self.autolabel_class_location) > 0:
                    self.lblPath.setStyleSheet("color: lightgreen; font-size:5pt;")
                    self.lblPath.setText("Path: " + self.autolabel_folder)

            if 'autoannotate' in data:
                self.StartProcessDetect_flag = data['autoannotate'] 
                if self.StartProcessDetect_flag:
                    self.SwitchAnnotation.setIcon(QIcon(self.on_icon))
                    if os.path.isfile(self.autolabel_folder + "/classes.txt"):
                        os.remove(self.autolabel_folder + "/classes.txt")
                    else:
                        shutil.copy(self.autolabel_class_location, self.autolabel_folder + "/classes.txt")
                        # Initialize an empty list to store the data
                        class_data_list = []

                        # Open the file and read it line by line
                        with open(self.autolabel_folder + "/classes.txt", "r") as file:
                            for line in file:
                                # Remove leading and trailing whitespaces, and add it to the list
                                class_data_list.append(line.strip())

                        # Now, class_data_list contains the data from the file as a list
                        self.classes_data = class_data_list
                        print(type(self.classes_data))

                        self.classes_data_dict = {item: index for index, item in enumerate(self.classes_data)}
                        print("self.classes_data_dict :", self.classes_data_dict)
                        
                else:
                    self.SwitchAnnotation.setIcon(QIcon(self.off_icon))

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def browseSlot(self):
        self.fileLocation = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.fileLocation = ", self.fileLocation)

        self.lblPath.setText(self.fileLocation)
        self.folderSplitName = self.fileLocation.split("/")
        print("len(self.folderName)= ", len(self.folderSplitName))
        self.folderName = self.folderSplitName[len(self.folderSplitName) - 1]

        print("self.folderName = ", self.folderName)

#==========================================================================================
#==========================================================================================
class ObjectMapper(object):
    def __init__(self):
        self.processor = xml.user_object("annotation", Annotation, [
            xml.user_object("size", Size, [
                xml.integer("width"),
                xml.integer("height"),
            ]),
            xml.array(
                xml.user_object("object", Object, [
                    xml.string("name"),
                    xml.user_object("bndbox", Box, [
                        xml.integer("xmin"),
                        xml.integer("ymin"),
                        xml.integer("xmax"),
                        xml.integer("ymax"),
                    ], alias="box")
                ]),
                alias="objects"
            ),
            xml.string("filename")
        ])

    def bind(self, xml_file_path, xml_dir):
        ann = xml.parse_from_file(self.processor, xml_file_path=os.path.join(xml_dir, xml_file_path))
        ann.filename = xml_file_path
        return ann

    def bind_files(self, xml_file_paths, xml_dir):
        result = []
        for xml_file_path in xml_file_paths:
            try:
                result.append(self.bind(xml_file_path=xml_file_path, xml_dir=xml_dir))
            except Exception as e:
                logging.error("%s", e.args)
        return result


class Annotation(object):
    def __init__(self):
        self.size = None
        self.objects = None
        self.filename = None

    def __repr__(self):
        return "Annotation(size={}, object={}, filename={})".format(self.size, self.objects, self.filename)


class Size(object):
    def __init__(self):
        self.width = None
        self.height = None

    def __repr__(self):
        return "Size(width={}, height={})".format(self.width, self.height)


class Object(object):
    def __init__(self):
        self.name = None
        self.box = None

    def __repr__(self):
        return "Object(name={}, box={})".format(self.name, self.box)


class Box(object):
    def __init__(self):
        self.xmin = None
        self.ymin = None
        self.xmax = None
        self.ymax = None

    def __repr__(self):
        return "Box(xmin={}, ymin={}, xmax={}, ymax={})".format(self.xmin, self.ymin, self.xmax, self.ymax)

class Reader(object):
    def __init__(self, xml_dir):
        self.xml_dir = xml_dir

    def get_xml_files(self):
        xml_filenames = []
        for root, subdirectories, files in os.walk(self.xml_dir):
            for filename in files:
                if filename.endswith(".xml"):
                    file_path = os.path.join(root, filename)
                    file_path = os.path.relpath(file_path, start=self.xml_dir)
                    xml_filenames.append(file_path)    
        return xml_filenames

    @staticmethod
    def get_classes(filename):
        with open(os.path.join(os.path.dirname(os.path.realpath('__file__')), filename), "r", encoding="utf8") as f:
            lines = f.readlines()
            return {value: key for (key, value) in enumerate(list(map(lambda x: x.strip(), lines)))}

### Sorce:
### https://github.com/isabek/XmlToTxt

# ========================================================================
# ========================================================================

class Convert_xml2txt(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class Convert_xml2txt ---> Object Convert_xml2txt Function')

        self.content = content
        self.xml_dir = ""
        self.out_dir = ""
        self.class_file = ""

        self.YoloFormat = self.content.YoloFormat

        self.file_number = 0

        self.title = "Convert xml to txt"
        self.top    = 300
        self.left   = 600
        self.width  = 950
        self.height = 550
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.browsFiles = QPushButton(self)
        self.browsFiles.setGeometry(10,10,20,20)
        self.browsFiles.setIcon(QIcon(self.content.save_icon))
        self.browsFiles.clicked.connect(self.content.browseSlot)

        self.lblPath = QLabel("Path:" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(30,10,250,20)
        self.lblPath.setStyleSheet("font-size:6pt;")

        self.lblPath.setText(self.content.fileLocation)

        self.Convert_XML = QPushButton("Convert XML to TXT", self)
        self.Convert_XML.setGeometry(10,50,150,30)
        self.Convert_XML.clicked.connect(self.Convert_xml_txt)

        self.checkAuto = QCheckBox("Auto Convert xml to txt",self)
        self.checkAuto.setGeometry(170,55,100,20)
        self.checkAuto.setStyleSheet("color: #FC03C7; font-size:6pt;")

        self.checkYoloV3V4 = QCheckBox("Yolo V3/V4",self)
        self.checkYoloV3V4.setGeometry(10,85,200,20)
        self.checkYoloV3V4.setStyleSheet("color: lightblue; font-size:8pt;")
        self.checkYoloV3V4.stateChanged.connect(self.SelectYoloV4)

        self.checkYoloV5V8 = QCheckBox("Yolo V5/V8",self)
        self.checkYoloV5V8.setGeometry(10,110,200,20)
        self.checkYoloV5V8.setStyleSheet("color: yellow; font-size:8pt;")
        self.checkYoloV5V8.stateChanged.connect(self.SelectYoloV5)

        if self.YoloFormat  == "yolov5":
            self.checkYoloV5V8.setChecked(True)
            self.checkYoloV3V4.setChecked(False)

        else:
            self.checkYoloV5V8.setChecked(False)
            self.checkYoloV3V4.setChecked(True)

        # ==============================================================
        self.lblPath = QLabel("Setting Auto Label:" , self)
        self.lblPath.setAlignment(Qt.AlignLeft)
        self.lblPath.setGeometry(30,155,360,30)
        self.lblPath.setStyleSheet("color: lightgreen; font-size:8pt;")

        self.browseLabelFiles = QPushButton(self)
        self.browseLabelFiles.setGeometry(10,200,20,20)
        self.browseLabelFiles.setIcon(QIcon(self.content.save_icon))
        self.browseLabelFiles.clicked.connect(self.browseLabelFolder)

        self.lblPathFolder = QLabel("Label Path:" , self)
        self.lblPathFolder.setAlignment(Qt.AlignLeft)
        self.lblPathFolder.setGeometry(40,200,350,20)
        self.lblPathFolder.setStyleSheet("font-size:7pt;")
        if len(self.content.autolabel_folder) > 0:
            self.lblPathFolder.setText("Label Path: " + self.content.autolabel_folder)

        self.browseLabelClass = QPushButton(self)
        self.browseLabelClass.setGeometry(10,230,20,20)
        self.browseLabelClass.setIcon(QIcon(self.content.save_icon))
        self.browseLabelClass.clicked.connect(self.browseLabelClassFile)

        self.lblPathClass = QLabel("Class Path:" , self)
        self.lblPathClass.setAlignment(Qt.AlignLeft)
        self.lblPathClass.setGeometry(40,230,350,20)
        self.lblPathClass.setStyleSheet("font-size:7pt;")
        if len(self.content.autolabel_class_location) > 0:
            self.lblPathClass.setText("Class Path: " + self.content.autolabel_class_location)

        
        self.ObjDetect = QLineEdit("5", self)
        self.ObjDetect.setGeometry(40,270,100,20)
        self.ObjDetect.setPlaceholderText("Limit")

        # ==============================================================
    def browseLabelFolder(self):
        self.content.autolabel_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print("self.content.autolabel_folder = ", self.content.autolabel_folder)
        self.lblPathFolder.setText("Label Path: " + self.content.autolabel_folder)

    def browseLabelClassFile(self):
        self.content.autolabel_class_location = str(QFileDialog.getExistingDirectory(self, "Select Directory")) + "/classes.txt"
        print("self.content.autolabel_class_location = ", self.content.autolabel_class_location)
        self.lblPathClass.setText("Class Path: " + self.content.autolabel_class_location)

        if os.path.isfile(self.content.autolabel_folder + "/classes.txt"):
            os.remove(self.content.autolabel_folder + "/classes.txt")
        else:
            shutil.copy(self.content.autolabel_class_location, self.content.autolabel_folder + "/classes.txt")

            # Initialize an empty list to store the data
            class_data_list = []

            # Open the file and read it line by line
            with open(self.content.autolabel_class_location, "r") as file:
                for line in file:
                    # Remove leading and trailing whitespaces, and add it to the list
                    class_data_list.append(line.strip())

            # Now, class_data_list contains the data from the file as a list
            self.content.classes_data = class_data_list
            print("Convert_xml2txt ==> self.content.classes_data :", self.content.classes_data)
            print(type(self.content.classes_data))

            self.content.classes_data_dict = {item: index for index, item in enumerate(self.content.classes_data)}
            print("Update None Type to ==> self.classes_data_dict :", self.content.classes_data_dict)

    def SelectYoloV4(self, state):
        if state == QtCore.Qt.Checked:
            self.content.YoloFormat = "yolov4"
            self.checkYoloV5V8.setChecked(False)

    def SelectYoloV5(self, state):
        if state == QtCore.Qt.Checked:
            self.content.YoloFormat = "yolov5"
            self.checkYoloV3V4.setChecked(False)

    # ===================================================================

    def Convert_xml_txt(self):

        self.xml_dir = self.content.fileLocation
        print("self.xml_dir = ", self.xml_dir)
        if not os.path.exists(self.xml_dir):
            print("Provide the correct folder for xml files.")
            sys.exit()

        self.out_dir = self.content.fileLocation
        print("self.out_dir = ", self.out_dir)
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        if not os.access(self.out_dir, os.W_OK):
            print("%s folder is not writeable." % self.out_dir)
            sys.exit()
        
        # print("Convert_xml_txt : Path = ", self.content.Path[0:-9])
        # shutil.copy(self.content.Path[0:-9] + "/AI_Tools/data/predefined_classes.txt", self.content.fileLocation + "/classes.txt") # complete target filename given

        self.class_file = self.content.fileLocation +  "/classes.txt"
        print("self.class_file = ", self.class_file)

        print()

        if not os.access(self.class_file, os.F_OK):
            print("%s file is missing." % self.class_file)
            # sys.exit()

        if not os.access(self.class_file, os.R_OK):
            print("%s file is not readable." % self.class_file)
            sys.exit()
        
        #transformer = Transformer(xml_dir=xml_dir, out_dir=out_dir, class_file=class_file)
        self.transform()

    def transform(self):
        reader = Reader(xml_dir=self.xml_dir)
        print("reader = ", reader)
        print()

        self.xml_files = reader.get_xml_files()
        #print("xml_files = ", xml_files)
        #print()

        self.classes = reader.get_classes(self.class_file)
        print("classes = ", self.classes)
        print()

        object_mapper = ObjectMapper()
        annotations = object_mapper.bind_files(self.xml_files, xml_dir=self.xml_dir)
        self.write_to_txt(annotations, self.classes)
        self.content.msg.setText(
            "Convert xml to txt \n Completed !!!")

        retval = self.content.msg.exec_()
        print("retval = ", retval)

    def write_to_txt(self, annotations, classes):
        for annotation in annotations:
            output_path = os.path.join(self.out_dir, self.darknet_filename_format(annotation.filename))
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path))
            with open(output_path, "w+") as f:
                f.write(self.to_darknet_format(annotation, classes))

    def to_darknet_format(self, annotation, classes):
        result = []
        
        for obj in annotation.objects:
            if obj.name not in classes:
                print("Please, add: ", obj.name ," to classes.txt file. found in file name: ", self.xml_files[self.file_number])
                self.content.msg.setText(
                    "Please, add: "+ obj.name +" to classes.txt file. \nfound in file name: "+ self.xml_files[self.file_number])

                retval = self.content.msg.exec_()
                print("retval = ", retval)

                if retval == 1024:
                    exit()

                else:
                    continue

            x, y, width, height = self.get_object_params(obj, annotation.size)
            result.append("%d %.6f %.6f %.6f %.6f" % (classes[obj.name], x, y, width, height))
            
        self.file_number += 1
        print("self.file_number = ", self.file_number)

        return "\n".join(result)

    @staticmethod
    def get_object_params(obj, size):
        image_width = 1.0 * size.width
        image_height = 1.0 * size.height

        box = obj.box
        absolute_x = box.xmin + 0.5 * (box.xmax - box.xmin)
        absolute_y = box.ymin + 0.5 * (box.ymax - box.ymin)

        absolute_width = box.xmax - box.xmin
        absolute_height = box.ymax - box.ymin

        x = absolute_x / image_width
        y = absolute_y / image_height
        width = absolute_width / image_width
        height = absolute_height / image_height

        return x, y, width, height

    @staticmethod
    def darknet_filename_format(filename):
        pre, ext = os.path.splitext(filename)
        return "%s.txt" % pre
    

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 1, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(10, 145, 390, 145)
        painter.drawLine(400, 10, 400, 460)

    #================================================
    #Close Convert XML Setting ---> Save Check Point
    def closeEvent(self, event):
        if len(self.content.autolabel_folder) > 0 and len(self.content.autolabel_class_location) > 0:
            self.content.lblPath.setStyleSheet("color: lightgreen; font-size:5pt;")
            self.content.lblPath.setText("Path: " + self.content.autolabel_folder)

            if os.path.isfile(self.content.autolabel_folder + "/classes.txt"):
                os.remove(self.content.autolabel_folder + "/classes.txt")
            else:
                shutil.copy(self.content.autolabel_class_location, self.content.autolabel_folder + "/classes.txt")

                # Initialize an empty list to store the data
                class_data_list = []

                # Open the file and read it line by line
                with open(self.content.autolabel_folder + "/classes.txt", "r") as file:
                    for line in file:
                        # Remove leading and trailing whitespaces, and add it to the list
                        class_data_list.append(line.strip())

                # Now, class_data_list contains the data from the file as a list
                self.content.classes_data = class_data_list
                print(type(self.content.classes_data))

                self.content.classes_data_dict = {item: index for index, item in enumerate(self.content.classes_data)}
                print("Update None Type to ==> self.classes_data_dict :", self.content.classes_data_dict)

        self.content.SettingBtn.setEnabled(True)
        print("Close Convert XML Setting is closed !!!")

# =====================================================================================
# =====================================================================================
@register_node(OP_NODE_OBJDATASET)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_object_icon.png"
    op_code = OP_NODE_OBJDATASET
    op_title = "Obj AutoLabel"
    content_label_objname = "Obj AutoLabel"

    def __init__(self, scene):
        super().__init__(scene, inputs=[5], outputs=[2]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

        self.FirstInput = False
        self.timeString = ""

        self.i = 0
        self.dataAnnotation_path = ""

        self.new_payload = {}
        self.rx_payload_1 = {}
        self.rx_payload_2 = {}

        self.input_yolo_payload = {}
        self.input_img_payload = {}

        self.label_data = ""
        self.on_process = False

    def initInnerClasses(self):
        self.content = ObjectDataset(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        self.content.SwitchAnnotation.clicked.connect(self.StartAnnotation)
        self.content.browsFiles.clicked.connect(self.content.browseSlot)

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

    def evalImplementation(self):                 # <
        # Input CH1 Yolo Obj Found and Yolo Boxes
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.input_yolo_payload = input_node.eval()

            if self.input_yolo_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            elif type(self.input_yolo_payload) != type(None):
                if 'obj_found' in self.input_yolo_payload:
                    self.content.Yolo_obj_found = self.input_yolo_payload['obj_found']

                if 'yolo_boxes' in self.input_yolo_payload:
                    self.content.Yolo_boxes = self.input_yolo_payload['yolo_boxes']
                        
                if 'img' in self.input_yolo_payload:
                    if type(self.content.classes_data) != type(None) and len(self.content.classes_data) > 0:
                        if len(self.content.autolabel_folder) > 0 and self.content.StartProcessDetect_flag:
                            if self.content.Yolo_obj_found > 0:
                                img_h, img_w = self.input_yolo_payload['img'].shape[:2]
                                self.YoloV5_AutoAnnotation(self.input_yolo_payload, self.content.classes_data_dict, str(self.content.autolabel_folder), img_w, img_h)
                        else:
                            self.content.lblPath.setStyleSheet("color: red; font-size:5pt;")
                            self.content.lblPath.setText("Path: No seleted !!!")

                    else:
                        print("self.content.classes_data is None Type")
                        if len(self.content.autolabel_folder) > 0 and len(self.content.autolabel_class_location) > 0:
                            shutil.copy(self.content.autolabel_class_location, self.content.autolabel_folder + "/classes.txt")

                            # Initialize an empty list to store the data
                            class_data_list = []

                            # Open the file and read it line by line
                            with open(self.content.autolabel_folder + "/classes.txt", "r") as file:
                                for line in file:
                                    # Remove leading and trailing whitespaces, and add it to the list
                                    class_data_list.append(line.strip())

                            # Now, class_data_list contains the data from the file as a list
                            self.content.classes_data = class_data_list
                            print(type(self.content.classes_data))

                            self.content.classes_data_dict = {item: index for index, item in enumerate(self.content.classes_data)}
                            print("Update None Type to ==> self.classes_data_dict :", self.content.classes_data_dict)

                            self.content.lblPath.setStyleSheet("color: lightgreen; font-size:5pt;")
                            self.content.lblPath.setText("Path: " + self.content.autolabel_folder)
                                        
                        else:
                            self.content.lblPath.setStyleSheet("color: red; font-size:5pt;")    
                            
                            
        # input_node_1 = self.getInput(0)
        # if not input_node_1:
        #     self.grNode.setToolTip("Input is not connected")
        #     self.markInvalid()

        # else:
        #     self.rx_payload_1 = input_node_1.eval()
            
        # input_node_2 = self.getInput(1)
        # if not input_node_2:
        #     self.grNode.setToolTip("Input is not connected")
        #     self.markInvalid()

        # else:
        #     self.rx_payload_2 = input_node_2.eval()

        # if self.rx_payload_1 is None and self.rx_payload_2 is None:
        #     self.grNode.setToolTip("Input is NaN")
        #     self.markInvalid()
        #     return

        # else:
        #     if self.rx_payload_1 and self.rx_payload_2:
        #         if 'img' in self.rx_payload_2:
        #             self.rx_payload_2.pop('img')

        #         if type(self.rx_payload_1) is dict and type(self.rx_payload_2) is dict:
        #             self.new_payload = {**self.rx_payload_1, **self.rx_payload_2} 
            
        #     else:
        #         #self.rx_payload_2 is Empty
        #         self.new_payload = self.rx_payload_1

        #     # Operate Process Here !!!!!
        #     if 'img' in self.rx_payload_1:
        #         if len(str(self.rx_payload_1['img'])) > 100:
        #             #print("val['img'] = ", val['img'])
        #             if 'blink' in self.rx_payload_1:
        #                 if self.rx_payload_1['blink'] == True:
        #                     self.content.lbl.setText("<font color=#00FF00>-> Image Input</font>")
        #                 else:
        #                     self.content.lbl.setText("")

        #             if self.content.StartProcessDetect_flag:

        #                 if not self.FirstInput:
        #                     self.start_record = datetime.datetime.now()
        #                     self.timeString = self.start_record.strftime("%Y_%m_%d_%H%M%S")
        #                     print("self.timeString= ", self.timeString)

        #                     self.FirstInput = True

        #                 if 'run' in self.rx_payload_1:
        #                     if self.rx_payload_1['run']:
        #                         if 'yolo_boxes' in self.rx_payload_2:
        #                             if self.rx_payload_2['yolo_boxes']:
        #                                 if int(self.rx_payload_2['obj_found']) > 0:
        #                                     # if self.content.YoloFormat == "yolov5":
        #                                     #     self.YoloV5_AutoAnnotation()
        #                                     # else:
        #                                     self.Auto_Annotation_Function()

        #                     else:
        #                         #print("Stop to Extract")
        #                         self.FirstInput = False

        #                         self.i = 0

        #                         self.payload['result'] = "STOP"

        #                 if 'clock' in self.rx_payload_1:
        #                     if self.rx_payload_1['clock']:
        #                         if 'yolo_boxes' in self.rx_payload_2:
        #                             if self.rx_payload_2['yolo_boxes']:
        #                                 if int(self.rx_payload_2['obj_found']) > 0:
        #                                     # if self.content.YoloFormat == "yolov5":
        #                                     #     self.YoloV5_AutoAnnotation()
        #                                     # else:
        #                                     self.Auto_Annotation_Function()

        #                     else:
        #                         #print("Stop to Extract")
        #                         self.FirstInput = False

        #                         self.i = 0

        #                         self.payload['result'] = "STOP"

    def YoloV5_AutoAnnotation(self, payload, classes_data_dict, folder, img_width, img_height):
        # Create a text file for YOLOv5 labels
        txt_filename = folder + "/Image_" + str(datetime.datetime.now().strftime("%d_%m_%Y_%H%M%S")) + ".txt"
        # print("txt_filename :", txt_filename)
        with open(txt_filename, "w") as file:
            for box_info in payload['yolo_boxes']:
                x1, y1, x2, y2 = box_info['x1'], box_info['y1'], box_info['x2'], box_info['y2']
                obj_class = box_info['obj']

                # Convert class name to class index
                if obj_class in classes_data_dict:
                    class_idx = classes_data_dict[obj_class]
                else:
                    class_idx = -1  # Class not found

                # Write label information to the file
                if class_idx >= 0:
                    label_line = f"{class_idx} {((x1 + x2) / 2) / img_width:.6f} {((y1 + y2) / 2) / img_height:.6f} " \
                                 f"{(x2 - x1) / img_width:.6f} {(y2 - y1) / img_height:.6f}\n"
                    file.write(label_line)

        # Save the corresponding image
        img_filename = folder+ "/Image_" + str(datetime.datetime.now().strftime("%d_%m_%Y_%H%M%S")) + '.png'
        # print("img_filename :", img_filename)
        cv2.imwrite(img_filename, payload['img'])

    def StartAnnotation(self):
        if not self.content.StartProcessDetect_flag:
            self.content.SwitchAnnotation.setIcon(QIcon(self.content.on_icon))
            if not os.path.isfile(self.content.autolabel_folder + "/classes.txt"):
                shutil.copy(self.content.autolabel_class_location, self.content.autolabel_folder + "/classes.txt")

                # Initialize an empty list to store the data
                class_data_list = []

                # Open the file and read it line by line
                with open(self.content.autolabel_folder + "/classes.txt", "r") as file:
                    for line in file:
                        # Remove leading and trailing whitespaces, and add it to the list
                        class_data_list.append(line.strip())

                # Now, class_data_list contains the data from the file as a list
                self.content.classes_data = class_data_list
                print(type(self.content.classes_data))

                self.content.classes_data_dict = {item: index for index, item in enumerate(self.content.classes_data)}
                print("Update None Type to ==> self.classes_data_dict :", self.content.classes_data_dict)

                self.content.lblPath.setStyleSheet("color: lightgreen; font-size:5pt;")
                self.content.lblPath.setText("Path: " + self.content.autolabel_folder)
        else:
            self.content.SwitchAnnotation.setIcon(QIcon(self.content.off_icon))
            self.FirstInput = False

            self.i = 0
            self.content.cntImage.setText(str(int(self.i))) 

        self.content.StartProcessDetect_flag = not self.content.StartProcessDetect_flag

    # Annotation YoloV3 V4 with XML File
    def Auto_Annotation_Function(self):
        self.i += 1
        compensate_1 = 0
        compensate_2 = 2

        if self.i%5 == 0: 
            #print("Extract image from video, self.i = ", self.i)

            if os.path.isdir(self.content.lblPath.text()):
                self.dataAnnotation_path = self.content.lblPath.text() + '/Image_' + str(self.timeString) + "_" + str(self.i)

                cv2.imwrite(self.dataAnnotation_path + '.png', self.new_payload['img'])
                self.content.cntImage.setText(str(int(self.i/5))) 

                if not os.path.isfile(self.dataAnnotation_path + '.xml'):
                    AutoAnnotation_Data = "<annotation>\n\t<folder>" + str(self.content.folderName) + "</folder>" + \
                        "\n\t<filename>Image_" + str(self.timeString) + "_" + str(self.i) + ".png</filename>" + \
                        "\n\t<path>" + self.dataAnnotation_path + ".png</path>" + \
                        "\n\t<source>" + \
                        "\n\t\t<database>Unknown</database>" + \
                        "\n\t</source>" + \
                        "\n\t<size>" + \
                        "\n\t\t<width>640</width>" + \
                        "\n\t\t<height>480</height>" + \
                        "\n\t\t<depth>3</depth>" + \
                        "\n\t</size>" + \
                        "\n\t<segmented>0</segmented>"

                    OBJ_Annotation_Data = ""
                    for i in range(int(self.new_payload['obj_found'])):
                        OBJ_Annotation_Data = OBJ_Annotation_Data + "\n\t<object>" + \
                            "\n\t\t<name>" + str(self.new_payload['yolo_boxes'][i]['obj']) + "</name>" + \
                            "\n\t\t<pose>Unspecified</pose>" + \
                            "\n\t\t<truncated>0</truncated>" + \
                            "\n\t\t<difficult>0</difficult>" + \
                            "\n\t\t<bndbox>" + \
                            "\n\t\t\t<xmin>"+ str(int(self.new_payload['yolo_boxes'][i]['x1']  - compensate_1 )) + "</xmin>" + \
                            "\n\t\t\t<ymin>" + str(int(self.new_payload['yolo_boxes'][i]['y1'] - compensate_1 )) + "</ymin>" + \
                            "\n\t\t\t<xmax>" + str(int(self.new_payload['yolo_boxes'][i]['x2'] + compensate_2 )) + "</xmax>" + \
                            "\n\t\t\t<ymax>" + str(int(self.new_payload['yolo_boxes'][i]['y2'] + compensate_2 )) + "</ymax>" + \
                            "\n\t\t</bndbox>" + \
                            "\n\t</object>"

                    AutoAnnotation_Data = AutoAnnotation_Data + OBJ_Annotation_Data + "\n</annotation>"

                    #print("AutoAnnotation_Data = ", AutoAnnotation_Data)

                    file = open(self.dataAnnotation_path + '.xml','w')
                    file.write(AutoAnnotation_Data)
                    file.close()

            self.payload['result'] = "EXTRACT"

    def OnOpen_Setting(self):
        # if len(self.content.fileLocation) > 0:

        self.content.SettingBtn.setEnabled(False)
        self.Convert_xml2txt = Convert_xml2txt(self.content)
        self.Convert_xml2txt.show()

        # else:
        #     print ("Not select folder file location")
        #     self.content.msg.setText(
        #             "Not select folder \nfile location")

        #     retval = self.content.m



