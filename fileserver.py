from socket import socket, AF_INET, SOCK_STREAM
import thread

HOST = "127.0.0.1"
MAX_CLIENTS = 10

def recv_from_client(clientSocket, addr):
    print("As")

class FileServer:
    receiving_socket = socket(AF_INET, SOCK_STREAM)
    client_conns = list()

    def __init__(self, port):
        try:
            self.receiving_socket.bind((HOST, port))
        except socket.error as er:
            print(str(er))
        self.receiving_socket.listen(MAX_CLIENTS)

    def accept_client_conn(self):
        clientSocket, addr = self.receiving_socket.accept()
        self.client_conns.append(clientSocket)
        thread.start_new_thread(recv_from_client, (clientSocket, addr))

    def __del__(self):
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for sock in self.client_conns:
            sock.close()

def main():
    fileServer = FileServer(1000)
    while True:
        fileServer.accept_client_conn()


if __name__ == "__main__":
    main()

