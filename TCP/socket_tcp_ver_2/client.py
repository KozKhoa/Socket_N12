import socket
import os
import threading
import json
import time

FORMAT = "utf8"

def min(li = []):
    min = li[0]
    for i in li:
        if i < min:
            min = i
    return min

def max(li = []):
    max = li[0]
    for i in li:
        if i > max:
            max = i
    return max

def getFileData(fileDir = str()):
    data = b""
    with open(fileDir, "rb") as f:
        data = f.read()
        f.close()
    return data

def writeDataToFile(fileDir = str(), data = b"'"):
    with open(fileDir, "wb") as f:
        f.write(data)
        f.close()

def saveFile(fileDir = str(), data = b""):
    with open(fileDir, 'wb') as f:
        f.write(data)
        f.close()

def getHostIP():
    return socket.gethostbyname(socket.gethostname())

class Client:
    msg_require_file = "client_require_server_to_send_data"
    msg_require_list_file = "client_require_server_to_give_user_list_of_all_file_server_has"
    msg_client_send_data_to_server = "client_will_send_data_to_sever"
    msg_server_send_data_to_client = "server_will_send_data_to_client"
    msg_accept_the_reqire = "server_accept_client_require"
    msg_404_not_found = "server_annouce_that_file_does_not_exist_in_server"
    user = None
    ip = ""
    port = 0
    def __init__(self, IP, PORT) -> None:
        self.user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = IP
        self.port = PORT

    def connect(self):
        self.user.connect((self.ip, self.port))

    def listFileJson(self):
        fileDir = "client_asset.json"
        with open(fileDir, "r") as f:
            jsonFile = list(json.load(f))
            for file in jsonFile:
                print(f"{file["name"]}  -  {file["size"]}")
            f.close()


    def recvData(self, conn):
        packet = [b"", b"", b"", b""]
        DONE = False
        while not DONE:
            chunk = conn.recv(1024)
            if chunk[-7:] == "<<end>>".encode(FORMAT):
                chunk = chunk[:-7]
                DONE = True
            if (chunk[:11] == "<<packet1>>".encode(FORMAT)):
                packet[0] += chunk[11:]
            elif (chunk[:11] == "<<packet2>>".encode(FORMAT)):
                packet[1] += chunk[11:]
            elif (chunk[:11] == "<<packet3>>".encode(FORMAT)):
                packet[2] += chunk[11:]
            elif (chunk[:11] == "<<packet4>>".encode(FORMAT)):
                packet[3] += chunk[11:]
        data = b""
        for i in range(0, 4):
            data += packet[i]
        return data
            
    def checkFileInServer(self, fileName): ####################### error #######
        with open("client_asset.json", "rt") as f:
            jsonFile = list(json.loads(f))
            for file in jsonFile:
                if fileName == file["name"]:
                    return [file["name"], file["size"]]
            f.close()
        return ["404","404"]

    def requireFile(self, conn, fileName):
        require = self.msg_require_file + '@' + fileName
        conn.send(require.encode(FORMAT))
    def checkInputFile(self):
        fileDir = "input.txt"
        listFileInput = []
        with open(fileDir, "rt") as f:
            listFileInput = list(f.read().splitlines())
            f.close()

        listFileAsset = list(os.listdir("client_asset"))

        difference = set(listFileInput) - set(listFileAsset)
        for fileName in difference:
            fileInfo = self.checkFileInServer(fileName)
            if (fileInfo[0] == "404"):
                print(f"{fileName} does not exist")
            else:
                self.requireFile(self.user, fileName)
                data = self.recvData(self.user)
                saveFile(fileDir, data)

    def updateListFile(self, conn):
        conn.sendall(self.msg_require_list_file.encode(FORMAT))
        data = self.recvData(conn)
        saveFile("client_asset.json", data)

    def autoUpdate(self):
        while True:
            self.updateListFile(self.user)
            self.checkInputFile()
            time.sleep(5)

    def start_client(self):
        thread_auto_update = threading.Thread(target = self.autoUpdate)
        thread_auto_update.start()
        while True:
            try:
                print("[+] Press 1 to show all files")
                chosen = int(input(" >> "))
            except:
                print("[Error]")
            if (chosen == 1):
                self.listFileJson()



            
        
def main():
    port = int(input("PORT = "))
    user = Client(getHostIP(), port)
    user.connect()
    user.start_client()


main()

