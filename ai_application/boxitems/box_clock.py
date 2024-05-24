from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal

from datetime import datetime
import sys

class CLOCK(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.setting_icon = self.Path + "/icons/icons_settings_icon.png"
        self.save_icon = self.Path + "/icons/icons_save.png"

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(230,205,20,20)
        self.SettingBtn.setIcon(QIcon(self.setting_icon))

        # creating a timer object
        timer = QTimer(self)
  
        # adding action to the timer
        # update the whole code
        timer.timeout.connect(self.update)
  
        # setting start time of timer i.e 1 second
        timer.start(1000)
  
        # setting window title
        self.setWindowTitle('Clock')
  
        # setting window geometry
        self.setGeometry(200, 200, 300, 300)
  
        # setting background color to the window
        self.setStyleSheet("background-color: rgba(1, 31, 101, 150);")
  
        # creating hour hand
        self.hPointer = QtGui.QPolygon([QPoint(6, 7),
                                        QPoint(-6, 7),
                                        QPoint(0, -50)])
  
        # creating minute hand
        self.mPointer = QPolygon([QPoint(6, 7),
                                  QPoint(-6, 7),
                                  QPoint(0, -70)])
  
        # creating second hand
        self.sPointer = QPolygon([QPoint(1, 1),
                                  QPoint(-1, 1),
                                  QPoint(0, -90)])
        # colors
        # color for minute and hour hand
        self.bColor = QColor("#D6ECEFFF") #Qt.green
  
        # color for second hand
        self.sColor = Qt.green

        self.tik = None
        self.clock_out = QtCore.QTimer(self)

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.clock_out)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        self.SwitchAlarm = QPushButton(self)
        self.SwitchAlarm.setGeometry(215,5,37,20)
        self.SwitchAlarm.setIcon(QIcon(self.off_icon))
        self.SwitchAlarm.setIconSize(QtCore.QSize(37,20))
        self.SwitchAlarm.setStyleSheet("background-color: transparent; border: 0px;")  

        self.SetAlarm_flag = False
        self.alarm_clock = ""

        self.OntimeFlag = False
        self.NOF_Row = 1

        self.ClockSchedule = []
        self.weekly_schedule = []

        self.submit_flag = False
        self.clock_submit_flag = []
        self.stop_onetime = []

        self.lcd = QLCDNumber(self, digitCount=8)
        self.lcd.setGeometry(88,18,80,20)
        self.lcd.setStyleSheet("""QLCDNumber { 
            font-size:10pt;
            color: lightblue; }""")
        
        self.lblWeekDay = QLabel("Sun 06/06/2023", self)
        self.lblWeekDay.setGeometry(QtCore.QRect(5, 200, 150, 35))
        self.lblWeekDay.setStyleSheet("font-size:8pt; color:lightblue;")

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        res['alarmflag'] = self.SetAlarm_flag
        res['ClockSchedule'] = self.ClockSchedule
        res['WeeklySchedule'] = self.weekly_schedule
        res['number_of_row'] = self.NOF_Row
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            if 'alarmflag' in data:
                self.SetAlarm_flag = data['alarmflag']
                if self.SetAlarm_flag:
                    self.SwitchAlarm.setIcon(QIcon(self.on_icon))
                else:
                    self.SwitchAlarm.setIcon(QIcon(self.off_icon))

            if 'ClockSchedule' in data:
                self.ClockSchedule = data['ClockSchedule']

            if 'WeeklySchedule' in data:
                self.weekly_schedule = data['WeeklySchedule']

            if 'number_of_row' in data:
                self.NOF_Row = data['number_of_row']
                for l in range(self.NOF_Row):
                    self.clock_submit_flag.append(False)
                    self.stop_onetime.append(False)

            return True & res
        except Exception as e:
            dumpException(e)
        return res
        

    # method for paint event
    def paintEvent(self, event):
  
        # getting minimum of width and height
        # so that clock remain square
        rec = min(self.width(), self.height())
  
        # getting current time
        self.tik = QTime.currentTime()
  
        # creating a painter object
        painter = QPainter(self)
  
  
        # method to draw the hands
        # argument : color rotation and which hand should be pointed
        def drawPointer(color, rotation, pointer):
  
            # setting brush
            painter.setBrush(QBrush(color))
  
            # saving painter
            painter.save()
  
            # rotating painter
            painter.rotate(rotation)
  
            # draw the polygon i.e hand
            painter.drawConvexPolygon(pointer)
  
            # restore the painter
            painter.restore()
  
  
        # tune up painter
        painter.setRenderHint(QPainter.Antialiasing)
  
        # translating the painter
        painter.translate(self.width() / 2, self.height() / 2)
  
        # scale the painter
        painter.scale(rec / 200, rec / 200)
  
        # set current pen as no pen
        painter.setPen(QtCore.Qt.NoPen)
  
        # draw each hand
        drawPointer(self.bColor, (30 * (self.tik.hour() + self.tik.minute() / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (self.tik.minute() + self.tik.second() / 60)), self.mPointer)
        drawPointer(self.sColor, (6 * self.tik.second()), self.sPointer)
  
        # drawing background
        painter.setPen(QPen(self.bColor))
  
        # for loop
        for i in range(0, 60):
  
            # drawing background lines
            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)
  
            # rotating the painter
            painter.rotate(6)
  
        # ending the painter
        painter.end()

