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
import datetime

import serial.tools.list_ports

class RFID_Link(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.RFIDImagePath = self.Path + "/icons/icons_RFID4040.jpg"
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

        self.img = QPixmap(self.RFIDImagePath)
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
        self.lblComport.setGeometry(15,43,75,15)
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

        self.SelectModel = QComboBox(self)
        self.SelectModel.setGeometry(65,30,80,20)
        self.SelectModel.setStyleSheet("QComboBox"
                                   "{"
                                   "background-color : #33CCFF"
                                   "}") 
        
        self.SelectModel.addItem("None")
        self.SelectModel.addItem("SL500")

        self.SelectModel.activated[str].connect(self.onRFIDModelChanged)

        self.reader_sl500 = None
        self.SL500_state = False

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

        self.Addr_Tag = [0x3D,0x0E,0x20]                         #********* [Arrdess]
        self.Addr_Length = [3,7,3]                                #********* [Length]
        self.Addr_Name = ["engine_type","engine_no","back_no"]    #********* [Name]
        self.Addr_result= ["","",""]  
        self.Addr_count = len(self.Addr_Tag)
        self.Addr_Max = 0

        self.iRefresh = 0
        self.byte= {}

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
        res['COM'] = str(self.SelectComPort.currentText())
        res['sw_flag'] = self.StartSerial_flag 
        res['baudrate'] = self.BaudRate
        res['rfid_model'] = str(self.SelectModel.currentText())

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'serial_ava' in data:
                self.Serial_Avialable = data['serial_ava']

            if 'baudrate' in data:
                self.BaudRate = data['baudrate']
                print("Serial Load self.BaudRate = ", self.BaudRate)

            if 'COM' in data:
                self.COMPort = data['COM']

            if 'rfid_model' in data:
                self.SelectModel.setCurrentText(str(data['rfid_model']))

            if self.Serial_Explored():
                if 'sw_flag' in data:
                    self.StartSerial_flag = data['sw_flag']
                    if str(self.SelectModel.currentText()) == "None":
                        if self.StartSerial_flag:
                            #self.radioState.setChecked(True)
                            self.SwitchSerial.setIcon(QIcon(self.on_icon))
                            
                            self.SelectComPort.setCurrentText(str(self.COMPort))
                            self.serialPort = serial.Serial(port=self.COMPort, baudrate=self.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
                            self.init_Serial_Auto_On()

                        else:
                            self.Link_timer.stop()

                    elif str(self.SelectModel.currentText()) == "SL500":     
                        self.BaudRate = 19200          
                        self.reader_sl500 = SL500_RFID_Reader(self.COMPort, self.BaudRate)
                        self.reader_sl500.set_key('\xFF\xFF\xFF\xFF\xFF\xFF')
                        self.Link_timer.start()

                        self.SwitchSerial.setIcon(QIcon(self.on_icon))
            else:
                self.Re_Link_timer.start()


            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def onRFIDModelChanged(self):
        try:
            self.BaudRate = 19200
            self.reader_sl500 = SL500_RFID_Reader(str(self.SelectComPort.currentText()), self.BaudRate)
            self.reader_sl500.set_key('\xFF\xFF\xFF\xFF\xFF\xFF')
        except:
             print("No RFID Reader model SL500 Detect !!!!")

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

    def init_Serial_Auto_On(self):
        self.Addr_Tag = [0x3D,0x0E,0x20]                         #********* [Arrdess]
        self.Addr_Length =[3,7,3]                                #********* [Length]
        self.Addr_Name =["engine_type","engine_no","back_no"]    #********* [Name]
        self.Addr_result=["","",""]  
        self.Addr_count = len(self.Addr_Tag)
        self.Addr_Max = 0

        for j in range(0,self.Addr_count):
            if self.Addr_Max < self.Addr_Tag[j] + self.Addr_Length[j]:
                self.Addr_Max = self.Addr_Tag[j] + self.Addr_Length[j]

        #time.sleep(0.5)
        self.iRefresh = 0
        self.byte= {}
        print("Auto On Read start.")
        print("###################")

        if str(self.SelectModel.currentText()) == "None":
            self.Re_Link_timer.start()
            
            self.serialPort = serial.Serial(port=self.COMPort, baudrate=self.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
            self.SwitchSerial.setIcon(QIcon(self.on_icon))

            self.Link_timer.start()
            self.Serial_Avialable = True

        elif str(self.SelectModel.currentText()) == "SL500":
            self.SwitchSerial.setIcon(QIcon(self.on_icon))
            self.Link_timer.start()
            self.Serial_Avialable = True

# ====================================================================================================================================
class SL500_RFID_Reader(object):
	"""SL500 RFID Reader Python API by Soft Power Group""" 
	"""SoftPowerGroup.net"""

	"""Full Library for Read/Write data , Read/Write Value ,Inc/Dec Value""" 
	"""Please Contact"""
	"""SoftPowerGroup.net"""

	BAUD_4800	= '\x00'
	BAUD_9600	= '\x01'
	BAUD_14400	= '\x02'
	BAUD_19200	= '\x03'
	BAUD_28800	= '\x04'
	BAUD_38400	= '\x05'
	BAUD_57600	= '\x06'
	BAUD_115200	= '\x07'

	LED_OFF		= '\x00'
	LED_RED		= '\x01'
	LED_GREEN	= '\x02'
	LED_YELLOW	= '\x03'

	TYPE_A		= 'A'
	TYPE_B		= 'B'
	ISO15693	= '1'

	RF_OFF		= '\x00'
	RF_ON		= '\x01'

	REQ_STD		= '\x26'
	REQ_ALL		= '\x52'

	KEY_A		= '\x60'
	KEY_B		= '\x61'

	DEBUG_MODE	= False
	# DEBUG_MODE	= True
	MUTE_MODE	= False

	def __init__(self, port, baudrate):
		super(SL500_RFID_Reader, self).__init__()
		self.ser = serial.Serial(port, baudrate, timeout=0.02)
		self.rf_init_com()
		# self.rf_get_model()
		# self.rf_init_device_number()
		# self.rf_get_device_number()
		self.rf_init_type(self.TYPE_A) 
		self.rf_antenna_sta()

	def info(self):
		print(self.ser)
		print(self.BAUD_19200)
		
	# def min(self, a, b):
	# 	if (a < b):
	# 		return a
	# 	else:
	# 		return b

	# def max(self, a, b):
	# 	if (a > b):
	# 		return a
	# 	else:
	# 		return b

	def debug(self, source):
		if self.DEBUG_MODE:
			if isinstance(source, list):
				output = []
				for i in range(0, len(source)):
					output.insert(i, hex(ord(source[i])))
			else:
				output = source
			print(output)
		else:
			return

	def xor_strings(self, xs, ys):
		return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(xs, ys))


	# def read_response(self):
	# 	all_output = []
	# 	output = ''
	# 	i = 0
	# 	output = self.ser.read()
	# 	while output != '':
	# 		if i == 0:
	# 			pass
	# 		else:
	# 			output = self.ser.read()
	# 		if (i == 8) & (output != '\x00'):
	# 			return False
	# 		if output != '':
	# 			all_output.insert(i, output)
	# 		i += 1
	# 	self.ser.flushOutput()
	# 	return all_output
	def read_response(self):
		all_output = []
		i = 0

		while True:
			output = self.ser.read()
			
			if not output:
				break

			if i == 8 and output != b'\x00':
				return False
			
			all_output.append(output)
			i += 1

		self.ser.flushOutput()
		return all_output

	def send_request(self, dev_id, cmd_code, param):
		length = len(param) + 5
		ver = '\x00'
		buf = []
		buf.insert(0, '\xAA')				# Command head
		buf.insert(1, '\xBB')
		buf.insert(2, chr(length))			# Length
		buf.insert(3, '\x00')
		buf.insert(4, dev_id[0])			# Device ID
		buf.insert(5, dev_id[1])
		buf.insert(6, cmd_code[0])			# Command code
		buf.insert(7, cmd_code[1])

		k = 0
		for i in range(8 , 8 + len(param)):
			buf.insert(i, param[k])
			k += 1
		
		# print('buf A:', buf)
		for i in range(3 , len(buf)):
			# ver = self.xor_strings(ver, buf[i])
			if isinstance(buf[i], bytes):
				# print("The object is of type 'bytes'") 
				buf[i] = chr(buf[i][0])
				# print('buf[i]:', buf[i]) 
				# print(type(buf[i]))

			ver = self.xor_strings(ver, buf[i])

		buf.insert(len(buf), ver)

		buf_16 = [hex(ord(c)) for c in buf]
		buf_16 = [int(x, 16) for x in buf_16]

		# print(buf_16)
		# buf = [0xAA, 0xBB, 0x06, 0x00, 0x00, 0x00, 0x01, 0x01, 0x03, 0x03]

		self.debug(buf)
		self.ser.write(buf_16)
		self.ser.flushInput()

	def rf_init_com(self):
		self.send_request(['\x00','\x00'], ['\x01','\x01'], [self.BAUD_19200])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_get_model(self):
		self.send_request(['\x00','\x00'], ['\x04','\x01'], [])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_init_device_number(self):
		self.send_request(['\x00','\x00'], ['\x02','\x01'], ['\x11','\x12'])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_get_device_number(self):
		self.send_request(['\x00','\x00'], ['\x03','\x01'], [])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_beep(self, time):
		if not self.MUTE_MODE:
			self.send_request(['\x11','\x12'], ['\x06','\x01'], [chr(time)])
			result = self.read_response()
			self.debug(result)
			return result

	def rf_light(self, color):
		self.send_request(['\x11','\x12'], ['\x07','\x01'], [color])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_init_type(self, type):
		self.send_request(['\x00','\x00'], ['\x08','\x01'], [type])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_antenna_sta(self):
		self.send_request(['\x11','\x12'], ['\x0c','\x01'], [self.RF_OFF])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_request(self):
		self.send_request(['\x11','\x12'], ['\x01','\x02'], ['\x52'])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_anticoll(self):
		self.send_request(['\x11','\x12'], ['\x02','\x02'], [])
		result = self.read_response()
		self.debug(result)
		return result

	def rf_select(self, card_id):
		self.send_request(['\x11','\x12'], ['\x03','\x02'], card_id)
		result = self.read_response()
		self.debug(result)
		return result

	def rf_M1_authentication2(self, block, key):
		param = ['\x60', chr(block), key[0], key[1], key[2], key[3], key[4], key[5]]
		self.send_request(['\x11','\x12'], ['\x07','\x02'], param)
		result = self.read_response()
		self.debug(result)
		return result

	def rf_read(self, block):
		self.send_request(['\x11','\x12'], ['\x08','\x02'], [chr(block)])
		result = self.read_response()
		result = self.read_response()
		if result:
			self.debug(result)
			output = ''
			for i in range(9, len(result) - 1):
				output += str(result[i].encode('hex'))
			return output
		else:
			return 'Reading RFID card is failed'

	def read_block(self, block):
		self.rf_light(self.LED_RED)
		if self.rf_request():
			result = self.rf_anticoll()
			if result:
				card_id = [result[9],result[10],result[11],result[12]]
				# print(card_id)
				converted_string = ''.join([byte.hex().upper() for byte in card_id])
				# print(converted_string)

				if self.rf_select(card_id):
					self.rf_beep(1)
					self.rf_light(self.LED_GREEN)
					return converted_string

				# if self.rf_select(card_id):
					# if self.rf_M1_authentication2(block, self.key) != False:
					# 	self.rf_beep(1)
					# 	self.rf_light(self.LED_GREEN)
					# 	return self.rf_read(block)
					# else:
					# 	self.rf_beep(20)
					# 	self.rf_light(self.LED_RED)
					# 	return 'Authentication failed'		
		else:
			# self.rf_beep(20)
			self.rf_light(self.LED_RED)           
			return 'Cannot read RFID card'
	
	def set_key(self, key):
		self.key = key

	def close(self):
		self.ser.close()


	"""Full Library for Read/Write data , Read/Write Value ,Inc/Dec Value""" 
	"""Please Contact"""
	"""SoftPowerGroup.net"""		

# ====================================================================================================================================
            
@register_node(OP_NODE_RFID_READER)
class Open_RFID_READER(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_RFID4848.jpg"
    op_code = OP_NODE_RFID_READER
    op_title = "RFID Reader"
    content_label_objname = "RFID Reader"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = RFID_Link(self)                   # <----------- init UI with data and widget
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

    def evalImplementation(self):                           # <----------- Create Socket range Index
        pass

    def onLinkClicked(self):
        self.content.StartSerial_flag = not self.content.StartSerial_flag

        if self.content.StartSerial_flag:
            #self.ReLoadSerial()
            if str(self.content.SelectModel.currentText()) == "None":
                self.content.Addr_Tag = [0x3D,0x0E,0x20]                         #********* [Arrdess]
                self.content.Addr_Length =[3,7,3]                                #********* [Length]
                self.content.Addr_Name =["engine_type","engine_no","back_no"]    #********* [Name]
                self.content.Addr_result=["","",""]  
                self.content.Addr_count = len(self.content.Addr_Tag)
                self.content.Addr_Max = 0

                for j in range(0,self.content.Addr_count):
                    if self.content.Addr_Max < self.content.Addr_Tag[j] + self.content.Addr_Length[j]:
                        self.content.Addr_Max = self.content.Addr_Tag[j] + self.content.Addr_Length[j]

                #time.sleep(0.5)
                self.content.iRefresh = 0
                self.content.byte= {}
                print("Read start.")
                print("##############")
                
                try:
                    self.content.serialPort = serial.Serial(port=self.content.COMPort, baudrate=self.content.BaudRate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
                    self.content.SwitchSerial.setIcon(QIcon(self.content.on_icon))

                    self.content.Link_timer.start()
                    print("Serial On Button Checked !!!!")
                    self.content.Serial_Avialable = True
                except:
                    print("SerialException: could not open port")

            elif str(self.content.SelectModel.currentText()) == "SL500":
                self.content.SwitchSerial.setIcon(QIcon(self.content.on_icon))

                self.content.BaudRate = 19200
                self.content.reader_sl500 = SL500_RFID_Reader(str(self.content.SelectComPort.currentText()), self.content.BaudRate)
                self.content.reader_sl500.set_key('\xFF\xFF\xFF\xFF\xFF\xFF')

                self.content.Link_timer.start()
                self.content.Serial_Avialable = True

        else:
            self.content.Link_timer.stop()
            #print("Redic Button UnChecked !!!!")

            """self.content.radioState.setStyleSheet("QRadioButton"
                                   "{"
                                   "background-color : rgba(0, 124, 212, 150)"
                                   "}")"""
            
            self.content.lbl.setText("Not Running")
            self.content.lbl.setStyleSheet("color: red")

            self.content.Serial_Avialable = False

            if str(self.content.SelectModel.currentText()) == "None":
                if type(self.content.serialPort) != type(None):
                    self.content.serialPort.close()

            elif str(self.content.SelectModel.currentText()) == "SL500":
                self.content.reader_sl500.close()

            self.content.SwitchSerial.setIcon(QIcon(self.content.off_icon))
                                   
    def update_data(self):
        #print("Serial Link")

        if self.content.Serial_Avialable and self.content.StartSerial_flag:
            if self.content.TimerBlinkCnt >= 5:
                self.content.TimerBlinkCnt = 0
                if self.content.BlinkingState:

                    self.content.lbl.setText("Running...")
                    self.content.lbl.setStyleSheet("color: green")

                    self.payload['result'] = ""
                else:
                                    
                    self.content.lbl.setText(" ")

                self.content.BlinkingState = not self.content.BlinkingState

            self.content.TimerBlinkCnt += 1
            self.content.check_link_Error += 1

            if str(self.content.SelectModel.currentText()) == "None":
                try:
                    msgInfo=""
                    self.Get_Data(0)
                    self.content.byte = self.content.serialPort.read(4)

                    if len(self.content.byte)>=4:
                    
                        if self.content.byte[0]==int(0xBD) and self.content.byte[3]==int(0x00):   # Check Header=0xBD , Status = 0x00
                            #Tag_size=ord(byte[1])-3                    # Get Tag size    
                            Tag_size=(self.content.byte[1])-3                  
                            
                            Page_tag_use=[0]
                            
                            for j in range(0,self.content.Addr_count):
                                Page_Tag = self.content.Addr_Tag[j] / Tag_size  
                                                        
                                isDuplicate=False
                                for k in range(0,len(Page_tag_use)):
                                    
                                    if Page_tag_use[k]==Page_Tag:
                                        isDuplicate=True
                                        
                                if not isDuplicate : 
                                    Page_tag_use.append(int(Page_Tag))
                                    

                                Page_Tag = (self.content.Addr_Tag[j]+self.content.Addr_Length[j]-1)/ Tag_size                            
                                isDuplicate=False
                                for k in range(0,len(Page_tag_use)):
                                    if Page_tag_use[k]==Page_Tag:
                                        isDuplicate=True
                                if not isDuplicate : 
                                    Page_tag_use.append(int(Page_Tag))
                                    #print('append2: ', Page_Tag)

                            Data_tag = [chr(0x20)]
                            for k in range(1,self.content.Addr_Max):
                                Data_tag.append(chr(0x20))
                                #print('Data_tag: ',Data_tag)
                            for k in range(0,Tag_size):
                                Char = self.content.serialPort.read(1)
                                #print('ord(Char): ', ord(Char))
                                #print('0x20: ', 0x20)
                                if ord(Char)>=0x20:
                                    #print('Data_tag[k]: ', Data_tag[k])
                                    Data_tag[k]=Char

                            
                            isTagError = False
                            #print('len(Page_tag_use): ',len(Page_tag_use))
                            for j in range(1,len(Page_tag_use)):
                                #time.sleep(0.001)
                                #print('j: ', j)
                                #print('Page_tag_use[j]: ', Page_tag_use[j])
                                self.Get_Data(Page_tag_use[j])
                                self.content.byte = self.content.serialPort.read(4)
                                if len(self.content.byte)>=4:
                                    #print('type byte[3]: ', type(byte[3]), ':', 'type chr(0x00): ', type(int(0x00)))
                                    #print('byte[3]: ', byte[3], ':', 'chr(0x00): ', int(0x00))
                                    #if byte[0]==chr(0xBD) and byte[3]==chr(0x00): 
                                    if self.content.byte[0]==int(0xBD) and self.content.byte[3]==int(0x00):
                                        #Tag_size=ord(byte[1])-3
                                        Tag_size=(self.content.byte[1])-3
                                        iStart=Page_tag_use[j]*Tag_size
                                        iStop=iStart+Tag_size
                                        for k in range(iStart,iStop):
                                            Char = self.content.serialPort.read(1)
                                            if ord(Char)>=0x20:
                                                Data_tag[k]=Char

                                    else:
                                        isTagError = True  
                                        print('isTagError chr: ', isTagError)                      
                                        break
                                else:
                                    isTagError = True
                                    print('isTagError len: ', isTagError) 
                                    break

                            #print('isTagError: ', isTagError)
                            if not isTagError:
                                self.content.iRefresh=0    
                                msg = {}
                                msg["status"] = "OK"                
                                for j in range(0,self.content.Addr_count):
                                    Data_Result=""
                                    iStart=self.content.Addr_Tag[j]
                                    iStop=iStart+self.content.Addr_Length[j]
                                    for k in range(iStart,iStop):
                                        #Data_Result+=Data_tag[k]
                                        Data_Result+=str(Data_tag[k],'utf-8')
                                    self.content.Addr_result[j] = Data_Result        
                                    #msg[str(Addr_Name[j])] = Addr_result[j]    
                                    msg[str(self.content.Addr_Name[j])] = self.content.Addr_result[j]  

                                print('msg: ', msg)
                                print('engine type: ', msg['engine_type'])
                                print('engine no: ', msg['engine_no'])
                                print('backno: ', msg['back_no'])
                                self.payload['engine_type'] = msg['engine_type']
                                self.payload['engine_no'] = msg['engine_no']
                                self.payload['backno'] = msg['back_no']
                                self.payload['result'] = msg['back_no'] + " - " + msg['engine_type'] + msg['engine_no']
                                
                                #print("############## "+"Tag size = "+str(Tag_size*0x100)+" byte ; time = " + str(datetime.datetime.now().time()))
                                #time.sleep(2)   #********* Delay 5 Sec to repeat read **********

                                self.payload['tag_size'] = str(Tag_size*0x100)
                                self.payload['rfid_timestamp'] = str(datetime.datetime.now().time())

                                self.publish_payload()
                        else:
                            msgInfo = "No Tag"
                            self.payload['result'] = msgInfo
                            self.publish_payload()
                    
                    elif len(self.content.byte)==0:
                        msgInfo="Can not detect RFID reader"
                        self.content.iRefresh=50      

                        self.payload['result'] = msgInfo
                        self.publish_payload()

                    if self.content.iRefresh>=50 and len(msgInfo)>0:
                        self.content.iRefresh=0
                        print(msgInfo)

                        self.payload['result'] = msgInfo
                        self.publish_payload()

                    else:
                        self.content.iRefresh+=1

                except Exception as err:
                    print("##### Read Error ######")
                    print(err)
                    #serial.Serial(SERIAL_PORT, SERIAL_RATE).close()
                    #time.sleep(1)
                    #ser = serial.Serial(SERIAL_PORT, SERIAL_RATE, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=0.1)
                    #time.sleep(0.001)
                    #print(self.content.ser.in_waiting)
                    # if self.content.ser.in_waiting > 0:
                    #     # Print the contents of the serial data
                    #     # print("Serial Data In...")
                    #     serialString = self.content.ser.readline()
                    #     self.payload['result'] = str(serialString, 'utf-8')
                    #     self.publish_payload()

            elif str(self.content.SelectModel.currentText()) == "SL500":
                self.card_data = ""
                try:
                    self.card_data = self.content.reader_sl500.read_block(0)                    

                except:
                    if not self.content.SL500_state:
                        print("\033[91m {}\033[00m".format("RFID Reader SL500 link down !!!"))

                        self.content.lbl.setText("Not Running")
                        self.content.lbl.setStyleSheet("color: red")
                        self.payload['result'] = "SL500 link down"

                        self.content.reader_sl500.close()

                        self.content.SL500_state = True
                        self.content.SwitchSerial.setIcon(QIcon(self.content.off_icon))

                        self.content.Link_timer.stop()
                        self.content.Re_Link_timer.start()

                if type(self.card_data) != type(None):
                    if len(self.card_data) == 8:
                        self.payload['result'] = self.card_data

                self.publish_payload()

    def Get_Data(self,Addr):
        #print('Addr: ', Addr)
        values = bytearray([0xBA, 0x04, 0x33, Addr, 0x01, 0x00])
        #print('Chksum(values): ', Chksum(values))
        values[5]=self.Chksum(values)
        self.content.serialPort.flushInput()        
        self.content.serialPort.write(values)
        time.sleep(0.01)    
    
    def Chksum(self,dataByte):
        Chk = dataByte[0]    
        for i in range (1,5):
            Chk = Chk ^ dataByte[i]            
        return Chk            


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
            print("RFID Reader Serial Link Not Auto Start then Restart Again!!")

            if self.content.serialPort is not None:
                self.content.serialPort.close()

            self.content.Serial_Explored()
            time.sleep(1)
            
            self.content.StartSerial_flag = False
            self.onLinkClicked()
            self.content.Re_Link_timer.stop()

        else:
            if str(self.content.SelectModel.currentText()) == "None":
                self.content.check_link_Error = 0
                print("Auto RFID Already Started !!!")
                self.content.Re_Link_timer.stop()

            elif str(self.content.SelectModel.currentText()) == "SL500":
                print("Auto RFID Reader SL500 Already Re-Conneted !!!")
                self.content.Re_Link_timer.stop()

                self.content.BaudRate = 19200          
                self.content.reader_sl500 = SL500_RFID_Reader(self.content.COMPort, self.content.BaudRate)
                self.content.reader_sl500.set_key('\xFF\xFF\xFF\xFF\xFF\xFF')
                self.content.Link_timer.start()

                self.content.SL500_state = False
                self.content.SwitchSerial.setIcon(QIcon(self.content.on_icon))

            
        