from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *
from ai_application.Database.SQLite import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import datetime

class SQLITE(QDMNodeContentWidget):
    def initUI(self):
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.sqlite_icon = self.Path + "/icons/icons_sqlite.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(125,78,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        graphicsView.setScene(scene)

        graphicsView.resize(70,45)
        graphicsView.setGeometry(QtCore.QRect(5, 60, 60, 35))

        img = QPixmap(self.sqlite_icon)
        self.pixmap.setPixmap(img)

        #====================================================
        self.SwitchDatabase = QPushButton(self)
        self.SwitchDatabase.setGeometry(110,5,37,20)
        self.SwitchDatabase.setIcon(QIcon(self.off_icon))
        self.SwitchDatabase.setIconSize(QtCore.QSize(37,20))
        self.SwitchDatabase.setStyleSheet("background-color: transparent; border: 0px;")  

        #====================================================
        # Loading the GIF
        animate_movie = self.Path + "/icons/icons_gear_70.gif"

        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 10, 75, 75))
        self.label.setMinimumSize(QtCore.QSize(70, 70))
        self.label.setMaximumSize(QtCore.QSize(70, 70))
        #self.label.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:15pt;color:lightblue; border: 1px solid black; border-radius: 3%")

        self.movie = QMovie(animate_movie)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        #====================================================

        self.ConnectionStatus_flag = False
        self.SQLite_DBName = ""
        self.SQLite_TableName = ""
        self.NumberColumn = 0

        self.ColumnData_list0 = []
        self.ColumnData_list1 = []
        self.inputType = "payload"
        self.global_SQLite = ""

        self.Database_path = ""

        self.getGlobal_timer = QtCore.QTimer(self)

    def serialize(self):
        res = super().serialize()
        res['dbname'] = self.SQLite_DBName
        res['tablename'] = self.SQLite_TableName
        res['no_column'] = self.NumberColumn
        res['column_list'] = self.ColumnData_list0
        res['column_payload'] = self.ColumnData_list1
        res['input_typpe'] = self.inputType
        res['global_sqlite'] = self.global_SQLite
        res['process_flag'] = self.ConnectionStatus_flag
        res['db_path'] = self.Database_path
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'dbname' in data:
                self.SQLite_DBName = data['dbname']

            if 'tablename' in data:
                self.SQLite_TableName = data['tablename']

            if 'no_column' in data:
                self.NumberColumn = data['no_column']

            if 'column_list' in data:
                self.ColumnData_list0 = data['column_list']

            if 'column_payload' in data:
                self.ColumnData_list1 = data['column_payload']

            if 'process_flag' in data:
                self.ConnectionStatus_flag = data['process_flag']

            if 'input_typpe' in data:
                self.inputType = data['input_typpe']
                if self.inputType == "SQLite_Other" and self.ConnectionStatus_flag:
                    self.getGlobal_timer.start()
                    self.SwitchDatabase.setIcon(QIcon(self.on_icon))
                    self.movie.start()

                else:
                    self.getGlobal_timer.stop()
                    self.SwitchDatabase.setIcon(QIcon(self.off_icon))
                    self.movie.stop()

            if 'global_sqlite' in data:
                self.global_SQLite = data['global_sqlite']

            if 'db_path' in data:
                self.Database_path = data['db_path']

            return True & res
        except Exception as e:
            dumpException(e)
        return res

