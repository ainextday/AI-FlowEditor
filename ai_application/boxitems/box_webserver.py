from urllib import response
from ai_application.Flow_Conf import *
from ai_application.Flow_Node_Base import *
from ai_application.AIFlow_Editor.utils import dumpException
from ai_application.Database.GlobalVariable import *

import cv2
from PyQt5.QtGui import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# pip3 install flask
from flask import Flask, render_template, request, url_for, Response, jsonify
import datetime
import threading

DashboardName = ""
MapImage = ""
BoxListAddress = {}
UpateDeviceID = []
Param1List = []
Param2List = []
Param3List = []
timestamp = []

Global = GlobalVariable()

class WebServer(QDMNodeContentWidget):
    def initUI(self):
        self.Data = None
        self.Path = os.path.dirname(os.path.abspath(__file__))

        animate_movie = self.Path + "/icons/icons_data_transfer.gif"

        self.lbl = QLabel("No Input" , self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-size:7pt;color:lightblue;")
        self.lbl.setGeometry(5,2,140,20)
                
        #====================================================
        """self.graphicsView = QGraphicsView(self)
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.resize(95,70)
        self.graphicsView.setGeometry(QtCore.QRect(0, 20, 105, 75))

        img = QPixmap(animate_process)
        self.pixmap.setPixmap(img)"""

        #====================================================
        # Loading the GIF
        self.label = QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 20, 105, 75))
        self.label.setMinimumSize(QtCore.QSize(130, 75))
        self.label.setMaximumSize(QtCore.QSize(130, 75))

        self.movie = QMovie(animate_movie)
        self.label.setMovie(self.movie)
        self.movie.start()
        #====================================================

        import socket

        self.localhost = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.localhost = s.getsockname()[0]

        s.close()

        self.lbl.setText("http://" + str(self.localhost))

    def serialize(self):
        res = super().serialize()
        res['message'] = self.Data
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.Data = data['message']
            return True & res
        except Exception as e:
            dumpException(e)
        return res

class VideoCamera(object):
    def __init__(self):
        pass
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        #self.video = cv2.VideoCapture(0)

        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
        
    def __del__(self):
        #self.video.release()
        pass

    def get_frame(self):
        image = np.array(live_frame["img"]) #self.video.read()
        #print(image)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

@register_node(OP_NODE_WEBSERVER)
class Open_WebServer(FlowNode):
    Path = os.path.dirname(os.path.abspath(__file__))
    icon = Path + "/icons/icons_http_icon.png"
    op_code = OP_NODE_WEBSERVER
    op_title = "Web Server"
    content_label_objname = "Web Server"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2,3], outputs=[]) #<------ Set Box Input[1,2,3] Output Socket[1,2,3]
        self.payload = {}

    def initInnerClasses(self):
        self.content = WebServer(self)                   # <----------- init UI with data and widget
        self.grNode = FlowGraphicsFaceProcess(self)          # <----------- Box Image Draw in Flow_Node_Base

        self.stream_thread = threading.Thread(target=wapp.run, args=[self.content.localhost, 8080])
        self.stream_thread.daemon = True
        self.stream_thread.start()

    def evalImplementation(self):                       # <----------- Create Socket range Index
        global MapImage, DashboardName, BoxListAddress, UpateDeviceID, Param1List, Param2List, Param3List, timestamp

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
            if 'dashboardtype' in self.rx_payload:
                if self.rx_payload['dashboardtype'] == 'map':
                    # print("self.rx_payload = ", self.rx_payload)
                
                    if 'history_report' in self.rx_payload:
                        if len(self.rx_payload['history_report']) > 0:
                            print("history_report = ", self.rx_payload['history_report'])
                            BoxListAddress = self.rx_payload['history_report']['map_item']

                            Param1List = self.rx_payload['history_report']['map_param1']
                            Param2List = self.rx_payload['history_report']['map_param2']
                            Param3List = self.rx_payload['history_report']['map_param3']

                            timestamp = self.rx_payload['history_report']['map_timestamp']
                    
                    else:
                        # print("self.rx_payload = ", self.rx_payload)

                        DashboardName = self.rx_payload['titel_name']
                        MapImage = self.rx_payload['map_location']
                        BoxListAddress = self.rx_payload['map_item']
                        UpateDeviceID = self.rx_payload['map_iactive']

                        Param1List = self.rx_payload['map_param1']
                        Param2List = self.rx_payload['map_param2']
                        Param3List = self.rx_payload['map_param3']

                        timestamp = self.rx_payload['map_timestamp']

        """self.value = self.payload                       # <----------- Push payload to value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        #self.grNode.setToolTip("")
        self.evalChildren()

        #return self.value"""

wapp = Flask(__name__)

@wapp.route('/')
@wapp.route('/index', methods=['GET', 'POST'])
def index():
    now = datetime.datetime.now()
    dateString = now.strftime("%d-%m-%Y")
    templateData = {
        'titlename' : 'AI Flow Editor - Dashboard',
        'datestring' : dateString
    }

    action = ""

    if request.method == 'POST':
        print("POST ", request.form['historydate'])

    elif request.method == 'GET':
        print("len(GET /get_data HTTP/1.1) = ", len(str(request)))
        if len(str(request)) > 50:
            split_request_date = str(request).split("=")
            print()
            #print("split_request_date[0] = ", split_request_date[0])

            split_action = split_request_date[0].split("?")
            action = split_action[1]
            print("GET action = ", action)

            if action == "historydate":
                request_date = split_request_date[1].split("'")
            
                Global.setGlobal(action, str(request_date[0]))
                print("GET Request date = ", request_date[0])
                print()

        else:
            Global.setGlobal('historydate', None)
            Global.setGlobal('WebOTR', False)
            print("Defauat index home.")


        return render_template('index.html', **templateData)

    return render_template('index.html', **templateData)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@wapp.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@wapp.route('/get_data')
def languages():
    '''Return data in json format'''
    now = datetime.datetime.now()
    dateString = now.strftime("%d-%m-%Y")
    timeString = now.strftime("%H:%M:%S")

    """temp_data = str(SQLite().FetchDataLimit('SQLite_PoseEavaluate.db','Working_tbl','15'))
    SQLite_Data = temp_data.split(",")"""

    updatedata = {}

    updatedata['titlename'] = DashboardName
    updatedata['datestring'] = dateString
    updatedata['timestring'] = timeString
    updatedata['mapimage'] = MapImage

    intdata = 0

    # print("len(BoxListAddress) = ", len(BoxListAddress))

    for i in range(len(BoxListAddress)):
        updatedata['name' + str(intdata + 1)] = BoxListAddress[i]['boxname']
        updatedata['x' + str(intdata + 1)] = BoxListAddress[i]['x']
        updatedata['y' + str(intdata + 1)] = BoxListAddress[i]['y']

        updatedata['activeid' + str(intdata + 1)] = UpateDeviceID[i]
        updatedata['p1' + str(intdata + 1)] = Param1List[i]
        updatedata['p2' + str(intdata + 1)] = Param2List[i]
        updatedata['p3' + str(intdata + 1)] = Param3List[i]
        updatedata['lastUpdate' + str(intdata + 1)] = timestamp[i]

        intdata += 1

    return jsonify(updatedata)

