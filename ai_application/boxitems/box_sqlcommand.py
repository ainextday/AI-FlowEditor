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

from datetime import datetime

class SQLCommand(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"

        self.sqlInsert = QCheckBox("Insert",self)
        self.sqlInsert.setGeometry(10,5,80,20)
        self.sqlInsert.setStyleSheet("color: lightblue; font-size:5pt;")
        self.sqlInsert_flag = False

        self.sqlUpdate = QCheckBox("Update",self)
        self.sqlUpdate.setGeometry(10,30,80,20)
        self.sqlUpdate.setStyleSheet("color: lightgreen; font-size:5pt;")
        self.sqlUpdate_flag = False

        self.sqlSelect = QCheckBox("Select",self)
        self.sqlSelect.setGeometry(10,55,80,20)
        self.sqlSelect.setStyleSheet("color: lightyellow; font-size:5pt;")
        self.sqlSelect_flag = False

        self.sqlDelete = QCheckBox("Delete",self)
        self.sqlDelete.setGeometry(10,80,80,20)
        self.sqlDelete.setStyleSheet("color: lightpink; font-size:5pt;")
        self.sqlDelete_flag = False

        #=================================================#
        #For Data Input Key

        self.lblTable = QLabel("Table : " , self)
        self.lblTable.setAlignment(Qt.AlignLeft)
        self.lblTable.setGeometry(90,7,45,20)
        self.lblTable.setStyleSheet("font-size:5pt;")

        self.editTableName = QLineEdit(self)
        self.editTableName.setGeometry(135,7,80,20)
        self.editTableName.setStyleSheet("font-size:5pt;")
        self.editTableName.setPlaceholderText("Table Name")

        self.lblFrom = QLabel("FROM : " , self)
        self.lblFrom.setAlignment(Qt.AlignLeft)
        self.lblFrom.setGeometry(90,32,45,20)
        self.lblFrom.setStyleSheet("font-size:5pt;")
        self.lblFrom.setVisible(False)

        self.editFrom = QLineEdit(self)
        self.editFrom.setGeometry(135,32,80,20)
        self.editFrom.setPlaceholderText("FROM")
        self.editFrom.setStyleSheet("font-size:5pt;")
        self.editFrom.setVisible(False)

        self.lblWhere = QLabel("WHERE : " , self)
        self.lblWhere.setAlignment(Qt.AlignLeft)
        self.lblWhere.setGeometry(90,58,45,20)
        self.lblWhere.setStyleSheet("font-size:5pt;")
        self.lblWhere.setVisible(False)

        self.editWhere = QLineEdit(self)
        self.editWhere.setGeometry(135,58,80,20)
        self.editWhere.setPlaceholderText("WHERE")
        self.editWhere.setStyleSheet("font-size:5pt;")
        self.editWhere.setVisible(False)

        # ===============================================
        self.sqlDuplicate = QCheckBox(self)
        self.sqlDuplicate.setGeometry(90,80,100,20)
        self.sqlDuplicate.setStyleSheet("color: lightblue; font-size:5pt;")
        self.sqlDuplicate.setText("No Duplicate")
        self.sqlDuplicate.setVisible(False)
        self.sqlDuplicate_flag = False

        self.DataDupl = QLineEdit(self)
        self.DataDupl.setGeometry(180,80,35,20)
        self.DataDupl.setPlaceholderText("KEY")
        self.DataDupl.setStyleSheet("color: lightblue; font-size:5pt;")
        self.DataDupl.setVisible(False)

        self.key_no_duplicate = ""

        # ================================================
        # Update Process
        self.lblUpdateWhere = QLabel(" = " , self)
        self.lblUpdateWhere.setAlignment(Qt.AlignLeft)
        self.lblUpdateWhere.setGeometry(120,80,20,20)
        self.lblUpdateWhere.setStyleSheet("font-size:5pt;")
        self.lblUpdateWhere.setVisible(False)

        self.editUpdateWhereKey = QLineEdit(self)
        self.editUpdateWhereKey.setGeometry(135,80,80,20)
        self.editUpdateWhereKey.setPlaceholderText("Columns")
        self.editUpdateWhereKey.setStyleSheet("font-size:5pt;")
        self.editUpdateWhereKey.setVisible(False)

        self.key_update_data = ""

        self.RequestInterval_timer = QtCore.QTimer(self)

        # 'GlobalLocalMySQL'

        #================================================#

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data

        res['insert'] = self.sqlInsert_flag
        res['update'] = self.sqlUpdate_flag
        res['select'] = self.sqlSelect_flag
        res['delete'] = self.sqlDelete_flag
        res['duplicate'] = self.sqlDuplicate_flag

        res['tablename'] = self.editTableName.text()
        res['from'] = self.editFrom.text()
        res['where'] = self.editWhere.text()

        res['key_no_duplicate'] = self.key_no_duplicate
        res['update_where_key'] = self.editUpdateWhereKey.text()

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            if 'insert' in data:
                self.sqlInsert_flag = data['insert']
                if self.sqlInsert_flag:
                    self.sqlInsert.setChecked(True)
                else:
                    self.sqlInsert.setChecked(False)

            if 'update' in data:
                self.sqlUpdate_flag = data['update']
                if self.sqlUpdate_flag:
                    self.sqlUpdate.setChecked(True)

                else:
                    self.sqlUpdate.setChecked(False)

            if 'select' in data:
                self.sqlSelect_flag = data['select']
                if self.sqlSelect_flag:
                    self.sqlSelect.setChecked(True)
                else:
                    self.sqlSelect.setChecked(False)

            if 'delete' in data:
                self.sqlDelete_flag = data['delete']
                if self.sqlDelete_flag:
                    self.sqlDelete.setChecked(True)
                else:
                    self.sqlDelete.setChecked(False)

            if 'duplicate' in data:
                self.sqlDuplicate_flag = data['duplicate']
                if self.sqlDuplicate_flag:
                    self.sqlDuplicate.setText("Can Duplicate")
                    self.sqlDuplicate.setChecked(True)
                    self.DataDupl.setVisible(False)

                else:
                    self.sqlDuplicate.setText("No Duplicate")
                    self.sqlDuplicate.setChecked(False)
                    self.DataDupl.setVisible(True)
                    
                    if 'key_no_duplicate' in data:
                        self.key_no_duplicate = data['key_no_duplicate']
                        self.DataDupl.setText(self.key_no_duplicate)

            if 'tablename' in data:
                self.editTableName.setText(data['tablename'])

            if 'from' in data:
                self.editFrom.setText(data['from'])
                
            if 'where' in data:
                self.editWhere.setText(data['where'])

            if 'update_where_key' in data:
                self.key_update_data = data['update_where_key']
                self.editUpdateWhereKey.setText(self.key_update_data)

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
        painter.drawLine(83, 10, 83, 95)

@register_node(OP_NODE_SQLCOMMAND)
class Open_SQLCOMMAND(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_sql_command.png"
    op_code = OP_NODE_SQLCOMMAND
    op_title = "SQL Command"
    content_label_objname = "SQL Command"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.sql_payload = {}
        self.rx_payload = {}

        self.DataValue = None
        self.StrCanDuplicate = "FALSE"

        self.Wait_Debound_Request = False
        self.process_sql_command = False

    def initInnerClasses(self):
        self.content = SQLCommand(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsSQLComandProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.sqlInsert.stateChanged.connect(self.SelectInsertFunction)
        self.content.sqlUpdate.stateChanged.connect(self.SelectUpdateFunction)
        self.content.sqlSelect.stateChanged.connect(self.SelectSelectFunction)
        self.content.sqlDelete.stateChanged.connect(self.SelectDeleteFunction)

        self.content.sqlDuplicate.stateChanged.connect(self.CanDuplicate)

        self.Global = GlobalVariable()

        self.content.RequestInterval_timer.timeout.connect(self.Request_interval)
        self.content.RequestInterval_timer.setInterval(2000)

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
            if 'msg' in self.rx_payload:
                if len(self.rx_payload['msg']) > 0:
                    self.process_sql_command = True

                else:
                    self.process_sql_command = False

            if 'submit' in self.rx_payload:
                if self.rx_payload['submit'] == True:
                    self.process_sql_command = True

                else:
                    self.process_sql_command = False

            if self.process_sql_command:
                #'INSERT'
                # sql = "INSERT INTO tablename (name, address) VALUES (%s, %s)"
                if self.content.sqlInsert_flag:
                    # #print("self.content.editWhere.text() = ", self.content.editWhere.text())
                    # if str(self.content.editWhere.text()) == "today()":
                    #     self.DataValue = str(datetime.now().strftime("%d/%m/%Y"))

                    # elif str(self.content.editWhere.text()) == "now()":
                    #     pass

                    # else:
                    #     self.DataValue = self.content.editWhere.text()

                    if self.content.sqlDuplicate_flag:
                        self.StrCanDuplicate = "TRUE"
                    else:
                        self.StrCanDuplicate = "FALSE"

                    print("self.content.editWhere.text() :", self.content.editWhere.text())
                    # Remove double quotes and split the string into elements
                    cleaned_str = self.content.editWhere.text().replace('"', '').split(',')

                    # Convert the cleaned list into a tuple
                    value = tuple(cleaned_str)
                    print("value :", value)
                    print("type(value)", type(value))

                    str_value = ""
                    for i in range(len(value)):
                        str_value = str_value + "%s,"

                    str_value = str_value[:-1]
                    print("str_value :", str_value)
                    self.sql_payload['sql'] = "INSERT INTO " + self.content.editTableName.text() + \
                        " (" + self.content.editFrom.text() + ") VALUES (" + str_value + ")"
                    
                    self.sql_payload['val'] = value
                    self.sql_payload['Duplicate'] = self.StrCanDuplicate
                    if len(self.content.key_no_duplicate) == 0:
                        check_Duplicate = self.content.editFrom.text().split(",")
                        self.content.key_no_duplicate = check_Duplicate[0]
                    
                    print("self.content.key_no_duplicate :", self.content.key_no_duplicate)
                    self.sql_payload['Duplicate_key'] = self.content.key_no_duplicate

                # 'UPDATE'
                # sql = "UPDATE tablename SET address = 'Canyon 123' WHERE address = 'Valley 345'"
                if self.content.sqlUpdate_flag:
                    self.sql_payload['sql'] = "UPDATE " + self.content.editTableName.text() + \
                        " SET " + self.content.editFrom.text() + " WHERE " + self.content.editWhere.text() + " = '" + self.content.editUpdateWhereKey.text() + "'"
                    
                # 'SELECT'
                # "SELECT * FROM tablename"
                # "SELECT name, address FROM tablename"
                # "SELECT col1, col2,…colnN FROM tablename WHERE id = 10";
                if self.content.sqlSelect_flag:
                    sql = "SELECT "
                    if len(self.content.editFrom.text()) == 0:
                        sql = sql + "* FROM " + self.content.editTableName.text()
                    else:
                        sql = sql + self.content.editFrom.text() + " FROM " + self.content.editTableName.text()

                    if len(self.content.editWhere.text()) > 0 and self.content.editUpdateWhereKey.text():
                        sql = sql + self.content.editFrom.text() + " WHERE " + self.content.editWhere.text() + " = '" + self.content.editUpdateWhereKey.text() + "'"

                    self.sql_payload['sql'] = sql

                # "DELETE FROM tablename WHERE data = 'Mountain 21'"
                if self.content.sqlDelete_flag:
                    sql = "DELETE FROM " + self.content.editTableName.text() 
                    if len(self.content.editWhere.text()) > 0 and len(self.content.editUpdateWhereKey.text()):
                        sql = sql + " WHERE " + self.content.editWhere.text() + " = '" + self.content.editUpdateWhereKey.text() + "'"
                        
                    else:
                        sql = ""

                    self.sql_payload['sql'] = sql

            else:
                self.sql_payload['sql'] = ""

        self.value = self.sql_payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

    def SelectInsertFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.sqlInsert_flag = True
            self.content.sqlUpdate_flag = False
            self.content.sqlSelect_flag = False
            self.content.sqlDelete_flag = False


            self.content.sqlUpdate.setChecked(False)
            self.content.sqlSelect.setChecked(False)
            self.content.sqlDelete.setChecked(False)

            self.content.lblFrom.setText("Columns : ")
            self.content.lblFrom.setVisible(True)
            self.content.editFrom.setVisible(True)
            self.content.editFrom.setPlaceholderText("Columns")

            self.content.lblWhere.setText("VALUE : ")
            self.content.lblWhere.setVisible(True)
            self.content.editWhere.setVisible(True)
            self.content.editWhere.setPlaceholderText("Value")

            self.content.lblUpdateWhere.setVisible(False)
            self.content.editUpdateWhereKey.setVisible(False)

            if self.content.sqlDuplicate_flag:
                self.content.sqlDuplicate.setText("Can Duplicate")
                self.content.DataDupl.setVisible(False)
            else:
                self.content.sqlDuplicate.setText("No Duplicate")
                self.content.DataDupl.setVisible(True)

            self.content.sqlDuplicate.setVisible(True)
        else:
            self.content.sqlInsert_flag = False
            self.content.lblFrom.setVisible(False)
            self.content.editFrom.setVisible(False)
            self.content.lblWhere.setVisible(False)
            self.content.editWhere.setVisible(False)

            self.content.sqlDuplicate.setVisible(False)
            
    
    def SelectUpdateFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.sqlInsert_flag = False
            self.content.sqlUpdate_flag = True
            self.content.sqlSelect_flag = False
            self.content.sqlDelete_flag = False

            self.content.sqlInsert.setChecked(False)
            self.content.sqlSelect.setChecked(False)
            self.content.sqlDelete.setChecked(False)
            
            self.content.lblFrom.setText("SET : ")
            self.content.lblFrom.setVisible(True)
            self.content.editFrom.setVisible(True)
            self.content.editFrom.setPlaceholderText("Row ID")
            self.content.DataDupl.setVisible(False)

            self.content.lblWhere.setText("WHERE : ")
            self.content.lblWhere.setVisible(True)
            self.content.editWhere.setVisible(True)
            self.content.editWhere.setPlaceholderText("Whare")

            self.content.lblUpdateWhere.setVisible(True)
            self.content.editUpdateWhereKey.setVisible(True)

        else:
            self.content.sqlUpdate_flag = False

    def SelectSelectFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.sqlInsert_flag = False
            self.content.sqlUpdate_flag = False
            self.content.sqlSelect_flag = True
            self.content.sqlDelete_flag = False

            self.content.sqlInsert.setChecked(False)
            self.content.sqlUpdate.setChecked(False)
            self.content.sqlDelete.setChecked(False)

            self.content.lblFrom.setText("SELECT : ")
            self.content.lblFrom.setVisible(True)

            self.content.editFrom.setVisible(True)
            self.content.editFrom.setPlaceholderText("col1, col2")

            self.content.lblWhere.setText("WHERE : ")
            self.content.lblWhere.setVisible(True)
            self.content.editWhere.setVisible(True)
            self.content.editWhere.setPlaceholderText("Whare")

            self.content.lblUpdateWhere.setVisible(True)
            self.content.editUpdateWhereKey.setVisible(True)

        else:
            self.content.sqlSelect_flag = False

    def SelectDeleteFunction(self, state):
        if state == QtCore.Qt.Checked:
            self.content.sqlInsert_flag = False
            self.content.sqlUpdate_flag = False
            self.content.sqlSelect_flag = False
            self.content.sqlDelete_flag = True

            self.content.sqlUpdate.setChecked(False)
            self.content.sqlSelect.setChecked(False)
            self.content.sqlInsert.setChecked(False)

            self.content.lblWhere.setText("WHERE : ")
            self.content.lblWhere.setVisible(True)
            self.content.editWhere.setVisible(True)
            self.content.editWhere.setPlaceholderText("Whare")

            self.content.lblUpdateWhere.setVisible(True)
            self.content.editUpdateWhereKey.setVisible(True)

        else:
            self.content.sqlDelete_flag = False

    def CanDuplicate(self, state):
        if state == QtCore.Qt.Checked:
            self.content.sqlDuplicate_flag = True
            self.content.sqlDuplicate.setText("Can Duplicate")
            self.content.DataDupl.setVisible(False)
        else:
            self.content.sqlDuplicate_flag = False
            self.content.sqlDuplicate.setText("No Duplicate")
            self.content.DataDupl.setVisible(True)

            self.content.key_no_duplicate = self.content.DataDupl.text()

    def Request_interval(self):
        self.Wait_Debound_Request = False
        self.content.RequestInterval_timer.stop()




        