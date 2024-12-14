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
MSG_CLIENT_REQUIRE_JSON_FILE = 'client_require_list_of_file'
ACK = "<<ack>>".encode(FORMAT)

def signal_handel(sig, frame):
    delete = "\033[2K"
    print(f"{delete}\r{'-' * 20}")
    print("[STOP] Stop the program")
    print(f"{delete}\r{'-' * 20}")
    sys.exit()

def min(a, b):
    if a < b:
        return a
    return b

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
                break
            except Exception as e:
                pass
    def sendData(self, conn, data = b"", fileName = str()):
        try:
            size = f"{len(data)}"
            for i in range(len(size), 100):
                size = '0' + size
            conn.send(size.encode(FORMAT))
            time.sleep(1)
            ###
            conn.sendall(data)
            conn.sendall(END)
        except:
            pass

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
                if fileName == "<<sending_list_file>>" :
                    fileDir = "server_asset.json"

                client_ip = msg[2]
                ports = []
    
                for i in range(0, 4):
                    port = int(msg[i + 3])
                    ports.append(port)
                sendFile(conn, fileName, fileDir, client_ip, ports)
            else:
                print(f"Disconnected with {addr}")
                break
    except:
        print(f"Disconnected with {addr}")
    finally:
        conn.close()
        
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    signal.signal(signal.SIGINT, signal_handel)

    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    port = int(input("PORT = "))
    
    server.bind((ip, port))
    server.listen()
    print("Waiting ... ")

    thread_update_jsong = threading.Thread(target=updateJsonFile)
    thread_update_jsong.daemon = True # This is let theard die when the main process stop
    thread_update_jsong.start()

    while True:
        conn, addr = server.accept()
        print(f"Connected {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

except Exception as e:
    print(e)
finally:
    server.close()