class MultiCheckBoxWidget(QWidget):
    checkboxClicked = pyqtSignal(int, str, bool)

    def __init__(self, row, weekly_schedule, parent=None):
        super().__init__(parent)
        self.row = row
        self.weekly_schedule = weekly_schedule

        self.weekly = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        # print("MultiCheckBoxWidget --> self.weekly_schedule =", self.weekly_schedule)

        layout = QHBoxLayout()
        self.checkboxes = []
        for day in range(len(self.weekly)):
            checkbox = QCheckBox(self.weekly[day])
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            checkbox.stateChanged.connect(self.handle_checkbox_clicked)
        self.setLayout(layout)

        # print('self.weekly_schedule[0][0:1] :', str(self.weekly_schedule[0])[0:1])
        # print('self.weekly_schedule[0][2:5] :', str(self.weekly_schedule[0])[2:5])

        for i in range(len(self.weekly_schedule)):
            if row == int(str(self.weekly_schedule[i])[0:1]):
                self.checkboxes[self.weekly.index(str(self.weekly_schedule[i])[2:5])].setChecked(True)

    def handle_checkbox_clicked(self, state):
        sender = self.sender()
        checkbox_text = sender.text()
        checked = state == Qt.Checked
        self.checkboxClicked.emit(self.row, checkbox_text, checked)

class ClockSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        print('Class ClockSetting ---> ClockSetting Setting Function')

        self.content = content
        self.ClockSchedule = self.content.ClockSchedule
        self.weekly_schedule = self.content.weekly_schedule

        self.title = "Clock Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 1100
        self.height = 750
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.NOF_Row = self.content.NOF_Row
        print("self.NOF_Row = ", self.NOF_Row)

        self.lbl1 = QLabel("Clock Schedule: ", self)
        self.lbl1.setGeometry(QtCore.QRect(10, 5, 300, 30))
        self.lbl1.setStyleSheet("color: lightblue; font-size:10pt;")
        
        self.lbl2 = QLabel("Example : Start 10:30, Stop 22:30", self)
        self.lbl2.setGeometry(QtCore.QRect(10, 35, 300, 20))

        self.lblwarning = QLabel("", self)
        self.lblwarning.setGeometry(QtCore.QRect(310, 5, 600, 45))
        self.lblwarning.setStyleSheet("font-size:13pt; color:yellow;")
        self.lblwarning.setAlignment(Qt.AlignCenter)

        self.AddSchedule = QPushButton("Add Schedule", self)
        self.AddSchedule.setGeometry(880,15,135,30)
        # self.SubmitSchedule.setIcon(QIcon(self.content.save_icon))
        self.AddSchedule.clicked.connect(self.AddClock_Schedule)


        self.DelBtn = QPushButton("Delete", self)
        self.DelBtn.setGeometry(1030,15,50,30)
        self.DelBtn.clicked.connect(self.del_column)

        #====================================================
        # Create table
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(10,55,1070,680)
        #self.tableWidget.setStyleSheet("QTableWidget { background-color: rgba(0, 32, 130, 100); gridline-color: #fffff8; font-size: 10pt; }")
        self.tableWidget.setStyleSheet("background-color: rgba(0, 124, 212, 50);font-size:10pt;color: #178CEA; gridline-color: #fffff8;")
        
        self.tableWidget.setRowCount(self.NOF_Row)
        self.tableWidget.setColumnCount(3)

        font = QFont()
        font.setBold(True)
        self.tableWidget.setFont(font)

        # Set Fixed Collum Header Width
        header = self.tableWidget.horizontalHeader()       
        self.tableWidget.setColumnWidth(0 , 175)
        self.tableWidget.setColumnWidth(1 , 175)
        self.tableWidget.setColumnWidth(2 , 675)
        header.setStyleSheet("background-color: rgba(0, 32, 130, 200);")

        # Set Colume Alignment Center
        delegate = AlignDelegate(self.tableWidget)
        self.tableWidget.setItemDelegateForColumn(0, delegate)
        self.tableWidget.setItemDelegateForColumn(1, delegate)
        self.tableWidget.setItemDelegateForColumn(2, delegate)
        # self.tableWidget.setItemDelegateForColumn(3, delegate)

        self.tableWidget.setHorizontalHeaderLabels(['Start','Stop', 'Weekly'])

        self.weekly = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

        for row in range(self.NOF_Row):
            widget = MultiCheckBoxWidget(row, self.weekly_schedule)
            widget.checkboxClicked.connect(self.handle_checkbox_clicked)
            self.tableWidget.setCellWidget(row, 2, widget)

        self.exist_data = False
        if len(self.ClockSchedule) >= 2:
            print("load self.ClockSchedule :", self.ClockSchedule)
            # print(str(self.ClockSchedule[0])[0:3])
            # print(str(self.ClockSchedule[0])[4:5])

            for i in range(len(self.ClockSchedule)):
                if str(self.ClockSchedule[i])[0:3] == "row":

                    self.tableWidget.setItem(int(str(self.ClockSchedule[i])[4:5]),0, QTableWidgetItem(str(self.ClockSchedule[i + 1])))
                    self.tableWidget.setItem(int(str(self.ClockSchedule[i])[4:5]),1, QTableWidgetItem(str(self.ClockSchedule[i + 2])))

                    self.exist_data = True

    def handle_checkbox_clicked(self, row, checkbox_text, checked):
        if checked:
            result = f"{row}:{checkbox_text}" 
            self.weekly_schedule.append(result)

        else:
            print(f"{row}:{checkbox_text} is Uncheck" )
            self.weekly_schedule.pop(self.weekly_schedule.index(f"{row}:{checkbox_text}"))

    def AddClock_Schedule(self):
        # print("self.NOF_Row :", self.NOF_Row)
        print("Exiting self.ClockSchedule :", self.ClockSchedule)

        if self.NOF_Row == 1:
            if not self.exist_data:
                if type(self.tableWidget.item(0, 0)) != type(None) and type(self.tableWidget.item(0, 1)) != type(None):
                    self.ClockSchedule.append(f"row_0")
                    self.ClockSchedule.append(str(self.tableWidget.item(0, 0).text()))
                    self.ClockSchedule.append(str(self.tableWidget.item(0, 1).text()))

                    print("1st Row self.ClockSchedule :", self.ClockSchedule)
                    self.content.ClockSchedule = self.ClockSchedule

                    self.content.clock_submit_flag.append(False)
                    self.content.stop_onetime.append(False)
                
                    self.NOF_Row = 2
                    self.add_newrow(self.NOF_Row)
                    self.lblwarning.setText("")

                else:
                    # print("No Clock Data Add to Schedule !!!")
                    self.lblwarning.setText("No Start & Stop !!!")

            else:
                print("prepare new row!!!")
                self.NOF_Row += 1
                self.add_newrow(self.NOF_Row)
                self.exist_data = False
        else:
            if not self.exist_data:
                if type(self.tableWidget.item(self.NOF_Row - 1, 0)) != type(None) and type(self.tableWidget.item(self.NOF_Row - 1, 1)) != type(None):
                    self.ClockSchedule.append(f"row_{self.NOF_Row - 1}")
                    self.ClockSchedule.append(self.tableWidget.item(self.NOF_Row - 1, 0).text())
                    self.ClockSchedule.append(self.tableWidget.item(self.NOF_Row - 1, 1).text())

                    print("New self.ClockSchedule :", self.ClockSchedule)

                    self.content.clock_submit_flag.append(False)
                    self.content.stop_onetime.append(False)
                    
                    self.NOF_Row += 1
                    self.add_newrow(self.NOF_Row)
                    self.lblwarning.setText("")

                else:
                    self.lblwarning.setText("No Start & Stop !!!")
            else:
                print("prepare new row!!!")
                self.NOF_Row += 1
                self.add_newrow(self.NOF_Row)
                self.exist_data = False

    def add_newrow(self, rows):

        self.tableWidget.setRowCount(rows)
        self.tableWidget.setItem(rows,0, QTableWidgetItem(""))
        self.tableWidget.setItem(rows,1, QTableWidgetItem(""))

        for row in range(rows):
            widget = MultiCheckBoxWidget(row, self.weekly_schedule)
            widget.checkboxClicked.connect(self.handle_checkbox_clicked)
            self.tableWidget.setCellWidget(row, 2, widget)

    def del_column(self):
        self.NOF_Row -= 1
        if self.NOF_Row >= 0:
            self.tableWidget.setRowCount(self.NOF_Row)
        
            last_index = len(self.ClockSchedule)
            self.ClockSchedule.pop(last_index - 1)
            self.ClockSchedule.pop(last_index - 2)
            self.ClockSchedule.pop(last_index - 3)

            self.weekly_schedule = [item for item in self.weekly_schedule if not item.startswith(f'{self.NOF_Row}:')]

            self.content.clock_submit_flag.pop(last_index)
            self.content.stop_onetime.pop(last_index)

        else:
            self.NOF_Row = 0

    def closeEvent(self, event):
        self.content.SettingBtn.setEnabled(True)
        if len(self.ClockSchedule) < 2:
            self.content.weekly_schedule = []

        else:

            self.content.weekly_schedule = self.weekly_schedule
            
            actual_row = 0
            for i in range(len(self.ClockSchedule)):
                if str(self.ClockSchedule[i])[0:3] == "row":
                    if type(self.tableWidget.item(actual_row, 0)) != type(None) and type(self.tableWidget.item(actual_row, 1)) != type(None):
                        self.ClockSchedule[i + 1] = str(self.tableWidget.item(actual_row, 0).text())
                        self.ClockSchedule[i + 2] = str(self.tableWidget.item(actual_row, 1).text())

                    actual_row += 1

            print("Final self.ClockSchedule :", self.ClockSchedule)
            self.content.ClockSchedule = self.ClockSchedule
            self.content.NOF_Row = actual_row

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

