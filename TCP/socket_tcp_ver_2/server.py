import socket
import os
import threading

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



class Server:
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
    def getHostIP(self):
        return socket.gethostbyname(socket.gethostname())

    def sendPacket(self, conn, data = b"", header = str()): # only send packet, not send any msg
        while True:
            chunk = data[:1024]
            data = data[1024:]

            chunk = header.encode(FORMAT) + chunk
            
            conn.sendall(chunk)
    def sendFile(self, conn, data = b""):
        # thong nhat cac paket khi gui thi 11 bytes dau tien se la "<<packeti>>" voi i la so thu tu cua packet
        div = int(len(data) / 4)
        packet = []
        for i in range(1, 4):
            chunk = data[:div]
            data = data[div:]
            packet.append(chunk)
        packet.append(data)

        thread_packet = []
        for i in range(1, 5):
            thread_packet.append(threading.Thread(target = self.sendPacket, args = (conn, packet[i], f"<<packet{i + 1}>>")))
        for i in range(1, 5):
            thread_packet[i].start()
        


def main():
    try:
        
        while True:
            server = Server(server.getHostIP(), 5555)
    except:
        server.server.close() 

