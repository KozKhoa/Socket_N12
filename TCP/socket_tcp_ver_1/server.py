import socket
import os
import time
import threading
from tqdm import tqdm
import json

class Server:
    ip = ""
    port = 0
    server = None
    endNotifi = b"<<end>>"

    msg_require_file = "client_require_server_to_send_data"
    msg_client_send_data_to_server = "client_will_send_data_to_sever"
    msg_server_send_data_to_client = "server_will_send_data_to_client"
    msg_accept_the_reqire = "server_accept_client_require"
    msg_require_list_file = "client_require_server_to_give_user_list_of_all_file_server_has"

    def __init__(self, PORT) -> None:
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = PORT
    def createTCPconnect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
    def listen(self):
        self.server.listen()
        print("Waiting for client ... ")

    def sendListFile(self, connn):
        fileDir = "server_asset.json"
        with open(fileDir, "rb") as f:
            while True:
                data = f.read(1024)
                conn.send(data)
                ###
                if not data:
                    conn.send("<<END>>".encode())
                    break
                msg = conn.recv(1024).decode()
                while msg != "<<ACK>>":
                    conn.send(data)
                    msg = conn.recv(1024).decode()
            f.close()

    def updateJsonFile(self):
        while True:
            jsonFile = open("server_asset.json", 'wt')
            listFile = []
            for i in os.listdir("server_asset"):
                newOb = {
                    "name": i,
                    "size": os.path.getsize(f"server_asset/{i}")
                }
                listFile.append(newOb)
            json.dump(listFile, jsonFile, indent=4)
            jsonFile.close()
            time.sleep(5)

    def sendFile(self, conn, fileName): # des: destination
        fileDir = f"server_asset/{fileName}"
        fileSize = os.path.getsize(fileDir)
        print("\n")
        process = tqdm(range(fileSize), desc=fileName, 
                leave = True, unit="B", unit_scale=True)
        with open(fileDir, "rb") as f:
            while True:
                data = f.read(1024)
                conn.send(data)
                ###
                if not data:
                    conn.send("<<END>>".encode())
                    break
                msg = conn.recv(1024).decode()
                while msg != "<<ACK>>":
                    conn.send(data)
                    msg = conn.recv(1024).decode()
                process.update(len(data))
            f.close()

    def checkIfFileInServer(self, fileName):
        listFile = list(os.listdir("server_asset"))
        for name in listFile:
            if fileName == name:
                return True
        return False

    def responeToRequireFile(self, conn):
        try:
            conn.send(self.msg_accept_the_reqire.encode())
            fileName = conn.recv(1024).decode()
            if (self.checkIfFileInServer(fileName) == True):
                fileSize = int(os.path.getsize(f"server_asset/{fileName}"))
                conn.send(f"{fileName}@{fileSize}".encode())
            else:
                conn.send("<<???>>@0".encode())
                fileName = "<<???>>"
            
        except Exception as e:
            conn.send("<<???>>@0".encode())
        finally:
            return fileName

    def handle_client(self, conn, addr):
        try:
            while True:
                msg = conn.recv(1024).decode()
                if (msg == self.msg_require_file):
                    fileName = self.responeToRequireFile(conn)
                    if (fileName != "<<???>>"):
                        self.sendFile(conn, fileName)
                elif (msg == self.msg_require_list_file):
                    self.sendListFile(conn)
        except Exception as e:
            print(e)
            print(f"Disconnected with {addr}")

   

PORT = int(input("Enter PORT = ")) 
server = Server(PORT)
server.createTCPconnect()
server.listen()

# server.updateJsonFile()

try:
    jsonThread = threading.Thread(target=server.updateJsonFile)
    jsonThread.start()

    while True:
        conn, addr = server.server.accept()
        print(f"Connect with {addr}")
        thread = threading.Thread(target=server.handle_client, args=(conn, addr))
        thread.start()
except:
    server.server.close()




# server.sendFile(conn, "zalo-setup.exe")

