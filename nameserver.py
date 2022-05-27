#!/usr/bin/python3
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread

HOST = "127.0.0.1"
MAX_CLIENTS = int(10)
MAX_MSG_SIZE = 2048
NAMESERVER_PORT = int(10001)

def recv_from_client(clientSocket, addr):
    while True:
        msg = clientSocket.recv(MAX_MSG_SIZE)
        
        if(len(msg) == 0):
            print("Client closed connection")
            break

class NameServer:
    receiving_socket = socket(AF_INET, SOCK_STREAM)
    client_conns = list()

    def __init__(self, port):
        try:
            self.receiving_socket.bind((HOST, port))
        except socket.error as er:
            print(str(er))
        self.receiving_socket.listen(2)

    def accept_client_conn(self):
        clientSocket, addr = self.receiving_socket.accept()
        self.client_conns.append(clientSocket)
        print("Accepted connection from client with addr: " + str(addr))
        # thread.start_new_thread(recv_from_client, (clientSocket, addr))
        thread = Thread(target=recv_from_client, args=(clientSocket, addr))
        thread.start()

    def __del__(self):
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for sock in self.client_conns:
            sock.close()

def main():
    nameServer = NameServer(NAMESERVER_PORT)
    while True:
        nameServer.accept_client_conn()


if __name__ == "__main__":
    main()

