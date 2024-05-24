from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class JoinPayload(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        animate_process = self.Path + "/icons/icons_join_logo_w30.png"

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(35,35)
        graphicsView.setGeometry(QtCore.QRect(20, 5, 32, 32))

        img = QPixmap(animate_process)
        self.pixmap.setPixmap(img)
        #====================================================

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_JOINPAYLOAD)
class Open_JoinPayload(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_join_icon.png"
    op_code = OP_NODE_JOINPAYLOAD
    op_title = "Join"
    content_label_objname = "Join"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1,2], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.new_payload = {}

        self.image = None
        self.gap_size = 15

        self.rx_payload_1 = {}
        self.rx_payload_2 = {}

        self.obj_found1 = 0
        self.obj_found2 = 0

    def initInnerClasses(self):
        self.content = JoinPayload(self)                   # <----------- init UI with data and widget
        self.grNode = FlowJoinPayload(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node_1 = self.getInput(0)
        if not input_node_1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()

        else:
            self.rx_payload_1 = input_node_1.eval()

            if self.rx_payload_1 is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            else:
                # print("self.rx_payload_1 : ", self.rx_payload_1)
                self.new_payload = self.rx_payload_1

        input_node_2 = self.getInput(1)
        if not input_node_2:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()

        else:
            self.rx_payload_2 = input_node_2.eval()

            if self.rx_payload_2 is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            else:
                # print("self.rx_payload_2 : ", self.rx_payload_2)
                self.new_payload = self.rx_payload_2

        # if self.rx_payload_1 is not None and self.rx_payload_2 is None:
        #     self.grNode.setToolTip("Input is NaN")
        #     self.markInvalid()
        #     return

        # else:
        #     #print("type(self.rx_payload_1) = ", type(self.rx_payload_1))
        #     #print("type(self.rx_payload_2) = ", type(self.rx_payload_2))

        #     #print("self.rx_payload_1 = ", self.rx_payload_1)
        #     #print("self.rx_payload_2 = ", self.rx_payload_2)

        #     """self.rx_payload_1 = {'obj_found': 4, 
        #                         'yolo_boxes': [
        #                             {'x1': 249, 'y1': 283, 'x2': 329, 'y2': 367, 'score': 87, 'obj': 'md_vvt'}, 
        #                             {'x1': 168, 'y1': 303, 'x2': 187, 'y2': 323, 'score': 94, 'obj': 'guide_sparkplug'}, 
        #                             {'x1': 241, 'y1': 368, 'x2': 263, 'y2': 390, 'score': 90, 'obj': 'guide_sparkplug'}, 
        #                             {'x1': 188, 'y1': 242, 'x2': 206, 'y2': 281, 'score': 83, 'obj': 'hanger'}]
        #                         }

        #     self.rx_payload_2 = {'obj_found': 1, 
        #                         'yolo_boxes': [
        #                             {'x1': 22, 'y1': 289, 'x2': 86, 'y2': 357, 'score': 91, 'obj': 'oring_vvt'}]
        #                         }"""

        if self.rx_payload_1 and self.rx_payload_2:
            if 'obj_found' in self.rx_payload_1 and 'obj_found' in self.rx_payload_2:

                list_boxes1 = []
                list_boxes2 = []

                self.obj_found1 = self.rx_payload_1['obj_found']
                if self.obj_found1 > 0:
                    for i in range(0, int(self.obj_found1)):
                        if type(self.rx_payload_1['yolo_boxes'][i]['score']) is not list:
                            list_boxes1.append(self.rx_payload_1['yolo_boxes'][i])

                    #print("list_boxes_1 = ", list_boxes1)

                self.obj_found2 = self.rx_payload_2['obj_found']
                if self.obj_found2 > 0:
                    for l in range(0, int(self.obj_found2)):
                        if type(self.rx_payload_2['yolo_boxes'][l]['score']) is not list:
                            list_boxes2.append(self.rx_payload_2['yolo_boxes'][l])

                    #print("list_boxes_2 = ", list_boxes2)

                if 'inputtype' in self.rx_payload_1:
                    self.new_payload['inputtype']   = self.rx_payload_1['inputtype']

                if 'fps' in self.rx_payload_1:
                    self.new_payload['fps']         = self.rx_payload_1['fps']

                if 'clock' in self.rx_payload_1:
                    self.new_payload['clock']       = self.rx_payload_1['clock']

                """if 'img' in self.rx_payload_1:
                    self.new_payload['img']         = self.rx_payload_1['img']"""

                if 'focus_area' in self.rx_payload_1:
                    self.new_payload['focus_area']  = self.rx_payload_1['focus_area']

                elif 'focus_area' in self.rx_payload_2:
                    self.new_payload['focus_area']  = self.rx_payload_2['focus_area']

                if 'centers' in self.rx_payload_1:
                    self.new_payload['centers']     = self.rx_payload_1['centers']

                elif 'centers' in self.rx_payload_2:
                    self.new_payload['centers']     = self.rx_payload_2['centers']

                self.new_payload['obj_found'] = self.obj_found1 + self.obj_found2
                self.new_payload['yolo_boxes'] = [*list_boxes1, *list_boxes2]

            else:
                # Python Program to Merge Dictionaries (with Examples)
                # 1. dict_1.update(dict_2)
                # 2. result = dict_1 | dict_2       ===> it is only used in the python 3.9 version or more.
                # 3. dict_3 = {**dict_1,**dict_2}   ===> In Python 3.5 or greater:

                if self.rx_payload_1 and self.rx_payload_2:
                    self.new_payload = {**self.rx_payload_1, **self.rx_payload_2} 
                
                else:
                    #self.rx_payload_2 is Empty
                    self.new_payload = self.rx_payload_1

                if self.new_payload:
                    if 'nextaddress' in self.new_payload:
                        #print("Draw Next process in self.new_payload['img']")

                        if 'focus_area' in self.new_payload:
                            self.image = self.new_payload['img']

                            if self.new_payload['focus_area'] and self.new_payload['set_focus_area'] is not None and self.new_payload['set_new_scale'] is not None:

                                if 'gap' in self.new_payload:
                                    self.gap_size = int(self.new_payload['gap'])

                                if self.new_payload['nextaddress']['1'] is not None and self.new_payload['nextaddress']['2'] is not None:
                                    xl = int((int(self.new_payload['nextaddress']['1']) - self.new_payload['set_focus_area'][0]) / round(self.new_payload['set_new_scale'][0], 2))
                                    yl = int((int(self.new_payload['nextaddress']['2']) - self.new_payload['set_focus_area'][1]) / round(self.new_payload['set_new_scale'][1], 2))

                                    self.image = cv2.circle(self.image, (xl , yl), int(self.gap_size/round(self.new_payload['set_new_scale'][0], 2)), (95, 60 ,255), 2) #Blue Green Red (Orange)

                                if self.new_payload['nextaddress']['3'] is not None and self.new_payload['nextaddress']['4'] is not None:

                                    xr = int((int(self.new_payload['nextaddress']['3']) - self.new_payload['set_focus_area'][0]) / round(self.new_payload['set_new_scale'][0], 2))
                                    yr = int((int(self.new_payload['nextaddress']['4']) - self.new_payload['set_focus_area'][1]) / round(self.new_payload['set_new_scale'][1], 2))

                                    self.image = cv2.circle(self.image, (xr, yr), int(self.gap_size/round(self.new_payload['set_new_scale'][0], 2)), (43 ,425, 255), 2) #Blue Green Red (Orange)

                            else:
                                if 'gap' in self.new_payload:
                                    self.gap_size = int(self.new_payload['gap'])

                                if self.new_payload['nextaddress']['1'] is not None and self.new_payload['nextaddress']['2'] is not None:
                                    self.image = cv2.circle(self.image, (int(self.new_payload['nextaddress']['1']), int(self.new_payload['nextaddress']['2'])), self.gap_size, (95, 60 ,255), 2) #Blue Green Red (Orange)
                                
                                if self.new_payload['nextaddress']['3'] is not None and self.new_payload['nextaddress']['4'] is not None:
                                    self.image = cv2.circle(self.image, (int(self.new_payload['nextaddress']['3']), int(self.new_payload['nextaddress']['4'])), self.gap_size, (43 ,425, 255), 2) #Blue Green Red (Orange)

                        self.new_payload['img'] = self.image
                
        self.value = self.new_payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

