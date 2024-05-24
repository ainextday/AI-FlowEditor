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
        yolo_logo = self.Path + "/icons/icons_yolo_icon.png"

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
        self.ModelPath= self.Path[0:-9] + "/AI_Module/obj_model_data"
        print("self.ModelPath = ", self.ModelPath)

        self.configPath = self.ModelPath + "/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        self.modelPathdata =  self.ModelPath + "/frozen_inference_graph.pb"
        self.classesPath =  self.ModelPath + "/coco.names"

        self.net = cv2.dnn_DetectionModel(self.modelPathdata, self.configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/127.5)
        self.net.setInputMean((127.5,127.5,127.5))
        self.net.setInputSwapRB(True)

        with open(self.classesPath, 'r') as f:
            self.classesList = f.read().splitlines()

        self.classesList.insert(0, '__background__')

        np.random.seed(20)
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList),3))

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

@register_node(OP_NODE_OBJDETECT2)
class Open_ObjectDetect(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_object3.png"
    op_code = OP_NODE_OBJDETECT2
    op_title = "Obj Detect"
    content_label_objname = "Obj Detect"

    def __init__(self, scene):
        super().__init__(scene, inputs=[4], outputs=[3,5]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.detect_payload = {}

    def initInnerClasses(self):
        self.content = ObjectDetect(self)        # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

    def evalImplementation(self):                 # <
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.detect_payload = input_node.eval()

        if self.detect_payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return

        else:
            # Operate Process Here !!!!!
            if 'img' in self.detect_payload:
                if len(str(self.detect_payload['img'])) > 100:
                
                    #print("val['img'] = ", val['img'])
                    if 'fps' in self.detect_payload:
                        self.detect_payload['fps'] = self.detect_payload['fps']

                    if 'blink' in self.detect_payload:
                        if self.detect_payload['blink'] == True:
                            self.content.inputlbl.setText("<font color=#00FF00>-> Image Input</font>")
                        else:
                            self.content.inputlbl.setText("")

                        self.detect_payload['blink'] = self.detect_payload['blink']

                    classLabelIDs, confidences, bboxs = self.content.net.detect(self.detect_payload['img'], confThreshold = 0.5)

                    bboxs = list(bboxs)
                    confidences = list(np.array(confidences).reshape(1,-1)[0])
                    confidences = list(map(float, confidences))

                    bboxIdx = cv2.dnn.NMSBoxes(bboxs, confidences, score_threshold = 0.5, nms_threshold=0.2)

                    if len(bboxIdx) > 0:
                        for i in range(0, len(bboxIdx)):

                            bbox = bboxs[np.squeeze(bboxIdx[i])]
                            classConfidence = confidences[np.squeeze(bboxIdx[i])]
                            classLabelID = np.squeeze(classLabelIDs[np.squeeze(bboxIdx[i])])

                            if classConfidence > 0.65:
                                classLabel = self.content.classesList[classLabelID]

                                classColor = [int(c) for c in self.content.colorList[classLabelID]]

                                disPlayText = "{} : {:.2f}".format(classLabel, classConfidence)

                                x,y,w,h = bbox

                                cv2.rectangle(self.detect_payload['img'], (x,y), (x+w, y+h), color=classColor, thickness=1)
                                cv2.putText(self.detect_payload['img'], disPlayText, (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 1)

                                lineWidth = min(int(w*0.3), int(h*0.3))

                                cv2.line(self.detect_payload['img'], (x,y), (x + lineWidth, y), classColor, thickness=5)
                                cv2.line(self.detect_payload['img'], (x,y), (x, y + lineWidth), classColor, thickness=5)

                                cv2.line(self.detect_payload['img'], (x+w,y), (x + w - lineWidth, y), classColor, thickness=5)
                                cv2.line(self.detect_payload['img'], (x+w,y), (x +w, y + lineWidth), classColor, thickness=5)

                                #####################################################################

                                cv2.line(self.detect_payload['img'], (x,y+h), (x + lineWidth, y+h), classColor, thickness=5)
                                cv2.line(self.detect_payload['img'], (x,y+h), (x, y + h - lineWidth), classColor, thickness=5)

                                cv2.line(self.detect_payload['img'], (x+w,y+h), (x + w - lineWidth, y+h), classColor, thickness=5)
                                cv2.line(self.detect_payload['img'], (x+w,y+h), (x +w, y + h - lineWidth), classColor, thickness=5)

                                self.detect_payload['obj_detect'] = classLabel
                                self.detect_payload['obj_confidence'] = str(int(classConfidence*100))
                                self.detect_payload['obj_boxes'] = { 'x1':x, 'y1':y, 'x2':w, 'y2':h }
                    
                else:
                    self.content.inputlbl.setText("<font color='red'>Wrong Input !!!</font>")

        self.value = self.detect_payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value