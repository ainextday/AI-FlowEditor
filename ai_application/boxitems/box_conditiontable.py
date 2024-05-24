from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import*
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 

import cv2
import os
import numpy as np

import datetime
import time

# using ast.literal_eval()
import ast

class CONDITIONTABLE(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.bgImagePath = self.Path + "/icons/icons_gray_spot_30.png"
        self.edit_icon = self.Path + "/icons/icons_setting_20.gif"
        self.brows_icon = self.Path + "/icons/icons_save.png"
        self.save_icon = self.Path + "/icons/icons_save_icon_30.png"
        self.refresh_icon = self.Path + "/icons/icons_refresh.png"

        self.lbl = QLabel("No." , self)
        #self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setGeometry(10,5,20,20)
        self.lbl.setStyleSheet("color: orange")

        self.lblGap = QLabel("Gap : ", self)
        #self.lblGap.setAlignment(Qt.AlignLeft)
        self.lblGap.setGeometry(145,5,65,20)
        self.lblGap.setStyleSheet("color: orange")

        self.editGap = QLineEdit("15", self)
        self.editGap.setGeometry(175,5,30,20)
        self.editGap.setPlaceholderText("10")

        self.lblKey1 = QLabel("KEY 1 : ", self)
        #self.lblKey1.setAlignment(Qt.AlignLeft)
        self.lblKey1.setGeometry(235,5,65,20)
        self.lblKey1.setStyleSheet("color: orange")

        self.edit = QLineEdit(self)
        self.edit.setGeometry(275,5,30,20)
        self.edit.setPlaceholderText("key 1")

        self.lblKey2 = QLabel("KEY 2 : ", self)
        #self.lblKey2.setAlignment(Qt.AlignLeft)
        self.lblKey2.setGeometry(385,5,65,20)
        self.lblKey2.setStyleSheet("color: orange")

        self.edit2 = QLineEdit(self)
        self.edit2.setGeometry(425,5,30,20)
        self.edit2.setPlaceholderText("key 2")

        #====================================================
        self.lblPoseEval = QLabel(self)
        self.lblPoseEval.setGeometry(235,25,285,25)
        self.lblPoseEval.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:13pt;color:lightblue; border: 1px solid white; border-radius: 5%;")
        self.lblPoseEval.setAlignment(Qt.AlignCenter)
        self.lblPoseEval.setText("Pose Evaluation")

        self.lblDetection = QLabel(self)
        self.lblDetection.setGeometry(535,25,135,25)
        self.lblDetection.setStyleSheet("background-color: rgba(95, 150, 211, 225); font-size:13pt;color:lightblue; border: 1px solid white; border-radius: 5%;")
        self.lblDetection.setAlignment(Qt.AlignCenter)
        self.lblDetection.setText("Detection")

        self.resetBtn = QPushButton(self)
        self.resetBtn.installEventFilter(self)
        self.resetBtn.setGeometry(690,5,35,35)
        self.resetBtn.setIcon(QIcon(self.refresh_icon))

        #====================================================
        #====================================================
        self.checkSequence = QCheckBox("Sequence",self)
        self.checkSequence.setGeometry(50,5,80,20)
        self.checkSequence.setStyleSheet("color: lightblue")

        self.forceCtrlSQ = False

        self.pixmap = {}
        self.img = {}

        self.row_index = 55
        self.col_index = 7

        self.MatchIcon = [0 for x in range(self.row_index)]

        for i in range(self.row_index):
            """graphicsView = QGraphicsView(self)
            scene = QGraphicsScene()
            self.pixmap[i] = QGraphicsPixmapItem()
            scene.addItem(self.pixmap[i])
            graphicsView.setScene(scene)

            graphicsView.resize(30,30)
            graphicsView.setGeometry(QtCore.QRect(525, 50 + (i*35), 35, 35))"""

            self.MatchIcon[i] = QIcon(self.bgImagePath)

        ####################################################
        # Object Reference
        self.lblObjRef = QLabel("Ref : ", self)
        self.lblObjRef.setGeometry(535,5,65,20)
        self.lblObjRef.setStyleSheet("color: white")

        self.editObjRef = QLineEdit("", self)
        self.editObjRef.setGeometry(565,5,100,20)
        self.editObjRef.setPlaceholderText("Object Name")

        self.FirstObjRef_Rest = False
        #####################################################
        #====================================================
        # Create table
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(5,45,755,980)
        #self.tableWidget.setStyleSheet("QTableWidget { background-color: rgba(0, 32, 130, 100); gridline-color: #fffff8; font-size: 10pt; }")
        self.tableWidget.setStyleSheet("background-color: rgba(0, 124, 212, 50);font-size:10pt;color: #178CEA; gridline-color: #fffff8;")
        
        self.tableWidget.setRowCount(self.row_index)
        self.tableWidget.setColumnCount(self.col_index)

        font = QFont()
        font.setBold(True)
        self.tableWidget.setFont(font)

        self.cell0_width = 200

        # Set Fixed Collum Header Width
        header = self.tableWidget.horizontalHeader()       
        self.tableWidget.setColumnWidth(0 , self.cell0_width)
        self.tableWidget.setColumnWidth(1 , 75)
        self.tableWidget.setColumnWidth(2 , 75)
        self.tableWidget.setColumnWidth(3 , 75)
        self.tableWidget.setColumnWidth(4 , 75)
        self.tableWidget.setColumnWidth(5 , 150)
        self.tableWidget.setColumnWidth(6 , 55)
        """header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)"""
        header.setStyleSheet("background-color: rgba(0, 32, 130, 200);")

        # Set Colume Alignment Center
        delegate = AlignDelegate(self.tableWidget)
        #self.tableWidget.setItemDelegateForColumn(0, delegate)
        self.tableWidget.setItemDelegateForColumn(1, delegate)
        self.tableWidget.setItemDelegateForColumn(2, delegate)
        self.tableWidget.setItemDelegateForColumn(3, delegate)
        self.tableWidget.setItemDelegateForColumn(4, delegate)
        #self.tableWidget.setItemDelegateForColumn(5, delegate)
        self.tableWidget.setItemDelegateForColumn(6, delegate)

        # Set Fixed Row Height
        for i in range(self.row_index):
            self.tableWidget.setRowHeight(i, 35)

        self.tableWidget.setHorizontalHeaderLabels(['Element','X1', 'Y1', 'X2', 'Y2','Object','Match'])

        #Set ICon Size in Table
        self.tableWidget.setIconSize(QSize(30, 30))

        #===============================================
        """painter = QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.blue)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(100, 100, 100, 400)"""
        #===============================================

        self.lockflow = self.readFlowSetting('LockFlow')
        if self.lockflow == "true":
            self.edit.setEnabled(False)
            self.edit2.setEnabled(False)
            self.tableWidget.setEnabled(False)

        self.valid_Colnm = 0

        self.liststart = 0
        self.Data_list = list({'0':None , '1':None , '2':None , '3':None, '4':None, '5':None} for self.liststart in range(self.row_index))

        self.keyCheck1 = '15'
        self.keyCheck2 = '16'

        self.edit.setText(self.keyCheck1)
        self.edit2.setText(self.keyCheck2)

        self.Tolerances = int(self.editGap.text())
        print("===> self.Tolerances = ", self.Tolerances)

        self.Reset_timer = QtCore.QTimer(self)
        self.Select_timer = QtCore.QTimer(self)

        self.BlinkingState = False
        self.TimerBlinkCnt = 0

        #############################################################################
        #============================================================================
        # Setting Condition

        self.lableSteting_X = int(100)
        self.lableSteting_Y = int(896)

        self.lblSetting = QLabel(self)
        self.lblSetting.setGeometry(self.lableSteting_X + 5,self.lableSteting_Y - 3,550,26)
        self.lblSetting.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:13pt;color:lightblue; border: 1px solid white; border-radius: 5%;")

        self.labelPopupIconName = QLabel(self)
        self.labelPopupIconName.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:9pt;color:lightblue; border: 1px solid white; border-radius: 2%;")
        self.labelPopupIconName.setFixedWidth(55)
        self.labelPopupIconName.setFixedHeight(25)
        self.labelPopupIconName.setVisible(False)

        self.checkLoadData = QCheckBox("On Load",self)
        self.checkLoadData.setGeometry(self.lableSteting_X + 10, self.lableSteting_Y,80,20)
        self.checkLoadData.setStyleSheet("color: lightblue")

        ############################################
        #Move Load Table to Tab setting
        self.loadBtn = QPushButton(self)
        self.loadBtn.installEventFilter(self)
        self.loadBtn.setGeometry(self.lableSteting_X + 100,self.lableSteting_Y,20,20)
        self.loadBtn.setIcon(QIcon(self.brows_icon))

        self.saveBtn = QPushButton(self)
        self.saveBtn.installEventFilter(self)
        self.saveBtn.setGeometry(self.lableSteting_X + 132,self.lableSteting_Y,20,20)
        self.saveBtn.setIcon(QIcon(self.save_icon))

        ############################################

        self.undo_icon = self.Path + "/icons/icons_undo_15.png"
        self.undoBtn = QPushButton(self)
        self.undoBtn.installEventFilter(self)
        self.undoBtn.setGeometry(self.lableSteting_X + 350,self.lableSteting_Y,20,20)
        self.undoBtn.setIcon(QIcon(self.undo_icon))
        self.undoBtn.setStyleSheet("background-color: white")

        self.copy_icon = self.Path + "/icons/icons_copy_15.png"
        self.copyBtn = QPushButton(self)
        self.copyBtn.installEventFilter(self)
        self.copyBtn.setGeometry(self.lableSteting_X + 400,self.lableSteting_Y,20,20)
        self.copyBtn.setIcon(QIcon(self.copy_icon))
        self.copyBtn.setStyleSheet("background-color: white")

        self.cut_icon = self.Path + "/icons/icons_cut_15.png"
        self.cutBtn = QPushButton(self)
        self.cutBtn.installEventFilter(self)
        self.cutBtn.setGeometry(self.lableSteting_X + 430,self.lableSteting_Y,20,20)
        self.cutBtn.setIcon(QIcon(self.cut_icon))
        self.cutBtn.setStyleSheet("background-color: white")

        self.paste_icon = self.Path + "/icons/icons_paste_15.png"
        self.pasteBtn = QPushButton(self)
        self.pasteBtn.installEventFilter(self)
        self.pasteBtn.setGeometry(self.lableSteting_X + 460,self.lableSteting_Y,20,20)
        self.pasteBtn.setIcon(QIcon(self.paste_icon))
        self.pasteBtn.setStyleSheet("background-color: white")
        self.pasteBtn.setEnabled(False)

        self.inset_icon = self.Path + "/icons/icons_insert_15.png"
        self.insertBtn = QPushButton(self)
        self.insertBtn.installEventFilter(self)
        self.insertBtn.setGeometry(self.lableSteting_X + 490,self.lableSteting_Y,20,20)
        self.insertBtn.setIcon(QIcon(self.inset_icon))
        self.insertBtn.setStyleSheet("background-color: white")

        self.delete_action_flag = False
        self.delete_icon = self.Path + "/icons/icons_delete_15.png"
        self.deleteBtn = QPushButton(self)
        self.deleteBtn.installEventFilter(self)
        self.deleteBtn.setGeometry(self.lableSteting_X + 530,self.lableSteting_Y,20,20)
        self.deleteBtn.setIcon(QIcon(self.delete_icon))
        #self.deleteBtn.setStyleSheet("background-color: white")

        # ====== Jom Add Takt-Time Function ============================

        self.lblKey3 = QLabel("Takt-Time : ", self)
        self.lblKey3.setGeometry(self.lableSteting_X + 180, self.lableSteting_Y, 85, 20)
        self.lblKey3.setStyleSheet("color: orange")

        self.edit3 = QLineEdit("15",self)
        self.edit3.setGeometry(self.lableSteting_X + 250, self.lableSteting_Y, 30, 20)
        self.edit3.setPlaceholderText("Sec")

        #===============================================================

        self.LoadData_Flag = False

        self.startPopUpLBL_X = 250
        self.startPopUpLBL_Y = 370

        self.PopUplbl = QLabel(" Do you want to delete Row?" , self)
        self.PopUplbl.setGeometry(self.startPopUpLBL_X , self.startPopUpLBL_Y ,275,100)
        self.PopUplbl.setAlignment(Qt.AlignLeft)
        self.PopUplbl.setAlignment(Qt.AlignTop)
        self.PopUplbl.setStyleSheet("background-color: rgba(0, 32, 130, 225); font-size:12pt;color:lightblue; border: 1px solid white; border-radius: 5%")
        self.PopUplbl.setVisible(False)

        self.confirm_icon = self.Path + "/icons/icons_confirm_btn.png"
        self.no_icon = self.Path + "/icons/icons_no_btn.png"

        self.confirmBtn = QPushButton(self)
        self.confirmBtn.setGeometry(self.startPopUpLBL_X + 25 , self.startPopUpLBL_Y + 35 ,105,55)
        self.confirmBtn.setIcon(QIcon(self.confirm_icon))
        self.confirmBtn.setIconSize(QtCore.QSize(100,50))
        #Make Transparent
        self.confirmBtn.setStyleSheet("background-color: transparent; border: 0px;")  
        self.confirmBtn.setVisible(False)

        self.NoBtn = QPushButton(self)
        self.NoBtn.setGeometry(self.startPopUpLBL_X + 160 , self.startPopUpLBL_Y + 35 ,105,55)
        self.NoBtn.setIcon(QIcon(self.no_icon))
        self.NoBtn.setIconSize(QtCore.QSize(100,50))
        #Make Transparent
        self.NoBtn.setStyleSheet("background-color: transparent; border: 0px;")
        self.NoBtn.setVisible(False)

        #============================================================================
        #============================================================================
        #============================================================================

        self.logFilePath = self.Path[0:-9] + "/Database/log.txt"

    def serialize(self):
        if self.tableWidget is not None:
            for i in range(self.row_index):
                self.getdatarowcell(self.tableWidget ,i)

        #print("serialize +++> self.Data_list = ", self.Data_list)

        res = super().serialize()
        res['datalisttable'] = self.Data_list
        res['keydata1'] = self.keyCheck1
        res['keydata2'] = self.keyCheck2
        res['keydata3'] = self.edit3.text() # Jom adjust
        res['tolerances'] = self.Tolerances
        res['forceSquence'] = self.forceCtrlSQ
        res['loadData'] = self.LoadData_Flag
        res['objectNameRef'] = self.editObjRef.text()

        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'loadData' in data:
                self.LoadData_Flag = data['loadData']

                if self.LoadData_Flag:
                    self.checkLoadData.setChecked(True)

                    if 'datalisttable' in data:
                        self.Data_list = data['datalisttable']
                        #print("deserialize ---> self.Data_list = ", self.Data_list)
                        #print("deserialize ---> self.Data_list[3][2] = ", self.Data_list[3][str(2)])
                        
                        for i in range(len(self.Data_list)):
                            #print("Data_list[", i,"] = ", self.Data_list[i])
                            self.valid_Colnm = 0
                            for j in range(len(self.Data_list[i])):
                                if dict(self.Data_list[i]).get(str(j)) is not None:
                                    #print("deserialize ---> Data_list[" , i, "][", j, "] = ", self.Data_list[i][str(j)])
                                    self.tableWidget.setItem(i,j, QTableWidgetItem(str(self.Data_list[i][str(j)])))

                                    if len(self.Data_list[i][str(j)]) > 1:
                                        self.valid_Colnm += 1

                            if  self.valid_Colnm >= 2:
                                """self.img[i] = QPixmap(self.bgImagePath)
                                self.pixmap[i].setPixmap(self.img[i])"""

                                self.MatchIcon[i] = QIcon(self.bgImagePath)
                                self.tableWidget.setItem(i, 6, QTableWidgetItem(self.MatchIcon[i], ''))

                else:
                    self.checkLoadData.setChecked(False)

            if 'keydata1' in data:
                self.keyCheck1 = data['keydata1']
                self.edit.setText(self.keyCheck1)

            if 'keydata2' in data:
                self.keyCheck2 = data['keydata2']
                self.edit2.setText(self.keyCheck2)

            #========= Jom adjust function Takt Time===========
            if 'keydata3' in data:
                self.edit3.setText(str(data['keydata3']))
            #=============================================
            if 'tolerances' in data:
                self.Tolerances = data['tolerances']
                self.editGap.setText(str(self.Tolerances))

            if 'forceSquence' in data:
                self.forceCtrlSQ = data['forceSquence']
                if self.forceCtrlSQ:
                    self.checkSequence.setChecked(True)

            if 'objectNameRef' in data:
                if len(str(data['objectNameRef'])) > 0:
                    self.editObjRef.setText(str(data['objectNameRef']))

                else:
                    self.editObjRef.setText(str(data['pallet_track']))

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def stylesheet(self):
        return

    def readFlowSetting(self, key):
        settings = QSettings("Flow Setting")
        data = settings.value(key)
        return data

    def OnLoadFile(self):
        #print("load File")

        options = QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Text Files (*.txt)", options=options)

        if fileName:
            #print(fileName)
            file = open(fileName,'r', encoding="utf-8")
            text = file.read()
            #print()
            #print("text = ", text)
            #print()

            # Converting string to list
            list_text = ast.literal_eval(text)
            #list_text = json.loads(text)
            #print("list Text = ", list_text)
            #print()

            for i in range(len(list_text)):
                #print("Data_list[", i,"] = ", self.Data_list[i])
                for j in range(len(list_text[i])):
                    if dict(list_text[i]).get(str(j)) is not None:
                        #print("deserialize ---> list_text[" , i, "][", j, "] = ", list_text[i][str(j)])
                        self.tableWidget.setItem(i,j, QTableWidgetItem(str(list_text[i][str(j)])))
    
    def SaveFile(self, data):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            #print(fileName)

            file = open(fileName,'w', encoding="utf-8")
            #text = self.textEdit.toPlainText()
            
            file.write(str(data))
            file.close()

    #===================================================================
    # given a tablewidget which has a selected row...
    # return the column value in the same row which corresponds to a given column name
    # fyi: columnname is case sensitive
    #===================================================================

    def getdatarowcell(self, widget ,row):
        for j in range(self.col_index):
            if widget.item(row, j) is not None:
                
                self.Data_list[row][str(j)] = widget.item(row, j).text()
                #print("self.Data_list[", row ," , ", j ,"] = ", self.Data_list[row][str(j)])

        #print("self.Data_list[", row,"] = ", self.Data_list[row])

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(QtCore.Qt.blue)

        pen = QPen(Qt.white, 4, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawLine(227, 5, 227, 917)
        painter.drawLine(377, 5, 377, 917)
        painter.drawLine(527, 5, 527, 917)
        painter.drawLine(677, 5, 677, 917)

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.labelPopupIconName.setVisible(True)
            self.lableSteting_Y = int(896)
            
            if object == self.undoBtn:
                IconName = "Undo"
                PosX = self.lableSteting_X + 335  #Adjust -15

            elif object == self.copyBtn:
                IconName = "Copy"
                PosX = self.lableSteting_X + 385

            elif object == self.cutBtn:
                IconName = "Cut"
                PosX = self.lableSteting_X+ 415

            elif object == self.pasteBtn:
                IconName = "Paste"
                PosX = self.lableSteting_X + 445

            elif object == self.insertBtn:
                IconName = "Insert"
                PosX = self.lableSteting_X + 475

            elif object == self.deleteBtn:
                IconName = "Delete"
                PosX = self.lableSteting_X + 515

            elif object == self.loadBtn:
                IconName = "Browse"
                PosX = self.lableSteting_X + 85

            elif object == self.saveBtn:
                IconName = "Save"
                PosX = self.lableSteting_X + 115

            elif object == self.resetBtn:
                IconName = "Reset"
                PosX = 680
                self.lableSteting_Y = 80

            self.labelPopupIconName.setGeometry(PosX ,self.lableSteting_Y - 33, 50, 25)
            self.labelPopupIconName.setAlignment(Qt.AlignCenter)
            self.labelPopupIconName.setText(IconName)
            return True

        elif event.type() == QEvent.Leave:
            self.labelPopupIconName.setVisible(False)

        return False

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

@register_node(OP_NODE_CONDITION_TABLE)
class Open_CONDITIONTABLE(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_contable_icon.png"
    op_code = OP_NODE_CONDITION_TABLE
    op_title = "Condition Table"
    content_label_objname = "Condition Table"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}
        self.reciev_datazero = {}

        self.Now_secttime = 0

        self.Data = list({'0':None , '1':None , '2':None , '3':None, '4':None, '5':None} for self.content.liststart in range(self.content.row_index))
        self.compare_data = list({'0':None , '1':None , '2':None , '3':None} for self.content.liststart in range(self.content.row_index))
        self.matching = list({self.content.liststart:False} for self.content.liststart in range(self.content.row_index))
        self.matching_left = list({self.content.liststart:""} for self.content.liststart in range(self.content.row_index))
        self.matching_right = list({self.content.liststart:""} for self.content.liststart in range(self.content.row_index))
        self.matching_obj = list({self.content.liststart:""} for self.content.liststart in range(self.content.row_index))

        #==================Jom add for undo function=============================================
        self.Keep_For_Undo = list({'0': None , '1': None , '2': None , '3':None, '4':None} for self.content.liststart in range(self.content.row_index)) # list({'0': None , '1': None , '2': None , '3':None, '4':None} for self.content.liststart in range(self.content.row_index))
        self.Append_Keep_For_Undo = []
        self.Check_undo = 0
        #===============================================================

        self.save_matching = []
        self.match_time = []
        self.current_match = -1 # Jom fix bug for first circle
        self.latest_match = 0

        self.seq_matching = [-2,-1] # Jom add for keep matching sequence
        self.OnlyTrueSequence = 0   # Jom add for check real sequence
        self.Copy_Text = ['','','','','',''] # Jom add for copy text fucntion
        self.engine_model = "VVT" # Jom Rev2

        self.Macthed_cnt = 0
        self.TotalRow = 0
        self.ValidColum = 0
        self.All_TotalRow = 10 # Jom Rev2 = number equal process after skipped

        self.minute_flag = 0
        self.TotalRow_Const = 0

        self.match_start = False
        self.starttime = 0

        self.FirstMatch = False
        self.FirstStop = False
        self.FirstUpdateLog = False

        self.allow_process = False
        
        self.log = []
        self.LogEndProcess = ""
        self.round_cnt = 0

        self.prepareLogSave = ""
        self.LogSave = []

        self.select_row = 0
        self.select_collumn = 0

        self.NextSequence = 0

        self.payload['logtitlename'] = 'Pose Eval - STW'
        self.payload['inputtype'] = 'circlemark'

        self.select_onerowdata = ['', '', '', '', '','']
        self.select_row_flag = False

        self.copyText = None
        self.undo_cnt = 0
        self.backup_select_onerowdata = []

        self.undo = 0

    def initInnerClasses(self):
        self.content = CONDITIONTABLE(self)                   # <----------- init UI with data and widget
        self.grNode = FlowConditionTable(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.tableWidget.cellClicked.connect(self.cell_was_clicked)

        self.content.edit.textChanged.connect(self.ChangedKey1)
        self.content.edit2.textChanged.connect(self.ChangedKey2)
        self.content.editGap.textChanged.connect(self.GapChange)

        self.content.resetBtn.clicked.connect(self.ResetAllParam)
        self.content.loadBtn.clicked.connect(self.content.OnLoadFile)
        self.content.saveBtn.clicked.connect(self.OnSaveFile)

        self.content.checkSequence.stateChanged.connect(self.ControlSequence)

        self.content.Reset_timer.timeout.connect(self.ResetAllParam)
        self.content.Reset_timer.setInterval(2000)

        self.content.Select_timer.timeout.connect(self.HighligSelection)
        self.content.Select_timer.setInterval(100)

        self.content.checkLoadData.stateChanged.connect(self.ControlCheckLoadData)

        self.content.deleteBtn.clicked.connect(self.OnDeleRow)

        self.content.confirmBtn.clicked.connect(self.OnConfirmDelete)
        self.content.NoBtn.clicked.connect(self.OnCancelDelete)

        self.content.copyBtn.clicked.connect(self.CopyText)
        self.content.pasteBtn.clicked.connect(self.PasteText)

        # ===============Jom Add Copy paste ... button connect function
        self.content.cutBtn.clicked.connect(self.CutText)
        self.content.insertBtn.clicked.connect(self.InsertText)
        #self.content.deleteBtn.clicked.connect(self.DeleteText)
        self.content.undoBtn.clicked.connect(self.UndoText)
        #================================================

        self.Global = GlobalVariable()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        self.reciev_datazero = input_node.eval()

        if self.reciev_datazero is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()

            return

        elif self.reciev_datazero is not None:

            if 'clock' in self.reciev_datazero:
                #print("type(reciev_datazero['clock']) = ", type(self.reciev_datazero['clock']))  #Class str
                self.payload['clock'] = self.reciev_datazero['clock']

                secttime = time.strptime(self.reciev_datazero['clock'], '%H:%M:%S')
                if self.match_start:
                    Now_secttime = int(datetime.timedelta(hours=secttime.tm_hour,minutes=secttime.tm_min,seconds=secttime.tm_sec).total_seconds())
                    self.payload['secclock'] = Now_secttime - self.starttime

                else:
                    self.payload['secclock'] = 0

                if self.payload['secclock'] > 70:
                    self.content.FirstObjRef_Rest = False

            if 'stoptime' in self.reciev_datazero:
                self.payload['stoptime'] = self.reciev_datazero['stoptime']

            if self.Global.getGlobal("reset_log"):
                self.round_cnt = 0
                self.log.clear()
                self.Global.setGlobal("reset_log", False)

            # Jom rev2 ===========================================================
            try :
                if int(self.reciev_datazero['obj_found']) > 0:
                    for obj in range(int(self.reciev_datazero['obj_found'])):

                        #Check Object Reference Track if come to position then reset process
                        if str(self.reciev_datazero['yolo_boxes'][obj]['obj']) == self.content.editObjRef.text() and int(self.reciev_datazero['yolo_boxes'][obj]['score']) > 75 and \
                            not self.content.FirstObjRef_Rest and int(self.reciev_datazero['yolo_boxes'][obj]['x1']) > 95:
                            print()
                            print("Reset All Process by Object Referent !!!")
                            print()
                            self.content.FirstObjRef_Rest = True
                            self.ResetAllParam()
             
                        """if str(self.reciev_datazero['yolo_boxes'][obj]['obj']) == "bracket_engine" and int(self.reciev_datazero['yolo_boxes'][obj]['score']) > 75 and not self.content.FirstObjRef_Rest:
                            #Reset By bracket_engine
                            self.content.FirstObjRef_Rest = True
                            self.ResetAllParam()

                        if ( str(self.reciev_datazero['yolo_boxes'][obj]['obj']) == "bracket_engine" and int(self.reciev_datazero['yolo_boxes'][obj]['score']) > 75 and self.content.FirstObjRef_Rest):
                            self.engine_model = "Non-VVT"""

                        if self.Global.hasGlobal("back_no"):
                            if self.Global.getGlobal("back_no") == "503":
                                self.engine_model = "VVT"

                            else:
                                self.engine_model = "Non-VVT"

                            #print("1",self.engine_model)
                        #elif self.engine_model != "Non-VVT": 
                            #self.engine_model = "VVT"
                            #print("2",self.engine_model)
            except Exception as e :
                print(e)
                
            if 'centers' in self.reciev_datazero:

                """self.content.img = QPixmap(self.content.bgImagePath)
                self.content.pixmap.setPixmap(self.content.img)"""
                
                """print("centers = ",val['centers'])
                print()
                print("centers[7][0] = ", val['centers'][7][0])
                print("centers[7][1] = ", val['centers'][7][1])
                print()
                print("centers[4][0] = ", val['centers'][4][0])
                print("centers[4][1] = ", val['centers'][4][1])
                print()"""

                #print("type(val['centers']) = ", type(val['centers']))
                #print("centers = ",val['centers'])
                #print("centers[7] = ", val['centers'][7])
                #print("centers[4] = ", val['centers'][4])

                if self.content.tableWidget is not None:
                    for i in range(self.content.row_index):
                        self.ValidColum, self.compare_data[i] = self.reloaddatarowcell(self.content.tableWidget ,i)
                        self.matching_obj = list({self.content.liststart:""} for self.content.liststart in range(self.content.row_index))
                        if self.ValidColum > 0:
                            self.TotalRow += 1

                        # Jom rev2 ===========================================================
                        if (self.engine_model == "Non-VVT" and i == 1) or (self.engine_model == "Non-VVT" and i == 2):
                            self.content.bgImagePath = self.Path + "/icons/icons_skip_btn.png"
                            self.content.MatchIcon[1] = QIcon(self.content.bgImagePath)
                            self.content.tableWidget.setItem(1, 6, QTableWidgetItem(self.content.MatchIcon[1], ''))
                            self.content.MatchIcon[2] = QIcon(self.content.bgImagePath)
                            self.content.tableWidget.setItem(2, 6, QTableWidgetItem(self.content.MatchIcon[2], ''))
                            continue 

                        #==================================================================  
                            
                        #print("self.compare_data[",i,"].get('5') = ", self.compare_data[i].get('5'))
                        #print("len(self.compare_data[",i,"].get('5')) = ", len(str(self.compare_data[i].get('5'))))
                        #for j in range(len(self.compare_data[i])):

                        if dict(self.compare_data[i]).get('5') is not None and len(dict(self.compare_data[i]).get('5')) > 0:

                            if int(self.reciev_datazero['obj_found']) > 0:
                                #print("obj_found = ", self.reciev_datazero['obj_found'])

                                for obj in range(int(self.reciev_datazero['obj_found'])):
                                    #print("obj_found[", obj, "] = ", self.reciev_datazero['yolo_boxes'][obj]['obj'])
                                    #print("len(obj_found[", obj, "]) = ", len(str(self.reciev_datazero['yolo_boxes'][obj]['obj'])))

                                    if str(self.reciev_datazero['yolo_boxes'][obj]['obj']) == str(dict(self.compare_data[i]).get('5')) and int(self.reciev_datazero['yolo_boxes'][obj]['score']) > 55:
                                        self.matching_obj[i] = "matched"
                                        #print("self.matching_obj[",7,"=]",str(dict(self.compare_data[7]).get('5')))

                                        #print("self.matching_obj[", i, "] = ", self.matching_obj[i])

                        if dict(self.compare_data[i]).get('1') is not None and dict(self.compare_data[i]).get('2') is not None:
                            if int(self.content.keyCheck1) in self.reciev_datazero['centers']:
                                #print("Found key ", self.content.keyCheck1, " in reciev_datazero['centers']")

                                if 'focus_area' in self.reciev_datazero:
                                    if self.reciev_datazero['focus_area'] and self.reciev_datazero['set_focus_area'] is not None and self.reciev_datazero['set_new_scale'] is not None:

                                        diffX = float(round(self.reciev_datazero['set_new_scale'][0], 5))
                                        diffY = float(round(self.reciev_datazero['set_new_scale'][1], 5))
                                       
                                        xl = int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][0] * diffX) + self.reciev_datazero['set_focus_area'][0]
                                        yl = int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][1] * diffY) + self.reciev_datazero['set_focus_area'][1]

                                        #print("self.Global.getGlobal('teminal_pos_select') = ", self.Global.getGlobal("teminal_pos_select"))
                                        #print(" ---> Left self.reciev_datazero['centers'] = ", self.reciev_datazero['centers'], " ,xl = ", xl, " ,yl = ", yl, " ,diffX = ", diffX, " ,diffY = ", diffY)

                                        if ( xl > int(self.compare_data[i]['1']) - self.content.Tolerances and xl < int(self.compare_data[i]['1']) + self.content.Tolerances) and \
                                            ( yl > int(self.compare_data[i]['2']) - self.content.Tolerances and yl < int(self.compare_data[i]['2']) + self.content.Tolerances):
                                                #print("Match row[", i ,"] on keyCheck1")
                                                self.matching_left[i] = "matched"

                                                self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"

                                                self.content.img[i] = QPixmap(self.content.bgImagePath)
                                                self.content.pixmap[i].setPixmap(self.content.img[i])

                                        else:
                                            self.matching_left[i] = "not_matched"

                                    else:
                                        if ( int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][0]) > int(self.compare_data[i]['1']) - self.content.Tolerances and \
                                            int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][0]) < int(self.compare_data[i]['1']) + self.content.Tolerances) and \
                                            ( int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][1]) > int(self.compare_data[i]['2']) - self.content.Tolerances and \
                                            int(self.reciev_datazero['centers'][int(self.content.keyCheck1)][1]) < int(self.compare_data[i]['2']) + self.content.Tolerances):
                                                #print("Match row[", i ,"] on keyCheck1")
                                                self.matching_left[i] = "matched"

                                        else:
                                            self.matching_left[i] = "not_matched"
                        else:
                            self.matching_left[i] = "skip"

                        if dict(self.compare_data[i]).get('3') is not None and dict(self.compare_data[i]).get('4') is not None:
                            if int(self.content.keyCheck2) in self.reciev_datazero['centers']:
                                
                                if 'focus_area' in self.reciev_datazero:
                                    if self.reciev_datazero['focus_area']  and self.reciev_datazero['set_focus_area'] is not None and self.reciev_datazero['set_new_scale'] is not None:

                                        diffX = float(round(self.reciev_datazero['set_new_scale'][0], 5))
                                        diffY = float(round(self.reciev_datazero['set_new_scale'][1], 5))

                                        xr = int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][0] * diffX) + self.reciev_datazero['set_focus_area'][0]
                                        yr = int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][1] * diffY) + self.reciev_datazero['set_focus_area'][1]

                                        #print(" ---> Right self.reciev_datazero['centers'] = ", self.reciev_datazero['centers'], " ,xr = ", xr, " ,yr = ", yr, " ,diffX = ", diffX, " ,diffY = ", diffY)
                                        #print()

                                        if ( xr > int(self.compare_data[i]['3']) - self.content.Tolerances and xr < int(self.compare_data[i]['3']) + self.content.Tolerances) and \
                                                ( yr > int(self.compare_data[i]['4']) - self.content.Tolerances and yr < int(self.compare_data[i]['4']) + self.content.Tolerances):
                                                    #print("Match row[", i ,"] on keyCheck2")
                                                    self.matching_right[i] = "matched"

                                        else:
                                            self.matching_right[i] = "not_matched"

                                    else:
                                        if ( int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][0]) > int(self.compare_data[i]['3']) - self.content.Tolerances and \
                                            int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][0]) < int(self.compare_data[i]['3']) + self.content.Tolerances) and \
                                            ( int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][1]) > int(self.compare_data[i]['4']) - self.content.Tolerances and \
                                            int(self.reciev_datazero['centers'][int(self.content.keyCheck2)][1]) < int(self.compare_data[i]['4']) + self.content.Tolerances):
                                                #print("Match row[", i ,"] on keyCheck2")
                                                self.matching_right[i] = "matched"

                                        else:
                                            self.matching_right[i] = "not_matched"                                       
                            
                        else:
                            self.matching_right[i] = "skip"

                        if (self.matching_left[i] == "matched" and self.matching_right[i] == "matched") or self.matching_obj[i] == "matched":
                            self.matching[i] = True

                        elif (self.matching_left[i] == "matched" and self.matching_right[i] == "skip") or self.matching_obj[i] == "matched":
                            self.matching[i] = True

                        elif (self.matching_left[i] == "skip" and self.matching_right[i] == "matched") or self.matching_obj[i] == "matched":
                            self.matching[i] = True
                        else:
                            self.matching[i] = False

                        # elif (self.matching_left[i] == "skip" and self.matching_right[i] == "skip") and self.matching_obj[i] == "matched":
                        #     self.matching[i] = True

                        #print("self.matching[", i, "] = ", self.matching[i])

                        #First Match 
                        if self.matching[0] == True and not self.FirstMatch:
                                self.FirstMatch = True

                                # Clear all Result
                                print("Clear Match Parameter before run process <---")
                                self.content.bgImagePath = self.Path + "/icons/icons_gray_spot_30.png"
                                for i in range(int(self.TotalRow_Const)):
                                    self.matching[i] = False
                                    self.matching_left[i] = "not_matched"
                                    self.matching_right[i] = "not_matched"

                                    """self.content.img[i] = QPixmap(self.content.bgImagePath)
                                    self.content.pixmap[i].setPixmap(self.content.img[i])"""

                                    self.content.MatchIcon[i] = QIcon(self.content.bgImagePath)
                                    self.content.tableWidget.setItem(i, 6, QTableWidgetItem(self.content.MatchIcon[i], ''))

                                    #============== Jom add for green/red dot should be follow amount of row item
                                    """item = QtWidgets.QTableWidgetItem()
                                    icon = QtGui.QIcon()
                                    icon.addPixmap(QtGui.QPixmap(self.content.bgImagePath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                                    item.setIcon(icon)
                                    self.content.tableWidget.setItem(i, 6, item)
                                    size = QSize(30,30)
                                    self.content.tableWidget.setIconSize(size)"""
                                    #==========================================================================

                                print("Start Pose STW Process !!!")
                                self.match_start = True                 

                                self.FirstStop = False
                                self.FirstUpdateLog = False

                                sec_starttime = time.strptime(self.reciev_datazero['clock'], '%H:%M:%S')
                                self.starttime = int(datetime.timedelta(hours=sec_starttime.tm_hour,minutes=sec_starttime.tm_min,seconds=sec_starttime.tm_sec).total_seconds())

                                self.save_matching.clear()
                                self.match_time.clear()

                                for self.content.liststart in range(self.TotalRow_Const):
                                    self.save_matching.append(False)
                                    self.match_time.append("-")

                                self.allow_process = True
                        #print("Bself.matching[]" ,self.matching)
                        if self.matching[i] == True and self.allow_process:
                            """ ==================    Revise by pat for takt time function ==============="""
                            for l in range(self.content.row_index): # Count green signal for calculate score
                                if self.matching[l] == True and l not in self.seq_matching and ((l-self.seq_matching[-1]) == 1 or (l-self.seq_matching[-1]) == 2 or (l-self.seq_matching[-1]) == 3) :  # Prevent matching duplicate number                         
                                    self.seq_matching.append(l)

                                    # Jom Rev3 ===========================================================
                                    if self.matching[2] == 0 and self.engine_model == "Non-VVT" and len(self.seq_matching) == 3 :
                                        self.seq_matching.append(1) # append dummy for skip step 2
                                        self.seq_matching.append(2) # append dummy for skip step 3
                                        self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"
                                        self.content.MatchIcon[self.seq_matching[2]] = QIcon(self.content.bgImagePath)
                                        self.content.tableWidget.setItem(self.seq_matching[2], 6, QTableWidgetItem(self.content.MatchIcon[self.seq_matching[2]], '')) # if reach to this condition mean fisrt sequence matched correctly and Non-VVT type
                                    # End ===================================================================

                                    print("seq_matching.append = " ,self.seq_matching)
                                    self.OnlyTrueSequence += 1 # Count only True Sequence
                                    print('self.OnlyTrueSequence' , self.OnlyTrueSequence)
                                    if len(self.seq_matching) == 3: # check first match (No need to step 1 mathed)
                                        sec_starttime = time.strptime(self.reciev_datazero['clock'], '%H:%M:%S')
                                        self.starttime = int(datetime.timedelta(hours=sec_starttime.tm_hour,minutes=sec_starttime.tm_min,seconds=sec_starttime.tm_sec).total_seconds())
                                        print("Time Start = ",self.starttime)

                                    if not self.save_matching[l]:
                                        self.save_matching[l] = True

                                        Now_secttime = int(datetime.timedelta(hours=secttime.tm_hour,minutes=secttime.tm_min,seconds=secttime.tm_sec).total_seconds())
                                        self.match_time[l] = Now_secttime - self.starttime

                                        self.latest_match = l
                            """ ================== End Revise by Jom ==============="""

                            #Normal Stept which no squence
                            if not self.content.forceCtrlSQ:
                                self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"

                                """self.content.img[i] = QPixmap(self.content.bgImagePath)
                                self.content.pixmap[i].setPixmap(self.content.img[i])"""

                                self.content.MatchIcon[i] = QIcon(self.content.bgImagePath)
                                self.content.tableWidget.setItem(i, 6, QTableWidgetItem(self.content.MatchIcon[i], ''))

                                ##### ==================    Revise by Jom for icon follow table ==============="""    
                                """item = QtWidgets.QTableWidgetItem()
                                icon = QtGui.QIcon()
                                icon.addPixmap(QtGui.QPixmap(self.content.bgImagePath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                                item.setIcon(icon)
                                self.content.tableWidget.setItem(i, 6, item)
                                size = QSize(30,30)
                                self.content.tableWidget.setIconSize(size)"""
                                # self.content.img[i] = QPixmap(self.content.bgImagePath)
                                # self.content.pixmap[i].setPixmap(self.content.img[i])
                                #### End =================================================================================

                            else:
                                
                                """ ==================    Revise by Jom for check detect skip matching process ==============="""
                                try :
                                    if (self.seq_matching[-1] - self.seq_matching[-2]) == 1 and all(x < self.seq_matching[-1] for x in self.seq_matching[0:-1] ): #Check current with last diff = 1 and cur-match > all previouse match:
                                        self.content.bgImagePath = self.Path + "/icons/icons_green_spot_30.png"

                                        self.content.MatchIcon[self.seq_matching[-1]] = QIcon(self.content.bgImagePath)
                                        self.content.tableWidget.setItem(self.seq_matching[-1], 6, QTableWidgetItem(self.content.MatchIcon[self.seq_matching[-1]], ''))
                                       
                                        self.content.MatchIcon[self.seq_matching[-2]] = QIcon(self.content.bgImagePath)
                                        self.content.tableWidget.setItem(self.seq_matching[-2], 6, QTableWidgetItem(self.content.MatchIcon[self.seq_matching[-2]], ''))

                                        if (self.seq_matching[-1] - self.seq_matching[-2]) == 1 and (self.seq_matching[-2] - self.seq_matching[-3]) > 1 :
                                            self.content.bgImagePath = self.Path + "/icons/icons_red_spot_30.png"
                                            self.count_red = (self.seq_matching[-2] - self.seq_matching[-3]) - 1
                                            for a in range(self.count_red):
                                                self.content.MatchIcon[self.seq_matching[-2]-a-1] = QIcon(self.content.bgImagePath) # แดงตัวเดียวไม่ work
                                                self.content.tableWidget.setItem(self.seq_matching[-2]-a-1, 6, QTableWidgetItem(self.content.MatchIcon[self.seq_matching[-2]-a-1], ''))                                        

                                        # self.content.img[self.seq_matching[-1]] = QPixmap(self.content.bgImagePath)  # change i to relate with seq_matching[-1] and seq_matching[-2] 
                                        # self.content.pixmap[self.seq_matching[-1]].setPixmap(self.content.img[self.seq_matching[-1]])
                                        # self.content.img[self.seq_matching[-2]] = QPixmap(self.content.bgImagePath)  # change i to relate with seq_matching[-1] and seq_matching[-2] 
                                        # self.content.pixmap[self.seq_matching[-2]].setPixmap(self.content.img[self.seq_matching[-2]])
                                        
                                except Exception as e :
                                    pass
                                """ ================== End Revise by Jom ==============="""


                            if self.matching[self.TotalRow_Const - 1] == True and not self.FirstStop and len(self.seq_matching)+1 >= self.TotalRow_Const or \
                                (int(datetime.timedelta(hours=secttime.tm_hour,minutes=secttime.tm_min,seconds=secttime.tm_sec).total_seconds()) - self.starttime) > int(self.content.edit3.text()): # Check Final Step Matching """ ===Revise by Jom ==== Solved not completed when final step matched"""
                                
                                if int(self.payload['secclock']) > 70:
                                    self.FirstStop = True
                                    self.round_cnt += 1

                                    #self.seq_matching = [-2,-1] #  Jom add reset seq_count when finish loop
                                    
                                    #print("TotalRow = ", self.TotalRow_Const)
                                    print("End of Takt Time = ",self.Now_secttime)

                                    #print("TotalRow = ", self.TotalRow_Const)
                                    print("Stop... Pose STW Process !!!")

                                    self.allow_process = False

                                    self.content.FirstObjRef_Rest = False
                            
                            # self.current_match = i # Jom fix keep for the real match
                            #print("self.current_match = ", self.current_match)

                            #print("self.save_matching[", i, "] = ", self.save_matching[i])
                            # if not self.save_matching[i]:   # Jom move code to upper condition
                            #     self.save_matching[i] = True

                            #     Now_secttime = int(datetime.timedelta(hours=secttime.tm_hour,minutes=secttime.tm_min,seconds=secttime.tm_sec).total_seconds())
                            #     self.match_time[i] = Now_secttime - self.starttime

                            #     self.latest_match = i
                    
                    for m in range(self.content.row_index):
                        if self.matching[m] == True:
                            self.Macthed_cnt += 1
                        
                    #print("self.Macthed_cnt = ", self.Macthed_cnt)
                    #print("self.TotalRow = ", self.TotalRow)

                    self.payload['matched'] = self.Macthed_cnt
                    self.payload['matched_TrueSequence'] = self.OnlyTrueSequence
                    self.payload['nextprocess'] = self.current_match + 2
                    self.payload['nextaddress'] = self.compare_data[self.latest_match + 1] # Jom change for self.current_match to self.latest_match
                    # print(self.current_match)
                    # print(self.payload['nextaddress'])
                    self.payload['totprocess'] = self.TotalRow
                    self.TotalRow_Const = self.TotalRow

                    self.payload['gap'] = self.content.Tolerances

                    self.payload['texttitlename'] = "Match Element"
                    self.payload['matchtime'] = self.match_time

                    if 'fps' in self.payload:
                        self.payload.pop('fps')

                    self.Macthed_cnt = 0
                    self.TotalRow = 0

            # Condition End process
            if self.FirstStop and not self.FirstUpdateLog:
                if int(self.payload['secclock']) > 70:
                    self.content.Reset_timer.start()

                    self.FirstUpdateLog = True
                
                    self.Record_Log()
                
        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value

    def Record_Log(self):

        total_process = self.payload['totprocess']

        if self.engine_model == "Non-VVT":  
            total_process = total_process - 2

        MatchResult = ""

        print("Record_Log and Stop Record Video if has record process !!!")
        if int(self.payload['matched_TrueSequence']/total_process * 100) == 100:
            MatchResult = "In Std"
            self.Global.setGlobal('delete_video', True)
        else:
            self.Global.setGlobal('delete_video', False)
            MatchResult = "Out Std"

        self.LogEndProcess = str(self.round_cnt) + " . "+ self.engine_model + "; " + MatchResult + \
            " ( " + str(self.payload['secclock']) + " Sec )"

        LogSQLProcess = self.engine_model + ";" + MatchResult + \
            " ( " + str(self.payload['secclock']) + " Sec )"

        #print("LogEndProcess = ", self.LogEndProcess)
        self.log.append(self.LogEndProcess)

        self.payload['log'] = self.log
        #print("Condition Table ==> self.payload['log'] = ", self.payload['log'])

        self.timeString = datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")

        back_no = ""
        if self.Global.hasGlobal("back_no"):
            back_no = self.Global.getGlobal("back_no")

        engine_type = ""
        if self.Global.hasGlobal("engine_type"):
            engine_type = self.Global.getGlobal("engine_type")

        engine_no = ""
        if self.Global.hasGlobal("engine_no"):
            engine_no = self.Global.getGlobal("engine_no")

        convert_seq_matching = str(self.seq_matching)
        #print("convert_seq_matching = ", convert_seq_matching)

        """convert_seq_matching.replace(",", "|")
        print("New convert_seq_matching = ", convert_seq_matching)"""

        #Don't use special character as _ : 
        self.prepareLogSave = LogSQLProcess + ";" + str(convert_seq_matching) + ";" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +\
                ";" + str(back_no) + "-" + str(engine_type) + str(engine_no) + ";"
        self.Global.setGlobal("SQLite_Feed",self.prepareLogSave)

        self.prepareLogSave = self.prepareLogSave + "\n"
        self.LogSave.append(self.prepareLogSave) 
        #print("self.LogSave = ", self.LogSave)

        if os.path.isfile(self.content.logFilePath):
            #print ("File exist")

            strLog = ""
            strLog = strLog.join(map(str, self.LogSave))
            #print("strLog = ", strLog)

            file = open(self.content.logFilePath,'w')
            file.write(str(strLog))
            file.close()

            #print("Record Log Completed !!!")

        self.OnlyTrueSequence = 0  
        self.seq_matching = [-2,-1] #  Jom add reset seq_count when finish loop

    def ChangedKey1(self):
        self.content.keyCheck1 = self.content.edit.text()

    def ChangedKey2(self):
        self.content.keyCheck2 = self.content.edit2.text()

    def GapChange(self):
        self.content.Tolerances = int(self.content.editGap.text())
        
    def ResetAllParam(self):
        print("ResetAllParam()")
        print()
        print("self.FirstStop = ", self.FirstStop)
        print("self.OnlyTrueSequence = ", self.OnlyTrueSequence)
        print("self.payload['secclock'] = ", self.payload['secclock'])
        print("self.match_start = ", self.match_start)
        print()

        if not self.FirstStop and self.OnlyTrueSequence > 0 and self.payload['secclock'] > 30: #Make sure Reset From pending work process
            self.round_cnt += 1
            self.Record_Log()

        self.content.Reset_timer.stop()
        self.content.Select_timer.stop()

        self.FirstMatch = False
        self.seq_matching = [-2,-1] # Jom > Reset self.seq_matching by reset button
        self.match_start = False
        self.starttime = 0
        
        #self.round_cnt = 0
        self.current_match = -1
        self.latest_match = -1
        self.OnlyTrueSequence = 0
        self.Macthed_cnt = 0
        self.TotalRow = 0
        self.ValidColum = 0
        self.minute_flag = 0

        self.payload['secclock'] = 0

        self.match_time.clear()
        self.payload['matchtime'] = self.match_time

        self.engine_model = "VVT"

        #========================================
        # Reload New totalRow_Const

        self.TotalRow_Const = 0

        for m in range(self.content.row_index):
            self.ValidColum, self.compare_data[m] = self.reloaddatarowcell(self.content.tableWidget ,m)
                
            if self.ValidColum > 0:
                self.TotalRow_Const += 1

        print("New self.TotalRow_Const = ", self.TotalRow_Const)
        self.ValidColum = 0
        
        self.content.bgImagePath = self.Path + "/icons/icons_gray_spot_30.png"
        for i in range(int(self.TotalRow_Const)):
            self.matching[i] = False
            self.matching_left[i] = "not_matched"
            self.matching_right[i] = "not_matched"

            self.matching_obj[i] = "not_matched"

            """self.content.img[i] = QPixmap(self.content.bgImagePath)
            self.content.pixmap[i].setPixmap(self.content.img[i])"""

            """self.pic = QtGui.QPixmap()
            with open(self.content.bgImagePath, "rb") as image:
                f = image.read()

            self.pic.loadFromData(bytearray(f), 'png')

            self.content.lbPixmap[i].setScaledContents(True)
            self.content.lbPixmap[i].setPixmap(self.pic)
            self.content.lbPixmap[i].setVisible(True)
            self.content.tableWidget.setCellWidget(i, 6, self.content.lbPixmap[i])"""

            #Clear Icon in column 6 
            #self.content.tableWidget.setItem(i, 6, QTableWidgetItem(''))

            self.content.MatchIcon[i] = QIcon(self.content.bgImagePath)
            self.content.tableWidget.setItem(i, 6, QTableWidgetItem(self.content.MatchIcon[i], ''))

            # ====== Jom Add red icon follow current row when reset ==================
            """item = QtWidgets.QTableWidgetItem()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self.content.bgImagePath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            self.content.tableWidget.setItem(i, 6, item)
            size = QSize(30,30)
            self.content.tableWidget.setIconSize(size)"""
            # ====== Jom Add red icon follow current row when reset ==================

        print("self.matching",self.matching)

        self.payload['matched'] = self.Macthed_cnt
        self.payload['nextprocess'] = self.Macthed_cnt + 1
        self.payload['nextaddress'] = self.compare_data[self.Macthed_cnt]

        self.payload['totprocess'] = self.TotalRow_Const

        self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

    def OnSaveFile(self):
        #print("Save File")

        for i in range(self.content.row_index):
            ValidCol, self.compare_data[i] = self.reloaddatarowcell(self.content.tableWidget ,i)

        #print("self.Data_list = ", self.compare_data)
        #print("len(self.compare_data) = ", len(self.compare_data))

        self.content.SaveFile(self.compare_data)

    #===================================================================
    # given a tablewidget which has a selected row...
    # return the column value in the same row which corresponds to a given column name
    # fyi: columnname is case sensitive
    #===================================================================

    def reloaddatarowcell(self, widget ,row):
        valid_col = 0
        for j in range(self.content.col_index):
            if widget.item(row, j) is not None:
                #print("len(widget.item(row, j).text()) = ", len(widget.item(row, j).text()))
                if  len(widget.item(row, j).text()) > 1:
                    self.Data[row][str(j)] = widget.item(row, j).text()
                    #print("self.Data_list[", row ," , ", j ,"] = ", self.Data[row][j])

                    valid_col += 1

                    """ ================== Revise by Jom ===============""" # Revise bug when change value to 0 in the table
                    try:
                        if len(widget.item(row, 0).text()) > 1 :  # Debug for change X,Y to null (Data not update because len(null)=0 not matching to upper loop)
                            for k in range(self.content.col_index-1):
                                if len(widget.item(row, k+1).text()) == 0 :
                                    self.Data[row][str(k+1)] = None
                    except Exception as e:
                        # print(e)
                        pass    
                    """ ================== End Revise by Jom ==============="""

        #print("self.Data[", row,"] = ", self.Data[row])
        return valid_col, self.Data[row]

    #===================================================================
    def cell_was_clicked(self, row, column):
        #print("Row %d and Column %d was clicked" % (row, column))
        item = self.content.tableWidget.itemAt(row, column)
        
        self.content.tableWidget.clearSelection()
        self.select_onerowdata = ['', '', '', '', '', '']

        if column == 0:
            print("Select row ", row)
            self.content.Select_timer.stop()

            self.content.tableWidget.setRangeSelected(QTableWidgetSelectionRange(row, column, row, column + 6), True)
            for i in range(6):
                if self.content.tableWidget.item(row, i) is not None:
                    if  len(self.content.tableWidget.item(row, i).text()) > 1:
                        self.select_onerowdata[i] = self.content.tableWidget.item(row, i).text()

            # =================== Jom Set up the first value For Undo ==================================================
            if len(self.Append_Keep_For_Undo) == 0 :
                for a in range(6):
                    for b in range(0 , len(self.content.Data_list)):
                        if self.content.tableWidget.item(b, a) is not None: 
                            self.Keep_For_Undo[b][str(a)] = self.content.tableWidget.item(b, a).text()
                        else :
                            self.Keep_For_Undo[b][str(a)] = ''
                self.Append_Keep_For_Undo.append(self.Keep_For_Undo)
            # =================== Jom Set up the first value For Undo(END) ==================================================

            print("self.select_onerowdata = ", self.select_onerowdata)            
            self.select_row_flag = True
            
        elif column == 1 or column == 3:
            self.content.tableWidget.setRangeSelected(QTableWidgetSelectionRange(row, column, row, column + 1), True)
            self.content.Select_timer.start()

        elif column == 2 or column == 4:
            self.content.tableWidget.setRangeSelected(QTableWidgetSelectionRange(row, column, row, column - 1), True)
            self.content.Select_timer.start()

        else:
            self.content.Select_timer.stop()

        self.select_row = row
        self.select_collumn = column

    def HighligSelection(self):

        if self.content.TimerBlinkCnt >= 5:
            self.content.TimerBlinkCnt = 0
            if self.content.BlinkingState:
                if self.select_collumn == 1 or self.select_collumn == 3:
                    self.content.tableWidget.setRangeSelected(QTableWidgetSelectionRange(self.select_row, self.select_collumn, self.select_row, self.select_collumn + 1), True)

                elif self.select_collumn == 2 or self.select_collumn == 4:
                    self.content.tableWidget.setRangeSelected(QTableWidgetSelectionRange(self.select_row, self.select_collumn, self.select_row, self.select_collumn - 1), True)

                if self.Global.getGlobal("teminal_selectpos") is not None:
                    columnX = self.Global.getGlobal("teminal_selectpos")[0]
                    columnY = self.Global.getGlobal("teminal_selectpos")[1]

                    #print("columnX = ", columnX)
                    #print("columnY = ", columnY)

                    if self.select_collumn == 1 or self.select_collumn == 3:
                        self.content.tableWidget.setItem(self.select_row, self.select_collumn, QTableWidgetItem(str(columnX)))
                        self.content.tableWidget.setItem(self.select_row, self.select_collumn + 1, QTableWidgetItem(str(columnY)))

                    elif self.select_collumn == 2 or self.select_collumn == 4:
                        self.content.tableWidget.setItem(self.select_row, self.select_collumn - 1, QTableWidgetItem(str(columnX)))
                        self.content.tableWidget.setItem(self.select_row, self.select_collumn, QTableWidgetItem(str(columnY)))

                    self.Global.setGlobal("teminal_selectpos", None)

            else:
                self.content.tableWidget.clearSelection()
                
            self.content.BlinkingState = not self.content.BlinkingState

        self.content.TimerBlinkCnt += 1

    def ControlSequence(self, state):
        print("Set Forcre Control Sequene")

        if state == QtCore.Qt.Checked:
            self.content.forceCtrlSQ = True
        else:
            self.content.forceCtrlSQ = False

    def ControlCheckLoadData(self, state):
        print("Set Forcre Control Sequene")

        if state == QtCore.Qt.Checked:
            self.content.LoadData_Flag = True

        else:
            self.content.LoadData_Flag = False

    def OnDeleRow(self):
        print("Delete Row?")

        if self.select_row_flag:
            self.content.PopUplbl.setVisible(True)
            self.content.confirmBtn.setVisible(True)
            self.content.NoBtn.setVisible(True)
            self.content.delete_action_flag = True

    def OnConfirmDelete(self):
        self.content.tableWidget.removeRow(self.select_row)
        self.content.Data_list[self.select_row] = {'0':None , '1':None , '2':None , '3':None, '4':None, '5':None}
        
        self.select_row_flag = False
        self.content.PopUplbl.setVisible(False)
        self.content.confirmBtn.setVisible(False)
        self.content.NoBtn.setVisible(False)
        self.content.delete_action_flag = False

    def OnCancelDelete(self):
        self.select_row_flag = False
        self.content.PopUplbl.setVisible(False)
        self.content.confirmBtn.setVisible(False)
        self.content.NoBtn.setVisible(False)

        self.content.delete_action_flag = False

        self.content.Select_timer.stop()

    def CopyText(self):

        self.Copy_Text =  [self.select_onerowdata[0], self.select_onerowdata[1], self.select_onerowdata[2], self.select_onerowdata[3], self.select_onerowdata[4], self.select_onerowdata[5]]
        print(self.copyText)
        self.backup_select_onerowdata.append(self.select_onerowdata)
        self.undo_cnt += 1

        self.content.copyBtn.setEnabled(False)
        self.content.cutBtn.setEnabled(False)
        self.content.insertBtn.setEnabled(False)
        self.content.deleteBtn.setEnabled(False)
        self.content.pasteBtn.setEnabled(True)

    def PasteText(self):
        for n in range(6):
            self.content.Data_list[self.select_row][str(n)] = ''
            self.content.Data_list[self.select_row][str(n)] = self.Copy_Text[n]

        print( "Paste self.Data[",self.select_row,"] = ", self.content.Data_list[self.select_row])

        for i in range(len(self.content.Data_list)):
            #print("self.content.Data_list[", i,"] = ", self.content.Data_list[i])
            self.valid_Colnm = 0
            for j in range(len(self.content.Data_list[i])):
                if dict(self.content.Data_list[i]).get(str(j)) is not None:
                    #print("Paste ---> Data[" , i, "][", j, "] = ", self.content.Data_list[i][str(j)])
                    self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.content.Data_list[i][str(j)])))

                    if len(self.content.Data_list[i][str(j)]) > 1:
                        self.valid_Colnm += 1

            if  self.valid_Colnm >= 2:
                """self.content.img[i] = QPixmap(self.content.bgImagePath)
                self.content.pixmap[i].setPixmap(self.content.img[i])"""

                self.content.MatchIcon[i] = QIcon(self.content.bgImagePath)
                self.content.tableWidget.setItem(i, 6, QTableWidgetItem(self.content.MatchIcon[i], ''))

        #Clear self.select_onerowdata
        self.select_onerowdata = ['', '', '', '', '', '']

        self.content.copyBtn.setEnabled(True)
        self.content.cutBtn.setEnabled(True)
        self.content.insertBtn.setEnabled(True)
        self.content.deleteBtn.setEnabled(True)
        self.content.pasteBtn.setEnabled(False)

    # ============================= Jom Add all function ==========================================================================================================
    def DeleteText(self):
        self.First_strat_CutFn = 0
        if self.First_strat_CutFn == 0 :
            for a in range(6):
                for b in range(0 , len(self.content.Data_list)):
                    if self.content.tableWidget.item(b, a) is None:
                        self.content.Data_list[b][str(a)] = '' 

        for i in range(len(self.content.Data_list)):# Check จำนวน Row ล่าสุด (List)
            self.valid_Colnm = 0
            for j in range(len(self.content.Data_list[i])): # Check จำนวน  data ที่อยู่ใน Row ล่าสุด = 4 (Dict)
                if dict(self.content.Data_list[i]).get(str(j)) is not None:
                    #print("Paste ---> Data[" , i, "][", j, "] = ", self.Data[i][str(j)])
                    self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.content.Data_list[i][str(j)])))
            
        for m in range(6): 
            for p in range(self.select_row , len(self.content.Data_list)):
                try :
                    self.content.Data_list[p][str(m)] = self.content.tableWidget.item(p+1, m).text() #self.content.Data_list[p-1][str(m)]
                except Exception as e :
                    self.content.Data_list[p-1][str(m)] = ''
                    # print(e)
                    # print("m",m)
                    # print("p",p)
                    pass
            #print(self.content.Data_list)   
        #print("Insert Completed = " ,self.content.Data_list)

        for i in range(len(self.content.Data_list)):# Check จำนวน Row ล่าสุด (List)
            self.valid_Colnm = 0
            for j in range(len(self.content.Data_list[i])): # Check จำนวน  data ที่อยู่ใน Row ล่าสุด = 4 (Dict)
                if dict(self.content.Data_list[i]).get(str(j)) is not None:
                    #print("Paste ---> Data[" , i, "][", j, "] = ", self.Data[i][str(j)])
                    self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.content.Data_list[i][str(j)])))

                    if len(self.content.Data_list[i][str(j)]) > 1:
                        self.valid_Colnm += 1

            if  self.valid_Colnm >= 2:
                item = QtWidgets.QTableWidgetItem()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(self.content.bgImagePath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                item.setIcon(icon)
                self.content.tableWidget.setItem(i, 6, item)
                size = QSize(30,30)
                self.content.tableWidget.setIconSize(size)

        self.Append_Keep_For_Undo.append(self.content.Data_list) # Keep data for undo
        print("Deleted Completed")

    def InsertText(self):
        self.Insert_row = 0
        self.First_strat_InsertFn = 0
        if self.First_strat_InsertFn == 0 :
            for a in range(6):
                for b in range(0 , len(self.content.Data_list)):
                    if self.content.tableWidget.item(b, a) is None:
                        self.content.Data_list[b][str(a)] = '' 

        for i in range(len(self.content.Data_list)):# Check จำนวน Row ล่าสุด (List)
            self.valid_Colnm = 0
            for j in range(len(self.content.Data_list[i])): # Check จำนวน  data ที่อยู่ใน Row ล่าสุด = 4 (Dict)
                if dict(self.content.Data_list[i]).get(str(j)) is not None:
                    #print("Paste ---> Data[" , i, "][", j, "] = ", self.Data[i][str(j)])
                    self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.content.Data_list[i][str(j)])))
            
        for m in range(6):
            self.Insert_row = self.select_row +1 
            for p in range(self.Insert_row , len(self.content.Data_list)):
                try :
                    self.content.Data_list[p][str(m)] = self.content.tableWidget.item(p-1, m).text() #self.content.Data_list[p-1][str(m)]
                    self.content.Data_list[self.select_row][str(m)] = '' # ล้าง select_row?
                    #print(self.content.Data_list)
                except Exception as e :
                    self.content.Data_list[p-1][str(m)] = ''

                    pass
        #print("Insert Completed = " ,self.content.Data_list)

        for i in range(len(self.content.Data_list)):# Check จำนวน Row ล่าสุด (List)
            self.valid_Colnm = 0
            for j in range(len(self.content.Data_list[i])): # Check จำนวน  data ที่อยู่ใน Row ล่าสุด = 4 (Dict)
                if dict(self.content.Data_list[i]).get(str(j)) is not None:
                    #print("Paste ---> Data[" , i, "][", j, "] = ", self.Data[i][str(j)])
                    self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.content.Data_list[i][str(j)])))

                    if len(self.content.Data_list[i][str(j)]) > 1:
                        self.valid_Colnm += 1

            if  self.valid_Colnm >= 2:
                item = QtWidgets.QTableWidgetItem()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(self.content.bgImagePath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                item.setIcon(icon)
                self.content.tableWidget.setItem(i, 6, item)
                size = QSize(30,30)
                self.content.tableWidget.setIconSize(size)
        self.select_onerowdata = ['', '', '', '', '', '']
        self.Append_Keep_For_Undo.append(self.content.Data_list) # Keep data for undo
        #print(self.Keep_For_Undo)                                          
        print("Insert Text Completed")

    def CutText(self):
        self.Copy_Text = [self.select_onerowdata[0],self.select_onerowdata[1],self.select_onerowdata[2],self.select_onerowdata[3],self.select_onerowdata[4],self.select_onerowdata[5]]
        for j in range(6):
            self.content.tableWidget.setItem(self.select_row,j, QTableWidgetItem(str("")))
            self.content.Data_list[self.select_row][str(j)] = ''

        self.Append_Keep_For_Undo.append(self.content.Data_list) # Keep data for undo
        self.content.copyBtn.setEnabled(False)
        self.content.cutBtn.setEnabled(False)
        self.content.insertBtn.setEnabled(False)
        self.content.deleteBtn.setEnabled(False)
        self.content.pasteBtn.setEnabled(True)
        print("CutText Text Completed")

    def UndoText(self):
        if len(self.Append_Keep_For_Undo) > 0 and self.Check_undo == 0 :
            self.Check_undo += 1 
            self.undo = len(self.Append_Keep_For_Undo) - 2
        print(self.undo)
        if self.undo  >= 0 :    
            for i in range(len(self.content.Data_list)):
                for j in range(len(self.content.Data_list[i])): # Check จำนวน  data ที่อยู่ใน Row ล่าสุด = 4 (Dict)
                        if dict(self.content.Data_list[i]).get(str(j)) is not None:
                            self.content.tableWidget.setItem(i,j, QTableWidgetItem(str(self.Append_Keep_For_Undo[self.undo][i][str(j)])))

        self.undo = self.undo - 1
        print("Undo Text Text Completed")
    # ============================= Jom Add all function (End) ============================================================================================
