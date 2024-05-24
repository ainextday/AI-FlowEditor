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
import sys

class CommandPrompt(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None

        self.Path = os.path.dirname(os.path.abspath(__file__))
        cmd_image = self.Path + "/icons/icons_cmdimg.png"

        self.SettingBtn = QPushButton(self)
        self.SettingBtn.setGeometry(10,10,75,50)
        self.SettingBtn.setIcon(QIcon(cmd_image))
        self.SettingBtn.setIconSize(QtCore.QSize(75,50))
        #Make Transparent
        self.SettingBtn.setStyleSheet("background-color: transparent; border: 0px;")  

        self.command = ""

        # ==========================================================
        # For evalChildren
        self.script_name = sys.argv[0]
        base_name = os.path.basename(self.script_name)
        self.application_name = os.path.splitext(base_name)[0]
        # ==========================================================

    def serialize(self):
        res = super().serialize()
        res['command'] = self.command
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if 'command' in data:
                self.command = data['command']

            return True & res
        except Exception as e:
            dumpException(e)
        return res
    
# ===========================================================
class CMDSetting(QtWidgets.QMainWindow):
    def __init__(self, content, parent=None):
        super().__init__(parent)

        self.content = content
        self.edit_command = self.content.command

        self.title = "Command Prompt Setting"
        self.top    = 300
        self.left   = 600
        self.width  = 800
        self.height = 470
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.setStyleSheet("background-color: rgba(0, 32, 130, 155);")

        self.lbl = QLabel("Command Prompt : ", self)
        self.lbl.setGeometry(QtCore.QRect(10, 5, 150, 20))
        self.lbl.setStyleSheet("color: #42E3C8;")

        self.editCommandPrompt = QPlainTextEdit("",self)
        # self.editCommandPrompt.setFixedWidth(380)
        self.editCommandPrompt.setGeometry(10,30,780,250)
        self.editCommandPrompt.setStyleSheet("background-color: rgba(19, 21, 91, 225);font-size:12pt;color:#42E3C8;")
        self.editCommandPrompt.setPlaceholderText("Command Prompt")
        self.editCommandPrompt.setPlainText(self.edit_command)

    def closeEvent(self, event):
        self.content.command = self.editCommandPrompt.toPlainText()

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

# ==================================================================

@register_node(OP_NODE_CMD)
class Open_CMD(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_cmd.png"
    op_code = OP_NODE_CMD
    op_title = "cmd"
    content_label_objname = "cmd"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[3]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

        self.input_sanp_payload = {}
        self.Sigle_SnapInput = False

    def initInnerClasses(self):
        self.content = CommandPrompt(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsCamera(self)               # <----------- Box Image Draw in Flow_Node_Base

        self.content.SettingBtn.clicked.connect(self.OnOpen_Setting)


    def evalImplementation(self):                           # <----------- Create Socket range Index

        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            # return

            self.Sigle_SnapInput = False

        else:
            self.input_sanp_payload = input_node.eval()

            if self.input_sanp_payload is None:
                self.grNode.setToolTip("Input is NaN")
                self.markInvalid()

                self.Sigle_SnapInput = False

            elif type(self.input_sanp_payload) != type(None):
                if 'submit' in self.input_sanp_payload:
                    if self.input_sanp_payload['submit'] and not self.Sigle_SnapInput:
                        self.Sigle_SnapInput = True

                        multi_script = self.content.command.split('\n')
                        for i in range(len(multi_script)):
                            self.exe_command(str(multi_script[i]))
                            time.sleep(1)

                    else:
                        self.Sigle_SnapInput = False

        self.value = self.payload

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        if self.content.application_name == "ai_boxflow":
            self.evalChildren(op_code=self.op_code)
        else:
            self.evalChildren()

    def OnOpen_Setting(self):
        self.CMD_Setting = CMDSetting(self.content)
        self.CMD_Setting.show()

    def exe_command(self, commad_script):

        # root_part = self.Training_File_Path[0:2]

        shell = client.Dispatch("WScript.Shell")
        run_cmdScript = Exec_cmdScript()
        run_cmdScript.open_cmd(shell)
        # run_cmdScript.activate_venv(shell, root_part, self.Training_File_Path)
        run_cmdScript.run_cmd_script(shell, commad_script)
        time.sleep(1)
        run_cmdScript.run_cmd_script(shell, "exit")
        