class SQLiteSetting(QtWidgets.QMainWindow):
    def __init__(self, content, dbinstance, parent=None):
        super().__init__(parent)

        self.RPath = os.path.dirname(os.path.abspath(__file__))
        self.DBPath = self.RPath[0:-9]
        print("self.DBPath = ", self.DBPath)

        self.dbTABinstance = dbinstance
        print('Class SQLiteSetting ---> SQLite Setting Function; ', str(self.dbTABinstance))

        self.content = content

        self.title = "SQLite Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 400
        self.height = 430
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        #================================================
        # Host
        self.lbl1 = QLabel("Database: ", self)
        self.lbl1.setGeometry(QtCore.QRect(10, 5, 60, 20))

        self.editDBName = QLineEdit("",self)
        self.editDBName.setFixedWidth(150)
        self.editDBName.setGeometry(80,5,150,20)
        self.editDBName.setPlaceholderText("Databese Name")

        #=================================================
        # User
        self.lbl2 = QLabel("Table: ", self)
        self.lbl2.setGeometry(QtCore.QRect(10, 30, 60, 20))

        self.editTableName = QLineEdit("",self)
        self.editTableName.setFixedWidth(150)
        self.editTableName.setGeometry(80,30,150,20)
        self.editTableName.setPlaceholderText("Table Name")

        #=================================================

        self.setting_status = ""
        self.DB_Name = self.content.SQLite_DBName
        print("self.content.SQLite_DBName = ", self.content.SQLite_DBName)

        self.Table_Name = self.content.SQLite_TableName
        self.NOF_Column = self.content.NumberColumn
        print("self.NOF_Column = ", self.NOF_Column)

        self.lblcolumn = QLabel("Input :", self)
        self.lblcolumn.setGeometry(QtCore.QRect(240, 5, 40, 20))

        self.checkPayload = QCheckBox("Payload",self)
        self.checkPayload.setGeometry(290,5,90,20)
        self.checkPayload.setStyleSheet("color: #FC03C7")

        self.checkSQLite_Feed = QCheckBox("",self)
        self.checkSQLite_Feed.setGeometry(290,30,30,20)
        self.checkSQLite_Feed.setStyleSheet("color: lightblue")

        self.editGlobalSQL = QLineEdit("",self)
        self.editGlobalSQL.setGeometry(310,30,85,20)
        self.editGlobalSQL.setPlaceholderText("Global SQL")
        self.editGlobalSQL.setText(self.content.global_SQLite)

        if self.content.inputType == "payload":
            self.checkPayload.setChecked(True)
            self.checkSQLite_Feed.setChecked(False)

        else:
            self.checkPayload.setChecked(False)
            self.checkSQLite_Feed.setChecked(True)

        self.checkPayload.stateChanged.connect(self.SelectPayload)
        self.checkSQLite_Feed.stateChanged.connect(self.SelectSQLite_Feed)

        self.editDBName.setText(self.DB_Name)
        self.editTableName.setText(self.Table_Name)

        self.lblcolumn = QLabel("Create Column :", self)
        self.lblcolumn.setGeometry(QtCore.QRect(10, 60, 120, 30))
        self.lblcolumn.setAlignment(Qt.AlignLeft)
        self.lblcolumn.setAlignment(Qt.AlignTop)
        self.lblcolumn.setStyleSheet("background-color: rgba(0, 32, 130, 200); font-size:10pt;color:lightblue; border: 1px solid white; border-radius: 3%;")

        self.AddBtn = QPushButton("Add", self)
        self.AddBtn.setGeometry(270,60,50,30)

        self.DelBtn = QPushButton("Delete", self)
        self.DelBtn.setGeometry(330,60,50,30)

        self.AddBtn.clicked.connect(self.add_column)
        self.DelBtn.clicked.connect(self.del_column)

        #====================================================
        # Create table
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(10,105,370,310)
        #self.tableWidget.setStyleSheet("QTableWidget { background-color: rgba(0, 32, 130, 100); gridline-color: #fffff8; font-size: 10pt; }")
        self.tableWidget.setStyleSheet("background-color: rgba(0, 124, 212, 50);font-size:10pt;color: #178CEA; gridline-color: #fffff8;")
        
        self.tableWidget.setRowCount(self.NOF_Column)
        self.tableWidget.setColumnCount(2)

        font = QFont()
        font.setBold(True)
        self.tableWidget.setFont(font)

        # Set Fixed Collum Header Width
        header = self.tableWidget.horizontalHeader()       
        self.tableWidget.setColumnWidth(0 , 175)
        self.tableWidget.setColumnWidth(1 , 175)
        header.setStyleSheet("background-color: rgba(0, 32, 130, 200);")

        # Set Colume Alignment Center
        delegate = AlignDelegate(self.tableWidget)
        #self.tableWidget.setItemDelegateForColumn(0, delegate)
        self.tableWidget.setItemDelegateForColumn(1, delegate)
        self.tableWidget.setItemDelegateForColumn(2, delegate)

        self.tableWidget.setHorizontalHeaderLabels(['Column Name','Payload'])

        print("self.content.ColumnData_list0 = ", self.content.ColumnData_list0)
        if self.NOF_Column > 0:
            for i in range(self.NOF_Column):
                self.tableWidget.setItem(i,0, QTableWidgetItem(str(self.content.ColumnData_list0[i])))
                if len(self.content.ColumnData_list1) > 2:
                    self.tableWidget.setItem(i,1, QTableWidgetItem(str(self.content.ColumnData_list1[i])))

        self.column_list = []

    def add_column(self):
        self.NOF_Column += 1
        self.tableWidget.setRowCount(self.NOF_Column)
        self.tableWidget.setItem(self.NOF_Column,0, QTableWidgetItem(""))
        self.tableWidget.setItem(self.NOF_Column,1, QTableWidgetItem(""))

        print("Add Column : ", self.NOF_Column)

    def del_column(self):
        self.NOF_Column -= 1
        self.tableWidget.setRowCount(self.NOF_Column)
        print("Delete Column : ", self.NOF_Column)

    def SelectPayload(self, state):
        if state == QtCore.Qt.Checked:
            self.checkPayload.setChecked(True)
            self.checkSQLite_Feed.setChecked(False)
            self.content.inputType = "payload"

        else:
            self.checkPayload.setChecked(False)

    def SelectSQLite_Feed(self, state):
        if state == QtCore.Qt.Checked:
            self.checkPayload.setChecked(False)
            self.checkSQLite_Feed.setChecked(True)
            self.content.inputType = "SQLite_Other"
        else:
            self.checkSQLite_Feed.setChecked(False)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(10, 100, 380, 100)
        
    #================================================
    #Close Python IDE UI ---> Save All Python IDE
    def closeEvent(self, event):
        self.setting_status = "Close"

        if len(self.editDBName.text()) > 0:
            Result = self.dbTABinstance.CreateSQLite_DB(self.DBPath + "/Database/" + self.editDBName.text() + ".db")
            print("Connect SQLite Database Result = ", Result)

            if Result == "Success":
                self.content.SQLite_DBName = self.editDBName.text()

            if len(self.editTableName.text()) > 0:

                if self.NOF_Column > 0:
                    for i in range(self.NOF_Column):
                        self.column_list.append(self.tableWidget.item(i, 0).text())

                    print("SQLite closeEvent : self.column_list = ", self.column_list)
                    print()

                    self.DB_Name = self.editDBName.text()
                    self.Table_Name = self.editTableName.text()

                    self.content.Database_path = self.DBPath + "/Database/"
                    print("closeEvent : self.content.Database_path = ", self.content.Database_path)

                    self.content.SQLite_DBName = self.DB_Name
                    self.content.ColumnData_list0 = self.column_list
                    self.content.SQLite_TableName = self.editTableName.text()
                    self.content.NumberColumn = self.NOF_Column
                    self.content.global_SQLite = self.editGlobalSQL.text()

                #check_Table_existing
                TableExisting = self.dbTABinstance.Check_TableInDB(self.DBPath + "/Database/" + self.editDBName.text() + ".db", self.editTableName.text())
                if TableExisting:
                    print("Table " + self.editTableName.text() + " existing !!!")

                else:
                    print("Starting to Create Table.")
                    if self.NOF_Column > 0:

                        self.dbTABinstance.CreateSQLite_DatabaseTable(self.DBPath + "/Database/" + self.editDBName.text() + ".db", self.editTableName.text(), self.NOF_Column, self.column_list)
                        print("Create New Table name " + self.editTableName.text())

                        
                    else:
                        print("Not Success because No Column")

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

