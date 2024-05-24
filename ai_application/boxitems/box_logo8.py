from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId
import time

from pymodbus.client import ModbusTcpClient

class Logo8_Siemens(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.gray_dot = self.Path + "/icons/icons_gray_spot_30.png"
        self.green_dot = self.Path + "/icons/icons_green_spot_30.png"

        self.Logo8_logo = self.Path + "/icons/icons_logo8.png"

        self.lbipport = QLabel("IP : " , self)
        self.lbipport.setAlignment(Qt.AlignLeft)
        self.lbipport.setGeometry(15,10,50,20)
        self.lbipport.setStyleSheet("color: #10E60E; font-size:5pt;")
        
        self.lbipport = QLabel("Port / ID: " , self)
        self.lbipport.setAlignment(Qt.AlignLeft)
        self.lbipport.setGeometry(15,36,70,20)
        self.lbipport.setStyleSheet("color: #10E6EE; font-size:5pt;")

        self.editserver = QLineEdit("192.168.0.3", self)
        self.editserver.setGeometry(35,5,110,20)
        self.editserver.setPlaceholderText("LOGO!8 IP Address")
        self.editserver.setStyleSheet("font-size:6pt;")
        #self.editserver.setEnabled(False)

        self.editport = QLineEdit("502", self)
        self.editport.setGeometry(65,30,50,20)
        self.editport.setPlaceholderText("port")
        self.editport.setStyleSheet("font-size:5pt;")

        self.edit_id = QLineEdit("1", self)
        self.edit_id.setGeometry(115,30,30,20)
        self.edit_id.setPlaceholderText("id")
        self.edit_id.setStyleSheet("font-size:5pt;")

        self.lblP = QLabel("Payload" , self)
        self.lblP.setAlignment(Qt.AlignLeft)
        self.lblP.setGeometry(10,67,35,20)
        self.lblP.setStyleSheet("color: #FFDD00; font-size:5pt;")

        self.lblT = QLabel("Btn Write" , self)
        self.lblT.setAlignment(Qt.AlignLeft)
        self.lblT.setGeometry(10,88,100,20)
        self.lblT.setStyleSheet("color: #42E3C8; font-size:5pt;")

        self.lblF = QLabel("Btn Read" , self)
        self.lblF.setAlignment(Qt.AlignLeft)
        self.lblF.setGeometry(10,110,75,20)
        self.lblF.setStyleSheet("color: #FF9EAA; font-size:5pt;")

        # ==============================================================
        self.lbSETBIT = QLabel("SET" , self)
        self.lbSETBIT.setAlignment(Qt.AlignLeft)
        self.lbSETBIT.setGeometry(98,47,35,20)
        self.lbSETBIT.setStyleSheet("color: lightgreen; font-size:4pt;")

        self.checkbit0 = QCheckBox("bit0",self)
        self.checkbit0.setGeometry(95,57,70,20)
        self.checkbit0.setStyleSheet("color: lightblue; font-size:5pt;")

        self.checkbit1 = QCheckBox("bit1",self)
        self.checkbit1.setGeometry(95,92,70,20)
        self.checkbit1.setStyleSheet("color: lightblue; font-size:5pt;")

        self.checkbit2 = QCheckBox("bit2",self)
        self.checkbit2.setGeometry(95,127,70,20)
        self.checkbit2.setStyleSheet("color: lightblue; font-size:5pt;")

        self.checkbit3 = QCheckBox("bit3",self)
        self.checkbit3.setGeometry(95,162,70,20)
        self.checkbit3.setStyleSheet("color: lightblue; font-size:5pt;")

        #====================================================
        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(50,50)
        graphicsView.setGeometry(QtCore.QRect(5, 135, 50, 50))

        img = QPixmap(self.Logo8_logo)
        self.pixmap.setPixmap(img)

        #====================================================
        self.pixmap_dot = [0 for x in range(4)]
        self.BIT_Dot = [0 for x in range(4)]
        for i in range(len(self.BIT_Dot)):
            
            graphicsView_dot = QGraphicsView(self)
            scene_dot = QGraphicsScene()
            self.pixmap_dot[i] = QGraphicsPixmapItem()
            scene_dot.addItem(self.pixmap_dot[i])
            graphicsView_dot.setScene(scene_dot)

            graphicsView_dot.resize(30,30)
            graphicsView_dot.setGeometry(QtCore.QRect(62, 50 + (i*35), 35, 35))

            self.BIT_Dot[i] = QPixmap(self.gray_dot)
            self.pixmap_dot[i].setPixmap(self.BIT_Dot[i])

        self.lbERROR = QLabel("" , self)
        # self.lbERROR = QLabel("Failed to connect !!!" , self)
        self.lbERROR.setAlignment(Qt.AlignLeft)
        self.lbERROR.setGeometry(5,175,180,20)
        self.lbERROR.setStyleSheet("color: red; font-size:6pt;")

        self.ip_address = "192.168.0.3"     # Replace with the actual IP address of your LOGO!8 PLC
        self.port = 502                     # Default Modbus TCP port is 502
        self.unit_id = 1                    # Unit ID of the LOGO!8 PLC (typically set to 1)

        self.set_bit0 = False
        self.set_bit1 = False
        self.set_bit2 = False
        self.set_bit3 = False

        self.read_values = []

    def serialize(self):
        res = super().serialize()
        res['ip_address'] = self.editserver.text()
        res['port'] = self.editport.text()
        res['unit_id'] = self.edit_id.text()

        res['set_bit0'] = self.set_bit0
        res['set_bit1'] = self.set_bit1
        res['set_bit2'] = self.set_bit2
        res['set_bit3'] = self.set_bit3

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'ip_address' in data:
                self.editserver.setText(data['ip_address'])

            if 'port' in data:
                self.editport.setText(str(data['port']))

            if 'unit_id' in data:
                self.edit_id.setText(str(data['unit_id']))

            if 'set_bit0' in data:
                self.set_bit0 = data['set_bit0']
                if self.set_bit0:
                    self.checkbit0.setChecked(True)

            if 'set_bit1' in data:
                self.set_bit1 = data['set_bit1']
                if self.set_bit1:
                    self.checkbit1.setChecked(True)

            if 'set_bit2' in data:
                self.set_bit2 = data['set_bit2']
                if self.set_bit2:
                    self.checkbit2.setChecked(True)

            if 'set_bit3' in data:
                self.set_bit3 = data['set_bit3']
                if self.set_bit3:
                    self.checkbit3.setChecked(True)

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 1, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(60, 60, 60, 185)
    
# ==================================================================
# ==================================================================

@register_node(OP_NODE_LOGO8)
class Open_CMD(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_logo8.png"
    op_code = OP_NODE_LOGO8
    op_title = "LOGO! 8"
    content_label_objname = "LOGO! 8"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2,3,4], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.logo8_payload = {}

        self.input_payload = {}
        self.input_submit_wr = {}
        self.submit_write = False

        self.input_submit_rd = {}
        self.submit_read = False

        self.wr_command = []
        self.bit4_result = []

        self.Sigle_SnapInput = False
        self.data4bit_wr = [False, False, False, False]

    def initInnerClasses(self):
        self.content = Logo8_Siemens(self)                   # <----------- init UI with data and widget
        #self.grNode = FlowGraphics150x150Process(self)          # <----------- Box Image Draw in Flow_Node_Base
        self.grNode = FlowGraphicsCholeProcess(self)               # <----------- Box Image Draw in Flow_Node_Base

        self.grNode.width = 150
        self.grNode.height = 215

        self.content.checkbit0.stateChanged.connect(self.Check_Bit0)
        self.content.checkbit1.stateChanged.connect(self.Check_Bit1)
        self.content.checkbit2.stateChanged.connect(self.Check_Bit2)
        self.content.checkbit3.stateChanged.connect(self.Check_Bit3)

    def evalImplementation(self):                           # <----------- Create Socket range Index

        # ==================================================
        # Input 1 from Payload

        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.Sigle_SnapInput = False

        else:
            self.input_payload = input_node.eval()

            if self.input_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.Sigle_SnapInput = False

            elif type(self.input_payload) != type(None):
                if 'wr_logo8' in self.input_payload and not self.Sigle_SnapInput:
                    self.Sigle_SnapInput = True

                    self.wr_command = self.input_payload['wr_logo8']
                    if type(self.wr_command) == list:
                        try:
                            client = ModbusTcpClient(self.content.editserver.text(), port=int(self.content.editport.text()))

                            # Connect to the server
                            client.connect()
                            time.sleep(0.1)
                            self.content.lbERROR.setText("")

                            if len(self.wr_command) == 2:
                                coil_address = 8192
                                match self.wr_command[0]:
                                    case 0:
                                        coil_address = 8192
                                    case 1:
                                        coil_address = 8193
                                    case 2:
                                        coil_address = 8194
                                    case 3:
                                        coil_address = 8195
                                    case default:
                                        ...

                                client.write_coil(address=coil_address, value=self.wr_command[1])

                            elif len(self.wr_command) == 4:
                                client.write_coils(address=8192, values=self.wr_command)

                            # Close the connection
                            client.close()
                            self.Sigle_SnapInput = False

                            time.sleep(0.1)
                            self.read_data_logo8()

                        except Exception as error:
                            print("\033[91m {}\033[00m".format(str(error)))
                            self.Sigle_SnapInput = False

                            self.content.lbERROR.setText("Failed to connect !!!")

                if 'rd_logo8' in self.input_payload and not self.Sigle_SnapInput:
                    self.Sigle_SnapInput = True

                    self.read_command = self.input_payload['rd_logo8']
                    try:
                        self.read_data_logo8()
                        self.Sigle_SnapInput = False
                    except Exception as error:
                        print("\033[91m {}\033[00m".format(str(error)))
                        self.Sigle_SnapInput = False

                        self.content.lbERROR.setText("Failed to connect !!!")

        # ===================================================
        # ===================================================
        # Input2 From Submit Button Write
        input_node1 = self.getInput(1)
        if not input_node1:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.submit_write = False

        else:
            self.input_submit_rd = input_node1.eval()

            if self.input_submit_rd is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.submit_write = False

            elif type(self.input_submit_rd) != type(None):
                if 'submit' in self.input_submit_rd:
                    if self.input_submit_rd['submit'] and not self.submit_write:
                        self.submit_write = True

                        try:
                            self.write_data_logo8()
                            time.sleep(0.1)
                            self.read_data_logo8()

                            self.submit_write = False

                        except Exception as error:
                            print("\033[91m {}\033[00m".format(str(error)))
                            self.submit_write = False

                            self.content.lbERROR.setText("Failed to connect !!!")

                    else:
                        self.submit_write = False

        # ===================================================
        # ===================================================
        # Input3 From Submit Button Read
        input_node2 = self.getInput(2)
        if not input_node2:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.submit_read = False

        else:
            self.input_submit_wr = input_node2.eval()

            if self.input_submit_wr is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.submit_read = False

            elif type(self.input_submit_wr) != type(None):
                if 'submit' in self.input_submit_wr:
                    if self.input_submit_wr['submit'] and not self.submit_read:
                        self.submit_read = True

                        try:
                            self.read_data_logo8()
                            self.submit_read = False
                        
                        except Exception as error:
                            print("\033[91m {}\033[00m".format(str(error)))
                            self.submit_read = False

                            self.content.lbERROR.setText("Failed to connect !!!")

                    else:
                        self.submit_read = False

    def Check_Bit0(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_bit0 = True
        
        else:
            self.content.set_bit0 = False

    def Check_Bit1(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_bit1 = True
        
        else:
            self.content.set_bit1 = False

    def Check_Bit2(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_bit2 = True
        
        else:
            self.content.set_bit2 = False

    def Check_Bit3(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_bit3 = True
        
        else:
            self.content.set_bit3 = False

    def write_data_logo8(self):
        client = ModbusTcpClient(self.content.editserver.text(), port=int(self.content.editport.text()))

        # Connect to the server
        client.connect()
        self.content.lbERROR.setText("")

        self.data4bit_wr = [self.content.set_bit0, self.content.set_bit1, self.content.set_bit2, self.content.set_bit3]
        client.write_coils(address=8192, values=self.data4bit_wr)

        # Close the connection
        client.close()

    def read_data_logo8(self):
    
        client = ModbusTcpClient(self.content.editserver.text(), port=int(self.content.editport.text()))

        # Connect to the server9
        client.connect()
        self.content.lbERROR.setText("")
        time.sleep(0.1)

        self.bit4_result = client.read_coils(address=8192, count=8).bits
        coil_0 = client.read_coils(address=8192, count=1).bits[0]
        if coil_0:
            self.content.BIT_Dot[0] = QPixmap(self.content.green_dot)
            self.content.pixmap_dot[0].setPixmap(self.content.BIT_Dot[0])

            self.content.set_bit0 = True
            self.content.checkbit0.setChecked(True)

        else:
            self.content.BIT_Dot[0] = QPixmap(self.content.gray_dot)
            self.content.pixmap_dot[0].setPixmap(self.content.BIT_Dot[0])

            self.content.set_bit0 = False
            self.content.checkbit0.setChecked(False)

        coil_1 = client.read_coils(address=8193, count=1).bits[0]
        if coil_1:
            self.content.BIT_Dot[1] = QPixmap(self.content.green_dot)
            self.content.pixmap_dot[1].setPixmap(self.content.BIT_Dot[1])

            self.content.set_bit1 = True
            self.content.checkbit1.setChecked(True)

        else:
            self.content.BIT_Dot[1] = QPixmap(self.content.gray_dot)
            self.content.pixmap_dot[1].setPixmap(self.content.BIT_Dot[1])

            self.content.set_bit1 = False
            self.content.checkbit1.setChecked(False)

        coil_2 = client.read_coils(address=8194, count=1).bits[0]
        if coil_2:
            self.content.BIT_Dot[2] = QPixmap(self.content.green_dot)
            self.content.pixmap_dot[2].setPixmap(self.content.BIT_Dot[2])

            self.content.set_bit2 = True
            self.content.checkbit2.setChecked(True)

        else:
            self.content.BIT_Dot[2] = QPixmap(self.content.gray_dot)
            self.content.pixmap_dot[2].setPixmap(self.content.BIT_Dot[2])

            self.content.set_bit2 = False
            self.content.checkbit2.setChecked(False)

        coil_3 = client.read_coils(address=8195, count=1).bits[0]
        if coil_3:
            self.content.BIT_Dot[3] = QPixmap(self.content.green_dot)
            self.content.pixmap_dot[3].setPixmap(self.content.BIT_Dot[3])

            self.content.set_bit3 = True
            self.content.checkbit3.setChecked(True)

        else:
            self.content.BIT_Dot[3] = QPixmap(self.content.gray_dot)
            self.content.pixmap_dot[3].setPixmap(self.content.BIT_Dot[3])

            self.content.set_bit3 = False
            self.content.checkbit3.setChecked(False)

        # Close the connection
        client.close()

        self.logo8_payload['logo8_read'] = self.bit4_result

        self.value = self.logo8_payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()
