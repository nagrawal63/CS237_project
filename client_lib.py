#!/usr/bin/python3
from multiprocessing import Process, Queue, Pipe
from socket import socket, AF_INET, SOCK_STREAM
import random
import string
import json

import definitions as df

SERVER_IP = "127.0.0.1"
MAX_MSG_SIZE = 2048

class Client:
    nameserver_socket = socket(AF_INET, SOCK_STREAM)
    fileserver_socket = socket(AF_INET, SOCK_STREAM)
    uuid = str()

    def __init__(self, nameserver_port, fileserver_port):
        self.uuid = ''.join(random.choices(string.ascii_letters, k=10))
        try:
            self.nameserver_socket.connect((SERVER_IP, nameserver_port))
        except socket.error as er:
            print("Error while connecting to nameserver socket: " + str(er))
        
        #send out own uuid for nameserver's records
        self.nameserver_socket.send(self.uuid)

        # try:
        #     self.fileserver_socket.connect((SERVER_IP, fileserver_port))
        # except socket.error as er:
        #     print("Error while connecting to fileserver socket: " + str(er))

    def __del__(self):
        #Close the sockets opened ith the servers before closing
        self.nameserver_socket.close()
        self.fileserver_socket.close()

    def request_nameserver_for_blocks(self, filename, size):
        msg = {"msg_type": str(df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_N), "uuid": self.uuid, "filename": filename, "file_size": str(size)}

        #Request the nameserver for partitions for the file
        self.nameserver_socket.send(json.dumps(msg).encode('utf-8'))

        #Get list of partitions and cloud type to send the partition to
        partitions_data = self.nameserver_socket.recv(MAX_MSG_SIZE)

        try: 
            partitions_data = json.loads(partitions_data)
        except json.JSONDecodeError as er:
            print("Error decoding partition data received from nameserver: " + str(er))

        return partitions_data


    def read(self, filename):
        #Read a file given a filename
        print("Reading...")
        self.nameserver_socket.send(filename.encode('utf-8'))
        print("Done reading")

    def delete(self, filename):
        #Delete an existing file
        print("Asdc")

    def write(self, file):
        #Write to an existing file
        print("asdc")
        partition_data = self.request_nameserver_for_blocks(file)

        filePtr = open(file, 'rb')

        fileserver_msg = {}
        fileserver_msg["msg_type"] = str(df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_F)
        fileserver_msg["uuid"] = self.uuid
        fileContentArray = []
        for partition in partition_data["partitions"]:
            tmp = {}
            tmp["primary_storage_loc"] = partition["primary_storage_loc"]
            tmp["secondary_storage_loc"] = partition["secondary_storage_loc"]
            tmp["file_path"] = self.uuid + "/" + file + "/" + partition["block_num"]\
                + partition["partition_uuid"]

            fileContent = filePtr.read(partition["block_end"] - partition["block_start"] + 1)
            tmp["file_content"] = fileContent

            fileContentArray.append(tmp)

        fileserver_msg["file"] = fileContentArray

        #Send file contents to fileserver to be uploaded to the cloud
        self.fileserver_socket.send(json.dumps(fileserver_msg).encode('utf-8'))
        
        #wait for some response from the fileserver
        response_from_fileserver = self.fileserver_socket.recv(MAX_MSG_SIZE)

        return response_from_fileserver
