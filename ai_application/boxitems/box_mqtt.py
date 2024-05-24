from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import random

from paho.mqtt import client as mqtt_client
from datetime import datetime

import requests

import cv2
import base64
import ast
import sys

class MQTTCONECT(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        animate_process = self.Path + "/icons/icons_mqtt_logo.png"
        self.conn_icon  = self.Path + "/icons/icons_conn_icon.png"
        self.conn_icon_b = self.Path + "/icons/icons_conn_icon_b.png"

        self.editserver = QLineEdit("broker.emqx.io", self)
        self.editserver.setGeometry(10,5,85,20)
        self.editserver.setPlaceholderText("MQTT Server : ")
        self.editserver.setStyleSheet("font-size:5pt;")

        self.edittopic = QLineEdit("/ai/mqtt", self)
        self.edittopic.setGeometry(100,5,45,20)
        self.edittopic.setPlaceholderText("topic")
        self.edittopic.setStyleSheet("font-size:5pt;")

        self.editport = QLineEdit("1883", self)
        self.editport.setGeometry(10,30,50,20)
        self.editport.setPlaceholderText("1883")
        self.editport.setStyleSheet("font-size:5pt;")

        self.ConnectBtn = QPushButton(self)
        self.ConnectBtn.setGeometry(10,53,50,20)
        self.ConnectBtn.setIcon(QIcon(self.conn_icon_b))
        self.ConnectBtn.setEnabled(True)

        self.lbl = QLabel("Not Connect!" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(82,92,85,20)
        self.lbl.setStyleSheet("color: red; font-size:5pt;")

        self.checkSub = QCheckBox("Sub -->",self)
        self.checkSub.setGeometry(70,30,75,20)
        self.checkSub.setStyleSheet("color: #FC03C7; font-size:6pt;")
        self.checkSub.setChecked(True)

        self.checkPub = QCheckBox("--> Pub",self)
        self.checkPub.setGeometry(70,55,75,20)
        self.checkPub.setStyleSheet("color: lightblue; font-size:6pt;")
        self.checkPub.setChecked(False)

        self.PercentEdit = QLineEdit("50", self)
        self.PercentEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.PercentEdit.setGeometry(100,73,30,20)
        self.PercentEdit.setPlaceholderText("50%")
        self.PercentEdit.setStyleSheet("color: white; font-size:6pt;")

        self.lbl2 = QLabel("%" , self)
        self.lbl2.setAlignment(Qt.AlignLeft)
        self.lbl2.setGeometry(132,75,20,15)
        self.lbl2.setStyleSheet("color: white; font-size:5pt;")

        self.editName = QLineEdit(self)
        self.editName.setGeometry(5,105,140,17)
        self.editName.setPlaceholderText("MQTT Name")
        self.editName.setAlignment(QtCore.Qt.AlignCenter)
        self.editName.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:6pt;color:white; border: 1px solid white; border-radius: 3%;")

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(80,30)
        graphicsView.setGeometry(QtCore.QRect(0, 80, 80, 30))

        img = QPixmap(animate_process)
        self.pixmap.setPixmap(img)
        #====================================================

        self.lockflow = self.readFlowSetting('LockFlow')
        if self.lockflow == "true":
            self.editserver.setEnabled(False)
            self.editport.setEnabled(False)
            self.edittopic.setEnabled(False)
            self.ConnectBtn.setEnabled(False)
            self.checkSub.setEnabled(False)
            self.checkPub.setEnabled(False)

        self.broker = self.editserver.text()
        self.port = int(self.editport.text())
        self.topic = self.edittopic.text()
        self.client_id = f'aiflow-mqtt-{random.randint(0, 100000)}'

        self.playload_decode = None
        self.msg_topic = None

        self.button_flag = False

        self.autoconnect_flag = False

        self.connect_flag = False
        self.subscribe_flag = True
        self.publish_flag = False

        self.MQTT_timer = QtCore.QTimer(self)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.last_value = ""

        self.internet_flag = False
        self.InternetCheck = 0
        self.InternetCheck_timer = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.MQTT_timer)
            self.ListGlobalTimer.append(self.InternetCheck_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['mqttserver'] = self.broker
        res['mqttport'] = self.port
        res['mqtttopic'] = self.topic
        res['autoconnectflag'] = self.autoconnect_flag
        res['subscribflag'] = self.subscribe_flag
        res['publishflag'] = self.publish_flag
        res['mqtt_name'] = self.editName.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.broker = data['mqttserver']
            self.editserver.setText(self.broker)

            self.port = data['mqttport']
            self.editport.setText(str(self.port))

            self.topic = data['mqtttopic']
            self.edittopic.setText(str(self.topic))

            self.autoconnect_flag = data['autoconnectflag']
            self.subscribe_flag = data['subscribflag']
            self.publish_flag = data['publishflag']

            if 'mqtt_name' in data:
                self.editName.setText(data['mqtt_name'])

            #print("self.subscribe_flag = ", self.subscribe_flag)
            if self.subscribe_flag:
                self.checkSub.setChecked(True)
            else:
                self.checkSub.setChecked(False)

                if self.publish_flag:
                    self.checkPub.setChecked(True)
                else:
                    self.checkPub.setChecked(False)

            if self.autoconnect_flag:
                self.ConnectBtn.setIcon(QIcon(self.conn_icon))
                self.MQTT_timer.start()
            else:
                self.MQTT_timer.stop()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def readFlowSetting(self, key):
        settings = QSettings("Flow Setting")
        data = settings.value(key)
        return data

@register_node(OP_NODE_MQTT)
class Open_MQTT(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_mqtt_icon.png"
    op_code = OP_NODE_MQTT
    op_title = "MQTT"
    content_label_objname = "MQTT"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[3,4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.reciev_datamqtt = {}
        self.mqtt_payload = {}

        self.mqtt_client = None
        self.connected_flag = False
        self.ReConnected_flag = False

        self.payload['internet'] = False
        self.raw_mqtt_data = ""
        self.new_mqtt_data = ""

    def initInnerClasses(self):
        self.content = MQTTCONECT(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphics150x150Process(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.editserver.textChanged.connect(self.ChangedMqttURL)
        self.content.editport.textChanged.connect(self.ChangedMqttPort)
        self.content.edittopic.textChanged.connect(self.ChangeMqttTopic)

        self.content.ConnectBtn.clicked.connect(self.click_connect_mqtt)

        self.content.checkSub.stateChanged.connect(self.SelectSubscribe)
        self.content.checkPub.stateChanged.connect(self.SelectPublish)

        self.content.MQTT_timer.timeout.connect(self.mqtt_update_msg)
        self.content.MQTT_timer.setInterval(500)

        self.content.InternetCheck_timer.timeout.connect(self.InternetConnection)
        self.content.InternetCheck_timer.setInterval(500)
        self.content.InternetCheck_timer.start()

    def evalImplementation(self):                       # <----------- Create Socket range Index    
        if self.content.connect_flag:
            input_node = self.getInput(0)
            if not input_node:
                self.grNode.setToolTip("Input is not connected")
                self.markInvalid()
                return

            self.reciev_datamqtt = input_node.eval()

            if self.reciev_datamqtt is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                return

            else:
                #print("Process Plublish MQTT")
                if 'inputtype' in self.reciev_datamqtt:
                    if self.reciev_datamqtt['inputtype'] == 'img': 

                        if 'img' in self.reciev_datamqtt:
                            if len(str(self.reciev_datamqtt['img'])) > 100:
                                img = self.reciev_datamqtt['img']

                                scale_percent = 50 # percent of original size
                                width = int(img.shape[1] * int(self.content.PercentEdit.text()) / 100)
                                height = int(img.shape[0] * int(self.content.PercentEdit.text()) / 100)
                                dim = (width, height)
                                
                                # resize image
                                resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

                                #Encoding the Frame
                                _, buffer = cv2.imencode('.jpg', resized)

                                # Converting into encoded bytes
                                jpg_as_text = base64.b64encode(buffer)

                                # Publishig the Frame on the Topic home/server
                                self.mqtt_client.publish(self.content.topic, jpg_as_text)
                
                else:
                    if 'topic' in self.reciev_datamqtt:
                        self.content.topic = self.reciev_datamqtt['topic']
                        self.content.edittopic.setText(str(self.content.topic))
                    elif len(self.content.topic) > 0:
                        self.content.topic = self.content.edittopic.text()
                    else:
                        self.content.topic = "/ai/mqtt"

                    if self.content.publish_flag:
                        #print("type(val) = ", type(val))
                        if 'mqtt_payload' in self.reciev_datamqtt:
                            if str(self.reciev_datamqtt['mqtt_payload']) != self.content.last_value:
                                self.mqtt_client.publish(self.content.topic, str(self.reciev_datamqtt['mqtt_payload']))

                                self.content.last_value = str(self.reciev_datamqtt['mqtt_payload'])
          
                                self.payload['result'] = "Pub --> " + str(datetime.now().strftime("%H:%M:%S"))
                                self.sendFixOutputByIndex(self.payload, 1)          #<--------- Send Payload to output socket
                        else:
                            #print("None Format self.reciev_datamqtt = ", self.reciev_datamqtt)
                            self.mqtt_client.publish(self.content.topic, str(self.reciev_datamqtt))

            # self.sendFixOutputByIndex(self.mqtt_payload, 0)
            # self.sendFixOutputByIndex(self.reciev_datamqtt, 1)

    def ChangedMqttURL(self):
        print("MQTT Server Set")
        self.content.broker = self.content.editserver.text()

    def ChangedMqttPort(self):
        print("MQTT Port Set")
        self.content.port = int(self.content.editport.text())

    def ChangeMqttTopic(self):
        print("MQTT Topic Set")
        self.content.topic = self.content.edittopic.text()

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker! ",  datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.content.client_id)
        client.username_pw_set("", "")
        client.on_connect = on_connect
        client.connect(self.content.broker, self.content.port)
        return client

    def MQTTConnect(self):
        if not self.content.connect_flag:
            self.mqtt_client = self.connect_mqtt()
            if self.mqtt_client:
                print("MQTT Connected")
                self.content.lbl.setText("Connected")
                self.content.lbl.setStyleSheet("color: green; font-size:5pt;")
                self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon))
                self.content.connect_flag = True

                if self.content.subscribe_flag:
                    self.subscribe(self.mqtt_client)
                    self.content.MQTT_timer.start()

                self.content.autoconnect_flag = True

                self.mqtt_client.loop_start()

            else:
                self.content.lbl.setText("Fail !!")
                self.content.lbl.setStyleSheet("color: red; font-size:5pt;")
                self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon_b))
                self.content.MQTT_timer.stop()

                self.content.autoconnect_flag = False

    def click_connect_mqtt(self):
        self.content.button_flag = not self.content.button_flag
        if self.content.button_flag:
            self.MQTTConnect()
        else:
            print("MQTT DisConnected !!!")
            self.mqtt_client.disconnect()
            self.content.lbl.setText("Not Connect!")
            self.content.lbl.setStyleSheet("color: red; font-size:5pt;")
            self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon_b))
            self.content.connect_flag = False

            self.content.MQTT_timer.stop()

            self.content.autoconnect_flag = False

        print("self.content.button_flag = ", self.content.button_flag)


    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            self.content.playload_decode = msg.payload.decode()
            self.content.msg_topic = msg.topic

            # print("msg.playload.decode = ", self.content.playload_decode)
            # print("msg.msg.topic = ", self.content.msg_topic)

            if type(msg.payload.decode()) != type(None):
                self.raw_mqtt_data = msg.payload.decode()
                # print('self.raw_mqtt_data :', self.raw_mqtt_data )
                # print('type(self.raw_mqtt_data) :', type(self.raw_mqtt_data))
                # print('len(self.raw_mqtt_data) :', len(self.raw_mqtt_data))

                if len(self.raw_mqtt_data) > 13:
                    if self.raw_mqtt_data[0:11] == "{'result': ":
                        self.new_mqtt_data = self.raw_mqtt_data[11:len(self.raw_mqtt_data) - 1]
                        # print("MQTT From Payload data is : ", self.new_mqtt_data)
                        # print('type(self.new_mqtt_data) :', type(self.new_mqtt_data))

                        self.new_mqtt_data = ast.literal_eval(self.new_mqtt_data)
                        self.mqtt_payload['mqtt_payload'] = self.new_mqtt_data 
                        self.mqtt_payload['result'] = self.new_mqtt_data 

                    else:
                        self.mqtt_payload['mqtt_payload'] = self.raw_mqtt_data
                        self.mqtt_payload['result'] = self.raw_mqtt_data

            self.payload['topic'] = msg.topic
            self.payload['mqtt_timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if len(self.content.topic) > 0:
            self.content.topic = self.content.edittopic.text()
        else:
            self.content.topic = "/ai/mqtt"

        client.subscribe(self.content.topic)
        client.on_message = on_message

    def mqtt_update_msg(self):
        # Set Auto Connect After start process
        if self.content.autoconnect_flag and not self.connected_flag:
            self.MQTTConnect()
            self.connected_flag = True

        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                self.content.lbl.setText("Connected")
                self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon))
            else:
                self.content.lbl.setText("")
            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

    
        self.sendFixOutputByIndex(self.mqtt_payload, 0)                   #<--------- Send Payload to output socket

        self.payload['result'] = "Sub --> " + str(datetime.now().strftime("%H:%M:%S"))
        self.sendFixOutputByIndex(self.payload, 1)          #<--------- Send Payload to output socket

    def SelectSubscribe(self, state):
        if state == QtCore.Qt.Checked:
            self.content.subscribe_flag = True
            self.content.publish_flag = False
            self.content.checkPub.setChecked(False)
        else:
            self.content.subscribe_flag = False
            self.content.publish_flag = True
            self.content.checkPub.setChecked(True)
        
    def SelectPublish(self, state):
        if state == QtCore.Qt.Checked:
            self.content.publish_flag = True
            self.content.subscribe_flag = False
            self.content.checkSub.setChecked(False)
            self.content.MQTT_timer.stop()
        else:
            self.content.publish_flag = False
            self.content.subscribe_flag = True
            self.content.checkSub.setChecked(True)

    def InternetConnection(self):
    
        if self.content.InternetCheck >= 100 and self.connected_flag:
            self.content.InternetCheck = 0

            url = "http://www.openfog.net/"
            timeout = 5
            try:
                request = requests.get(url, timeout=timeout)
                # print("Connected to the Internet")

                if not self.content.internet_flag and not self.ReConnected_flag:
                    self.MQTTConnect()        
                    self.ReConnected_flag = True

                self.content.internet_flag = True

            except (requests.ConnectionError, requests.Timeout) as exception:
                print("MQTT DisConnected !!! - Cauase No Internet")
                self.mqtt_client.disconnect()
                self.content.lbl.setText("Not Connect!")
                self.content.lbl.setStyleSheet("color: red; font-size:5pt;")
                self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon_b))
                self.content.connect_flag = False
                self.content.MQTT_timer.stop()

                self.ReConnected_flag = False

                self.content.internet_flag = False

                print("No internet connection. ", datetime.now().strftime("%H:%M:%S"))


            self.payload['internet'] = str(self.content.internet_flag)               
            self.sendFixOutputByIndex(self.payload, 1)          #<--------- Send Payload to output socket

        self.content.InternetCheck += 1

    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(index, self.op_code)
        else:
            self.evalChildren(index)

