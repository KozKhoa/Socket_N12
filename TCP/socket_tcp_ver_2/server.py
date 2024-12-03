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

def getHostIP():
    return socket.gethostbyname(socket.gethostname())

class Server:
    msg_require_file = "client_require_server_to_send_data"    
    msg_require_list_file = "client_require_server_to_give_user_list_of_all_file_server_has"
    msg_client_send_data_to_server = "client_will_send_data_to_sever"
    msg_server_send_data_to_client = "server_will_send_data_to_client"
    msg_accept_the_reqire = "server_accept_client_require"
    msg_404_not_found = "server_annouce_that_file_does_not_exist_in_server"

    server = None
    ip = ""
    port = 0

    def __init__(self, IP = str(), PORT = int()) -> None:
        self.ip = IP
        self.port = PORT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
    def listen(self):
        self.server.listen()

    # def checkUpdateInServer(self, conn):
    #     assetList = os.listdir("server_asset")
    #     assetJson = []
    #     with open("server_asset.json", "rt") as f:
    #         assetJson = list(json.load(f))
    #     diff = set(assetList) - set(assetList)
    #     if diff != {}:
    #         return True
    #     return False


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

    def sendPacket(self, conn, data = b"", header = str(), fileName = str(), packet = int()): # only send packet, not send any msg
        length = len(data)                                                    # fileName dung de hien thi ten file ra
        i = 1
        while data != b"":
            chunk = data[:1024]
            data = data[1024:]

            chunk = header.encode(FORMAT) + chunk
            
            conn.sendall(chunk)
            
            print(f"Sending {fileName} part {packet} ... {min([100, round(i * 1024 / length, 0)])} %\r")
            i += 1
    def sendFile(self, conn, data = b"", fileName = str()):
        # thong nhat cac paket khi gui thi 11 bytes dau tien se la "<<packeti>>" voi i la so thu tu cua packet
        div = int(len(data) / 4)
        packet = []
        for i in range(1, 4): # Chia goi tin ra thanh 4 packet
            chunk = data[:div]
            data = data[div:]
            packet.append(chunk)
        packet.append(data)

        thread_packet = []
        for i in range(0, 4): # Tien hanh phan luong viec chia cac goi tin
            thread_packet.append(threading.Thread
                (target = self.sendPacket, args = (conn, packet[i], f"<<packet{i + 1}>>", fileName, i + 1)))
        for i in range(0, 4): 
            thread_packet[i].start()
        conn.send("<<end>>".encode(FORMAT))
    
    def sendListFile(self, conn):
        self.sendFile(conn, getFileData("server_asset.json"), "client_asset.json")
    
    def handle_client(self, conn, addr):
        
        while True:
            msg = conn.recv(1024).decode(FORMAT).split("@")
            if msg[0] == self.msg_require_file:
                fileName = msg[1]
                fileDir = f"server_asset/{fileName}"
                self.sendFile(conn, getFileData(fileDir), fileName)
            elif msg[0] == self.msg_require_list_file:
                fileName = "server_asset.json"
                fileDir = "server_asset.json"
                self.sendFile(conn, getFileData(fileDir), fileName)
            # print(f"[+] Disconnected wiht {addr}")
    def accept(self):
        return self.server.accept()



def main():
    port = int(input("PORT = "))
    server = Server(getHostIP(), port)
    server.listen()
    jsonThread = threading.Thread(target = server.updateJsonFile)
    jsonThread.start()
    while True:
        print("HI")
        conn, addr = server.accept()
        print(f"[+] Connect with {addr}")
        threading.Thread(target = server.handle_client, args=(conn, addr)).start()

main()

