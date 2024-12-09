import socket
import os
import threading
import time
import json
import signal
import sys

FORMAT = "utf8"
END = "<<end>>".encode(FORMAT)
MSG_CLIENT_REQUIRE_FILE = 'client_requrie_file'
ACK = "<<ack>>".encode(FORMAT)
FORMAT = "utf8"

def signal_handel(sig, frame):
    delete = "\033[2K"
    print(f"{delete}\r{'-' * 20}")
    print("[STOP] Stop the program")
    print(f"{delete}\r{'-' * 20}")
    sys.exit(0)

def getAvailablePort(ip = str(), start = int()):
    ports = []  
    port = start
    while len(ports) < 4:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((ip, port))
                ports.append(port)
            except:
                pass
        port += 1
    return ports

class p2p:
    ip = ""
    port = 0
    soc = None
    conn = None
    addr = None
    fileName = ""
    return_recv_data = b""

    def __init__(self, IP, PORT) -> None:
        self.ip = IP
        self.port = int(PORT)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def listen(self):
        self.soc.bind((self.ip, self.port))
        self.soc.listen()
        self.conn, self.addr = self.soc.accept() ####
    def connect(self):
        while True:
            try:
                self.soc.connect((self.ip, self.port))
                print("Connected !")
                break
            except Exception as e:
                print("Connecting ... ")

    def recvData(self):
        data = b""
        size = int(self.conn.recv(100).decode())
        DONE = False
        while not DONE:
            chunk = self.conn.recv(65355)
            if chunk[-7:] == END:
                DONE = True
                chunk = chunk[:-7]
            data += chunk
            if ("client_asset.json" not in self.fileName):
                part = int(self.fileName[-1:])
                down = f"\033[{part}B"
                up = f"\033[{part}A"
                delete = "\033[2K"
                print(f"\r{down}{delete}\rDownloading {self.fileName} ... {min(100, round((len(data) / size) * 100, 0))}%\r{up}",end="")
        self.return_recv_data = data
        return data
        
def requireFile(conn, fileName, ip, port):  
    
    soc = []
    client_ip = socket.gethostbyname(socket.gethostname())
    msg = MSG_CLIENT_REQUIRE_FILE + '@' + fileName + '@' + str(client_ip)

    ports = getAvailablePort(client_ip, port + 1) # Lay cac port cua ip dang kha dung

    for i in range(0, 4): # Sau khi co duoc cac port kha dung, tien hanh tao 4 socket de server gui file ket noi
        new_soc = p2p(client_ip, ports[i])
        new_soc.fileName = f"{fileName} part {i + 1}"
        soc.append(new_soc)

    for i in range(0, 4): # Cau hinh tin nhan gom "yeu cau gui file@ten file@port 1@port2@port 3@port 4"
        msg += '@' + f"{ports[i]}"
    conn.sendall(msg.encode(FORMAT))

    thread = []
    for i in range(0, 4): # Tien hanh lang nghe cac ket noi
        thread.append(threading.Thread(target=soc[i].listen))
        thread[i].start()

    for i in range(0, 4): # Doi cho den khi server ket noi thanh cong den 4 ket noi song song
        thread[i].join()
    return (soc, ports)
    
def recvFile(conn, fileName = str(), saveDir = str(), ip = str(), soc = socket, ports = list):
    
    thread = []
    for i in range(0, 4): # Nhan file tu 4 ket noi song song da mo o requireFile
        soc[i].fileName = f"{fileName} part {i + 1}"
        temp = threading.Thread(target=soc[i].recvData)
        temp.start()
        thread.append(temp)

    data = b""
    for i in range(0, 4): # Nhan file tu recvData da mo o tren
        thread[i].join()
        mini_data = soc[i].return_recv_data
        data += mini_data

    with open(saveDir,"wb") as f: # Ghi data vao file
        f.write(data)
        f.close()

    for i in range(0, 4): # Dong ket noi
        soc[i].conn.close()
    soc = None
    
def updateJsonFile(jsonDir):
    dir = jsonDir
    name = 'server_asset.json'
    soc, ports = requireFile(client, name, server_ip, port)
    recvFile(client, dir, dir, server_ip, soc, ports)

def printJsonFile(fileDir):
    fileDir = "client_asset.json"
    down = f"\033[{6}B" # 3 dong sau la di chuyen con tro console
    up = f"\033[{6}A"
    delete = "\033[2K"
    print(f"\r{down}", end="")
    num_of_file = 0
    with open(fileDir, "rt") as f:
        jsonFile = list(json.load(f))
        for file in jsonFile:
            print(f"{delete}\r{file["name"]}  -  {round(file["size"] / 1024, 0)}MB")
            num_of_file += 1
        f.close()
    print(f"\033[{6 + num_of_file}A", end="")

def checkFileInServer(fileName = str()): # Kiem tra file yeu cau co o trong server khong
    with open("client_asset.json", "rt") as f:
        jsonFile = list(json.load(f))
        for file in jsonFile:
            if file['name'] == fileName:
                f.close()
                return [file['name'], file['size']]
        f.close()
    return ["404", "404"]
        
def updateInputFile(inputDir = str()): # Cap nhat file input
    listFileInput = []
    with open(inputDir, "rt") as f:
        listFileInput = list(f.read().splitlines())
        f.close()
    listFileAsset = list(os.listdir("client_asset"))
    difference = set(listFileInput) - set(listFileAsset)

    down = f"\033[{1}B" # 3 dong sau la di chuyen con tro console
    up = f"\033[{1}A"
    delete = "\033[2K"

    for fileName in difference:
        fileInfo = checkFileInServer(fileName)
        if (fileInfo[0] == "404"):
            print(f"{up}[+] {fileName} does not exist", end=f" | {down}")
        else:
            name = fileInfo[0]
            saveDir = f"client_asset/{name}"
            soc, ports = requireFile(client, fileName, server_ip, port)
            recvFile(client, fileName, saveDir, server_ip, soc, ports)
        
def start_client():
    print(f"Connect with {client}\n\n")
    while True:
        updateJsonFile('client_asset.json')
        printJsonFile('client_asset.json')
        updateInputFile('input.txt')
        time.sleep(5)

try:
    signal.signal(signal.SIGINT, signal_handel)
    server_ip = input("IP = ")
    print(server_ip)
    port = int(input("PORT = "))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, port))

    start_client()
    client.close()
except Exception as e:
    print(e)
