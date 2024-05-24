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

import mediapipe as mp

class MediaPipe(QDMNodeContentWidget):
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

        self.checkskeleton = QCheckBox("skeleton",self)
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

@register_node(OP_NODE_MEDIAPIPE)
class Open_MediaPipe(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_mediapipe_icon.png"
    op_code = OP_NODE_MEDIAPIPE
    op_title = "M - Pose"
    content_label_objname = "M - Pose"

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

        self.crop_img = None
        self.image = None

    def initInnerClasses(self):
        self.content = MediaPipe(self)                   # <----------- init UI with data and widget
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

                    # Convert the BGR image to RGB.
                    
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

                    #image = cv2.cvtColor(self.crop_img, cv2.COLOR_BGR2RGB)

                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    self.image.flags.writeable = False
                    results = self.content.pose.process(self.image)

                    # Draw the pose annotation on the image.
                    self.image.flags.writeable = True
                    image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

                    if self.content.selskeleton:
                        self.content.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.content.mp_pose.POSE_CONNECTIONS)

                    if results.pose_landmarks:
                        #mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
                        #mpDraw.draw_landmarks(img, results.pose_landmarks)

                        for id, lm in enumerate(results.pose_landmarks.landmark):
                            h, w, c = image.shape

                            cx, cy = int(lm.x * w), int(lm.y * h)

                            if id == 15:
                                self.left_hand = (cx, cy)

                                if self.content.selwrist:
                                    cv2.circle(image, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                                    cv2.putText(image , "%d" % int(id), (cx-5, cy+5),  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
                                    #print(id, cx, cy)

                            if id == 16:
                                self.right_hand = (cx, cy)

                                if self.content.selwrist:
                                    cv2.circle(image, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
                                    cv2.putText(image , "%d" % int(id), (cx-5, cy+5),  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
                                    #print(id, cx, cy)

                    self.rx_payload['img'] = image
                    self.rx_payload['centers'] = {15:self.left_hand, 16:self.right_hand}

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
            
