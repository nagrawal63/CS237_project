#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM
import random
import string
import json
import time
import os
import definitions as df
from azure.storage.blob import BlockBlobService

import cloud_lib as cl

SERVER_IP = "127.0.0.1"

class Client:
    nameserver_socket = socket(AF_INET, SOCK_STREAM)
    fileserver_socket = socket(AF_INET, SOCK_STREAM)
    uuid = str()

    def __init__(self, nameserver_port, fileserver_port):
        cl.azure_blob_service_client = BlockBlobService(
            account_name='cs237version1azure', account_key='71c5QApXXLqW0Q4dqPm8BVYrf2fR3R35aqMNcejMoUBMnx/mkIq/PNq+tgaIoz+1lzQoZF5aFZDFTSSX5B4eCA==')
        
        # cloud.azure_container_name = 'cs237version1'
        # cloud.azure_blob_service_client.create_container(cloud.azure_container_name)
        self.uuid = ''.join(random.choices(string.ascii_letters, k=10))
        try:
            self.nameserver_socket.connect((SERVER_IP, nameserver_port))
        except socket.error as er:
            print("Error while connecting to nameserver socket: " + str(er))
        
        time.sleep(0.1)
        #send out own uuid for nameserver's records
        self.nameserver_socket.send(self.uuid.encode('utf-8'))

        try:
            self.fileserver_socket.connect((SERVER_IP, fileserver_port))
        except socket.error as er:
            print("Error while connecting to fileserver socket: " + str(er))

        time.sleep(0.1)

        #send out own uuid for fileserver's records
        self.fileserver_socket.send(self.uuid.encode('utf-8'))

    def __del__(self):
        #Close the sockets opened ith the servers before closing
        self.nameserver_socket.close()
        self.fileserver_socket.close()

    def __request_nameserver_for_new_blocks(self, filename, size):
        msg = {"msg_type": df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_N, "uuid": self.uuid, "filename": filename, "file_size": str(size)}

        #Request the nameserver for partitions for the file
        self.nameserver_socket.send(json.dumps(msg).encode('utf-8'))

        #Get list of partitions and cloud type to send the partition to
        partitions_data = self.nameserver_socket.recv(df.MAX_MSG_SIZE).decode('utf-8')
        # print("Partitions data: " + partitions_data)
        try: 
            partitions_data = json.loads(partitions_data)
        except json.JSONDecodeError as er:
            print("[Nameserver] Error decoding partition data received from nameserver: " + str(er))

        return partitions_data

    def __get_file_blocks_from_nameserver(self, filename):
        msg = {"msg_type": df.MSG_TYPES.REQUEST_FILE_DOWNLOAD_C_2_N, "uuid": self.uuid, "filename": filename}

        #Request nameserver for partitions of the file
        self.nameserver_socket.send(json.dumps(msg).encode('utf-8'))

        #Receive partitions data from the nameserver
        partitions_data = self.nameserver_socket.recv(df.MAX_MSG_SIZE).decode('utf-8')
        try:
            partitions_data = json.loads(partitions_data)
        except json.JSONDecodeError as er:
            print("[Nameserver] Error decoding file's partition data received from nameserver: " + str(er))
        return partitions_data

    def read(self, filename):
        #Read a file given a filename
        print("Reading...")
        file_partitions = self.__get_file_blocks_from_nameserver(filename)

        if file_partitions["have_access"] == 'N':
            print("You don't have access to " + filename)
            return
        else:
            num_partitions = len(file_partitions["partitions"])
            file_data = [None for _ in range(num_partitions)]
            # print("Number of partitions to read from: " + str(num_partitions))
            for partition in file_partitions["partitions"]:
                partition_content = cl.download_file_partition(partition["primary_storage_loc"], partition["file_path"])
                #COuld not get partition data from primary location,
                #try secondary location
                if partition_content == None:
                    partition_content = cl.download_file_partition(partition["secondary_storage_loc"], partition["file_path"])
                    if partition_content == None:
                        print("[Cloud_lib] Could not download file partition from the network, aborting")
                        return
                file_data[int(partition["block_num"]) - 1] = partition_content
            
            return ''.join(file_data)

    def update(self, filename):
        #update an existing file
        self.write(filename)

    def delete(self, filename):
        pass


    def write(self, file):
        #Write to an existing file
        filesize = os.path.getsize(file)
        partition_data = self.__request_nameserver_for_new_blocks(file, filesize)
        
        #File already exists, update the file
        if partition_data["msg_type"] == df.MSG_TYPES.REPLY_EXISTING_FILE_UPLOAD_N_2_C:
            for partition in partition_data["old_partitions"]:
                print(partition)
                file_path = self.uuid + "/" + file + "/" + partition["block_num"]\
                    + "/" + partition["partition_uuid"]
                cl.delete_file(partition["primary_storage_loc"], file_path)
                cl.delete_file(partition["secondary_storage_loc"], file_path)
                # partition_data = json.loads(self.nameserver_socket.recv(df.MAX_MSG_SIZE).decode('utf-8'))
            

        if len(partition_data["partitions"]) == 0:
            print("[Client_lib] No partition of file to upload, abort")
            return False

        fileserver_msg = {}
        fileserver_msg["msg_type"] = df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_F
        fileserver_msg["uuid"] = self.uuid
        fileContentArray = []

        with open(file, 'rb') as filePtr:
            for partition in partition_data["partitions"]:
                tmp = {}
                tmp["primary_storage_loc"] = partition["primary_storage_loc"]
                tmp["secondary_storage_loc"] = partition["secondary_storage_loc"]
                tmp["file_path"] = self.uuid + "/" + file + "/" + partition["block_num"]\
                    + "/" + partition["partition_uuid"]

                fileContent = filePtr.read(partition["block_end"] - partition["block_start"] + 1)
                tmp["file_content"] = fileContent.decode('utf-8')
                fileContentArray.append(tmp)

        fileserver_msg["file"] = fileContentArray

        #Send file contents to fileserver to be uploaded to the cloud
        self.fileserver_socket.send(json.dumps(fileserver_msg).encode('utf-8'))
        
        #wait for some response from the fileserver
        response_from_fileserver = json.loads(self.fileserver_socket.recv(df.MAX_MSG_SIZE))

        return True if response_from_fileserver["ACK"]=="ACK" else False
