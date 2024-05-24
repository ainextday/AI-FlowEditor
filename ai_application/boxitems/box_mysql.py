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

import mysql.connector
from mysql.connector import errorcode

from datetime import datetime

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId
import time
import sys

class MySQL(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        self.adddatabase_icon = self.Path + "/icons/icons_database_50.png"
        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        animate_movie = self.Path + "/icons/icons_data_monitor.gif"

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(125,78,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        self.lbl_link = QLabel("Localhost", self)
        self.lbl_link.setGeometry(QtCore.QRect(101, 22, 60, 30))
        self.lbl_link.setStyleSheet("color: lightgreen; font-size:5pt;")
        # self.lbl_link.setVisible(False)

        self.lbl_Onlielink = QLabel("Online", self)
        self.lbl_Onlielink.setGeometry(QtCore.QRect(113, 44, 60, 30))
        self.lbl_Onlielink.setStyleSheet("color: pink; font-size:5pt;")
        # self.lbl_Onlielink.setVisible(False)

        #====================================================
        # Loading the GIF
        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(7, 5, 90, 90))
        self.label.setMinimumSize(QtCore.QSize(90, 90))
        self.label.setMaximumSize(QtCore.QSize(90, 90))
        self.label.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:15pt;color:lightblue; border: 1px solid black; border-radius: 3%")

        self.movie = QMovie(animate_movie)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        #====================================================

        #====================================================
        # Database Image
        self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(55,55)
        self.graphicsView.setGeometry(QtCore.QRect(100, 26, 52, 52))

        img = QPixmap(self.adddatabase_icon)
        self.pixmap.setPixmap(img)

        self.graphicsView.setVisible(False)
        #====================================================

        self.SwitchDatabase = QPushButton(self)
        self.SwitchDatabase.setGeometry(110,5,37,20)
        self.SwitchDatabase.setIcon(QIcon(self.off_icon))
        self.SwitchDatabase.setIconSize(QtCore.QSize(37,20))
        self.SwitchDatabase.setStyleSheet("background-color: transparent; border: 0px;")  

        self.lbl_dbname = QLabel("No Database Name !!", self)
        self.lbl_dbname.setGeometry(QtCore.QRect(3, 78, 118, 20))
        self.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: red; font-size:6pt;")

        # ===========================================
        # Local Host
        self.mydb = None

        self.host = ""
        self.user = ""
        self.password = ""
        self.dbname = ""

        self.ConnectionStatus_flag = False
        self.ConnectionBlink = 0

        self.mycursor = None

        self.set_UseLocalhost = False
        self.database_link = False

        self.sqlUpdate_flag = False

        # ===========================================
        # Online Host
        self.my_onlinedb = None

        self.host_online = ""
        self.user_online = ""
        self.password_online = ""
        self.dbname_online = ""

        self.ConnectionStatus_online_flag = False
        self.Connection_onlineBlink = 0

        self.mycursor_online = None

        self.set_UseOnlinehost = False
        self.database_onlinelink = False

        self.sqlUpdate_onlineflag = False
        # ===========================================

        self.Connection_timer = QtCore.QTimer(self)
        self.ListGlobalTimer = []

        self.Global = GlobalVariable()

        self.On_Start_MySQL = False
        # =============================================================================
        # Local Host
        if self.Global.hasGlobal("GlobalLocalMySQL"):
            self.On_Start_MySQL = self.Global.getGlobal("GlobalLocalMySQL")

        # =============================================================================
        # Online Host
        self.On_Start_MySQL_Online = False
        if self.Global.hasGlobal("On_Start_MySQL_Online"):
            self.On_Start_MySQL_Online = self.Global.getGlobal("On_Start_MySQL_Online")

        # =============================================================================
        if self.Global.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(self.Global.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.Connection_timer)
            self.Global.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        # =============================================================================
            
        # ==========================================================
        # For evalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['mysql_host'] = self.host
        res['mysql_user'] = self.user
        res['mysql_password'] = self.password
        res['mysql_dbname'] = self.dbname
        res['use_localhost'] = self.set_UseLocalhost

        res['mysql_host_online'] = self.host_online
        res['mysql_user_online'] = self.user_online
        res['mysql_password_online'] = self.password_online
        res['mysql_dbname_online'] = self.dbname_online
        res['use_onlinehost'] = self.set_UseOnlinehost

        res['auto_connect'] = self.ConnectionStatus_flag
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            if 'use_localhost' in data:
                self.set_UseLocalhost = data['use_localhost']

                if self.set_UseLocalhost:
                    if self.Global.hasGlobal("GlobalLocalMySQL"):
                        if not self.Global.getGlobal("GlobalLocalMySQL"):
                            print("Xampp Directory :", self.Path[:-8] + "Database/xampp")
                            if not os.path.isfile(self.Path[:-8] + "Database/xampp/Latest_directory.txt"):
                                file = open(self.Path[:-8] + "Database/xampp/Latest_directory.txt",'w')
                                file.write(self.Path[:-8])
                                file.close()

                                # Request Set up new xampp
                                self.OnLoad_exe_command("setup_xampp.bat")

                            else:
                                with open(self.Path[:-8] + "Database/xampp/Latest_directory.txt", 'r') as file:
                                    # Read the entire content of the file into a string
                                    Last_xampp_dir = file.read()
                                    if Last_xampp_dir != self.Path[:-8]:
                                        # Request Setup new xampp
                                        print("Run Setup new xampp")
                                        self.OnLoad_exe_command("setup_xampp.bat")

                                        file = open(self.Path[:-8] + "Database/xampp/Latest_directory.txt",'w')
                                        file.write(self.Path[:-8])
                                        file.close()

                                    else:
                                        if self.set_UseLocalhost and not self.On_Start_MySQL:
                                            self.On_Start_MySQL = True

                                            # Start Apache and Start MySQL
                                            # self.OnLoad_exe_command("apache_start.bat")
                                            self.OnLoad_exe_command("mysql_start.bat")

                                            self.Global.setGlobal("GlobalLocalMySQL", self.On_Start_MySQL)
                                            print("\033[92m {}\033[00m".format("deserialize ==> Start MySQL Localhost"))

            if 'mysql_host' in data:
                self.host = data['mysql_host']

            if 'mysql_user' in data:
                self.user = data['mysql_user']

            if 'mysql_password' in data:
                self.password = data['mysql_password']

            if 'mysql_dbname' in data:
                self.dbname = data['mysql_dbname']
                if len(self.dbname) > 0:
                    self.lbl_dbname.setText(self.dbname)
                    self.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: blue; font-size:6pt;")

            if 'mysql_host_online' in data:
                self.host_online = data['mysql_host_online']

            if 'mysql_user_online' in data:
                self.user_online = data['mysql_user_online']

            if 'mysql_password_online' in data:
                self.password_online = data['mysql_password_online']

            if 'mysql_dbname_online' in data:
                self.dbname_online = data['mysql_dbname_online']

            if 'use_onlinehost' in data:
                self.set_UseOnlinehost = data['use_onlinehost']

            if 'auto_connect' in data:
                self.ConnectionStatus_flag = data['auto_connect']
                # Check first innit Xampp
                self.check_xampp_innit()
                print("auto_connect :", self.ConnectionStatus_flag)
                if self.ConnectionStatus_flag:
                    if self.set_UseLocalhost and not self.On_Start_MySQL:
                        self.On_Start_MySQL = True

                        # Start Apache and Start MySQL
                        # self.OnLoad_exe_command("apache_start.bat")
                        self.OnLoad_exe_command("mysql_start.bat")

                        self.Global.setGlobal("GlobalLocalMySQL", self.On_Start_MySQL)
                        print("\033[92m {}\033[00m".format("auto_connect ==> Start MySQL Localhost"))

                        self.reconnect_localhost()
                

                    # Check If Also Using Online MySQL
                    if self.set_UseOnlinehost and not self.On_Start_MySQL_Online:
                        self.On_Start_MySQL_Online = True

                        self.reconnect_onlinehost()
      

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def MySQL_Connection(self):
        try:
            if len(self.dbname) > 0:
                if self.set_UseLocalhost:
                    self.host = "localhost"

                self.mydb = mysql.connector.connect(
                    host = self.host,
                    user = self.user,
                    password = self.password,
                    database = self.dbname
                )
                print("self.mydb with database = ", self.mydb)

                return True

            else:
                self.mydb = mysql.connector.connect(
                    host = self.host,
                    user = self.user,
                    password = self.password
                )
                print("Connection self.mydb = ", self.mydb)

                return True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                return False

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                return False

            else:
                print(err)
                return False
            
    def reconnect_localhost(self):
        #self.mycursor = self.mydb.cursor()
        #print("Auto Connect self.mycursor = ", self.mycursor)
        
        self.MySQL_Connection()

        self.mycursor = self.mydb.cursor()
        #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
        # get list of all databases
        self.mycursor.execute("SHOW DATABASES")

        #print all databases
        print("onload")
        for db in self.mycursor:
            print(db)
            if db[0] ==  self.dbname:
                self.database_link = True
                print("On load Auto Start Connect MySQL Database  !!!!")
                self.SwitchDatabase.setIcon(QIcon(self.on_icon))
                self.Connection_timer.start()

                self.movie.start()

    def reconnect_onlinehost(self):
        self.my_onlinedb = mysql.connector.connect(
            host = self.host_online,
            user = self.user_online,
            password = self.password_online,
            database = self.dbname_online
        )

        self.mycursor_online = self.my_onlinedb.cursor()
        #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
        # get list of all databases
        self.mycursor_online.execute("SHOW DATABASES")

        #print all databases
        for db in self.mycursor_online:
            print(db)
            if db[0] ==  self.dbname_online:
                self.database_onlinelink = True
                self.Global.setGlobal("On_Start_MySQL_Online", self.On_Start_MySQL_Online)
                print("\033[94m {}\033[00m".format("auto_connect ==> Connect to Online MySQL"))

                self.SwitchDatabase.setIcon(QIcon(self.on_icon))
                self.Connection_timer.start()

                self.movie.start()

            
    def OnLoad_exe_command(self,commad_script):
        root_part = self.Path[0:2]

        shell = client.Dispatch("WScript.Shell")
        run_cmdScript = Exec_cmdScript()
        run_cmdScript.open_cmd(shell)
        run_cmdScript.activate_venv(shell, root_part, self.Path[:-8] + "Database/xampp")
        run_cmdScript.run_cmd_script(shell, commad_script)
        time.sleep(1)
        run_cmdScript.run_cmd_script(shell, "  exit")

    def check_xampp_innit(self):
        print("check_xampp_innit ==> Directory :", self.Path[:-8] + "Database/xampp")
        if not os.path.isfile(self.Path[:-8] + "Database/xampp/Latest_directory.txt"):
            file = open(self.Path[:-8] + "Database/xampp/Latest_directory.txt",'w')
            file.write(self.Path[:-8])
            file.close()

            # Request Set up new xampp
            self.OnLoad_exe_command("setup_xampp.bat")

        else:
            with open(self.Path[:-8] + "Database/xampp/Latest_directory.txt", 'r') as file:
                # Read the entire content of the file into a string
                Last_xampp_dir = file.read()
                if Last_xampp_dir != self.Path[:-8]:
                    # Request Setup new xampp
                    print("Run Setup new xampp")
                    self.OnLoad_exe_command("setup_xampp.bat")

                    file = open(self.Path[:-8] + "Database/xampp/Latest_directory.txt",'w')
                    file.write(self.Path[:-8])
                    file.close()
            
# ==================================================================
class Exec_cmdScript:
    def set_cmd_to_foreground(self, hwnd, extra):
        """sets first command prompt to forgeround"""

        if "cmd.exe" in GetWindowText(hwnd):
            SetForegroundWindow(hwnd)
            return

    def get_pid(self):
        """gets process id of command prompt on foreground"""

        window = GetForegroundWindow()
        return GetWindowThreadProcessId(window)[1]
    
    def activate_venv(self, shell, root_path, venv_location):
        """activates venv of the active command prompt"""

        print("root_path : ", root_path)
        
        shell.AppActivate(self.get_pid())
        shell.SendKeys("cd \ {ENTER}")
        shell.SendKeys("%s {ENTER}" % root_path)
        shell.SendKeys(r"cd %s {ENTER}" % venv_location)

    def run_cmd_script(self,shell, script):
        """runs the py script"""

        # shell.SendKeys("cd ../..{ENTER}")
        shell.SendKeys(f"{script}"+ " {ENTER}")

    def open_cmd(self, shell):
        """ opens cmd """

        shell.run("cmd.exe")
        time.sleep(1)

# ========================================================================
# ========================================================================
class MySQLSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class MySQLSetting ---> MySQL Setting Function')

        self.content = content

        self.SetHost = self.content.host
        self.SetUser = self.content.user
        self.SetPassword = self.content.password
        self.databasname = self.content.dbname

        self.title = "My SQL Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 500
        self.height = 430
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        #================================================
        # Host
        self.lbl1 = QLabel("Host: ", self)
        self.lbl1.setGeometry(QtCore.QRect(10, 35, 40, 20))

        self.editHostName = QLineEdit("",self)
        self.editHostName.setGeometry(80,35,400,20)
        self.editHostName.setPlaceholderText("localhost")

        # self.localhost_ready = QLabel("Localhost Or http://127.0.0.1 ( Activated )", self)
        # self.localhost_ready.setGeometry(QtCore.QRect(130, 35, 250, 20))
        # self.localhost_ready.setStyleSheet("color: lightgreen; font-size:8pt;")

        # ===============================================
        # Localhost
        self.UseLocalhost = QCheckBox("MySQL Localhost",self)
        self.UseLocalhost.setGeometry(10,5,175,25)
        self.UseLocalhost.setStyleSheet("color: pink; font-size:8pt;")

        self.StartApache = QPushButton("Start Apache", self)
        self.StartApache.setGeometry(180,5,125,25)
        self.StartApache.clicked.connect(self.ManualStartApache)

        self.XamppControl = QPushButton("Xampp - Control", self)
        self.XamppControl.setGeometry(325,5,150,25)
        self.XamppControl.clicked.connect(self.ManualStartXampp)

        self.CreateDatabase = QPushButton("Link To Database", self)
        self.CreateDatabase.setGeometry(10,115,150,30)
        self.CreateDatabase.setEnabled(False)
        self.CreateDatabase.clicked.connect(self.LinkMyDatabase)

        # print("self.content.set_UseLocalhost :", self.content.set_UseLocalhost)
        if self.content.set_UseLocalhost:
            self.UseLocalhost.setChecked(True)
            self.CreateDatabase.setEnabled(True)
    
            self.editHostName.setText("localhost Or http://127.0.0.1 ( Activated )")
            self.editHostName.setStyleSheet("color: lightgreen; font-size:8pt;")
            self.editHostName.setEnabled(False)

            self.SetHost = "localhost"
            self.SetUser = "root"

        else:
            self.UseLocalhost.setChecked(False)
            self.CreateDatabase.setEnabled(False)
            self.editHostName.setEnabled(True)
            self.editHostName.setText(self.SetHost)

        self.UseLocalhost.stateChanged.connect(self.ChangeMySQL_Host)

        #=================================================
        # User
        self.lbl2 = QLabel("User: ", self)
        self.lbl2.setGeometry(QtCore.QRect(10, 60, 40, 20))

        self.editUserName = QLineEdit("",self)
        self.editUserName.setGeometry(80,60,400,20)
        self.editUserName.setPlaceholderText("your username")

        #=================================================
        # Password
        self.lbl3 = QLabel("Password: ", self)
        self.lbl3.setGeometry(QtCore.QRect(10, 85, 60, 20))

        self.editPassword = QLineEdit("",self)
        self.editPassword.setGeometry(80,85,400,20)
        self.editPassword.setPlaceholderText("your password")

        self.editUserName.setText(self.SetUser)
        self.editPassword.setText(self.SetPassword)

        self.editDatabase = QLineEdit("",self)
        self.editDatabase.setGeometry(165,120,315,20)
        self.editDatabase.setPlaceholderText("Database Name")

        self.lbl_linktodb = QLabel("Localhost MySQL Already linkage !!", self)
        self.lbl_linktodb.setGeometry(QtCore.QRect(10, 155, 650, 30))
        self.lbl_linktodb.setStyleSheet("color: lightgreen; font-size:10pt;")
        self.lbl_linktodb.setVisible(False)

        # ================================================================================
        # Local Host 
        if len(self.content.dbname) > 0:  
            print("Exiting Global.hasGlobal(mysql_dbname)")

            self.databasname = self.content.dbname
            print("Open DB Name from load Global with self.databasname = ", self.databasname)

            # self.lbltitledbname.setVisible(True)
            # self.lbldbname.setVisible(True)
            self.editDatabase.setText(self.databasname)

            try:
                if self.content.Global.hasGlobal("GlobalLocalMySQL"): 
                    if self.content.Global.getGlobal("GlobalLocalMySQL"): 
                        if self.content.set_UseLocalhost:
                            self.SetHost = "localhost"

                        else:
                            self.SetHost = self.editHostName.text()

                        self.content.mydbtb = mysql.connector.connect(
                            host = self.SetHost,
                            user = self.editUserName.text(),
                            password = self.editPassword.text(),
                            database= self.databasname
                        )

                        self.content.mycursor = self.content.mydbtb.cursor()
                        #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                        # get list of all databases
                        self.content.mycursor.execute("SHOW DATABASES")

                        #print all databases
                        for db in self.content.mycursor:
                            print(db)
                            if db[0] ==  self.editDatabase.text():
                                self.content.database_link = True

                                self.content.lbl_dbname.setText(self.editDatabase.text())
                                self.content.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: blue; font-size:6pt;")

                                self.lbl_linktodb.setVisible(True)

                        if not self.content.database_link:
                            self.lbl_linktodb.setText("No Database Name in MySQL")
                            self.lbl_linktodb.setStyleSheet("color: red; font-size:10pt;")

            except Exception as e:
                self.lbl_linktodb.setText("Fail linkage to Localhost")
                self.lbl_linktodb.setStyleSheet("color: red; font-size:10pt;")
                print(e)

        # else:
        #     self.CreateDatabase.setVisible(True)
        #     self.editDatabase.setVisible(True)

        # ================================================================================
        # ================================================================================
        # Online Host + Y position 205
        Online_Position = 200
        self.UseOnline_host = QCheckBox("MySQL Online Host",self)
        self.UseOnline_host.setGeometry(10,Online_Position + 5,200,25)
        self.UseOnline_host.setStyleSheet("color: orange; font-size:8pt;")

        # Online Host
        self.lbl_onlineHost = QLabel("Online Host: ", self)
        self.lbl_onlineHost.setGeometry(QtCore.QRect(10, Online_Position + 35, 100, 20))

        self.edit_OnlineHostName = QLineEdit("",self)
        self.edit_OnlineHostName.setGeometry(120, Online_Position + 35,355,20)
        self.edit_OnlineHostName.setPlaceholderText("103.74.254.101")
        self.edit_OnlineHostName.setText(self.content.host_online)

        self.Create_LinkOnlineDatabase = QPushButton("Link To Online Database", self)
        self.Create_LinkOnlineDatabase.setGeometry(10,Online_Position + 115,200,30)
        self.Create_LinkOnlineDatabase.setEnabled(False)
        self.Create_LinkOnlineDatabase.clicked.connect(self.Link_OnlineMyDatabase)

        if self.content.set_UseOnlinehost:
            self.UseOnline_host.setChecked(True)
            self.Create_LinkOnlineDatabase.setEnabled(True)

        else:
            self.UseOnline_host.setChecked(False)
            self.Create_LinkOnlineDatabase.setEnabled(False)

        self.UseOnline_host.stateChanged.connect(self.ChangeMySQL_OnlineHost)

        #=================================================
        # Online User
        self.lbl_online_user = QLabel("Online User: ", self)
        self.lbl_online_user.setGeometry(QtCore.QRect(10, Online_Position + 60, 100, 20))

        self.edit_OnlineUserName = QLineEdit("",self)
        self.edit_OnlineUserName.setGeometry(120, Online_Position + 60,355,20)
        self.edit_OnlineUserName.setPlaceholderText("your username")
        self.edit_OnlineUserName.setText(self.content.user_online)

        #=================================================
        # Online Password
        self.lbl_onlinePass = QLabel("Online Password: ", self)
        self.lbl_onlinePass.setGeometry(QtCore.QRect(10, Online_Position + 85, 100, 20))

        self.edit_OnlinePassword = QLineEdit("",self)
        self.edit_OnlinePassword.setGeometry(120,Online_Position + 85,355,20)
        self.edit_OnlinePassword.setPlaceholderText("your password")
        self.edit_OnlinePassword.setText(self.content.password_online)

        self.edit_OnlineDatabase = QLineEdit("",self)
        self.edit_OnlineDatabase.setGeometry(215,Online_Position + 120,260,20)
        self.edit_OnlineDatabase.setPlaceholderText("Database Name")
        self.edit_OnlineDatabase.setText(self.content.dbname_online)

        self.lbl_linktoOnlinedb = QLabel("Online MySQL Already linkage !!", self)
        self.lbl_linktoOnlinedb.setGeometry(QtCore.QRect(10, Online_Position + 155, 470, 30))
        self.lbl_linktoOnlinedb.setStyleSheet("color: yellow; font-size:10pt;")
        self.lbl_linktoOnlinedb.setVisible(False)

        self.Link_OnlineMyDatabase()

        # ================================================================================

    def ChangeMySQL_OnlineHost(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_UseOnlinehost = True
            self.Create_LinkOnlineDatabase.setEnabled(True)

        else:
            self.content.set_UseOnlinehost = False

    def Link_OnlineMyDatabase(self):
        if self.content.set_UseOnlinehost:
            if len(self.edit_OnlineHostName.text()) > 0 and len(self.edit_OnlineHostName.text()) > 0 and len(self.edit_OnlinePassword.text()) > 0 and len(self.edit_OnlineDatabase.text()) > 0:
                self.content.my_onlinedb = mysql.connector.connect(
                    host = self.content.host_online,
                    user = self.content.user_online,
                    password = self.content.password_online,
                    database = self.content.dbname_online
                )

                self.content.mycursor_online = self.content.my_onlinedb.cursor()
                #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                # get list of all databases
                self.content.mycursor_online.execute("SHOW DATABASES")

                #print all databases
                for db in self.content.mycursor_online:
                    print(db)
                    if db[0] ==  self.content.dbname_online:
                        self.content.database_onlinelink = True
                        self.lbl_linktoOnlinedb.setVisible(True)

                if not self.content.database_onlinelink:
                        self.lbl_linktodb.setText("No Online Database")
                        self.lbl_linktodb.setStyleSheet("color: red; font-size:10pt;")

            else:
                print("\033[91m {}\033[00m".format("Still not set Online Database !!!"))


    def LinkMyDatabase(self):
            print("Link to database to ", str(self.editDatabase.text()))
            if not self.content.On_Start_MySQL:
                self.content.On_Start_MySQL = True

                # Start Apache and Start MySQL
                # self.exe_command("apache_start.bat")
                self.exe_command("mysql_start.bat")

                self.content.Global.setGlobal("GlobalLocalMySQL", self.content.On_Start_MySQL)
                print("\033[92m {}\033[00m".format("LinkMyDatabase ==> Start MySQL Localhost"))

            if len(str(self.editDatabase.text())) > 0:
                if self.content.set_UseLocalhost:
                    self.SetHost = "localhost"

                else:
                    self.SetHost = self.editHostName.text()

                self.content.mydb = mysql.connector.connect(
                    host = self.SetHost,
                    user = self.SetUser,
                    password = self.editPassword.text(),
                    database = self.editDatabase.text()
                )

                self.content.mycursor = self.content.mydb.cursor()
                #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                # get list of all databases
                self.content.mycursor.execute("SHOW DATABASES")

                #print all databases
                for db in self.content.mycursor:
                    print(db)
                    if db[0] ==  self.editDatabase.text():
                        self.content.database_link = True

                        self.content.lbl_dbname.setText(self.editDatabase.text())
                        self.content.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: blue; font-size:6pt;")

                        self.lbl_linktodb.setVisible(True)

                if not self.content.database_link:
                    self.lbl_linktodb.setText("No Database Name in MySQL")
                    self.lbl_linktodb.setStyleSheet("color: red; font-size:10pt;")

            else:
                print("\033[91m {}\033[00m".format("Still not set Database name !!!"))

    def ChangeMySQL_Host(self, state):
        if state == QtCore.Qt.Checked:
            self.content.set_UseLocalhost = True
            self.editHostName.setStyleSheet("color: lightgreen; font-size:8pt;")
            self.editHostName.setText("localhost Or http://127.0.0.1 ( Activated )")
            self.editHostName.setEnabled(False)

            self.CreateDatabase.setEnabled(True)

            print("Xampp Directory :", self.content.Path[:-8] + "Database/xampp")
            if not os.path.isfile(self.content.Path[:-8] + "Database/xampp/Latest_directory.txt"):
                file = open(self.content.Path[:-8] + "Database/xampp/Latest_directory.txt",'w')
                file.write(self.content.Path[:-8])
                file.close()

                # Request Set up new xampp
                self.exe_command("setup_xampp.bat")

            else:
                with open(self.content.Path[:-8] + "Database/xampp/Latest_directory.txt", 'r') as file:
                    # Read the entire content of the file into a string
                    Last_xampp_dir = file.read()
                    if Last_xampp_dir != self.content.Path[:-8]:
                        # Request Setup new xampp
                        print("Run Setup new xampp")
                        self.exe_command("setup_xampp.bat")

        else:
            self.content.set_UseLocalhost = False

            self.editHostName.setStyleSheet("color: white; font-size:7pt;")
            self.editHostName.setText(self.content.host)
            self.editHostName.setEnabled(True)

    def ManualStartApache(self):
        self.exe_command("apache_start.bat")

    def ManualStartXampp(self):
        self.exe_command("xampp-control.exe")

    def exe_command(self, commad_script):
        root_part = self.content.Path[0:2]

        shell = client.Dispatch("WScript.Shell")
        run_cmdScript = Exec_cmdScript()
        run_cmdScript.open_cmd(shell)
        run_cmdScript.activate_venv(shell, root_part, self.content.Path[:-8] + "Database/xampp")
        run_cmdScript.run_cmd_script(shell, commad_script)
        time.sleep(1)
        run_cmdScript.run_cmd_script(shell, "  exit")

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(10, 200, 475, 200)

    #================================================
    #Close Python IDE UI ---> Save All Python IDE
    def closeEvent(self, event):
        #print("MySQL Setting is closed !!!")

        #print("self.editHostName.text() = ", self.editHostName.text())

        if self.content.set_UseLocalhost:
            self.content.host = "localhost"
        else:
            self.content.host = self.editHostName.text()

        self.content.user = self.editUserName.text()
        self.content.password =  self.editPassword.text()

        self.content.dbname = self.editDatabase.text()
        if len(self.content.dbname) > 0:
            self.content.lbl_dbname.setText(self.content.dbname)
            self.content.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: blue; font-size:6pt;")

        # Save Online MySQL Infomation
        self.content.host_online = self.edit_OnlineHostName.text()
        self.content.user_online = self.edit_OnlineUserName.text()
        self.content.password_online = self.edit_OnlinePassword.text()
        self.content.dbname_online = self.edit_OnlineDatabase.text()

        self.content.SettingBtn.setEnabled(True)

# ==========================================================================================================
# ==========================================================================================================
@register_node(OP_NODE_MYSQL)
class Open_MySQL(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_mysql.png"
    op_code = OP_NODE_MYSQL
    op_title = "MySQL"
    content_label_objname = "MySQL"

    def __init__(self, scene):
        super().__init__(scene, inputs=[3], outputs=[1,4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.input_command_payload = {}
        self.sql_out_payload = {}
        self.sql_out_online_payload = {}

        self.local_exiting_id = False
        self.online_exiting_id = False

    def initInnerClasses(self):
        self.content = MySQL(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        # self.Global = GlobalVariable()

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)
        self.content.SwitchDatabase.clicked.connect(self.StartConnectDB)

        self.content.Connection_timer.timeout.connect(self.status_connection)
        self.content.Connection_timer.setInterval(200)

    def evalImplementation(self):                       # <----------- Create Socket range Index
        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.input_command_payload = input_node.eval()

            if self.input_command_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

            elif type(self.input_command_payload) != type(None):
                # try:
                    print("self.input_command_payload['sql'] :", self.input_command_payload['sql'])
                    if self.content.ConnectionStatus_flag:
                        if self.content.database_link:
                            # print("\033[92m {}\033[00m".format("Localhost ==> self.content.mycursor : " + str(self.content.mycursor)))
                            if type(self.content.mycursor) == type(None):
                                if self.content.set_UseLocalhost:
                                    self.content.host = "localhost"

                                self.content.mydb = mysql.connector.connect(
                                    host = self.content.host,
                                    user = self.content.user,
                                    password = self.content.password,
                                    database = self.content.dbname
                                )

                                self.content.mycursor = self.content.mydb.cursor()
                                #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                                # get list of all databases
                                self.content.mycursor.execute("SHOW DATABASES")

                        if self.content.database_onlinelink:
                            # print("\033[96m {}\033[00m".format("Online ==> self.content.mycursor_online : " + str(self.content.mycursor_online)))
                            if type(self.content.mycursor_online) == type(None):
                                self.content.my_onlinedb = mysql.connector.connect(
                                    host = self.content.host_online,
                                    user = self.content.user_online,
                                    password = self.content.password_online,
                                    database = self.content.dbname_online
                                )

                                self.content.mycursor_online = self.content.my_onlinedb.cursor()
                                #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                                # get list of all databases
                                self.content.mycursor_online.execute("SHOW DATABASES")

                        if 'sql' in self.input_command_payload:
                            print("type(self.input_command_payload['sql']) :", type(self.input_command_payload['sql']))
                            command = str(self.input_command_payload['sql']).split(" ")

                            # "INSERT INTO aiflow_editor_test (data,value) VALUES (%s,%s)"
                            if command[0] == "INSERT":
                                print("INSERT INTO = ", command[2])
                                print("DATA = ", command[3])
                                print("VALUES = ", command[5])

                                sql = "INSERT INTO " + command[2] + " " + command[3] + " VALUES " + command[5]
                                # print("sql :", sql)

                                val = ()
                                if 'val' in self.input_command_payload:
                                    val = self.input_command_payload['val']
                                    print("val : ", val)
                                    print("type(val) : ", type(val))

                                if 'Duplicate' in self.input_command_payload:
                                    if self.input_command_payload['Duplicate'] == "FALSE":
                                        # No Duplicat
                                        key_no_duplicate = ""
                                        if 'Duplicate_key' in self.input_command_payload:
                                            key_no_duplicate = self.input_command_payload['Duplicate_key']

                                        # if len(key_no_duplicate) == 0:
                                        #     key_no_duplicate = command[2].split(",")
                                        
                                        print("key_no_duplicate :", key_no_duplicate)

                                        value_no_duplicate = ""
                                        if 'Duplicate_value' in self.input_command_payload:
                                            value_no_duplicate = self.input_command_payload['Duplicate_value']

                                        # SELECT * FROM dialy_record WHERE date='28/01/2022'
                                        check_dupl_sql = "SELECT * FROM "+ command[2] +" WHERE "+ str(key_no_duplicate) +"='"+ str(value_no_duplicate) + "'"
                                        print("No Duplicate SQL = ", check_dupl_sql)
                                        print("self.content.mycursor = ", self.content.mycursor)

                                        # localhost
                                        if self.content.set_UseLocalhost:
                                            try:
                                                self.content.mycursor.execute(check_dupl_sql)
                                                myresult = self.content.mycursor.fetchall()
                                                print("No Duplicate myresult = ", len(myresult))
                                                if len(myresult) > 0:
                                                    print("\033[93m {}\033[00m".format("Localhost - Exiting RowID"))
                                                    self.sql_out_payload['result'] = "Exiting RowID"
                                                    self.local_exiting_id = True

                                            except Exception as e:
                                                print(e)
                                                self.content.reconnect_localhost()

                                        #Online Host
                                        if self.content.set_UseOnlinehost:
                                            try:
                                                self.content.mycursor_online.execute(check_dupl_sql)
                                                my_onlineresult = self.content.mycursor_online.fetchall()
                                                print("No Duplicate myresult = ", len(my_onlineresult))
                                                if len(my_onlineresult) > 0:
                                                    print("\033[93m {}\033[00m".format("Online Host - Exiting RowID"))
                                                    self.sql_out_online_payload['result'] = "Exiting RowID"
                                                    self.online_exiting_id = True

                                            except Exception as e:
                                                print(e)
                                                self.content.reconnect_onlinehost()

                                print("sql :", sql)     
                                if len(sql) > 0 and  len(val) > 0:
                                    # Local Host
                                    if self.content.database_link and self.content.set_UseLocalhost and not self.local_exiting_id:
                                        try:
                                            self.content.mycursor.execute(sql, val)
                                            self.content.mydb.commit()
                                            # print(self.content.mycursor.rowcount, "data inserted.")
                                            print("\033[92m {}\033[00m".format("Localhost ==> data inserted : " + str(self.content.mycursor.rowcount)))

                                            if self.content.mycursor.rowcount > 0:
                                                self.sql_out_payload['result'] = "inserted success"
                                            else:
                                                self.sql_out_payload['result'] = "inserted fail"
                                        
                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_localhost()

                                    # Online Host
                                    if self.content.database_onlinelink and self.content.set_UseOnlinehost and not self.online_exiting_id:
                                        try:
                                            self.content.mycursor_online.execute(sql, val)
                                            self.content.my_onlinedb.commit()
                                            # print(self.content.mycursor_online.rowcount, "data inserted.")
                                            print("\033[96m {}\033[00m".format("Online ==> data inserted : " + str(self.content.mycursor_online.rowcount)))

                                            if self.content.mycursor_online.rowcount > 0:
                                                self.sql_out_online_payload['result'] = "inserted success"
                                            else:
                                                self.sql_out_online_payload['result'] = "inserted fail"

                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_onlinehost()

                            # "UPDATE tablename SET address = 'Canyon 123' WHERE address = 'Valley 345'"
                            if command[0] == "UPDATE":
                                print("UPDATE = ", command[1])
                                print("SET ", command[3])
                                print("WHERE ", command[5])

                                sql = str(self.input_command_payload['sql'])
                                print("sql :", sql)

                                if len(sql) > 0:
                                    # Local Host
                                    if self.content.database_link and self.content.set_UseLocalhost:
                                        try:
                                            self.content.mycursor.execute(sql)

                                            self.content.mydb.commit()

                                            # print(self.content.mycursor.rowcount, "data update")
                                            print("\033[92m {}\033[00m".format("Localhost ==> data update : " + str(self.content.mycursor.rowcount)))

                                            if self.content.mycursor.rowcount > 0:
                                                self.sql_out_payload['result'] = "updated success"
                                            else:
                                                self.sql_out_payload['result'] = "updated fail"

                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_localhost()

                                    # Online Host
                                    if self.content.database_onlinelink and self.content.set_UseOnlinehost:
                                        self.content.mycursor_online.execute(sql)

                                        self.content.my_onlinedb.commit()

                                        # print(self.content.mycursor_online.rowcount, "data update")
                                        print("\033[96m {}\033[00m".format("Online ==> data update : " + str(self.content.mycursor_online.rowcount)))

                                        if self.content.mycursor_online.rowcount > 0:
                                            self.sql_out_online_payload['result'] = "updated success"
                                        else:
                                            self.sql_out_online_payload['result'] = "updated fail"

                            # 'SELECT  * FROM tablename'
                            if command[0] == "SELECT":
                                sql = str(self.input_command_payload['sql'])
                                print("sql :", sql)

                                if len(sql) > 0:
                                    # Local Host
                                    if self.content.database_link and self.content.set_UseLocalhost:
                                        try:
                                            self.content.mycursor.execute(sql)

                                            myresult = self.content.mycursor.fetchall()
                                            self.sql_out_payload['result'] = myresult
                                            for x in myresult:
                                                print("\033[92m {}\033[00m".format("Localhost ==> data select : " + str(x)))
                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_localhost()

                                    # Online Host
                                    if self.content.database_onlinelink and self.content.set_UseOnlinehost:
                                        try:
                                            self.content.mycursor_online.execute(sql)

                                            my_omlineresult = self.content.mycursor_online.fetchall()
                                            self.sql_out_online_payload['result'] = my_omlineresult
                                            for y in my_omlineresult:
                                                print("\033[96m {}\033[00m".format("Online ==> data select : " + str(y)))
                                        
                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_onlinehost()

                            # "DELETE FROM tablename WHERE address = 'Mountain 21'"
                            if command[0] == "DELETE":
                                sql = str(self.input_command_payload['sql'])
                                print("sql :", sql)

                                if len(sql) > 0:
                                    # Local Host
                                    if self.content.database_link and self.content.set_UseLocalhost:
                                        try:
                                            self.content.mycursor.execute(sql)
                                            self.content.mydb.commit()

                                            # print(self.content.mycursor.rowcount, "record(s) deleted")
                                            print("\033[92m {}\033[00m".format("Localhost ==> deleted : " + str(self.content.mycursor.rowcount)))

                                            if self.content.mycursor.rowcount > 0:
                                                self.sql_out_payload['result'] = "delete success"
                                            else:
                                                self.sql_out_payload['result'] = "delete fail"
                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_localhost()

                                    # Online Host
                                    if self.content.database_onlinelink and self.content.set_UseOnlinehost:
                                        try:
                                            self.content.mycursor_online.execute(sql)
                                            self.content.my_onlinedb.commit()

                                            # print(self.content.mycursor_online.rowcount, "record(s) deleted")
                                            print("\033[96m {}\033[00m".format("Online ==> data deleted : " + str(self.content.mycursor_online.rowcount)))

                                            if self.content.mycursor_online.rowcount > 0:
                                                self.sql_out_online_payload['result'] = "delete success"
                                            else:
                                                self.sql_out_online_payload['result'] = "delete fail"

                                        except Exception as e:
                                                print(e)
                                                self.content.reconnect_onlinehost()

                        self.local_exiting_id = False
                        self.online_exiting_id = False

                # except Exception as e:
                #     if self.content.set_UseLocalhost:
                #         self.content.MySQL_Connection()
                #         self.content.mycursor = self.content.mydb.cursor()
                #         self.content.mycursor.execute("SHOW DATABASES")

                #         #print all databases
                #         print("onload")
                #         for db in self.content.mycursor:
                #             print(db)
                #             if db[0] ==  self.content.dbname:
                #                 self.content.database_link = True
                #                 print("On load Auto Start Connect MySQL Database  !!!!")
                #                 self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                #                 self.content.Connection_timer.start()

                #                 self.content.movie.start()

                #     # Check If Also Using Online MySQL
                #     if self.content.set_UseOnlinehost:
                #         self.On_Start_MySQL_Online = True

                #         self.content.my_onlinedb = mysql.connector.connect(
                #             host = self.content.host_online,
                #             user = self.content.user_online,
                #             password = self.content.password_online,
                #             database = self.content.dbname_online
                #         )

                #         self.content.mycursor_online = self.content.my_onlinedb.cursor()
                #         self.content.mycursor_online.execute("SHOW DATABASES")

                #         #print all databases
                #         for db in self.content.mycursor_online:
                #             print(db)
                #             if db[0] ==  self.content.dbname_online:
                #                 self.content.database_onlinelink = True
                #                 self.content.Global.setGlobal("On_Start_MySQL_Online", self.On_Start_MySQL_Online)
                #                 print("\033[94m {}\033[00m".format("Connect to Online MySQL"))
                        

        self.sendFixOutputByIndex(self.sql_out_payload, 0)
        self.sendFixOutputByIndex(self.sql_out_online_payload, 1)

    def status_connection(self):
        if self.content.ConnectionBlink >= 5:
            self.content.ConnectionBlink = 0
            if self.content.set_UseLocalhost:
                self.content.lbl_link.setVisible(True)

            if self.content.set_UseOnlinehost:
                self.content.lbl_Onlielink.setVisible(True)

        else:
            self.content.lbl_link.setVisible(False)
            self.content.lbl_Onlielink.setVisible(False)
            #Clear SQL Command in Global 
            
        self.content.ConnectionBlink += 1

    def StartConnectDB(self):
        print("self.content.ConnectionStatus_flag :", self.content.ConnectionStatus_flag)
        if not self.content.ConnectionStatus_flag:
            # self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
            print("self.content.database_link :", self.content.database_link)

            if self.content.set_UseLocalhost:
                if self.content.database_link:
                    self.content.movie.start()
                    self.content.Connection_timer.start()

                    self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                    self.content.ConnectionStatus_flag = True

                else:
                    if not self.content.Global.hasGlobal("GlobalLocalMySQL"):
                        print("Localhost still not Starting !!!")
                        # Check host/ Checke db

                        print("self.content.set_UseLocalhost :", self.content.set_UseLocalhost)
                        print("self.content.On_Start_MySQL :", self.content.On_Start_MySQL)

                        if not self.content.On_Start_MySQL:
                            self.content.On_Start_MySQL = True

                            # Start Apache and Start MySQL
                            # self.content.OnLoad_exe_command("apache_start.bat")
                            self.content.OnLoad_exe_command("mysql_start.bat")

                            self.content.Global.setGlobal("GlobalLocalMySQL", self.content.On_Start_MySQL)
                            print("\033[92m {}\033[00m".format("StartConnectDB ==> Start MySQL Localhost"))
                    
                            #self.content.mycursor = self.content.mydb.cursor()
                            #print("Auto Connect self.content.mycursor = ", self.content.mycursor)

                        if self.content.set_UseLocalhost:
                            self.content.host = "localhost"

                        self.mydb = mysql.connector.connect(
                            host = self.content.host,
                            user = self.content.user,
                            password = self.content.password,
                            database = self.content.dbname
                        )

                        self.content.mycursor = self.mydb.cursor()
                        #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                        # get list of all databases
                        self.content.mycursor.execute("SHOW DATABASES")

                        #print all databases
                        print("onload")
                        for db in self.content.mycursor:
                            print(db)
                            if db[0] ==  self.content.dbname:
                                self.content.database_link = True
                                print("On load Auto Start Connect MySQL Database  !!!!")
                                self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                                self.content.Connection_timer.start()
                                self.content.movie.start()
                                self.content.ConnectionStatus_flag = True
                    else:
                        if self.content.MySQL_Connection():
                            self.content.mycursor = self.content.mydb.cursor()
                            #db_cursor.execute("CREATE DATABASE " + self.editDatabase.text())
                            # get list of all databases
                            self.content.mycursor.execute("SHOW DATABASES")

                            #print all databases
                            print("StartConnectDB")
                            for db in self.content.mycursor:
                                print(db)
                                if db[0] ==  self.content.dbname:
                                    self.content.database_link = True
                                    print("On load Auto Start Connect MySQL Database  !!!!")
                                    self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                                    self.content.movie.start()
                                    self.content.Connection_timer.start()

                                    self.content.ConnectionStatus_flag = True

            # else:
            #     self.content.lbl_dbname.setStyleSheet("background-color: white; border: 1px solid white; border-radius: 2%; color: red; font-size:6pt;")
            #     self.content.lbl_dbname.setText("No Database Name")

            #     self.MySQL_Setting = MySQLSetting(self.content)
            #     self.MySQL_Setting.show()
            #     self.content.SettingBtn.setEnabled(False)


            if self.content.set_UseOnlinehost:
                if self.content.database_onlinelink:
                    self.content.movie.start()
                    self.content.Connection_timer.start()

                    self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                    self.content.ConnectionStatus_flag = True

                else:
                    self.content.my_onlinedb = mysql.connector.connect(
                        host = self.content.host_online,
                        user = self.content.user_online,
                        password = self.content.password_online,
                        database = self.content.dbname_online
                    )

                    self.content.mycursor_online = self.content.my_onlinedb.cursor()
                    self.content.mycursor_online.execute("SHOW DATABASES")

                    #print all databases
                    for db in self.content.mycursor_online:
                        print(db)
                        if db[0] ==  self.content.dbname_online:
                            self.content.On_Start_MySQL_Online = True

                            self.content.database_onlinelink = True
                            self.content.Global.setGlobal("On_Start_MySQL_Online", self.content.On_Start_MySQL_Online)
                            print("\033[94m {}\033[00m".format("StartConnectDB ==> Connect to Online MySQL"))

                            self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))
                            self.content.Connection_timer.start()
                            self.content.movie.start()

                            self.content.ConnectionStatus_flag = True


        else:
            print("Disconnect MySQL Database <----")
            self.content.SwitchDatabase.setIcon(QIcon(self.content.off_icon))
            self.content.Connection_timer.stop()

            self.content.lbl_link.setVisible(False)
            self.content.lbl_Onlielink.setVisible(False)
            self.content.movie.stop()

            self.content.ConnectionStatus_flag = False
    
    def sendFixOutputByIndex(self, value, index):

        self.value = value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(index, op_code=self.op_code)

        else:
            self.evalChildren(index)

    def OnOpen_Setting(self):
        self.MySQL_Setting = MySQLSetting(self.content)
        self.MySQL_Setting.show()
        self.content.SettingBtn.setEnabled(False)


