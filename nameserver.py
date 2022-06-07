#!/usr/bin/python3
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread
import json
import definitions as df
import math
import uuid
import random

MAX_CLIENTS = int(10)
BLOCK_SIZE = 100
REPLICATION_FACTOR = 2

CLOUDS = ["aws", "gcp", "azure"]

def do_client_cleanup(client_socket):
    client_socket.close()


#Choose randomly for now
def choose_clouds_for_partition(filename):
    return random.sample(CLOUDS, REPLICATION_FACTOR)

def partition_file(filesize, filename, client_uuid, file_table):
    filesize = int(filesize)
    num_blocks = int(math.ceil(filesize/BLOCK_SIZE))
    file_partition_details = []
    start, end = 0, filesize
    for i in range(0, num_blocks):
        partition_dict = {}
        partition_uuid = str(uuid.uuid1())
        storage_locations_for_partition = choose_clouds_for_partition(filename)
        partition_dict["partition_uuid"] = partition_uuid
        partition_dict["block_num"] = str(i+1)
        partition_dict["block_start"] = start
        partition_dict["block_end"] = min(start + BLOCK_SIZE - 1, end)
        partition_dict["primary_storage_loc"] = storage_locations_for_partition[0]
        partition_dict["secondary_storage_loc"] = storage_locations_for_partition[1]

        start = partition_dict["block_end"] + 1
        file_partition_details.append(partition_dict)
    file_json = {}
    file_json["filename"] = file_partition_details
    file_table[client_uuid].append(file_json)
    return file_partition_details

def recv_from_client(clientSocket, addr, client_conns, file_table):
    #Receive the first set of 10 bytes from the client which contains
    #the client's uuid
    client_uuid = clientSocket.recv(df.MAX_MSG_SIZE).decode('utf-8')
    print("[Nameserver] Received uuid of client is: " + client_uuid)
    if len(client_uuid) != 10:
        print("[NameServer] Error in client uuid, terminating connection, reconnect plis")
        del client_conns[addr]
        clientSocket.close()
        return
    else:
        file_table[client_uuid] = []
        client_conns[addr]["client_uuid"] = client_uuid

    while True:
        msg = clientSocket.recv(df.MAX_MSG_SIZE).decode('utf-8')
        print("[Nameserver] Received message is : " + msg)
        # A close socket message received from client
        if(len(msg) == 0):
            do_client_cleanup(clientSocket)
            print("[NameServer] Client closed connection")
            break
        else:
            try:
                msg_json = json.loads(msg)
            except json.JSONDecodeError as er:
                print("[Nameserver] Error decoding message from client at nameserver")
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
                partitions = partition_file(msg_json["file_size"], msg_json["filename"], client_uuid, file_table)

                #construct reply message for client
                msg = {}
                msg["msg_type"] = df.MSG_TYPES.REPLY_FILE_UPLOAD_N_2_C
                msg["uuid"] = client_conns[addr]["client_uuid"]
                msg["filename"] = msg_json["filename"]
                msg["file_size"] = msg_json["file_size"]
                msg["partitions"] = partitions

                #send reply to client
                clientSocket.send(json.dumps(msg).encode('utf-8'))
            else:
                print("[NameServer] Invalid message type, ignoring request")
class NameServer:
    receiving_socket = socket(AF_INET, SOCK_STREAM)
    client_conns = {}
    file_table = {}

    def __init__(self, port):
        try:
            self.receiving_socket.bind((df.HOST, port))
        except socket.error as er:
            print(str(er))
        self.receiving_socket.listen(2)

    def accept_client_conn(self):
        clientSocket, addr = self.receiving_socket.accept()
        self.client_conns[addr] = {"socket": clientSocket}

        print("[NameServer] Accepted connection from client with addr: " + str(addr))
        # thread.start_new_thread(recv_from_client, (clientSocket, addr))
        thread = Thread(target=recv_from_client, args=(clientSocket, addr, self.client_conns, self.file_table))
        thread.start()

    def __del__(self):
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for sock in self.client_conns:
            sock.close()
        

def main():
    nameServer = NameServer(df.NAMESERVER_PORT)
    while True:
        nameServer.accept_client_conn()


if __name__ == "__main__":
    main()