@register_node(OP_NODE_SQLITE)
class Open_SQLITE(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_sqllite.png"
    op_code = OP_NODE_SQLITE
    op_title = "SQLite 3"
    content_label_objname = "sqllite"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1,5], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.SQL_payload = {}

    def initInnerClasses(self):
        self.content = SQLITE(self)                     # <----------- init UI with data and widget
        self.dbinstance = SQLite()
        self.grNode = FlowGraphicsFaceProcess(self)     # <----------- Box Image Draw in Flow_Node_Base

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)
        self.content.SwitchDatabase.clicked.connect(self.StartConnectDB)

        self.content.getGlobal_timer.timeout.connect(self.global_update_table)

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.SQL_payload = input_node.eval()

        SQL_Datalist = []

        if self.SQL_payload is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            #self.content.Debug_timer.stop()
            return
        else:

            if self.content.inputType == "payload" and self.content.ConnectionStatus_flag:
                if len(self.content.ColumnData_list1) > 5:
                    print("self.payload = ", self.SQL_payload)
                    for i in range(self.content.NumberColumn):
                        if self.content.ColumnData_list1[i] in self.SQL_payload:
                            SQL_Datalist.append(self.SQL_payload[self.content.ColumnData_list1[i]])

                    db_location = self.content.Database_path + self.content.SQLite_DBName + '.db'
                    print("Inset Table to : ", db_location)

                    self.dbinstance.Insert_Database(db_location, self.content.SQLite_TableName, self.content.ColumnData_list0 , SQL_Datalist, self.content.NumberColumn, self.content.inputType)

        self.value = self.SQL_payload   #---> * Important to return value back to main payload

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        self.SQL_payload.clear()

    def global_update_table(self):
        #print("self.content.global_SQLite = ", self.content.global_SQLite)
        if len(self.content.global_SQLite) > 0:
            if self.Global.hasGlobal(self.content.global_SQLite):
                if len(str(self.Global.getGlobal(self.content.global_SQLite))) > 5:
                    SQL_Datalist = self.Global.getGlobal(self.content.global_SQLite)

                    """
                    SQL_Command = str(self.Global.getGlobal(self.content.global_SQLite)).split(";")
                    for i in range(self.content.NumberColumn):
                        print("SQL_Command[", i, "] = ", SQL_Command[i])"""

                    #INSERT INTO Loop_Record (Model,Result,Sequence,WorkingTime,EngineNumber) VALUES ("Non-VVT","In Std [ 89 Sec ]","[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]","2022-05-27 15:08:06","-")
                    
                    db_location = self.content.Database_path + self.content.SQLite_DBName + '.db'
                    # print("Inset Table to : ", db_location)
                    # print("self.content.SQLite_TableName = ", self.content.SQLite_TableName)
                    # print("self.content.ColumnData_list0 = ", self.content.ColumnData_list0)
                    # print("SQL_Datalist = ", SQL_Datalist)
                    # print("self.content.NumberColumn = ", self.content.NumberColumn)
                    # print("self.content.inputType = ", self.content.inputType)

                    self.dbinstance.Insert_Database(db_location, self.content.SQLite_TableName, self.content.ColumnData_list0 , SQL_Datalist, self.content.NumberColumn, self.content.inputType)

                    self.Global.setGlobal(self.content.global_SQLite, "")

                    self.SQL_payload['result'] = "Update\n" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                    self.update_payload()

    def StartConnectDB(self):
        if not self.content.ConnectionStatus_flag and len(self.content.SQLite_DBName) > 0:
            self.content.SwitchDatabase.setIcon(QIcon(self.content.on_icon))

            self.content.ConnectionStatus_flag = True

            Result = self.dbinstance.CreateSQLite_DB("SQLite_PoseEavaluate.db")
            print("Connect SQLite Database Result = ", Result)

            self.content.movie.start()

            if self.content.inputType == "SQLite_Other" and len(self.content.global_SQLite) > 0:
                self.content.getGlobal_timer.start()

        else:
            print("Disconnect MySQL Database <----")
            self.content.SwitchDatabase.setIcon(QIcon(self.content.off_icon))

            self.content.ConnectionStatus_flag = False

            self.content.movie.stop()
            self.content.getGlobal_timer.stop()

    def OnOpen_Setting(self):
        self.SQLite_Setting = SQLiteSetting(self.content, self.dbinstance)
        self.SQLite_Setting.show()

    def update_payload(self):
        self.value = self.SQL_payload   #---> * Important to return value back to main payload

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()