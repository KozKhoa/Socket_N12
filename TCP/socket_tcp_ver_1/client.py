import socket
import os
import time
from tqdm import tqdm
import threading
import json


class Client:
    ip = ""
    port = 0
    user = None

    endNotifi = b"<<end>>"

    msg_require_file = "client_require_server_to_send_data"
    msg_require_list_file = "client_require_server_to_give_user_list_of_all_file_server_has"
    msg_client_send_data_to_server = "client_will_send_data_to_sever"
    msg_server_send_data_to_client = "server_will_send_data_to_client"
    msg_accept_the_reqire = "server_accept_client_require"

    def __init__(self, PORT) -> None:
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = PORT
    def starClient(self):
        self.user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user.connect((self.ip, self.port))
    
    def requireFile(self, conn, fileName):
        conn.send(self.msg_require_file.encode())
        msg = conn.recv(1024).decode()
        if (msg == self.msg_accept_the_reqire):
            conn.send(fileName.encode())
        fileInfo = conn.recv(1024).decode().split("@")
        print(fileInfo)
        fileName = fileInfo[0]
        fileSize = int(fileInfo[1])
        return (fileName, fileSize)

    def recvListFile(self, conn):
        fileDir = "client_asset.json"
        with open(fileDir, "wb") as f:
            while True:
                data = conn.recv(1024)
                if (data[-7:] == "<<END>>".encode()):
                    f.write(data[:-7])
                    break
                f.write(data)
                ###
                conn.send("<<ACK>>".encode())
            f.close()

    def checkInputFile(self):
        fileDir = "input.txt"
        while True:
            listFileInput = []
            with open(fileDir, "rt") as f:
                listFileInput = list(f.read().splitlines())
                f.close()

            listFileAsset = list(os.listdir("client_asset"))

            difference = set(listFileInput) - set(listFileAsset)
            for fileName in difference:
                name, size = self.requireFile(self.user, fileName)
                if (name == "<<???>>"):
                    print(f"Cannot found file name {fileName}")
                else:
                    self.recvFile(self.user, fileName, size)

            # print(listFileAsset)
            ###
            time.sleep(1)

            time.sleep(4)

    def recvFile(self, conn, fileName, fileSize): # sour : source, where the file come from
        fileDir = f"client_asset/{fileName}"

        print("\n")
        process = tqdm(range(fileSize),desc=fileName, leave = True, unit="B", unit_scale=True)
        with open(fileDir, "wb") as f:
            while True:
                data = conn.recv(1024)
                if (data[-7:] == "<<END>>".encode()):
                    f.write(data[:-7])
                    break
                f.write(data)
                ###
                conn.send("<<ACK>>".encode())
                process.update(len(data))
            f.close()

        
PORT = int(input("Enter PORT = "))
client = Client(PORT)
client.starClient()

# client.checkInputFile()

thread = threading.Thread(target=client.checkInputFile)
thread.start()
while True:
    print(f"1. List all file that serveer have")
    chosen = int(input(">> "))
    if (chosen == 1):
        client.user.send(client.msg_require_list_file.encode())
        client.user
        
client.user.close()