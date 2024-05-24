# Version 1.0; write external xxx.py file and Execute xxx.py
# Version 2.0; Remove write external xxx.py file and Execute internal code self
# Version 3.0; Sizeable IDE
# Version 4.0; Separate color text
# Version 4.1; Add Auto code Global
# Version 4.2; Add True / False condition
# Version 5.0; Add Image in Python Box
# Version 6.0; Add pip install pythonlibrary
# Version 6.1; Fix bug symbol <
# Version 6.2; Fix bug Enter with cursor
# Version 6.3; Add Auto code Link button
# Version 6.4; Add Lable Function Name and change
# Version 6.5; Fix bug add submit code and jump cursor
# Version 6.6; Scale Size IDE for close right screen
# Version 7.0; Add Mirror to VSCode
# Version 7.1; Add Message Execute Error
# Version 7.2; Add Function Name
# Version 7.3; Add Channel 1, 2 with using payload_ch1 and payload_ch2 and Add more keyword color
# Version 7.4; Add Tab, Back Tab and Ctrl+/
# Version 7.5; Add LOGO!8 How to connect
# Version 7.6; Add MySQL Command
# Version 7.7; Add Log Result
# Version 7.8; Add Best Image For OCR
# Version 7.9; Add Notify NG

from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 

import cv2
import os
import os.path

import traceback
from datetime import datetime
import numpy as np
import time
import pkg_resources
import shutil
import imutils
import time
import math

import sys
import re

from win32com import client
from win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow
from win32process import GetWindowThreadProcessId
from win32api import GetSystemMetrics

import pyautogui

class Python_IDE(QDMNodeContentWidget):
    def initUI(self):
        self.Path = os.path.dirname(os.path.abspath(__file__))
        browse_icon = self.Path + "/icons/icons_insert_text.png"
        animate_movie = self.Path + "/icons/icons_python_gif.gif"

        self.off_icon = self.Path + "/icons/icons_slide_off.png"
        self.on_icon = self.Path + "/icons/icons_slide_on.png"

        self.vscode_icon = self.Path + "/icons/icons_vscode.png"
            
        #====================================================
        # Loading the GIF
        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 35, 125, 75))
        self.label.setMinimumSize(QtCore.QSize(35, 35))
        self.label.setMaximumSize(QtCore.QSize(35, 35))

        self.movie = QMovie(animate_movie)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        #====================================================

        self.Run_cbox = QCheckBox("Run", self)
        self.Run_cbox.setGeometry(10,5,70,25)
        self.Run_cbox.setStyleSheet("color: #A1E43D; font-size:6pt;")

        self.Run_Python = QPushButton(self)
        self.Run_Python.setGeometry(105,5,37,20)
        self.Run_Python.setIcon(QIcon(self.off_icon))
        self.Run_Python.setIconSize(QtCore.QSize(37,20))
        self.Run_Python.setStyleSheet("background-color: transparent; border: 0px;")  

        self.processave_flag = False

        self.BrowsModel = QPushButton(self)
        self.BrowsModel.setGeometry(55,38,30,30)
        self.BrowsModel.setIcon(QIcon(browse_icon))

        self.lblP = QLabel("Payload" , self)
        self.lblP.setAlignment(Qt.AlignLeft)
        self.lblP.setGeometry(105,27,35,20)
        self.lblP.setStyleSheet("color: #FFDD00; font-size:5pt;")

        self.lblT = QLabel("CH1, True" , self)
        self.lblT.setAlignment(Qt.AlignLeft)
        self.lblT.setGeometry(95,43,50,20)
        self.lblT.setStyleSheet("color: #42E3C8; font-size:5pt;")

        self.lblF = QLabel("CH2, False" , self)
        self.lblF.setAlignment(Qt.AlignLeft)
        self.lblF.setGeometry(95,60,50,20)
        self.lblF.setStyleSheet("color: #FF9EAA; font-size:5pt;")

        self.lblExcEror = QLabel("Error !!!" , self)
        self.lblExcEror.setAlignment(Qt.AlignLeft)
        self.lblExcEror.setGeometry(55,5,60,20)
        self.lblExcEror.setStyleSheet("color: #FF0000; font-size:7pt;")
        self.lblExcEror.setVisible(False)

        self.editFuntionName = QLineEdit(self)
        self.editFuntionName.setGeometry(5,77,140,18)
        self.editFuntionName.setPlaceholderText("Function Name")
        self.editFuntionName.setAlignment(QtCore.Qt.AlignCenter)
        self.editFuntionName.setStyleSheet("background-color: rgba(34, 132, 217, 225); font-size:8pt;color:white; border: 1px solid white; border-radius: 3%;")

        self.lockflow = self.readFlowSetting('LockFlow')
        if self.lockflow == "true":
            self.Run_cbox.setEnabled(False)
            self.Run_Python.setEnabled(False)
            self.BrowsModel.setEnabled(False)

        self.AutoExecute_flag = False
        self.python_code = ""

        self.check_link_button = False
        self.keysubmit_flag = False
        self.submit_button_incode = False

        self.update_timer = QtCore.QTimer()
        self.TimerBlinkCnt = 0
        self.BlinkingState = False

        GlobaTimer = GlobalVariable()
        self.ListGlobalTimer = []

        if GlobaTimer.hasGlobal("GlobalTimerApplication"):
            self.ListGlobalTimer = list(GlobaTimer.getGlobal("GlobalTimerApplication"))

            self.ListGlobalTimer.append(self.update_timer)
            GlobaTimer.setGlobal("GlobalTimerApplication", self.ListGlobalTimer)

        self.No_CodeLine = 0

        # ==========================================================
        # For EvalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['python_execut'] = self.AutoExecute_flag
        res['python_code'] = self.python_code
        res['on_python'] = self.processave_flag
        res['no_codeline'] = self.No_CodeLine
        res['function_name'] = self.editFuntionName.text()
        res['submit_btn_code'] = self.submit_button_incode
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'python_execut' in data:
                self.AutoExecute_flag = data['python_execut']

                if self.AutoExecute_flag:
                    self.update_timer.start()
                    self.Run_cbox.setChecked(True)
                    
                else:
                    self.update_timer.stop()
                    self.Run_cbox.setChecked(False)

            if 'python_code' in data:
                self.python_code = data['python_code']
                
            if 'on_python' in data:
                self.processave_flag = data['on_python']

                if self.processave_flag:
                    self.movie.start()
                    self.Run_Python.setIcon(QIcon(self.on_icon))

                else:
                    self.movie.stop()
                    self.Run_Python.setIcon(QIcon(self.off_icon))

            if 'no_codeline' in data:
                self.No_CodeLine = data['no_codeline']

            if 'function_name' in data:
                self.editFuntionName.setText(data['function_name'])

            if 'submit_btn_code' in data:
                self.submit_button_incode = data['submit_btn_code']

            return True & res
        except Exception as e:
            dumpException(e)
        return res

    def readFlowSetting(self, key):
        settings = QSettings("Flow Setting")
        data = settings.value(key)
        return data

#=====================================================================================
# Text Editor
#=====================================================================================

