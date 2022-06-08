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

def do_client_cleanup(client_socket, client_conns, addr):
    client_socket.close()
    del client_conns[addr]

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
    file_json[filename] = file_partition_details
    file_table[client_uuid].append(file_json)
    return file_partition_details

def find_file_in_file_table(client_uuid, file_table, filename):
    if client_uuid not in file_table.keys():
        print("[Nameserver] Don't know client with the given uuid")
        return None
    
    for file_json in file_table[client_uuid]:
        if filename in file_json.keys():
            return file_json

    print("[Nameserver] Requested file not found at nameserver")
    return None

def get_file_partitions(client_uuid, filename, file_table):
    file_json = find_file_in_file_table(client_uuid, file_table, filename)
    if file_json == None:
        return file_json

    # partitions = file_json[filename]
    partitions = []
    for partition in file_json[filename]:
        file_partition = {}
        file_partition["file_path"] = client_uuid + "/" + filename + "/" + partition["block_num"] \
                                + "/" + partition["partition_uuid"]
        file_partition["block_num"] = partition["block_num"]
        file_partition["primary_storage_loc"] = partition["primary_storage_loc"]
        file_partition["secondary_storage_loc"] = partition["secondary_storage_loc"]
        file_partition["block_start"] = partition["block_start"]
        file_partition["block_end"] = partition["block_end"]
        partitions.append(file_partition)
    return partitions

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
            do_client_cleanup(clientSocket, client_conns, addr)
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
            elif msg_type == df.MSG_TYPES.REQUEST_FILE_DOWNLOAD_C_2_N:
                file_partitions = get_file_partitions(msg_json["uuid"], msg_json["filename"], file_table)
                msg = {"msg_type": df.MSG_TYPES.REPLY_FILE_DOWNLOAD_N_2_C}
                msg["uuid"] = client_conns[addr]["client_uuid"]
                msg["filename"] = msg_json["filename"]
                if file_partitions == None:
                    msg["have_access"] = "N"
                else:
                    msg["have_access"] = "Y"
                    msg["partitions"] = file_partitions
                
                # print("[Nameserver] Reply for request file download from nameserver")
                # print(json.dumps(msg))
                #Send reply to client
                clientSocket.send(json.dumps(msg).encode('utf-8'))

            elif msg_type == df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_N:
                #Check if file already present
                file_json = find_file_in_file_table(client_uuid, file_table, msg_json["filename"])
                if file_json != None:
                    #TODO: Change this to actually deleting and then updating the file

                    print("[Nameserver] File already present, doing nothing for now")
                    msg = {"msg_type": df.MSG_TYPES.REPLY_FILE_UPLOAD_N_2_C, "uuid": client_uuid}
                    msg["filename"] = msg_json["filename"]
                    msg["file_size"] = msg_json["file_size"]
                    msg["partitions"] = []
                    clientSocket.send(json.dumps(msg).encode('utf-8'))
                    continue

                #Break file into partitions
                partitions = partition_file(msg_json["file_size"], msg_json["filename"], client_uuid, file_table)

                #construct reply message for client
                msg = {}
                msg["msg_type"] = df.MSG_TYPES.REPLY_FILE_UPLOAD_N_2_C
                msg["uuid"] = client_uuid
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
        #Close receiving socket for new connections
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for client_addr in self.client_conns.keys():
            self.client_conns[client_addr]["socket"].close()
            del self.client_conns[client_addr]
        

def main():
    nameServer = NameServer(df.NAMESERVER_PORT)
    while True:
        nameServer.accept_client_conn()


if __name__ == "__main__":
    main()

