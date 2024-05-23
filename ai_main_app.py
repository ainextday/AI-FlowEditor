#========================================================================
""" Make Application Auto Start in Windows """

# C:\Documents and Settings\All Users\Start Menu\Programs\Startup

""" put a shortcut to your python program. It should be executed every time your system starts up. """

import warnings
warnings.filterwarnings("ignore", message="torch.distributed.reduce_op is deprecated")

import os

#========================================================================
#Use GPU to Training AI
#For RTX20XX Series

os.environ['CUDA_VISIBLE_DEVICES'] = '0'  #GPU for Training AI
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

# limit the number of cpus used by high performance libraries
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

#========================================================================
class bcolors:
    HEADER = '\033[35m'     #Purple
    OKBLUE = '\033[94m'     #Blue
    FLAG = '\033[96m'       #Skyblue
    OK = '\033[92m'         #Green
    WARNING = '\033[93m'    #Yellow
    NG = '\033[91m'         #Red
    ENDC = '\033[0m'        #White
    BOLD = '\033[1m'        
    UNDERLINE = '\033[4m'

import sys

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

from tensorflow.python.client import device_lib
print("device_list = ", device_lib.list_local_devices())

import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
print(f'\nGPUs = {gpus}')
if len(gpus) > 0:
    try: tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError: pass

# =======================================================================
# Check in stall ids peak
# C:\Program Files\IDS\ids_peak

folder_path = r'C:\\Program Files\\IDS\\ids_peak'

if os.path.exists(folder_path):
    print(f"The folder '{folder_path}' exists.")
    print()
    print(f"{bcolors.NG} *** If AI_FlowEditer not start please restart your computer or manual install ids_peak_2.5.0.0.exe in folder ai_application/AI_Tools ***")
    print(f"{bcolors.ENDC}")
    
else:
    print(f"The folder '{folder_path}' does not exist.")
    # Replace 'ids_peak_2.5.0.0.exe' with the actual name of your installer file
    installer_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "ai_application", "AI_Tools", "ids_peak_2.5.0.0.exe"))

    # Run the installer with the path enclosed in double quotes
    os.system(f'"{installer_file}"')

#========================================================================
from PyQt5.QtWidgets import *
import sys

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from ai_application.AI_FlowEdit_window import AIFlowEditWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    wnd = AIFlowEditWindow()
    wnd.showMaximized()

    sys.exit(app.exec_())
    
