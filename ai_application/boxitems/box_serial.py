from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import serial
import time

import serial.tools.list_ports

class SerialLink(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.SerialImagePath = self.Path + "/icons/icons_serial_image.png"
        self.Switch_Activate = self.Path + "/icons/icons_slide_off.png"
        self.edit_icon = self.Path + "/icons/icons_setting_20.gif"
        self.reload_icon = self.Path + "/icons/icons_refresh.png"
        self.conn_icon = self.Path + "/icons/icons_conn_icon.png"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.remove_icon = self.Path + "/icons/icons_cancel_btn.png"

        #====================================================

        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(42,42)
        graphicsView.setGeometry(QtCore.QRect(5, 0, 45, 45))

        self.img = QPixmap(self.SerialImagePath)
        self.pixmap.setPixmap(self.img)
        
        #====================================================
        #====================================================

        """#vbox layout object
        self.vbox = QVBoxLayout()
 
        #create QLCDNumber object
        self.lcd = QLCDNumber()

        #give background color for the lcd number"""
        #self.lcd.setStyleSheet("""QLCDNumber { 
        #    background-color: rgba(0, 170, 255, 20); 
        #    color: white; }""")
        
        #lcd.setStyleSheet('background: rgba(0, 170, 255, 20)')
        """"
        #add lcd number to vertical box layout
        self.vbox.addWidget(self.lcd)
 
        #create time object
        #time = QTime.currentTime()
        #text = time.toString('hh:mm')
 
        #displat the system time in the lcd
        self.lcd.display("00")
 
        self.setLayout(self.vbox)
        """
        """graphicsView_sw = QGraphicsView(self)
        scene_sw = QGraphicsScene()
        self.pixmap_sw = QGraphicsPixmapItem()
        scene_sw.addItem(self.pixmap_sw)
        graphicsView_sw.setScene(scene_sw)

        graphicsView_sw.resize(49,29)
        graphicsView_sw.setGeometry(QtCore.QRect(95, 8, 49, 29))

        self.img_sw = QPixmap(self.Switch_Activate)
        self.pixmap_sw.setPixmap(self.img_sw)

        self.slide_sw = QPushButton(self)
        self.slide_sw.setGeometry(98,8,47,20)

        self.background = "background-color : lightblue; background-image : url(" + self.Switch_Activate + ");"
        print("self.background = ", self.background)
        self.slide_sw.setStyleSheet(self.background)
        #self.slide_sw.setStyleSheet("color : rgba(0, 0, 0, 10)")

        #self.slide_sw.setIcon(QIcon(self.Switch_Activate))

        #self.edit.setObjectName(self.node.content_label_objname)"""

        self.Linklbl = QLabel("Link" , self)
        self.Linklbl.setAlignment(Qt.AlignLeft)
        self.Linklbl.setGeometry(75,7,25,20)
        self.Linklbl.setStyleSheet("color: orange; font-size:6pt;")

        """self.radioState = QRadioButton(self)
        self.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : rgba(0, 124, 212, 150)"
                                   "}")
        self.radioState.setGeometry(98,5,45,20)
        self.radioState.setIcon(QIcon(self.conn_icon))"""

        self.SwitchSerial = QPushButton(self)
        self.SwitchSerial.setGeometry(100,5,37,20)
        self.SwitchSerial.setIcon(QIcon(self.off_icon))
        self.SwitchSerial.setIconSize(QtCore.QSize(37,20))
        self.SwitchSerial.setStyleSheet("background-color: transparent; border: 0px;")  

        self.StartSerial_flag = False

        #====================================================

        self.lblComport = QLabel("COM Port" , self)
        self.lblComport.setAlignment(Qt.AlignLeft)
        self.lblComport.setGeometry(15,40,75,15)
        self.lblComport.setStyleSheet("color: orange; font-size:6pt;")

        self.SelectComPort = QComboBox(self)
        """self.SelectComPort.addItem("COM0")
        self.SelectComPort.addItem("COM1")
        self.SelectComPort.addItem("COM2")
        self.SelectComPort.addItem("COM3")
        self.SelectComPort.addItem("COM4")
        self.SelectComPort.addItem("COM5")
        self.SelectComPort.addItem("COM6")
        self.SelectComPort.addItem("COM7")
        self.SelectComPort.addItem("COM8")
        self.SelectComPort.addItem("COM9")
        self.SelectComPort.addItem("COM10")"""

        self.SelectComPort.setGeometry(10,60,80,20)
        self.SelectComPort.move(10, 60)
        self.SelectComPort.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : #33CCFF"
                                   "}") 

        #self.SelectComPort.setCurrentText(str(self.BCMSelectPin))

        #====================================================
        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(100,75,20,20)
        self.SettingBtn.setIcon(QIcon(self.edit_icon))

        self.RelaodBtn = QPushButton(self)
        self.RelaodBtn.setGeometry(125,75,20,20)
        self.RelaodBtn.setIcon(QIcon(self.reload_icon))

        #====================================================

        self.lbl = QLabel("Not Running" , self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(15,82,80,20)
        self.lbl.setStyleSheet("color: red; font-size:6pt;")

        """self.checkPoint = QCheckBox("Link",self)
        self.checkPoint.setGeometry(100,45,60,20)
        self.checkPoint.setStyleSheet("color: #FC03C7")
        self.checkPoint.setChecked(True)"""

        #====================================================
        # Popup Setting

        self.PopUplbl = QLabel(" Setting" , self)
        self.PopUplbl.setGeometry(5,5,140,90)
        self.PopUplbl.setAlignment(Qt.AlignLeft)
        self.PopUplbl.setAlignment(Qt.AlignTop)
        self.PopUplbl.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:6pt;color:orange; border: 1px solid white; border-radius: 5%")
        self.PopUplbl.setVisible(False)

        self.ExitPopUp = QPushButton(self)
        self.ExitPopUp.setGeometry(120,7,20,20)
        self.ExitPopUp.setIcon(QIcon(self.remove_icon))
        self.ExitPopUp.setVisible(False)

        self.lblBaudrate = QLabel("baudrate:" , self)
        self.lblBaudrate.setAlignment(Qt.AlignLeft)
        self.lblBaudrate.setGeometry(10,35,60,15)
        self.lblBaudrate.setStyleSheet("color: lightblue; font-size:6pt;")
        self.lblBaudrate.setVisible(False)

        self.BaudRate = 115200

        self.SettingComPort = QComboBox(self)
        self.SettingComPort.addItem("9600")
        self.SettingComPort.addItem("19200")
        self.SettingComPort.addItem("38400")
        self.SettingComPort.addItem("57600")
        self.SettingComPort.addItem("115200")
        self.SettingComPort.addItem("230400")
        self.SettingComPort.addItem("250000")
        self.SettingComPort.addItem("500000")
        self.SettingComPort.addItem("1000000")
        self.SettingComPort.addItem("2000000")

        self.SettingComPort.setGeometry(65,32,75,20)
        self.SettingComPort.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : #33CCFF"
                                   "}") 

        self.SettingComPort.setCurrentText(str(self.BaudRate))
        self.SettingComPort.setVisible(False)

        self.lblBytesize = QLabel("bytesize:" , self)
        self.lblBytesize.setAlignment(Qt.AlignLeft)
        self.lblBytesize.setGeometry(10,55,75,15)
        self.lblBytesize.setStyleSheet("color: white; font-size:6pt;")
        self.lblBytesize.setVisible(False)

        self.lblStopbits = QLabel("stopbits:" , self)
        self.lblStopbits.setAlignment(Qt.AlignLeft)
        self.lblStopbits.setGeometry(10,75,75,15)
        self.lblStopbits.setStyleSheet("color: white; font-size:6pt;")
        self.lblStopbits.setVisible(False)

        #====================================================

        self.Link_timer = QtCore.QTimer(self)
        self.Re_Link_timer = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.Link_timer)
            self.ListGlobalTimer.append(self.Re_Link_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0
        self.check_link_Error = 0

        self.Serial_Avialable = False
        self.COMPort = ""

        self.stored_comport = ""
        self.Serial_Explored()

        #print(self.serial_ports())

        self.serialPort = None
        #self.COMPort = "COM3"
        #self.SelectComPort.setCurrentText(str(self.COMPort))

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['serial_ava'] = self.Serial_Avialable
        res['COM'] = self.COMPort
        res['sw_flag'] = self.StartSerial_flag 
        res['baudrate'] = self.BaudRate

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'serial_ava' in data:
                self.Serial_Avialable = data['serial_ava']

            if 'baudrate' in data:
                self.BaudRate = data['baudrate']
                print("Serial Load self.BaudRate = ", self.BaudRate)

            if 'sw_flag' in data:
                self.StartSerial_flag = data['sw_flag']

                if 'COM' in data:
                    self.COMPort = data['COM']

                if self.Serial_Explored():
                    if self.StartSerial_flag:
                        #self.radioState.setChecked(True)
                        self.SwitchSerial.setIcon(QIcon(self.on_icon))
                        
                        self.SelectComPort.setCurrentText(str(self.COMPort))
                        self.serialPort = serial.Serial(port=self.COMPort, baudrate=self.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
                        self.Link_timer.start()
                        self.Re_Link_timer.start()

                    else:
                        self.Link_timer.stop()
                else:
                    self.Re_Link_timer.start()
                

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    #def lcd_number(self):
  

    def Serial_Explored(self):
        ports = serial.tools.list_ports.comports()
        #print("------------------------")

        if len(ports) > 0:
            for port, desc, hwid in sorted(ports):
                #print("desc = ", desc)
                #print("{}: {} [{}]".format(port, desc, hwid))
                #print("port[0:4] = ", port[0:4])
                x = str(desc).find(" (COM")
                #print("x = ", x)
                #print("desc[0:x] = ", desc[0:x])
                #print("------------------------")

                if len(str(port[0:4])) > 3:
                    if self.stored_comport != str(port[0:4]):
                        self.SelectComPort.addItem(str(port[0:4]))
                        self.stored_comport = str(port[0:4])

                    self.Serial_Avialable = True

                    return True

                else:
                    return False

        else:
            if self.StartSerial_flag:
                self.serialPort = None

                self.Link_timer.stop()
                self.SwitchSerial.setIcon(QIcon(self.off_icon))

                self.Re_Link_timer.start()

@register_node(OP_NODE_SERIAL)
class Open_SERAIL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_serial_icon.png"
    op_code = OP_NODE_SERIAL
    op_title = "Serial Link"
    content_label_objname = "Serial Link"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.eval()

    def initInnerClasses(self):
        self.content = SerialLink(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.SwitchSerial.clicked.connect(self.onLinkClicked)
        self.content.Link_timer.timeout.connect(self.update_data)
        self.content.Link_timer.setInterval(100)

        self.content.SelectComPort.activated[str].connect(self.onComPortChanged)

        self.content.SettingBtn.clicked.connect(self.SettingSerial)
        self.content.ExitPopUp.clicked.connect(self.ExitSetting)
        self.content.RelaodBtn.clicked.connect(self.ReLoadSerial)

        self.content.Re_Link_timer.timeout.connect(self.checkSeriaConnection)
        self.content.Re_Link_timer.setInterval(30000)

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.rx_payload = input_node.eval()

            if self.rx_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                # return

            else:
                #print("self.rx_payload = ", self.rx_payload)
                #print("self.rx_payload[0:3] = ", self.rx_payload['msg'][0:3])

                if self.content.Serial_Avialable:
                    if 'msg' in self.rx_payload and self.rx_payload['msg'] is not None:
                        send_data = self.rx_payload['msg'] + "\n"
                        #print("send_data = ", send_data)
                        self.content.serialPort.write(send_data.encode())
                        self.rx_payload['msg'] = None

    def onLinkClicked(self):
        self.content.StartSerial_flag = not self.content.StartSerial_flag

        if self.content.StartSerial_flag:
            #self.ReLoadSerial()
            print("port = ", self.content.COMPort)

            self.content.serialPort = serial.Serial(port=self.content.COMPort, baudrate=self.content.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
            self.content.SwitchSerial.setIcon(QIcon(self.content.on_icon))

            self.content.Link_timer.start()
            print("Serial On Button Checked !!!!")
            self.content.Serial_Avialable = True

        else:
            self.content.Link_timer.stop()
            #print("Redic Button UnChecked !!!!")

            """self.content.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : rgba(0, 124, 212, 150)"
                                   "}")"""
            
            self.content.lbl.setText("Not Running")
            self.content.lbl.setStyleSheet("color: red; font-size:6pt;")

            self.content.Serial_Avialable = False

            if type(self.content.serialPort) != type(None):
                self.content.serialPort.close()

            self.content.SwitchSerial.setIcon(QIcon(self.content.off_icon))
                                   
    def update_data(self):
        #print("Serial Link")

        if self.content.Serial_Avialable and self.content.StartSerial_flag:
            if self.content.TimerBlinkCnt >= 5:
                self.content.TimerBlinkCnt = 0
                if self.content.BlinkingState:

                    self.content.lbl.setText("Running...")
                    self.content.lbl.setStyleSheet("color: green")
                else:
                                    
                    self.content.lbl.setText(" ")

                self.content.BlinkingState = not self.content.BlinkingState

            self.content.TimerBlinkCnt += 1
            self.content.check_link_Error += 1

            if self.content.Serial_Explored():
                if self.content.serialPort is not None:
                    if self.content.serialPort.in_waiting > 0:
                        # Print the contents of the serial data
                        # print("Serial Data In...")
                        serialString = self.content.serialPort.readline()
                        self.payload['result'] = str(serialString, 'utf-8')
                        self.publish_payload()

    def onComPortChanged(self, text):

        if self.content.StartSerial_flag and type(self.content.serialPort) != type(None):
            self.content.serialPort.close()

        self.content.StartSerial_flag = False
        self.content.Serial_Avialable = False

        self.content.SwitchSerial.setIcon(QIcon(self.content.off_icon))

        self.content.COMPort = text
        print("Selec Comport = ", self.content.COMPort)
        self.content.SelectComPort.setCurrentText(str(self.content.COMPort))
        try:
            self.content.serialPort = serial.Serial(port=text, baudrate=self.content.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        except:
            print("SerialException: could not open port")

    def publish_payload(self):
        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

    def SettingSerial(self):
        self.content.PopUplbl.setVisible(True)
        self.content.ExitPopUp.setVisible(True)
        self.content.lblBaudrate.setVisible(True)
        self.content.SettingComPort.setVisible(True)
        self.content.lblBytesize.setVisible(True)
        self.content.lblStopbits.setVisible(True)

    def ExitSetting(self):
        self.content.PopUplbl.setVisible(False)
        self.content.ExitPopUp.setVisible(False)
        self.content.lblBaudrate.setVisible(False)
        self.content.SettingComPort.setVisible(False)
        self.content.lblBytesize.setVisible(False)
        self.content.lblStopbits.setVisible(False)

        self.content.BaudRate = int(str(self.content.SettingComPort.currentText()))
        print("Setting BaudRate = ", self.content.BaudRate)

    def ReLoadSerial(self):

        if self.content.StartSerial_flag and type(self.content.serialPort) != type(None):
            self.content.serialPort.close()

        self.content.StartSerial_flag = False
        self.content.Serial_Avialable = False
        self.content.SelectComPort.clear()
        self.content.SwitchSerial.setIcon(QIcon(self.content.off_icon))

        self.content.Link_timer.stop()

        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            print(desc)
            #print("{}: {} [{}]".format(port, desc, hwid))
            print(port[0:4])
            x = str(desc).find(" (COM")
            print(x)
            print(desc[0:x])

            self.content.SelectComPort.addItem(str(port[0:4]))
            self.content.Serial_Avialable = True

    def checkSeriaConnection(self):
        if self.content.check_link_Error < 5:

            print("Serial Reader Link Not Auto Start then Restart Again!!")

            if type(self.content.serialPort) != type(None):
                self.content.serialPort.close()

            self.content.Serial_Explored()
            time.sleep(1)
            
            self.content.StartSerial_flag = False
            self.onLinkClicked()
            self.content.Re_Link_timer.stop()

        else:
            self.content.check_link_Error = 0
            print("Auto Serial Already Started !!!")
            self.content.Re_Link_timer.stop()