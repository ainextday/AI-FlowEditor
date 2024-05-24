from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import os

import cv2
import numpy as np
import tensorflow as tf
from ai_application.AI_Module.yolo.yolov4 import Create_Yolo
from ai_application.AI_Module.yolo.utils import detect_video, Load_Yolo_model
from ai_application.AI_Module.yolo.configs import *

class ObjectDetect(QDMNodeContentWidget):
    def initUI(self):
        
        self.Path = os.path.dirname(os.path.abspath(__file__))
        print("Object Detect self.Path = " , self.Path)
        self.save_icon = self.Path + "/icons/icons_save.png"
        yolo_logo = self.Path + "/icons/icons_mobilenetssd_icon.jpg"

        self.Data = None

        self.inputlbl = QLabel("No Input" , self)
        self.inputlbl.setAlignment(Qt.AlignLeft)
        self.inputlbl.setGeometry(10,10,100,20)

        #====================================================
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(95,80)
        self.graphicsView.setGeometry(QtCore.QRect(15, 20, 125, 85))

        img = QPixmap(yolo_logo)
        self.pixmap.setPixmap(img)

        #=====================================================
        self.ModelPath = self.Path[0:-9] + "/AI_Module/mobilenetssd"
        print("self.YoloPath = ", self.ModelPath)

        self.CLASSES = ["BACKGROUND", "AEROPLANE", "BICYCLE", "BIRD", "BOAT",
                    "BOTTLE", "BUS", "CAR", "CAT", "CHAIR", "COW", "DININGTABLE",
                    "DOG", "HORSE", "MOTORBIKE", "PERSON", "POTTEDPLANT", "SHEEP",
                    "SOFA", "TRAIN", "TVMONITOR"]

        self.COLORS = np.random.uniform(0,255, size=(len(self.CLASSES), 3))
        self.net = cv2.dnn.readNetFromCaffe(self.ModelPath + "/MobileNetSSD.prototxt", self.ModelPath + "/MobileNetSSD.caffemodel")

    def serialize(self):
        res = super().serialize()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data

            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_MOBILENETSSD)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_mobilenetssd.png"
    op_code = OP_NODE_MOBILENETSSD
    op_title = "Obj MobileNet"
    content_label_objname = "Obj MobileNet"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[3,5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.mbn_payload = {}

    def initInnerClasses(self):
        self.content = ObjectDetect(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

    def evalImplementation(self):                 # <
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.mbn_payload  = input_node.eval()

        if self.payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return

        else:
            # Operate Process Here !!!!!
            if 'img' in self.mbn_payload:
                if len(str(self.mbn_payload['img'])) > 100:
                
                    #print("val['img'] = ", val['img'])
                    if 'fps' in self.mbn_payload :
                        self.mbn_payload['fps'] = self.mbn_payload['fps']

                    if 'blink' in self.mbn_payload :
                        if self.mbn_payload['blink'] == True:
                            self.content.inputlbl.setText("<font color=#00FF00>-> Image Input</font>")
                        else:
                            self.content.inputlbl.setText("")

                        self.mbn_payload['blink'] = self.mbn_payload['blink']

                    (h,w) = self.mbn_payload ['img'].shape[:2]
                    
                    blob = cv2.dnn.blobFromImage(self.mbn_payload['img'], 0.007843, (300,300), 127.5)
                    self.content.net.setInput(blob)
                    
                    detections = self.content.net.forward()

                    for i in np.arange(0, detections.shape[2]):
                        percent = detections[0,0,i,2]
                        
                        if percent > 0.65:
                            class_index = int(detections[0,0,i,1])
                            box = detections[0,0,i,3:7]*np.array([w,h,w,h])
                            (startX, startY, endX, endY) = box.astype("int")

                            label = "{} [{:.2f}%]".format(self.content.CLASSES[class_index], percent*100)
                            cv2.rectangle(self.mbn_payload['img'], (startX, startY), (endX, endY), self.content.COLORS[class_index], 2)
                            cv2.rectangle(self.mbn_payload['img'], (startX-1, startY-30), (endX+1, startY), self.content.COLORS[class_index], cv2.FILLED)
                            y = startY - 15 if startY-15>15 else startY+15
                            cv2.putText(self.mbn_payload['img'], label, (startX+20, y+5), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)

                            self.mbn_payload['mbn_detect'] = label
                            self.mbn_payload['mbn_confidence'] = str(percent*100)
                            self.mbn_payload['mbn_boxes'] = { 'x1':startX, 'y1':startY, 'x2':endX, 'y2':endY }

                else:
                    self.content.inputlbl.setText("<font color='red'>Wrong Input !!!</font>")

        self.value = self.mbn_payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value