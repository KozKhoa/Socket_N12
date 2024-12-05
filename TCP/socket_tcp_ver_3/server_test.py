import socket
import os
import threading
import time
import json

FORMAT = "utf8"
END = "<<end>>".encode(FORMAT)
MSG_CLIENT_REQUIRE_FILE = 'client_requrie_file'
MSG_CLIENT_REQUIRE_JSON_FILE = 'client_require_list_of_file'
ACK = "<<ack>>".encode(FORMAT)

def min(a, b):
    if a < b:
        return a
    return b

class p2p:
    ip = ""
    port = 0
    soc = None
    format = "utf8"
    ACK = "<<ack>>".encode(format)
    conn = None
    addr = None

    fileName = ""

    return_recv_data = None

    def __init__(self, IP, PORT) -> None:
        self.ip = IP
        self.port = int(PORT)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def listen(self):
        self.soc.bind((self.ip, self.port))
        self.soc.listen()
        self.conn, self.addr = self.soc.accept()
    def connect(self):
        while True:
            try:
                self.soc.connect((self.ip, self.port))
                # print("Connected !")
                break
            except Exception as e:
                # print("Connecting ... ")
                i = 1
    def sendData(self, conn, data = b"", fileName = str()):
        size = f"{len(data)}"
        for i in range(len(size), 100):
            size = '0' + size
        conn.send(size.encode(FORMAT))
        time.sleep(1)
        ###
        conn.sendall(data)
        conn.sendall(END)
    def recvData(self):
        data = b""
        DONE = False
        while not DONE:
            chunk = self.conn.recv(1024 * 1024)
            if chunk[-7:] == END:
                DONE = True
                chunk = chunk[:-7]
            data += chunk
            # print(f"\Downloading {self.fileName} ... {min(100, round((len(data) / 1) * 100, 0))}%", end="")
        self.return_recv_data = data
        return data

def sendFile(conn, fileName, fileDir, ip, ports):
    soc = []
    for i in range(0, 4):
        socket = p2p(ip, ports[i])
        socket.connect()
        soc.append(socket)

    data = b""
    with open(fileDir, "rb") as f:
        data = f.read()

    div = int(len(data) / 4)
    chunk = []
    for i in range(0, 3):
        chunk.append(data[:div])
        data = data[div:]
    chunk.append(data)

    thread = []
    for i in range(0, 4):
        name = f"{fileName} part {i + 1}"
        thread.append(threading.Thread(target=soc[i].sendData, args=(soc[i].soc, chunk[i], name)))
        thread[i].start()

    for i in range(0, 4):
        thread[i].join()
        soc[i].soc.close()

    soc = []        

def requireFile(conn, fileName, ip, port):
    soc = []
    ports = []
    msg = MSG_CLIENT_REQUIRE_FILE + '@' + fileName

    for i in range(0, 4):
        socket = p2p(ip, 0)
        socket.soc.bind(('', 0))
        port = socket.soc.getsockname()[1]
        socket.port = port
        socket.fileName = f"{fileName} part {i + 1}"

        soc.append(socket)
        ports.append(port)

    for i in range(0, 4):
        msg += '@' + f"{ports[i]}"
    conn.sendall(msg.encode(FORMAT))
    for i in range(0, 4):
        soc[i].listen()

    return (soc, ports)
    
def recvFile(conn, fileName = str(), saveDir = str(), ip = str(), soc = socket, ports = list):
    
    thread = []
    for i in range(0, 4):
        temp = threading.Thread(target=soc[i].recvData)
        temp.start()
        thread.append(temp)

    packet = [b""]
    for i in range(0, 4):
        thread[i].join()
        data = soc[i].return_recv_data
        packet.append(data)
    data = b""
    for i in packet:
        data += i

    with open(saveDir,"wb") as f:
        f.write(data)
        f.close()

    for i in range(0, 4):
        soc[i].conn.close()
    soc = None
   
def updateJsonFile():
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

def handle_client(conn, addr):
    try:
        while True:
            msg = conn.recv(1024).decode(FORMAT).split('@')
            if msg[0] == MSG_CLIENT_REQUIRE_FILE:
                fileName = msg[1]
                fileDir = 'server_asset/' + fileName
                if fileName == 'server_asset.json':
                    fileDir =  fileName
                ports = []
                for i in range(0, 4):
                    port = int(msg[i + 2])
                    ports.append(port)
                sendFile(conn, fileName, fileDir, ip, ports)
            else:
                print(f"Disconnected with {addr}")
                break
    except:
        print(f"Disconnected with {addr}")
    finally:
        conn.close()
        
# ip = "127.0.0.0"
ip = socket.gethostbyname(socket.gethostname())
print(ip)
port = int(input("PORT = "))



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

print("Waiting ... ")
threading.Thread(target=updateJsonFile).start()
while True:
    conn, addr = server.accept()
    print(f"Connected {addr}")
    threading.Thread(target=handle_client, args=(conn, addr)).start()
    
