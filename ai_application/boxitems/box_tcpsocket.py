from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException

import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import random

# Import socket module
import socket

class TCPCONECT(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.conn_icon  = self.Path + "/icons/icons_conn_icon.png"
        self.conn_icon_b = self.Path + "/icons/icons_conn_icon_b.png"

        animate_movie = self.Path + "/icons/icons_tcp_logo.gif"

        self.editserver = QLineEdit("127.0.0.1", self)
        self.editserver.setGeometry(10,5,125,20)
        self.editserver.setPlaceholderText("TCP Server : ")
        self.editserver.setStyleSheet("font-size:6pt;")
        self.editserver.setEnabled(False)

        self.editport = QLineEdit("52617", self)
        self.editport.setGeometry(10,30,50,20)
        self.editport.setPlaceholderText("52617")
        self.editport.setStyleSheet("font-size:5pt;")

        self.ConnectBtn = QPushButton(self)
        self.ConnectBtn.setGeometry(10,53,50,20)
        self.ConnectBtn.setIcon(QIcon(self.conn_icon_b))
        self.ConnectBtn.setEnabled(True)

        self.lbl = QLabel("Not Connect!" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(85,85,85,20)
        self.lbl.setStyleSheet("color: red; font-size:5pt;")

        self.checkServer= QCheckBox("Server ->",self)
        self.checkServer.setGeometry(67,29,75,20)
        self.checkServer.setStyleSheet("color: orange; font-size:5pt;")
        self.checkServer.setChecked(True)

        self.checkClient = QCheckBox("-> Client",self)
        self.checkClient.setGeometry(67,51,75,20)
        self.checkClient.setStyleSheet("color: #FC03C7; font-size:5pt;")
        self.checkClient.setChecked(False)

        self.radioState = QRadioButton("Reply", self)
        self.radioState.setStyleSheet("color: lightblue; font-size:5pt;")
        self.radioState.setGeometry(90,67,55,20)

        #====================================================
        #====================================================
        # Loading the GIF
        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(5, 72, 80, 30))
        self.label.setMinimumSize(QtCore.QSize(80, 30))
        self.label.setMaximumSize(QtCore.QSize(80, 30))

        self.movie = QMovie(animate_movie)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        #====================================================

        self.lockflow = self.readFlowSetting('LockFlow')
        if self.lockflow == "true":
            self.editserver.setEnabled(False)
            self.editport.setEnabled(False)
            self.ConnectBtn.setEnabled(False)
            self.checkServer.setEnabled(False)
            self.checkClient.setEnabled(False)

        self.host = self.editserver.text()
        self.port = self.editport.text()
        self.client_id = f'aiflow-mqtt-{random.randint(0, 100000)}'

        self.TCPMode = "server"

        self.playload_decode = None
        self.msg_topic = None

        self.autoconnect_flag = False
        self.connect_flag = False
        self.reply_flag = False

        self.TCP_timer = QtCore.QTimer(self)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        self.last_value = ""

    def serialize(self):
        res = super().serialize()
        res['tcpserver'] = self.host
        res['tcpport'] = self.port
        res['autoconnectflag'] = self.autoconnect_flag
        res['tcpmode'] = self.TCPMode
        res['reply'] = self.reply_flag
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.host = data['tcpserver']
            self.editserver.setText(self.host)

            self.port = data['tcpport']
            self.editport.setText(str(self.port))

            self.autoconnect_flag = data['autoconnectflag']
            self.TCPMode = data['tcpmode']

            #print("self.subscribe_flag = ", self.subscribe_flag)
            if self.TCPMode == "server":
                self.checkServer.setChecked(True)
                self.checkClient.setChecked(False)
            else:
                self.checkServer.setChecked(False)
                self.checkClient.setChecked(True)

            self.reply_flag = data['reply']
            if self.reply_flag:
                self.radioState.setChecked(True)
  
            if self.autoconnect_flag:
                self.TCP_timer.start()
            else:
                self.TCP_timer.stop()

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def readFlowSetting(self, key):
        settings = QSettings("Flow Setting")
        data = settings.value(key)
        return data

@register_node(OP_NODE_TCPIP)
class Open_MQTT(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_tcp_icon.png"
    op_code = OP_NODE_TCPIP
    op_title = "TCP/IP"
    content_label_objname = "TCP/IP"

    def __init__(self, scene):
        super().__init__(scene, inputs=[3], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.reciev_datatcp = {}

        self.TCP = None
        self.conn = None
        self.server_socket = None
        self.client_socket = None
        
        self.connected_flag = False

    def initInnerClasses(self):
        self.content = TCPCONECT(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.editserver.textChanged.connect(self.ChangedTCPURL)
        self.content.editport.textChanged.connect(self.ChangedTCPPort)

        self.content.checkServer.stateChanged.connect(self.SelectServerMode)
        self.content.checkClient.stateChanged.connect(self.SelectClientMode)
        self.content.radioState.toggled.connect(self.onClicked)

        self.content.ConnectBtn.clicked.connect(self.TCPConnect)

        self.content.TCP_timer.timeout.connect(self.tcp_update_msg)
        self.content.TCP_timer.setInterval(200)

    def evalImplementation(self):                       # <----------- Create Socket range Index    
        self.reciev_datatcp = None

        if self.content.connect_flag:
            input_node = self.getInput(0)
            if not input_node:
                self.grNode.setToolTip("Input is not connected")
                self.markInvalid()
                return

            self.reciev_datatcp = input_node.eval()

            if self.reciev_datatcp is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                return

            else:
                print("Client Mode Process send data to server")
                if 'msg' in self.reciev_datatcp:
                    if self.reciev_datatcp is None:
                        self.reciev_datatcp['msg'] = ''

        self.InternalCommonEval()

    def TCPConnect(self):
        if not self.content.connect_flag:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print ("Socket successfully created")
            except socket.error as err:
                print ("socket creation failed with error %s" %(err))

            if self.content.TCPMode == 'server':
                localhost = ""
                s.connect(("8.8.8.8", 80))
                localhost = s.getsockname()[0]
                print(localhost)

                # get the hostname
                self.content.host = localhost
                print("Server host = ", self.content.host)
                self.content.port = int(self.content.editport.text())  # initiate port no above 1024

                self.server_socket = socket.socket()  # get instance
                # look closely. The bind() function takes tuple as argument
                self.server_socket.bind((self.content.host, self.content.port))  # bind host address and port together

                # configure how many client the server can listen simultaneously
                self.server_socket.listen(10)
                self.conn, address = self.server_socket.accept()  # accept new connection
                print("Connection from: " + str(address))

            else:
                self.content.host = self.content.editserver.text()  # as both code is running on same pc
                self.content.port = int(self.content.editport.text())  # socket server port number

                self.client_socket = socket.socket()  # instantiate
                try:
                    self.client_socket.connect((self.content.host, self.content.port))  # connect to the server
                except socket.error as err:
                    print ("socket creation failed with error %s" %(err))

            print("TCP Connected")
            self.content.lbl.setText("Connected")
            self.content.lbl.setStyleSheet("color: green; font-size:5pt;")
            self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon))

            self.content.autoconnect_flag = True

            #self.connect_flag = True
            self.content.TCP_timer.start()
            self.content.movie.start()

        else:
            self.content.TCP_timer.stop()
            self.content.movie.stop()

            #self.connect_flag = False

            if self.content.TCPMode == 'server':
                self.conn.close()  # close the connection

            else:
                self.client_socket.close()  # close the connection

            self.content.lbl.setText("Not Connect!")
            self.content.lbl.setStyleSheet("color: red; font-size:5pt;")
            self.content.ConnectBtn.setIcon(QIcon(self.content.conn_icon_b))

            self.content.autoconnect_flag = False

        self.content.connect_flag = not self.content.connect_flag

    def tcp_update_msg(self):
        # Set Auto Connect After start process
        if self.content.autoconnect_flag and not self.connected_flag:
            self.TCPConnect()
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

        if self.content.TCPMode == 'server':
            print("Update TCP Server Mode")

            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = self.conn.recv(1024).decode()
            if not data:
                # if data is not received break
                self.content.TCP_timer.stop()
            print("from connected user: " + str(data))

        else:
            if 'msg' in self.reciev_datatcp:
                #print("self.reciev_datatcp['msg'] = ", self.reciev_datatcp['msg'])
               
                if self.reciev_datatcp['msg'] is not None:
                    #print("len(self.reciev_datatcp['msg']) = " , len(self.reciev_datatcp['msg']))
                    if len(self.reciev_datatcp['msg']) > 0:
                        self.client_socket.send(str(self.reciev_datatcp['msg']).encode())  # send message
                        self.reciev_datatcp['msg'] = ""

                        if self.content.reply_flag:
                            self.reciev_datatcp['tcp_payload'] = self.client_socket.recv(1024).decode()
                            if len(self.reciev_datatcp['tcp_payload']) > 0:
                                print("self.reciev_datatcp['tcp_payload'] = ", self.reciev_datatcp['tcp_payload'])
                                self.InternalCommonEval()

    def ChangedTCPURL(self):
        print("TCP Server Set")
        self.content.host = self.content.editserver.text()

    def ChangedTCPPort(self):
        print("TCP Port Set")
        self.content.port = self.content.editport.text()

    def SelectServerMode(self, state):
        if state == QtCore.Qt.Checked:
            self.content.TCPMode = "server"
            self.content.checkServer.setChecked(True)
            self.content.checkClient.setChecked(False)

            self.content.editserver.setEnabled(False)
        else:
            self.content.TCPMode = "client"
            self.content.checkServer.setChecked(False)
            self.content.checkClient.setChecked(True)

            self.content.editserver.setEnabled(True)

    def SelectClientMode(self, state):
        if state == QtCore.Qt.Checked:
            self.content.TCPMode = "client"
            self.content.checkServer.setChecked(False)
            self.content.checkClient.setChecked(True)

            self.content.editserver.setEnabled(True)
        else:
            self.content.TCPMode = "server"
            self.content.checkServer.setChecked(True)
            self.content.checkClient.setChecked(False)

            self.content.editserver.setEnabled(False)

    def onClicked(self):
        radioButton = self.content.sender()
        if radioButton.isChecked():
            self.content.reply_flag = True
        else:
            self.content.reply_flag = False

    def InternalCommonEval(self):
        self.value = self.reciev_datatcp

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()
    
