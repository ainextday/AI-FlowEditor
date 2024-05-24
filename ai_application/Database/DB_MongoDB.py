import pymongo
import socket

class MongoDB:

    def __init__(self):
        super().__init__()

        self.DatabaseName = None
        self.localhost = ""

        self.initUI()

    def initUI(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.localhost = s.getsockname()[0]
        print(self.localhost)
        s.close()

    def CreateDB(self, localhost):
        myclient = pymongo.MongoClient(localhost, 27017)
        mydb = myclient["mydatabase"]
        
        dblist = myclient.list_database_names()
        if "databsename" in dblist:
            print("The database exists.")