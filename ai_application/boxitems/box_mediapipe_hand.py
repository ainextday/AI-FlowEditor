from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time, sys
import mediapipe as mp

class MediaPipe_Hands(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        animate_process = self.Path + "/icons/icons_mediapipe_icon.png"
        self.edit_icon = self.Path + "/icons/icons_setting_20.gif"

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic

        self.pose = self.mp_pose.Pose()

        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,5,105,45)

        self.checkskeleton = QCheckBox("Index",self)
        self.checkskeleton.setGeometry(75,25,70,20)
        self.checkskeleton.setStyleSheet("color: lightblue; font-size:5pt;")

        self.checkwrist = QCheckBox("wrist",self)
        self.checkwrist.setGeometry(75,50,70,20)
        self.checkwrist.setStyleSheet("color: lightgreen; font-size:5pt;")

        self.FocusArea = QCheckBox("F.Area",self)
        self.FocusArea.setGeometry(75,75,70,20)
        self.FocusArea.setStyleSheet("color: lightyellow; font-size:5pt;")

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(70,70)
        graphicsView.setGeometry(QtCore.QRect(5, 15, 70, 82))

        img = QPixmap(animate_process)
        self.pixmap.setPixmap(img)

        #====================================================

        self.selskeleton = True
        self.selwrist = True
        self.selFocusArea = False

        self.checkskeleton.setChecked(True)
        self.checkwrist.setChecked(True)
        self.FocusArea.setChecked(False)

        self.setFocusArea = None
        self.recordNewScale = None

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.6)
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['selectskeleton'] = self.selskeleton
        res['selectwrist'] = self.selwrist
        res['selectedFocusArea'] = self.selFocusArea
        res['setFocusArea'] = self.setFocusArea
        res['newScale'] = self.recordNewScale
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']

            if data['selectskeleton']:
                self.checkskeleton.setChecked(True)
                self.selskeleton = True
            else:
                self.checkskeleton.setChecked(False)
                self.selskeleton = False

            if data['selectwrist']:
                self.checkwrist.setChecked(True)
                self.selwrist = True
            else:
                self.checkwrist.setChecked(False)
                self.selwrist = False

            if data['selectedFocusArea']:
                self.FocusArea.setChecked(True)
                self.selFocusArea = True

                if data['setFocusArea'] is not None:
                    self.setFocusArea = data['setFocusArea']

                if data['newScale'] is not None:
                    self.recordNewScale = data['newScale']
            else:
                self.FocusArea.setChecked(False)
                self.selFocusArea = False
            
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_MPIPEHAND)
class Open_MediaPipe_Hands(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_mediapipe_icon.png"
    op_code = OP_NODE_MPIPEHAND
    op_title = "M - Hand"
    content_label_objname = "M - Hand"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        #self.eval()

        self.left_hand = ( 0, 0 )
        self.right_hand = ( 0, 0 )

        self.startX = 0
        self.startY = 0
        self.endX = 0
        self.endY = 0

        self.NOF_Hand = 0

        self.wr_x = 0
        self.wr_y = 0

        self.md_x = 0
        self.md_y = 0

        self.fg_x = 0
        self.fg_y = 0

        self.crop_img = None
        self.image = None

        self.hand_info = []

    def initInnerClasses(self):
        self.content = MediaPipe_Hands(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.checkskeleton.stateChanged.connect(self.SelectSkeleton)
        self.content.checkwrist.stateChanged.connect(self.SelectWrist)
        self.content.FocusArea.stateChanged.connect(self.UseFocusArea)

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.rx_payload = input_node.eval()

        if self.rx_payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        else:
            #print("Process Data")
            if 'img' in self.rx_payload:
                if len(str(self.rx_payload['img'] )) > 100:
                    if 'blink' in self.rx_payload:
                        if self.rx_payload['blink'] == True:
                            self.content.lbl.setText("<font color: lightblue>-> Image Input</font>")
                        else:
                            self.content.lbl.setText("")

                    # Select Focus Area with cut image
                    if self.content.selFocusArea and self.content.setFocusArea is not None:
                        #print("self.Global.getGlobal(teminal_pos_select) = ", self.Global.getGlobal("teminal_pos_select"))
                        self.startX = self.content.setFocusArea[0]
                        self.startY = self.content.setFocusArea[1]
                        self.endX = self.content.setFocusArea[2]
                        self.endY = self.content.setFocusArea[3]

                        #print("self.startX = ", self.startX)
                        #print("self.startY = ", self.startY)
                        #print("self.endX = ", self.endX)
                        #print("self.endY = ", self.endY)

                        self.crop_img = self.rx_payload['img'][self.startY : self.endY, self.startX : self.endX ]
                        #print("self.crop_img = ", self.crop_img)

                        self.image = cv2.resize(self.crop_img, dsize=(640 , 480), interpolation=cv2.INTER_AREA)
                        self.rx_payload['focus_area'] = True

                        self.rx_payload['set_focus_area'] = self.content.setFocusArea
                        self.rx_payload['set_new_scale'] = self.content.recordNewScale

                    else:
                        self.image = self.rx_payload['img']
                        self.rx_payload['focus_area'] = False

                    # # Convert the BGR image to RGB.
                    # self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

                    # # Flip on horizontal
                    # #self.image = cv2.flip(self.image, 1)

                    # # Set flag
                    # self.image.flags.writeable = False
                    
                    # # Detections
                    # results = self.content.hands.process(self.image)
                    # print(results.multi_hand_landmarks)
                    
                    # # Set flag to true
                    # self.image.flags.writeable = True
                    
                    # # RGB 2 BGR
                    # self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

                    # # Rendering results
                    # if results.multi_hand_landmarks:
                    #     for num, hand in enumerate(results.multi_hand_landmarks):
                    #         self.content.mp_drawing.draw_landmarks(self.image, hand, self.content.mp_hands.HAND_CONNECTIONS, 
                    #                                 self.content.mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    #                                 self.content.mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                    #                                 )

                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    self.image.flags.writeable = False
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    results = self.content.hands.process(self.image)
                    
                    self.image.flags.writeable = True
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

                    image_height, image_width, _ = self.image.shape

                    if results.multi_hand_landmarks:
                        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
                            self.content.mp_drawing.draw_landmarks(
                                self.image,
                                hand_landmarks,
                                self.content.mp_hands.HAND_CONNECTIONS,
                                self.content.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.content.mp_drawing_styles.get_default_hand_connections_style())
                            
                            # print(f'HAND NUMBER: {hand_no+1}')
                            # print('-----------------------')
                            self.NOF_Hand = hand_no+1
                            self.hand_info = []

                            for i in range(21):    
                                # print(f'{self.content.mp_hands.HandLandmark(i).name}:') 
                                # print(f'x: {hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].x * image_width}')
                                # print(f'y: {hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].y * image_height}')
                                # print(f'z: {hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].z * image_width}n')
                                
                                _hand_info = "{\'hand_name\':\'" + str(self.content.mp_hands.HandLandmark(i).name) + "\', \'x\':\'" + str(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].x * image_width) + "\', \'y\':\'" + str(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].y * image_height) + "\', \'z\':\'" + str(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].z * image_width) + "\'}"
                                # print("_hand_info : ", _hand_info)

                                dict_hand_info = eval(_hand_info)
                                # print("dict_hand_info : ", dict_hand_info)
                                # print(type(dict_hand_info))

                                # append this dictionary to the
                                # empty list using copy() method
                                self.hand_info.append(dict_hand_info.copy())

                                if self.content.selwrist:
                                    if str(self.content.mp_hands.HandLandmark(i).name) == "WRIST":
                                        self.wr_x = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].x * image_width)
                                        self.wr_y = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].y * image_height)

                                        self.image = cv2.circle(self.image, (self.wr_x,self.wr_y), 15, (0,255,0), 2)
                                        self.image = cv2.putText(self.image, "15 : " + str(self.content.mp_hands.HandLandmark(i).name), (self.wr_x-37,self.wr_y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (235,253,122), 1, cv2.LINE_AA)

                                    if str(self.content.mp_hands.HandLandmark(i).name) == 'MIDDLE_FINGER_MCP':
                                        self.md_x = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].x * image_width)
                                        self.md_y = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].y * image_height)

                                        self.image = cv2.circle(self.image, (self.md_x,self.md_y), 15, (130,8,255), 2)
                                        self.image = cv2.putText(self.image, "16", (self.md_x-8,self.md_y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (235,253,122),1, cv2.LINE_AA)

                                else:
                                    self.wr_x  = 0
                                    self.wr_y = 0

                                    self.md_x  = 0
                                    self.md_y = 0

                                if self.content.selskeleton:
                                    if str(self.content.mp_hands.HandLandmark(i).name) == 'INDEX_FINGER_TIP':
                                        self.fg_x = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].x * image_width)
                                        self.fg_y = int(hand_landmarks.landmark[self.content.mp_hands.HandLandmark(i).value].y * image_height)

                                        self.image = cv2.circle(self.image, (self.fg_x,self.fg_y), 15, (42,232,255), 2)
                                        # self.image = cv2.putText(self.image, "16", (self.fg_x-8,self.fg_y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (42,232,255),1, cv2.LINE_AA)

                    self.rx_payload['img'] = self.image
                    self.rx_payload['hand_info'] = self.hand_info
                    self.rx_payload['centers'] = {15:(self.wr_x , self.wr_y), 16:(self.md_x, self.md_y)}
                    self.rx_payload['hand_no'] = self.NOF_Hand

        self.value = self.rx_payload                      # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        return self.value

    def SelectSkeleton(self, state):
        if state == QtCore.Qt.Checked:
            self.content.selskeleton = True
        else:
            self.content.selskeleton = False

    def SelectWrist(self, state):
        if state == QtCore.Qt.Checked:
            self.content.selwrist = True
        else:
            self.content.selwrist = False

    def UseFocusArea(self, state):
        print("Use Focus Area", self.Global.getGlobal("teminal_pos_select"))

        if state == QtCore.Qt.Checked:
            self.content.selFocusArea = True

            if self.content.setFocusArea is None and self.content.recordNewScale is None:
                self.content.setFocusArea = self.Global.getGlobal("teminal_pos_select")
                self.content.recordNewScale = self.Global.getGlobal('new_image_scale')

        else:
            self.content.selFocusArea = False
            
