import socket
import os
import threading
import time
import json

FORMAT = "utf8"
END = "<<end>>".encode(FORMAT)
MSG_CLIENT_REQUIRE_FILE = 'client_requrie_file'
ACK = "<<ack>>".encode(FORMAT)
FORMAT = "utf8"

class p2p:
    ip = ""
    port = 0
    soc = None
    format = "utf8"
    ACK = "<<ack>>".encode(format)
    conn = None
    addr = None

    fileName = ""

    return_recv_data = b""

    def __init__(self, IP, PORT) -> None:
        self.ip = IP
        self.port = int(PORT)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def listen(self):
        # self.soc.bind((self.ip, self.port)) ## You don't have to bind because the previous did that
        self.soc.listen()
        self.conn, self.addr = self.soc.accept()
    def connect(self):
        while True:
            try:
                self.soc.connect((self.ip, self.port))
                print("Connected !")
                break
            except Exception as e:
                print("Connecting ... ")
    def sendData(self, conn, data = b"", fileName = str()):
        conn.sendall(data)
        conn.sendall(END)

    def recvData(self):
        data = b""
        size = int(self.conn.recv(100).decode())
        DONE = False
        while not DONE:
            chunk = self.conn.recv(1024 * 1024)
            if chunk[-7:] == END:
                DONE = True
                chunk = chunk[:-7]
            data += chunk
            if ("client_asset.json" not in self.fileName):
                part = int(self.fileName[-1:])
                down = f"\033[{part}B"
                up = f"\033[{part}A"
                delete = "\033[2K"
                # enter = ""
                # for i in range(0, part):
                #     enter += '\n'
                print(f"\r{down}{delete}\rDownloading {self.fileName} ... {min(100, round((len(data) / size) * 100, 0))}%\r{up}",end="")
        self.return_recv_data = data
        return data
        
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
        soc[i].listen() ######

    return (soc, ports)
    
def recvFile(conn, fileName = str(), saveDir = str(), ip = str(), soc = socket, ports = list):
    
    thread = []
    for i in range(0, 4):
        soc[i].fileName = f"{fileName} part {i + 1}"
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
        
    
def updateJsonFile(jsonDir):
    dir = jsonDir
    name = 'server_asset.json'
    soc, ports = requireFile(client, name, ip, port)
    recvFile(client, dir, dir, ip, soc, ports)

def printJsonFile(fileDir):
    fileDir = "client_asset.json"
    down = f"\033[{6}B"
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

def checkFileInServer(fileName = str()):
    with open("client_asset.json", "rt") as f:
        jsonFile = list(json.load(f))
        for file in jsonFile:
            if file['name'] == fileName:
                f.close()
                return [file['name'], file['size']]
        f.close()
    return ["404", "404"]
        
def updateInputFile(inputDir = str()):
    listFileInput = []
    with open(inputDir, "rt") as f:
        listFileInput = list(f.read().splitlines())
        f.close()
    listFileAsset = list(os.listdir("client_asset"))
    difference = set(listFileInput) - set(listFileAsset)

    down = f"\033[{1}B"
    up = f"\033[{1}A"

    for fileName in difference:
        fileInfo = checkFileInServer(fileName)
        if (fileInfo[0] == "404"):
            print(f"{up}[+] {fileName} does not exist", end=f" | {down}")
        else:
            name = fileInfo[0]
            size = fileInfo[1]
            saveDir = f"client_asset/{name}"
            soc, ports = requireFile(client, fileName, ip, port)
            recvFile(client, fileName, saveDir, ip, soc, ports)
        
def start_client():
    print(f"Connect with {client}\n\n")
    while True:
        updateJsonFile('client_asset.json')
        printJsonFile('client_asset.json')
        updateInputFile('input.txt')
        time.sleep(5)

ip = "127.0.0.0"
print(ip)
port = int(input("PORT = "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))

start_client()