# =========================================================================================================
@register_node(OP_NODE_CLOCK)
class Open_CLOCK(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_clock_icon.png"
    op_code = OP_NODE_CLOCK
    op_title = "Clock"
    content_label_objname = "Clock"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[4]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = CLOCK(self)                   # <----------- init UI with data and widget
        self.grNode = FlowAnalogClock(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.content.clock_out.timeout.connect(self.send_clkout)
        self.content.clock_out.setInterval(200)
        self.content.clock_out.start()

        self.content.SwitchAlarm.clicked.connect(self.SetAlarmClock)
        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)

    def evalImplementation(self):                       # <----------- Create Socket range Index
        ...

    def clock_period(self, time_str, start_str, end_str):
        time_obj = datetime.strptime(time_str, "%H:%M")
        start_obj = datetime.strptime(start_str, "%H:%M")
        end_obj = datetime.strptime(end_str, "%H:%M")

        if time_obj < start_obj:
            return "Before"
        elif time_obj == end_obj:
            return "End"
        elif time_obj > end_obj:
            return "Over"
        else:
            return "Within"

    def send_clkout(self):
        self.payload['clock'] = datetime.now().strftime("%H:%M:%S")
        self.payload['weekday'] = datetime.now().strftime('%a')
        # print(current_weekday)

        self.content.lcd.display(self.payload['clock'])
        self.content.lblWeekDay.setText(str(self.payload['weekday']) + " " + datetime.now().strftime('%d/%m/%Y'))

        if self.content.SetAlarm_flag:
            for i in range(len(self.content.ClockSchedule)):
                if str(self.content.ClockSchedule[i])[0:3] == "row":
                    # str(self.content.ClockSchedule[0])[4:5]

                    if self.clock_period(str(datetime.now().strftime("%H:%M")), str(self.content.ClockSchedule[i + 1]), str(self.content.ClockSchedule[i + 2])) == "Within":
                        for m in range(len(self.content.weekly_schedule)):
                            if str(self.content.weekly_schedule[m])[0:1] == str(self.content.ClockSchedule[i])[4:5] and datetime.now().strftime('%a') == str(self.content.weekly_schedule[m])[2:5]:
                                if not self.content.clock_submit_flag[int(str(self.content.ClockSchedule[i])[4:5])]:
                                    self.content.clock_submit_flag[int(str(self.content.ClockSchedule[i])[4:5])] = True    
                                    print("Tricker Start @ ", self.payload['clock'])
                                    self.payload['schedule_process'] = "Start"

                    if self.clock_period(str(datetime.now().strftime("%H:%M")), str(self.content.ClockSchedule[i + 1]), str(self.content.ClockSchedule[i + 2])) == "End":
                        for n in range(len(self.content.weekly_schedule)):
                            if str(self.content.weekly_schedule[n])[0:1] == str(self.content.ClockSchedule[i])[4:5] and datetime.now().strftime('%a') == str(self.content.weekly_schedule[n])[2:5]:
                                if self.content.clock_submit_flag[int(str(self.content.ClockSchedule[i])[4:5])] and not self.content.stop_onetime[int(str(self.content.ClockSchedule[i])[4:5])]:
                                    self.content.stop_onetime[int(str(self.content.ClockSchedule[i])[4:5])] = True
                                    print("Tricker Stop@ ", self.payload['clock'])
                                    self.payload['schedule_process'] = "Stop"

                    if self.clock_period(str(datetime.now().strftime("%H:%M")), str(self.content.ClockSchedule[i + 1]), str(self.content.ClockSchedule[i + 2])) == "Over":
                        self.content.stop_onetime[int(str(self.content.ClockSchedule[i])[4:5])] = False
                        self.content.clock_submit_flag[int(str(self.content.ClockSchedule[i])[4:5])] = False    

        self.value = self.payload
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(op_code=self.op_code)
        else:
            self.evalChildren()

            
    def SetAlarmClock(self):
        if len(self.content.ClockSchedule) > 2:
            
            if not self.content.SetAlarm_flag:
                self.content.SetAlarm_flag = True
                self.content.SwitchAlarm.setIcon(QIcon(self.content.on_icon))

                print(self.content.ClockSchedule)
                print(self.content.weekly_schedule)


            else:
                self.content.SetAlarm_flag = False
                self.content.SwitchAlarm.setIcon(QIcon(self.content.off_icon))

        else:
            self.content.SetAlarm_flag = False
            self.content.SwitchAlarm.setIcon(QIcon(self.content.off_icon))
            print("Still not set clock schedule!!!")

    def OnOpen_Setting(self):
        self.Clock_Setting = ClockSetting(self.content)
        self.Clock_Setting.show()

        self.content.SettingBtn.setEnabled(False)



