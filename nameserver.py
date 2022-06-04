#!/usr/bin/python3
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread
import json
import definitions as df
import math
import uuid
import random

HOST = "127.0.0.1"
MAX_CLIENTS = int(10)
MAX_MSG_SIZE = 2048
NAMESERVER_PORT = int(10001)
BLOCK_SIZE = 100
REPLICATION_FACTOR = 2

CLOUDS = ["aws", "gcp", "azure"]

def do_client_cleanup():
    pass



class NameServer:
    receiving_socket = socket(AF_INET, SOCK_STREAM)
    client_conns = {}
    file_table = {}

    def __init__(self, port):
        try:
            self.receiving_socket.bind((HOST, port))
        except socket.error as er:
            print(str(er))
        self.receiving_socket.listen(2)

    def accept_client_conn(self):
        clientSocket, addr = self.receiving_socket.accept()
        self.client_conns[addr] = {"socket": clientSocket}

        print("Accepted connection from client with addr: " + str(addr))
        # thread.start_new_thread(recv_from_client, (clientSocket, addr))
        thread = Thread(target=recv_from_client, args=(clientSocket, addr))
        thread.start()

    def __del__(self):
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for sock in self.client_conns:
            sock.close()
    
    def recv_from_client(self, clientSocket, addr):
        #Receive the first set of 10 bytes from the client which contains
        #the client's uuid
        client_uuid = clientSocket.recv(MAX_MSG_SIZE)
        if len(client_uuid) != 10:
            print("Error in client uuid, terminating connection, reconnect plis")
            del self.client_conns[addr]
            clientSocket.close()
            return
        else:
            self.file_table[client_uuid] = []
            self.client_conns[addr]["client_uuid"] = client_uuid

        while True:
            msg = clientSocket.recv(MAX_MSG_SIZE)
            
            # A close socket message received from client
            if(len(msg) == 0):
                do_client_cleanup()
                print("Client closed connection")
                break
            else:
                msg_json = json.loads(msg)
                msg_type = msg_json["msg_type"]
                if msg_type == df.MSG_TYPES.REQUEST_FILE_DELETE_C_2_N:
                    pass
                # elif msg_type == df.MSG_TYPES.REQUEST_FILE_DELETE_C_2_F:
                #     pass
                # elif msg_type == df.MSG_TYPES.REQUEST_FILE_DOWNLOAD_C_2_F:
                #     pass
                # elif msg_type == df.MSG_TYPES.REQUEST_FILE_DOWNLOAD_C_2_N:
                #     pass
                # elif msg_type == df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_F:
                #     pass
                elif msg_type == df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_N:
                    #Break file into partitions
                    partitions = self.partition_file(msg_json["file_size"], msg_json["filename"])

                    #construct reply message for client
                    msg = {}
                    msg["msg_type"] = str(df.MSG_TYPES.REPLY_FILE_UPLOAD_N_2_C)
                    msg["uuid"] = self.client_conns[addr]["client_uuid"]
                    msg["filename"] = msg_json["filename"]
                    msg["file_size"] = msg_json["file_size"]
                    msg["partitions"] = partitions

                    #send reply to client
                    clientSocket.send(msg)
                else:
                    print("Invalid message type, ignoring request")

    #Choose randomly for now
    def choose_clouds_for_partition(self, filename):
        return random.sample(CLOUDS, REPLICATION_FACTOR)
        
    def partition_file(self, filesize, filename, client_uuid):
        filesize = int(filesize)
        num_blocks = int(math.ceil(filesize/BLOCK_SIZE))
        file_partition_details = []
        start, end = 0, filesize
        for i in range(0, num_blocks):
            partition_dict = {}
            partition_uuid = uuid.uuid1()
            storage_locations_for_partition = self.choose_clouds_for_partition(filename)
            partition_dict["partition_uuid"] = partition_uuid
            partition_dict["block_num"] = str(i+1)
            partition_dict["block_start"] = start
            partition_dict["block_end"] = math.min(start + BLOCK_SIZE, end)
            partition_dict["primary_storage_loc"] = storage_locations_for_partition[0]
            partition_dict["secondary_storage_loc"] = storage_locations_for_partition[1]

            start += partition_dict["block_end"]
            file_partition_details.append(partition_dict)

        self.file_table[client_uuid]["filename"] = file_partition_details
        return file_partition_details

def main():
    nameServer = NameServer(NAMESERVER_PORT)
    while True:
        nameServer.accept_client_conn()


if __name__ == "__main__":
    main()