class ActivateVenv:
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
        # shell.SendKeys("activate {ENTER}")

    def run_py_script(self,shell, venv_location, pip_command):
        """runs the py script"""

        required = {'virtualenv'}

        installed = {pkg.key for pkg in pkg_resources.working_set}
        print("installed : ", installed)

        missing = required - installed

        print()
        print("missing : ", missing)

        if missing:
            list_command = list(missing)
            print("list_command : ", list_command)
            print("len(list_command) : ", len(list_command))

            shell.SendKeys("pip install " + str(list_command[0]) + "{ENTER}")

        else:
            print("python library already installed")

        # shell.SendKeys("cd ../..{ENTER}")
        shell.SendKeys("python -m venv env {ENTER}")
        shell.SendKeys("env\Scripts\\activate {ENTER}")
        shell.SendKeys("%s {ENTER}" % pip_command)

        library_name = str(pip_command).split(" ")
        print("library_name[2] = ", library_name[2])

        library_folder = venv_location + "\env\Lib\site-packages"
        # shell.SendKeys("cd %s {ENTER}" %library_folder)

        library_folder_source = library_folder + "\\"+ library_name[2]
        print("Sorce Folder = ", library_folder_source)

        library_folder_end = venv_location + "\\"+ library_name[2]
        print("Destination = ", library_folder_end)
        
        # "xcopy", "source", "destination" /t /e
        copy_command = "xcopy \"" + library_folder_source + "\" \"" + library_folder_end + "\" /i"
        print("copy_command = ", copy_command)
        shell.SendKeys("%s {ENTER}" %copy_command)

        # exit
        shell.SendKeys("exit {ENTER}")

        if os.path.isdir(library_folder_source):
            ## Try to remove tree; if failed show an error using try...except on screen
            print("Remove : ", library_folder_source)
            try:
                shutil.rmtree(library_folder_source)
            except OSError as e:
                print ("Error: %s - %s." % (e.filename, e.strerror))

    def open_cmd(self, shell):
        """ opens cmd """

        shell.run("cmd.exe")
        time.sleep(1)

class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(int(self.editor.lineNumberAreaWidth()), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

# =================================================================================

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        # Vilolet Color
        self.list_special_word = ["import", "as", "assert", "break","continue", "del", "elif", "else","except", "finally", "for", "from",
                        "global", "if", "in", "lambda", "pass", "raise", "return", "try", "with", "yield"]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(228, 0, 241, 255))
        # keyword_format.setFontWeight(QFont.Bold)

        self.highlighting_rules = [(re.compile(r"\b%s\b" % keyword), keyword_format) for keyword in self.list_special_word]

        # Yellow Color 
        self.list_payload_word   = ["payload", "new_payload", "ifelse", "history_report", "url","fromkeys","payload_ch1", "payload_ch2",
                                    "print", "exec", "len", "image", "setForeground", "GetSystemMetrics", "append",
                                    "setText", "setChecked", "setEnabled", "setStyleSheet", "start", "stop", "width", "height", "text", "toPlainText",
                                    "setGlobal", "getGlobal", "hasGlobal", "removeGlobal", "log", "ord", "abs", "zeros", "frombuffer", "compile",
                                    "circle", "line", "rectangle", "putText", "ellipse","sorted", "format_exc", "format", "dumps", "loads", "value",
                                    "wr_logo8", "rd_logo8", "all", "any", "ascii", "bin", "callable", "chr", "delattr", "dir", "divmod", "eval",
                                    "getattr", "globals", "hasattr", "hash", "help", "hex", "id", "input", "isinstance", "issubclass", "iter", "locals",
                                    "max", "min", "next", "oct", "open", "pow", "repr", "round", "setattr", "sum", "vars", "remove", "write", "close",
                                    "clear", "copy", "count", "extend", "index", "insert", "pop", "reverse", "sort"]
        
        key_payload_format = QTextCharFormat()
        key_payload_format.setForeground(QColor(255, 252, 175, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_payload_format) for keyword in self.list_payload_word]
        
        # Light Green Color
        self.list_green_color    = ["Global", "GlobalVariable", "ai_application", "Database", "range", "type", "str", "float", "int", "datetime", "now", "strftime",
                                    "FONT_HERSHEY_DUPLEX", "cv2", "np", "fromstring", "reshape", "pandas", "pd","math", "tuple", "list", "dict", "bool","map", "DataFrame",
                                    "traceback", "json", "colorama", "bytearray", "bytes", "classmethod", "enumerate", "filter", "frozenset", "memoryview",
                                    "object", "property", "reversed", "set", "slice", "staticmethod", "super", "zip", "function",
                                    "ArithmeticError", "AssertionError", "AttributeError", "Exception", "EOFError", "FloatingPointError",
                                    "GeneratorExit", "ImportError", "IndentationError", "IndexError", "KeyError", "KeyboardInterrupt",
                                    "LookupError", "MemoryError", "NameError", "NotImplementedError", "OSError", "OverflowError",
                                    "ReferenceError", "RuntimeError", "StopIteration", "SyntaxError", "TabError", "SystemError",
                                    "SystemExit", "TypeError", "UnboundLocalError", "UnicodeError", "UnicodeEncodeError",
                                    "UnicodeDecodeError", "UnicodeTranslateError", "ValueError", "ZeroDivisionError" ]
              
        key_green_format = QTextCharFormat()
        key_green_format.setForeground(QColor(11, 255, 118, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_green_format) for keyword in self.list_green_color]

        # Light Blue Color
        self.list_blue_color     = ["None", "True", "False", "def", "class", "not", "is", "None:", "and", "or", "self", "lambda", "nonlocal"]
        key_blue_formate = QTextCharFormat()
        key_blue_formate.setForeground(QColor(74, 109, 229, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_blue_formate) for keyword in self.list_blue_color]

        # # White color
        # self.list_sign_color     = [str("=="), str("+="), str(">"), str("<"), str(">="), str("<="), str("!="), str(","), str("-="), str("+"), str("-"), str("*"), str("/"), str("%"), str("=")]   
        # key_white_color = QTextCharFormat()
        # key_white_color.setForeground(QColor(0, 0, 255, 255))
        # self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_white_color) for keyword in self.list_sign_color]

        # Red Color
        self.list_red_color      = ["while", "Test_Insert_Text"]
        key_red_color = QTextCharFormat()
        key_red_color.setForeground(QColor(255, 0, 0, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_red_color) for keyword in self.list_red_color]

        # Orange Color
        self.list_orange_color   = ["result", "msg", "mqtt_payload", "topic", "sql", "img", "submit", "inputtype", "key", "fps", 
                                    "yolo_boxes", "clock", "obj_found"]
        key_orange_color = QTextCharFormat()
        key_orange_color.setForeground(QColor(249, 124, 37, 255))
        self.highlighting_rules += [(re.compile(r"\b%s\b" % keyword), key_orange_color) for keyword in self.list_orange_color]

        # Add Comment Rule
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("green"))
        self.highlighting_rules.append((re.compile(r"#[^\n]*"), comment_format))

        #==========================================================================
        # multi_comment
        self.multi_comment_format  = QTextCharFormat()
        self.multi_comment_format .setForeground(QColor("orange"))
        # self.highlighting_rules.append((re.compile(r'"""[^\n]*'), self.multi_comment_format))
        self.highlighting_rules.append((re.compile(r'"""(.*?)"""', re.DOTALL), self.multi_comment_format))

        self.in_multi_comment = False
        #==========================================================================
        
    def highlightBlock(self, text):
        if not self.in_multi_comment:
            start_index = text.find('"""')
            if start_index >= 0:
                end_index = text.find('"""', start_index + 3)
                if end_index == -1:
                    self.setFormat(start_index, len(text) - start_index, self.multi_comment_format)
                    self.in_multi_comment = True
                else:
                    self.setFormat(start_index, end_index - start_index + 3, self.multi_comment_format)

            else:
                for pattern, format in self.highlighting_rules:
                    expression = re.compile(pattern)
                    for match in expression.finditer(text):
                        self.setFormat(match.start(), match.end() - match.start(), format)
        
        elif self.in_multi_comment:
            end_index = text.find('"""')
            if end_index >= 0:
                self.setFormat(0, end_index + 3, self.multi_comment_format)
                self.in_multi_comment = False
            else:
                self.setFormat(0, len(text), self.multi_comment_format)

    # ================================================================================
    # def highlightBlock(self, text):
    #     for pattern, format in self.highlighting_rules:
    #         expression = re.compile(pattern)
    #         for match in expression.finditer(text):
    #             self.setFormat(match.start(), match.end() - match.start(), format)

# ====================================================================================
# ====================================================================================
class Ui_PythonIDE_MainWindow(object):
    def setupUi(self, MainWindow):

        self.MainWindow = MainWindow

        self.title = "Python Code IDE Ver 7.9 !!!"
        self.top    = 50
        self.left   = int((GetSystemMetrics(0)/8))
        self.width  = int((GetSystemMetrics(0)/4)*3.5)
        self.height = int(GetSystemMetrics(1) - int(GetSystemMetrics(1))/10)
        self.MainWindow.setWindowTitle(self.title)
        self.MainWindow.setGeometry(self.left, self.top, self.width, self.height) 
        # self.MainWindow.setFixedWidth(self.width)
        # self.MainWindow.setFixedHeight(self.height)
        self.MainWindow.setStyleSheet("background-color: rgba(9, 54, 87, 100);")

        self.QPlainTextEdit = QtWidgets.QPlainTextEdit(self.MainWindow)
        self.QPlainTextEdit.setFont(QtGui.QFont("Consolas", 15))
        # self.QPlainTextEdit.setStyleSheet("QPlainTextEdit {background-color: #2B2B2B; color: #BFBFBF;}")

        font = self.QPlainTextEdit.font()
        fontMetrics = QtGui.QFontMetricsF(font)
        spaceWidth = fontMetrics.width(' ')
        self.QPlainTextEdit.setTabStopDistance(spaceWidth * 4)
        self.QPlainTextEdit.setTabStopWidth(50)

        #self.highlighter = PythonHighlighter(self.QPlainTextEdit.document())
        # self.QPlainTextEdit.setGeometry(0, 70, 970, 570) 

        self.payloadLabel = QtWidgets.QLabel(self.MainWindow)
        self.payloadLabel.setGeometry(10,5,500,60)
        self.payloadLabel.setAlignment(QtCore.Qt.AlignTop)
        self.payloadLabel.setWordWrap(True)

        self.FunctionNameLabel = QtWidgets.QLabel(self.MainWindow)
        self.FunctionNameLabel.setGeometry(510,5,180,60)
        self.FunctionNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.FunctionNameLabel.setWordWrap(True)
        self.FunctionNameLabel.setStyleSheet("background-color: rgba(9, 18, 71 , 200)  ;font-size:25px;color:lightgreen ")

        self.VSCode_Btn = QtWidgets.QPushButton(self.MainWindow)
        self.VSCode_Btn.setGeometry(720,5,150,60)

        self.ExecuteBtn = QtWidgets.QPushButton(self.MainWindow)
        self.ExecuteBtn.setGeometry(780,5,150,60)
        self.ExecuteBtn.setText("Execute")

        self.OutputLabel = QtWidgets.QLabel("Execute : ",self.MainWindow)
        self.OutputLabel.setGeometry(5,645,965,60)
        self.OutputLabel.setAlignment(QtCore.Qt.AlignTop)
        self.OutputLabel.setWordWrap(True)
        self.OutputLabel.setStyleSheet("background-color: gray;font-size:15px;color:#A1E43D")

        self.ErrorLabel = QtWidgets.QPlainTextEdit("Error :", self.MainWindow)
        self.ErrorLabel.setGeometry(5,710,965,200)
        # self.ErrorLabel.setAlignment(QtCore.Qt.AlignTop)
        # self.ErrorLabel.setWordWrap(True)
        self.ErrorLabel.setStyleSheet("background-color: gray;font-size:15px;color:orange")

        self.checkGlobal = QCheckBox("Global",self.MainWindow)
        self.checkGlobal.setGeometry(880,5,90,20)
        self.checkGlobal.setStyleSheet("color: yellow; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.checkIfEls = QCheckBox("If Else",self.MainWindow)
        self.checkIfEls.setGeometry(880,35,90,20)
        self.checkIfEls.setStyleSheet("color: lightgreen; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.checkLogo8 = QCheckBox("LOGO!8",self.MainWindow)
        self.checkLogo8.setGeometry(880,65,90,20)
        self.checkLogo8.setStyleSheet("color: lightblue; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.checkMySQL = QCheckBox("MySQL",self.MainWindow)
        self.checkMySQL.setGeometry(880,95,90,20)
        self.checkMySQL.setStyleSheet("color: pink; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.checkLogResult = QCheckBox("Log",self.MainWindow)
        self.checkLogResult.setGeometry(880,125,90,20)
        self.checkLogResult.setStyleSheet("color: lightblue; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.checkOCCR = QCheckBox("OCR",self.MainWindow)
        self.checkOCCR.setGeometry(880,160,90,20)
        self.checkOCCR.setStyleSheet("color: lightgreen; font-size:8pt; background-color : rgba(39, 50, 80 , 200);")

        self.Find_edit = QLineEdit("", self.MainWindow)
        self.Find_edit.setAlignment(Qt.AlignLeft)
        self.Find_edit.setGeometry(300,10,250,40)
        self.Find_edit.setPlaceholderText("Find                     (Ctrl+F)")

        self.CancelFindBtn = QtWidgets.QPushButton(self.MainWindow)
        self.CancelFindBtn.setGeometry(500,15,30,30)
        self.CancelFindBtn.setText("X")

        self.pipinstall_btn = QtWidgets.QPushButton(self.MainWindow)
        self.pipinstall_btn.setGeometry(880,550,60,20)
        self.pipinstall_btn.setText("Install")

        self.piplibrary_edit = QLineEdit("", self.MainWindow)
        self.piplibrary_edit.setAlignment(Qt.AlignLeft)
        self.piplibrary_edit.setGeometry(680,550,150,20)
        self.piplibrary_edit.setPlaceholderText("pip install pythonlibrary")

#=====================================================================================
# Python Editor Class
#=====================================================================================
class PythonIDEEditor(QWidget):
    resized = pyqtSignal()
    def __init__(self, content, payload:dict, grNode_addr, parent=None):
        super().__init__(parent=parent)

        self.content = content
        self.payload = payload

        self.check_codeLine = None
        self.FunctionName = self.content.editFuntionName.text()

        self.new_after_check = ''

        self.current_Number_codeLine = self.content.No_CodeLine
        self.current_cursor_Pos = 0

        self.keyPress_Event = False
        self.PreesKeyTab = False
        self.PressTab_cnt = 0

        self.PreesKeyEnter = False
        self.list_keysubmit_flag = self.content.keysubmit_flag

        self.spacial_word_flag = False
        self.spacebar_flag = False

        self.submit_incode = self.content.submit_button_incode
        self.vscode_icon = self.content.vscode_icon

        self.code = ""
        self.traceback_var = ""
        self.DictMember = ""

        self.grNode_addr = grNode_addr
        self.Global = GlobalVariable()

        self.Test_ExecuteError = False
        self.Python_tempfile = ""

        self.BlinkingState = False
        self.TimerBlinkCnt = 0
        self.start_mirror = False

        self.Path_Folder = "C:\AI_Temp"
        self.isExist = os.path.isdir(self.Path_Folder)

        self.Python_tempfile = self.Path_Folder + "/Python_tempfile_" + self.grNode_addr + ".py"

        if self.payload:
            # print("self.payload: ", self.payload)
            # print("type(self.payload) = ", type(self.payload))

            if type(self.payload) is dict:
                self.DictMember = "{ "
                for name,value in self.payload.items():
                    if name != 'img':
                        if name != 'error':   
                            if type(value) == str:
                                self.DictMember = self.DictMember + "\'" + name + "\': " + "\'" + str(value) + "\'" + ", "
                            else:
                                self.DictMember = self.DictMember + "\'" + name + "\': " + str(value) + ", "
                    
                    else:
                        # print("type(value) = ", type(value))  #<class 'numpy.ndarray'>
                        if type(value) != type(None):
                            self.DictMember = self.DictMember + "\'" + name + "\': " + str(bytes(value)) + ", "

                self.DictMember = self.DictMember[0:-2] + " }"
                #print("len(self.passpayload) > 2:")
                # print("PythonIDEEditor ---> self.DictMember = \n", self.DictMember)
                #print()

            elif type(self.payload) is list:

                self.DictMember = "{ 'list_data':" + str(self.payload)
                self.DictMember = self.DictMember + " }"

                # print("\033[93m {}\033[00m".format("payload type list : " + str(self.DictMember)))

        else:
            self.DictMember = "{" + "}"
            #print("else:")
            #print("PythonIDEEditor ---> self.DictMember = \n", self.DictMember)
            #print()

        # print("self.payload :", self.payload)
        # print("type(self.payload) :", type(self.payload))

        self.content.python_code = self.content.python_code.replace("    ", '\t')
        # print("self.content.python_code: ",self.content.python_code)

        self.Renew_width = 1020
        self.Renew_height = 1000

        self.ui = Ui_PythonIDE_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainWindow.installEventFilter(self)
        self.resized.connect(self.ReDrawGeometry)

        self.ui.QPlainTextEdit.installEventFilter(self)
        self.ui.QPlainTextEdit.setEnabled(True)
    
        self.ui.payloadLabel.setWordWrap(True)
        self.ui.payloadLabel.setText("payload : " + self.DictMember)

        self.ui.FunctionNameLabel.setText(self.FunctionName)

        self.lineNumberArea = QLineNumberArea(self)
        self.ui.QPlainTextEdit.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.ui.QPlainTextEdit.updateRequest.connect(self.updateLineNumberArea)
        self.ui.QPlainTextEdit.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.ui.QPlainTextEdit.setStyleSheet("background-color: rgba(19, 21, 91, 225);font-size:15pt;color:#42E3C8;")
        self.updateLineNumberAreaWidth(0)

        self.ui.VSCode_Btn.setIcon(QIcon(self.vscode_icon))
        self.ui.VSCode_Btn.setIconSize(QtCore.QSize(50,50))
        self.ui.VSCode_Btn.clicked.connect(self.OpenVSCodeProgram)

        self.ui.ExecuteBtn.clicked.connect(self.TestExecute)
        self.ui.checkGlobal.stateChanged.connect(self.AddGlobalLink)
        self.ui.checkIfEls.stateChanged.connect(self.AddIfElse)
        self.ui.checkLogo8.stateChanged.connect(self.AddLogo8)
        self.ui.checkMySQL.stateChanged.connect(self.AddMySQL)
        self.ui.checkLogResult.stateChanged.connect(self.AddLogResult)
        self.ui.checkOCCR.stateChanged.connect(self.AddOCRResult)
        self.ui.QPlainTextEdit.setPlainText(self.content.python_code)

        self.ui.pipinstall_btn.clicked.connect(self.pip_install_python)

        #=======================================================================
        # Find Wording
        self.ui.Find_edit.setStyleSheet("font-size:10pt;color:orange;")
        self.ui.Find_edit.textChanged.connect(self.ChangedKeyWord)
        self.ui.Find_edit.setVisible(False)
        
        self.ui.CancelFindBtn.clicked.connect(self.Close_FindWording)

        self.ui.CancelFindBtn.setVisible(False)

        self.keyword = "text"
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor("#FFFF00"))  # Yellow background
        self.highlight_format.setProperty(QTextCharFormat.FullWidthSelection, True)

        self.last_search_position = None
        #=======================================================================
        # Tab, Back Tab and Ctrl+/

        self.covered_text = ""
        #=======================================================================

        self.checkcode_timer = QtCore.QTimer()
        self.checkcode_timer.timeout.connect(self.checkcode_python)
        self.checkcode_timer.setInterval(500)
        self.checkcode_timer.start()

        self.debugcode_timer = QtCore.QTimer()
        self.debugcode_timer.timeout.connect(self.debugcode_python)
        self.debugcode_timer.setInterval(50)
        self.debugcode_timer.start()

        self.mirror_code_timer = QtCore.QTimer()
        self.mirror_code_timer.timeout.connect(self.mirrorcode_python)
        self.mirror_code_timer.setInterval(50)

        self.highlighter = PythonHighlighter(self.ui.QPlainTextEdit.document())

        # ===========================================
        # Add Auto Coding In Python Boxes
        if self.payload is not None:
            if 'submit' in self.payload and not self.content.check_link_button and not self.list_keysubmit_flag:
                if not self.submit_incode:
                    self.content.check_link_button = True

                    self.AddButtonCondition()

    #=================================================================================================================
    def ReDrawGeometry(self):
        #print("Re Draw Geometry")
        self.Renew_width = self.frameGeometry().width()
        self.Renew_height = self.frameGeometry().height()

        if self.Renew_width < 1000:
            self.Renew_width = 1000

        if self.Renew_height < 500:
            self.Renew_height = 500

        self.ui.VSCode_Btn.setGeometry(self.Renew_width - 275,5,60,60)

        #print("width = ", width , "; height = ", height)
        self.ui.ExecuteBtn.setGeometry(self.Renew_width - 200,5,90,60)
        self.ui.checkGlobal.setGeometry(self.Renew_width - 100,5,90,30)
        self.ui.checkIfEls.setGeometry(self.Renew_width - 100,35,90,30)
        self.ui.checkLogo8.setGeometry(self.Renew_width - 100,65,90,30)
        self.ui.checkMySQL.setGeometry(self.Renew_width - 100,95,90,30)
        self.ui.checkLogResult.setGeometry(self.Renew_width - 100,125,90,30)
        self.ui.checkOCCR.setGeometry(self.Renew_width - 100,160,90,30)

        self.ui.payloadLabel.setGeometry(10,5,self.Renew_width -300 ,60)
        self.ui.FunctionNameLabel.setGeometry(self.Renew_width - 515 ,10 ,220 ,50)
        self.ui.QPlainTextEdit.setGeometry(0, 70, self.Renew_width -10, self.Renew_height - 360) 

        self.ui.OutputLabel.setGeometry(5, self.Renew_height - 285, self.Renew_width -15,60)
        self.ui.ErrorLabel.setGeometry(5, self.Renew_height - 220, self.Renew_width -15, 170)

        self.ui.pipinstall_btn.setGeometry(self.Renew_width - 80, self.Renew_height - 85, 60 , 30)
        self.ui.piplibrary_edit.setGeometry(20, self.Renew_height - 85, self.Renew_width - 110 , 30)

        self.ui.Find_edit.setGeometry(self.Renew_width - 800 ,10 ,282 ,40)
        self.ui.CancelFindBtn.setGeometry(self.Renew_width - 550 ,15 ,30 ,30)

    #================================================
    def pip_install_python(self):
        
        # \ai_application\boxitems

        self.Folder_Path = self.content.Path[0:-24]
        print("PythonIDEEditor self.Path = ", self.Folder_Path)

        root_part = self.Folder_Path[0:2]

        shell = client.Dispatch("WScript.Shell")
        run_venv = ActivateVenv()
        run_venv.open_cmd(shell)
        # EnumWindows(run_venv.set_cmd_to_foreground, None)
        run_venv.activate_venv(shell, root_part, self.Folder_Path)
        run_venv.run_py_script(shell, self.Folder_Path, self.ui.piplibrary_edit.text())

        res = QMessageBox.warning(self, "Done For Install " + str(self.ui.piplibrary_edit.text()),
                "Reqire to Re-Open Application",
                QMessageBox.Ok
            )

        if res == QMessageBox.Ok:
            sys.exit(0)

    #================================================
    def OpenVSCodeProgram(self):
        if not self.start_mirror:
            self.ui.QPlainTextEdit.setEnabled(False)

            if not self.isExist :
                os.makedirs(self.Path_Folder)
            else:
                for f in os.listdir(self.Path_Folder):
                    if not f.endswith(".py"):
                        continue
                    # os.remove(os.path.join(self.Path_Folder, f))
                    file_path = os.path.join(self.Path_Folder, f)  # Construct the file path as a string
                    os.remove(file_path)  # Remove the file using the file path
            
            if not os.path.isfile(self.Python_tempfile):
                file = open(self.Python_tempfile, 'w')
                file.write(str(self.ui.QPlainTextEdit.toPlainText()))
                file.close()

            start_command= "code " + self.Python_tempfile
            os.system(start_command)
            self.mirror_code_timer.start()

            self.BlinkingState = True

        else:
            self.mirror_code_timer.stop()
            self.BlinkingState = False
            self.ui.VSCode_Btn.setIcon(QIcon(self.vscode_icon))
            self.ui.QPlainTextEdit.setEnabled(True)

        self.start_mirror = not self.start_mirror
        
        
    def mirrorcode_python(self):
        if os.path.isfile(self.Python_tempfile):
            read_file_name = open(self.Python_tempfile,'r') #, encoding="utf-8")
            self.temp_python_code = read_file_name.read()
            self.ui.QPlainTextEdit.setPlainText(self.temp_python_code )

        if self.TimerBlinkCnt >= 5:
            self.TimerBlinkCnt = 0
            if self.BlinkingState:
                self.payload['blink'] = True
                self.ui.VSCode_Btn.setIcon(QIcon(self.vscode_icon))
            else:
                self.payload['blink'] = False
                self.ui.VSCode_Btn.setIcon(QIcon())
            self.BlinkingState = not self.BlinkingState

        self.TimerBlinkCnt += 1

    #================================================
    def TestExecute(self):
        #Delete File STW_Master.txt
        self.ui.OutputLabel.setText("Execute : ")
        self.ui.ErrorLabel.setPlainText("Error : ")

        Test_Payload = {}
        expression = "payload = " + self.DictMember + "\n\n" + self.ui.QPlainTextEdit.toPlainText()
        print("Len Test expression = ", len(expression))

        try:
            exec(expression, None, Test_Payload)
            #print("Test_Payload = " , Test_Payload)
            self.content.python_code = self.ui.QPlainTextEdit.toPlainText()

            if os.path.isfile(self.Python_tempfile):
                file = open(self.Python_tempfile, 'w')
                file.write(str(self.content.python_code))
                file.close()

            self.Test_ExecuteError = False

            self.content.lblExcEror.setVisible(False)

        except:
            self.traceback_var = traceback.format_exc()
            self.ui.ErrorLabel.setStyleSheet("background-color: gray;font-size:15px;color:orange")
            self.ui.ErrorLabel.setPlainText("")
            self.ui.ErrorLabel.setPlainText("Error : " + self.traceback_var)
            self.Test_ExecuteError = True

            self.content.lblExcEror.setVisible(True)

        # if 'log' in Test_Payload:
        #     self.log = Test_Payload['log']
        #     self.ui.ErrorLabel.setStyleSheet("background-color: yellow;font-size:40px;color:blue")
        #     self.ui.ErrorLabel.setPlainText("")
        #     self.ui.ErrorLabel.setPlainText("log : " + self.log)

        self.ui.OutputLabel.setText("Execute : \n" + str(Test_Payload))

    def AddGlobalLink(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            self.ui.QPlainTextEdit.insertPlainText('from ai_application.Database.GlobalVariable import * \nGlobal = GlobalVariable()\n\n# Example\n# Global.setGlobal("key","value")\n# value = Global.getGlobal("key")\n# Global.hasGlobal("key")\n# Global.removeGlobal("key")\n\n# Global.setGlobal("notify_ng", True)\n\n')
            
            try:
                cursor.setPosition(9)
            except:
                ...

        else:
            try:
                for i in range(9):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)

    def AddIfElse(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            self.ui.QPlainTextEdit.insertPlainText('ifelse = False\n# Defualt set new_payload to ==> False Channel\n# ifelse = True is set new_payload to ==> True Channel\n# Can change key new_payload = { "key":"value" }\n\n# Also able to using \n# payload_ch1 = { "key":"value" }\n# And \n# payload_ch2 = { "key":"value" }\n\nif "img" in payload:\n\timage = np.fromstring(payload["img"], np.uint8)\n\timage = image.reshape(payload["img_h"],payload["img_w"], 3)\n\t#===============================\n\t#Put_Your_Code_Here\n\n\timage = cv2.putText( image , "Test_Insert_Text" , ( 60, 450 ), cv2.FONT_HERSHEY_DUPLEX, 2, ( 0, 0, 255 ), 2)\n\n\n\t#===============================\n\tnew_payload = { "result" : datetime.now().strftime("%H:%M:%S") , "img" : image , "inputtype" : "img", "fps" : payload["fps"]}\n\nelse:\n\tnew_payload = { "result" : datetime.now().strftime("%H:%M:%S") }\n\n')

            try:
                cursor.setPosition(24)
            except:
                ...

        else:
            try:
                for i in range(24):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)

    def AddLogo8(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            self.ui.QPlainTextEdit.insertPlainText('# Write and Read LOGO!8\n# Write\n# payload_ch1 = { "wr_logo8": [ 0, True ] } # ==> [ bit : bool ] Write 1 bit = 0 to 3\n# payload_ch1 = { "wr_logo8": [ True, True, True, True ] } # ==> Write 4 Bit\n\n# Read\n# payload_ch1 = { "rd_logo8": 1 } # ==> 1 is read loop\n\n')

            try:    
                cursor.setPosition(7)
            except:
                ...

        else:
            try:
                for i in range(7):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)

    def AddMySQL(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            # sql = "INSERT INTO aiflow_editor_test (data,value) VALUES (%s,%s)"
            # val = 'ai','innovation'

            # payload_ch1 = { "sql":sql, "val":val}
            text_guide = '# Python MySQL\
                            \n# INSERT\n\
                            \n# sql = "INSERT INTO aiflow_editor_test (data,value) VALUES (%s,%s)"\
                            \n# val = "ai","innovation"\
                            \n# payload_ch1 = { "sql":sql, "val":val, "Duplicate": "FALSE", "Duplicate_key": "data", "Duplicate_value": "ai"}\
                            \n\n# UPDATE\
                            \n# "UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition"\n\
                            \n# sql = "UPDATE aiflow_editor_test SET value = \'Road 111\' WHERE data = \'Anna\'"\
                            \n# payload_ch1 = { "sql":sql}\
                            \n\n# SELECT\
                            \n# "SELECT * FROM tablename"\
                            \n# "SELECT name, address FROM tablename"\
                            \n# "SELECT col1, col2,…colnN FROM tablename WHERE id = 10";\n\
                            \n# sql = "SELECT  * FROM aiflow_editor_test WHERE id = 1"\
                            \n# payload_ch1 = { "sql":sql}\
                            \n\n# DELETE\
		                    \n# sql = "DELETE FROM aiflow_editor_test WHERE data = \'Anna\'"\
		                    \n# payload_ch1 = { "sql":sql}\
                            \n\n'
                
            self.ui.QPlainTextEdit.insertPlainText(text_guide)

            try:    
                cursor.setPosition(7)
            except:
                ...

        else:
            try:
                for i in range(7):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)

    def AddLogResult(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            # sql = "INSERT INTO aiflow_editor_test (data,value) VALUES (%s,%s)"
            # val = 'ai','innovation'

            # payload_ch1 = { "sql":sql, "val":val}
            text_guide = '# Python Log Result\
                            \n# payload_ch2 = { "logtitlename" : "Process Log" , "log" : log}\n\
                            \n\n'
                
            self.ui.QPlainTextEdit.insertPlainText(text_guide)

            try:    
                cursor.setPosition(7)
            except:
                ...

        else:
            try:
                for i in range(7):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)

    def AddOCRResult(self, state):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())
        if state == QtCore.Qt.Checked:
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)

            # insert text at the cursor
            # sql = "INSERT INTO aiflow_editor_test (data,value) VALUES (%s,%s)"
            # val = 'ai','innovation'

            # payload_ch1 = { "sql":sql, "val":val}
            text_guide = '# Python Select Best Image\
                            \nfrom ai_application.Database.GlobalVariable import * \
                            \nGlobal = GlobalVariable()\
                            \n\nif "img" in payload:\
                            \n\timage = np.fromstring(payload["img"], np.uint8)\
                            \n\timage = image.reshape(480,640, 3)\
                            \n\tif Global.hasGlobal("start_process"):\
                            \n\t\tif Global.getGlobal("start_process"):\
                            \n\t\t\tpayload_ch1 = { "img" : image , "inputtype" : "img" , "crop_output" : True }\n\
                            \n\t\telse:\
                            \n\t\t\tblack_image = np.zeros((480, 640, 3), dtype=np.uint8)\
                            \n\t\t\tpayload_ch1 = { "img" : black_image , "inputtype" : "img" , "crop_output" : False }\n\
                            \n\n'
                
            self.ui.QPlainTextEdit.insertPlainText(text_guide)

            try:    
                cursor.setPosition(7)
            except:
                ...

        else:
            try:
                for i in range(7):
                    cursor.setPosition(i)
                    cursor.select(i)
                    cursor.removeSelectedText()
            except:
                ...

            cursor.setPosition(0)


    def AddButtonCondition(self):
        # set the cursor position to 0
        cursor = QTextCursor(self.ui.QPlainTextEdit.document())

        # set the cursor position (defaults to 0 so this is redundant)
        cursor.setPosition(0)
        self.ui.QPlainTextEdit.setTextCursor(cursor)

        # insert text at the cursor
        self.ui.QPlainTextEdit.insertPlainText('if "submit" in payload: \n\tif payload["submit"]: \n\t\tresult = True \n\n\telse:\n\t\tresult = False \n\n')

        try:    
            cursor.setPosition(9)
        except:
            ...

        self.submit_incode = True

    # =======================================================================================================
    #========================================================================================================
    #Close Python IDE UI ---> Save All Python IDE
    def closeEvent(self, event):
        print("Python IDE is closed !!!")

        self.content.python_code = self.ui.QPlainTextEdit.toPlainText()

        self.content.Run_cbox.setText("Run")
        self.content.Run_cbox.setStyleSheet("color: #A1E43D")

        self.content.Run_cbox.setEnabled(True)
        self.content.Run_Python.setEnabled(True)
        self.content.BrowsModel.setEnabled(True)

        self.content.No_CodeLine = self.current_Number_codeLine
        self.content.keysubmit_flag = self.list_keysubmit_flag
        self.content.submit_button_incode = self.submit_incode

        self.Global.removeGlobal('pythonIDELog' + self.grNode_addr)

        if os.path.isfile(self.Python_tempfile):
            os.remove(self.Python_tempfile)

        self.mirror_code_timer.stop()
        self.BlinkingState = False
        self.start_mirror = False

        self.ui.QPlainTextEdit.setEnabled(True)

        # Auto Save When Close IDE
        pyautogui.hotkey('ctrl', 's')

        self.checkcode_timer.stop()
        self.debugcode_timer.stop()
        self.content.movie.start()

    #==============================================================
    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.ui.QPlainTextEdit.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1

        space = 10 + self.fontMetrics().width(str(digits)) * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.ui.QPlainTextEdit.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.ui.QPlainTextEdit.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        #self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
        self.lineNumberArea.setGeometry(QRect(cr.left(),70, self.lineNumberAreaWidth(), self.Renew_height - 360))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.ui.QPlainTextEdit.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(0, 100, 94, 150).lighter(0)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.ui.QPlainTextEdit.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

            if self.keyPress_Event:
                self.current_cursor_Pos = selection.cursor.position()
                # print("self.current_cursor_Pos = ", selection.cursor.position())
                self.keyPress_Event = False

        self.ui.QPlainTextEdit.setExtraSelections(extraSelections)
        # print("cursor_Pos = ", self.current_cursor_Pos)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.ui.QPlainTextEdit.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.ui.QPlainTextEdit.blockBoundingGeometry(block).translated(self.ui.QPlainTextEdit.contentOffset()).top()
        bottom = top + self.ui.QPlainTextEdit.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, int(top) + 8, int(self.lineNumberArea.width()), int(height), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.ui.QPlainTextEdit.blockBoundingRect(block).height()
            blockNumber += 1
            self.current_Number_codeLine = blockNumber - 1

    # =============================================================================
    # Find Keyword
    # =============================================================================
    def find_and_highlight(self, keyword):
        self.keyword = keyword

        self.clear_extra_selections()
        if keyword:
            cursor = self.document().find(keyword)

            while not cursor.isNull():
                selection = QTextEdit.ExtraSelection()
                selection.format = self.highlight_format
                selection.cursor = cursor
                self.setExtraSelections(self.extraSelections() + [selection])

                cursor = self.document().find(keyword, cursor)

            self.last_search_position = self.ui.QPlainTextEdit.textCursor()

    def move_cursor_to_next_find(self, cursor):
        if self.keyword:
            next_cursor = self.ui.QPlainTextEdit.document().find(self.keyword, cursor)
            if not next_cursor.isNull():
                #print("move_cursor_to_next_find --> next_cursor = ", next_cursor)
                self.ui.QPlainTextEdit.setTextCursor(next_cursor)
            else:
                # Loop back to the first find occurrence
                self.ui.QPlainTextEdit.setTextCursor(QTextCursor())
                self.last_search_position = None

                self.updateLineNumberAreaWidth(0)

    def Close_FindWording(self):
        self.ui.Find_edit.setVisible(False)
        self.ui.CancelFindBtn.setVisible(False)

        self.ui.Find_edit.clear()
        self.updateLineNumberAreaWidth(0)

    def ChangedKeyWord(self):
        self.keyword = self.ui.Find_edit.text()

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Slash:
            # print("Ctrl+/ pressed!")
            self.toggle_comment_selected_text()

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            #print("Ctrl+F pressed!")
            self.ui.Find_edit.setVisible(True)
            self.ui.CancelFindBtn.setVisible(True)
            
            # set the cursor position (defaults to 0 so this is redundant)
            cursor = QTextCursor(self.ui.QPlainTextEdit.document())
            cursor.setPosition(0)
            self.ui.QPlainTextEdit.setTextCursor(cursor)
            self.ui.Find_edit.setFocus(True)

        # Press Enter
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.ui.Find_edit.setText(self.keyword)
            self.ui.Find_edit.setFocus(False)
            
            if len(str(self.ui.Find_edit.text())) > 0:
                cursor = self.ui.QPlainTextEdit.textCursor()
                self.move_cursor_to_next_find(cursor)
                #print("Press Enter and find Next Keyword = ", cursor)
        else:
            super().keyPressEvent(event)


    def eventFilter(self, obj, event):
        if obj is self.ui.QPlainTextEdit and event.type() == QtCore.QEvent.KeyPress:
            # self.highlighter.rehighlight()

            if event.key() == Qt.Key_Backtab:
                # print("Back Tab/ pressed!")
                self.shift_left_selected_text()

            elif event.key() == Qt.Key_Tab:
                # print("Tab/ pressed!")
                cursor = self.ui.QPlainTextEdit.textCursor()
                # print("cursor :", cursor)
                if cursor.hasSelection():
                    self.indent_selected_text()
                else:
                    super().keyPressEvent(event)  # Allow normal Tab key
        else:
            if (event.type() == QtCore.QEvent.Resize):
                self.resized.emit()

        return super().eventFilter(obj, event)
    

    # =========================================================================================
    # =========================================================================================
    # Tab, Back Tab and Ctrl+/

    # def keyPressEvent(self, event):
    #     if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Slash:
    #         self.toggle_comment_selected_text()
    #     elif event.key() == Qt.Key_Backtab:
    #         self.shift_left_selected_text()
    #     elif event.key() == Qt.Key_Tab:
    #         cursor = self.textCursor()
    #         if cursor.hasSelection():
    #             self.indent_selected_text()
    #         else:
    #             super().keyPressEvent(event)  # Allow normal Tab key
    #     else:
    #         super().keyPressEvent(event)

    def indent_selected_text(self):
        cursor = self.ui.QPlainTextEdit.textCursor()
        if not cursor.hasSelection():
            # print("not cursor.hasSelection()")
            return

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        print("start:", start, ", end:", end)

        # Store the covered text
        self.covered_text = self.ui.QPlainTextEdit.toPlainText()[start:end]
        # print("self.covered_text :", self.covered_text)

        # Tab each line of selected text
        lines = self.covered_text.splitlines()
        # print("lines:", lines)
        tabbed_text = "\n".join(["\t" + line for line in lines])
        print("tabbed_text:", tabbed_text)

        # Replace the selected text with the tabbed text
        cursor.beginEditBlock()
        #cursor.removeSelectedText()
        cursor.insertText(tabbed_text)
        cursor.endEditBlock()

        # Reset the cursor to maintain the covered text
        #cursor.setPosition(start)
        #cursor.setPosition(end, QTextCursor.KeepAnchor)
        #cursor.beginEditBlock()
        # self.ui.QPlainTextEdit.setTextCursor(cursor)

        # Loop back to the first find occurrence
        # self.ui.QPlainTextEdit.setTextCursor(QTextCursor())

    def shift_left_selected_text(self):
        cursor = self.ui.QPlainTextEdit.textCursor()
        if not cursor.hasSelection():
            return

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        # Store the covered text
        self.covered_text = self.ui.QPlainTextEdit.toPlainText()[start:end]

        # Split the text into lines
        lines = self.covered_text.splitlines()

        # Find the minimum indentation level
        min_indent = float('inf')
        for line in lines:
            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                min_indent = indent

        # Shift each line of selected text back to the left side
        shifted_text = "\n".join([line[min_indent:] for line in lines])

        # Replace the selected text with the shifted text
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(shifted_text)
        cursor.endEditBlock()

        # Reset the cursor to maintain the covered text
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.ui.QPlainTextEdit.setTextCursor(cursor)

    def toggle_comment_selected_text(self):
        cursor = self.ui.QPlainTextEdit.textCursor()
        if not cursor.hasSelection():
            return

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        # Store the covered text
        self.covered_text = self.ui.QPlainTextEdit.toPlainText()[start:end]

        # Check if any line in the selected text has "#" at the beginning
        has_commented_lines = any(line.startswith("#") for line in self.covered_text.splitlines())

        # Toggle comments based on the presence of "#" at the beginning of lines
        modified_lines = []
        for line in self.covered_text.splitlines():
            if has_commented_lines:
                modified_lines.append(line.lstrip("#"))
            else:
                modified_lines.append("#" + line)

        # Replace the selected text with the modified text
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText("\n".join(modified_lines))
        cursor.endEditBlock()

        # Reset the cursor to maintain the covered text
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.ui.QPlainTextEdit.setTextCursor(cursor)
    
    #==========================================================================================
    #==========================================================================================

    def checkcode_python(self):
        list_keysubmit = "submit"

        self.check_codeLine = self.ui.QPlainTextEdit.toPlainText()
        if list_keysubmit in self.check_codeLine:
            self.list_keysubmit_flag = True
            self.checkcode_timer.stop()

            print("Found Submit in QPlainTextEdit")
            self.submit_incode = True

        else:
            self.list_keysubmit_flag = False
            self.content.check_link_button = False
            self.submit_incode = False

    def debugcode_python(self):
        if self.Global.hasGlobal('pythonIDELog' + self.grNode_addr) and not self.Test_ExecuteError:
            self.log = self.Global.getGlobal('pythonIDELog' + self.grNode_addr)
            self.ui.ErrorLabel.setStyleSheet("background-color: yellow;font-size:40px;color:blue")
            self.ui.ErrorLabel.setPlainText("")
            self.ui.ErrorLabel.setPlainText("Console log : " + str(self.log))

        if self.Global.hasGlobal("PythonIDEUpdatePayload" + self.grNode_addr):
            self.payload = self.Global.getGlobal("PythonIDEUpdatePayload" + self.grNode_addr)
            self.ui.payloadLabel.setText("payload : " + str(self.payload))

#====================================================================================
# Main Box Function
#====================================================================================
@register_node(OP_NODE_PYTHON_IDE)
class Open_Python_Function(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_python_icon_48.png"
    op_code = OP_NODE_PYTHON_IDE
    op_title = "Python V3"
    content_label_objname = "Python V3"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[3,1,4])
        self.payload = {}

        self.data_payload = self.payload

        self.next_payload = {}

        self.IDE_Widget = None
        self.round_open = 0

        self.execute_running = 0
        self.DictPayloadMember = ""

        self.cnt = 0

        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def initInnerClasses(self):
        self.content = Python_IDE(self)
        self.grNode = FlowGraphicsFaceProcess(self)  # <----------- Box Image Draw in Flow_Node_Base

        #=============================================================
        # Resizeable
        self.grNode_addr = str(self.grNode)[-13:-1]
        print("Python IDE ---> grNode_addr = ", self.grNode_addr)
        print("op_code =", self.op_code)

        self.content.BrowsModel.clicked.connect(self.BrowsEdittext)
        self.content.Run_cbox.stateChanged.connect(self.AutoExecute)
        self.content.Run_Python.clicked.connect(self.onAutoExecute)

        self.content.update_timer.timeout.connect(self.autorun_python)
        self.content.update_timer.setInterval(100)

        self.Global = GlobalVariable()

    def evalImplementation(self):

        # Input CH1
        #===================================================
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

        else:
            self.payload = input_node.eval()

            if self.payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()
                #self.content.Debug_timer.stop()
                # return

            elif self.payload is not None:
                #print("val Len = ", len(str(self.payload['img'])))

                if self.content.processave_flag:
                    self.data_payload = self.payload

                    self.Global.setGlobal("PythonIDEUpdatePayload" + self.grNode_addr, self.data_payload)
                    self.Execute_python()

                # End Input
                #==========================================================================
                self.sendFixOutputByIndex(self.next_payload, 0)

            # self.value = self.next_payload

            # self.markDirty(False)
            # self.markInvalid(False)

            # self.markDescendantsInvalid(False)
            # self.markDescendantsDirty()

            # #self.grNode.setToolTip("")
            # self.evalChildren()


    def Execute_python(self):

        if (len(self.content.python_code)) > 0:
            if len(self.data_payload) > 0:

                # print("self.payload: ", self.data_payload)
                # print("type(self.payload) = ", type(self.data_payload))

                if type(self.data_payload) is dict:
                    # print("self.payload is dict")

                    self.DictPayloadMember = "{ "
                    for name,value in self.data_payload.items():
                        if name != 'img':
                            if name != 'error':   
                                if type(value) == str:
                                    self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + "\'" + str(value) + "\'" + ", "
                                else:
                                    self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + str(value) + ", "

                        else:
                            # print("type(value) = ", type(value))  #<class 'numpy.ndarray'>
                            if type(value) != type(None):
                                self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + str(bytes(value)) + ", "

                    self.DictPayloadMember = self.DictPayloadMember[0:-2] + " }"

                elif type(self.data_payload) is list:

                    self.DictPayloadMember = "{ 'list_data':" + str(self.data_payload)
                    self.DictPayloadMember = self.DictPayloadMember + " }"

                    # print("\033[93m {}\033[00m".format("payload type list : " + str(self.DictPayloadMember)))
            else:
                self.DictPayloadMember = "{" + "}"

            # print("Execute_python ---> self.DictPayloadMember = ", self.DictPayloadMember)

            Execute_Payload = {}
            expression = "payload = " + self.DictPayloadMember + "\n\n" + self.content.python_code
            # print("Len Execute_python expression = ", len(expression))

        # ==========================================================================================
        # ORG Code
        # if (len(self.content.python_code)) > 0:
        #     if len(self.data_payload) > 0:
        #         self.DictPayloadMember = "{ "
        #         for name,value in self.data_payload.items():
        #             if name != 'img':
        #                 if name != 'error':   
        #                     if type(value) == str:
        #                         self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + "\'" + str(value) + "\'" + ", "
        #                     else:
        #                         self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + str(value) + ", "

        #             else:
        #                 # print("type(value) = ", type(value))  #<class 'numpy.ndarray'>
        #                 self.DictPayloadMember = self.DictPayloadMember + "\'" + name + "\': " + str(bytes(value)) + ", "

        #         self.DictPayloadMember = self.DictPayloadMember[0:-2] + " }"
        #     else:
        #         self.DictPayloadMember = "{" + "}"

        #     #print("Execute_python ---> self.DictPayloadMember = ", self.DictPayloadMember)

        #     Execute_Payload = {}
        #     expression = "payload = " + self.DictPayloadMember + "\n\n" + self.content.python_code
        #     #print("Execute_python expression = ", expression)

            # ==========================================================================================
            # ORG Code

            try:
                exec(expression, None, Execute_Payload)
                # print("Execute_python = " , Execute_Payload)
            except:
                error = traceback.format_exc()
                self.content.TimerBlinkCnt += 1
                if self.content.TimerBlinkCnt >= 5:
                    self.content.TimerBlinkCnt = 0
                    if self.content.BlinkingState:
                        print("\033[91m {}\033[00m".format('Error from Python Box : [ ' + self.content.editFuntionName.text() + ' ]:'))
                        print("\033[93m {}\033[00m".format('Message Error :'+ error))
                        self.content.lblExcEror.setVisible(False)

                    else:
                        self.content.lblExcEror.setVisible(True)
                self.content.BlinkingState = not self.content.BlinkingState

            self.content.TimerBlinkCnt += 1

            # print("Execute_Payload['result'] :", Execute_Payload['result'])
            if 'result' in Execute_Payload:
                self.next_payload['result'] = Execute_Payload['result']

            if 'ifelse' in Execute_Payload:
                ifelse_state = Execute_Payload['ifelse']
                # print("ifelse_state = ", ifelse_state)

                if 'new_payload' in Execute_Payload:
                    Execute_Output = Execute_Payload['new_payload']
                    # print("Execute_Output = ", Execute_Output)
                    if ifelse_state:
                        self.sendFixOutputByIndex(Execute_Output, 1)
                    else:
                        self.sendFixOutputByIndex(Execute_Output, 2)

            if 'payload_ch1' in Execute_Payload:
                Execute_Output_ch1 = Execute_Payload['payload_ch1']
                self.sendFixOutputByIndex(Execute_Output_ch1, 1)
                        
            if 'payload_ch2' in Execute_Payload:
                Execute_Output_ch2 = Execute_Payload['payload_ch2']
                self.sendFixOutputByIndex(Execute_Output_ch2, 2)

            if 'mqtt_payload' in Execute_Payload:
                self.next_payload['mqtt_payload'] = Execute_Payload['mqtt_payload']

            if 'topic' in Execute_Payload:
                self.next_payload['topic'] = Execute_Payload['topic']

            if 'sql' in Execute_Payload:
                self.next_payload['sql'] = Execute_Payload['sql']

            if 'msg' in Execute_Payload:
                self.next_payload['msg'] = Execute_Payload['msg']

            if 'history_report' in Execute_Payload:
                self.next_payload['history_report'] = Execute_Payload['history_report']

            """if 'result' not in Execute_Payload and 'mqtt_payload' not in Execute_Payload and 'topic' not in Execute_Payload:
                self.next_payload = Execute_Payload"""
            
            if 'log' in Execute_Payload:
                self.Global.setGlobal('pythonIDELog' + self.grNode_addr, Execute_Payload['log'])

            if self.execute_running > 5:
                self.execute_running = 0
                #self.content.lbl.setText("<font color=#0000FF>Execute</font>")
                self.content.Run_cbox.setText("R")
            else:
                #self.content.lbl.setText("")
                self.content.Run_cbox.setText("")

            self.execute_running += 1

        else:
            # self.content.lbl.setText("<font color=#FF0000>No Code!</font>")
            self.content.Run_cbox.setText("NC!")
            self.content.update_timer.stop()

    def AutoExecute(self, state):
        if state == QtCore.Qt.Checked:
            if len(self.content.python_code) > 0:
                self.content.AutoExecute_flag = True
                self.content.update_timer.start()
        else:
            #self.content.lbl.setText("<font color=#FFFFFF>Not Run</font>")
            self.content.Run_cbox.setText(" ")
            self.content.AutoExecute_flag = False
            self.content.update_timer.stop()

    def onAutoExecute(self):
        if not self.content.processave_flag:
            self.content.movie.start()
            self.content.Run_Python.setIcon(QIcon(self.content.on_icon))
            self.content.processave_flag = True

        else:
            self.content.movie.stop()
            self.content.Run_Python.setIcon(QIcon(self.content.off_icon))
            self.content.processave_flag = False

            self.content.update_timer.stop()


    def BrowsEdittext(self):
        #global temp_variable

        self.content.Run_cbox.setText("Edit")
        self.content.Run_cbox.setStyleSheet("color: red")

        self.content.AutoExecute_flag = False
        self.content.update_timer.stop()

        self.content.movie.stop()

        self.content.Run_cbox.setChecked(False)
        self.content.Run_cbox.setEnabled(False)
        self.content.Run_Python.setEnabled(False)
        self.content.BrowsModel.setEnabled(False)

        self.PythonIDEEditor = PythonIDEEditor(self.content, self.payload, self.grNode_addr)
        self.PythonIDEEditor.show()

    def autorun_python(self):
        if self.content.AutoExecute_flag:
            self.Execute_python()

            # self.cnt += 1

            # # End Input
            # #==========================================================================

            self.sendFixOutputByIndex(self.next_payload, 0)
            # self.sendFixOutputByIndex({'result': datetime.now().strftime("%H:%M:%S")}, 1)
            # self.sendFixOutputByIndex({'result':self.cnt}, 2)

        else:
            self.content.update_timer.stop()

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

  