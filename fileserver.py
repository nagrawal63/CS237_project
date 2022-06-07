from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import json
import definitions as df
import cloud_lib as cloud

from azure.storage.blob import BlockBlobService, PublicAccess

MAX_CLIENTS = int(10)

def do_client_cleanup(client_socket, client_conns, addr):
    client_socket.close()
    del client_conns[addr]

def recv_from_client(clientSocket, addr, client_conns):
    #Receive the first set of 10 bytes from the client which contains
    #the client's uuid
    client_uuid = clientSocket.recv(df.MAX_MSG_SIZE).decode('utf-8')
    print("[Fileserver] Received uuid of client is: " + client_uuid)
    if len(client_uuid) != 10:
        print("[FileServer] Error in client uuid, terminating connection, reconnect plis")
        del client_conns[addr]
        clientSocket.close()
        return
    else:
        client_conns[addr]["client_uuid"] = client_uuid

    while True:
        msg = clientSocket.recv(df.MAX_MSG_SIZE).decode('utf-8')
        
        # A close socket message received from client
        if(len(msg) == 0):
            do_client_cleanup(clientSocket, client_conns, addr)
            print("[FileServer] Client closed connection")
            break
        else:
            # print("[Fileserver] message received: " + msg)
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
            elif msg_type == df.MSG_TYPES.REQUEST_FILE_UPLOAD_C_2_F:
                for file_partition in msg_json["file"]:
                    print("Primary cloud: " + file_partition["primary_storage_loc"])
                    print("Secondary clud: "+ file_partition["secondary_storage_loc"])
                    cloud.upload_file(file_partition["primary_storage_loc"], \
                        file_partition["file_path"], file_partition["file_content"])
                    cloud.upload_file(file_partition["secondary_storage_loc"], \
                        file_partition["file_path"], file_partition["file_content"])

                respond_to_client_msg = {}
                respond_to_client_msg["msg_type"] = df.MSG_TYPES.REPLY_FILE_UPLOAD_F_2_C
                respond_to_client_msg["uuid"] = msg_json["uuid"]
                respond_to_client_msg["ACK"] = "ACK"

                #send reply to client
                clientSocket.send(json.dumps(respond_to_client_msg).encode('utf-8'))
            else:
                print("[FileServer] Invalid message type, ignoring request")
class FileServer:
    receiving_socket = socket(AF_INET, SOCK_STREAM)
    client_conns = {}

    def __init__(self, port):
        try:
            self.receiving_socket.bind((df.HOST, port))
        except socket.error as er:
            print(str(er))
        self.receiving_socket.listen(MAX_CLIENTS)

    def accept_client_conn(self):
        clientSocket, addr = self.receiving_socket.accept()
        print(str(addr))
        self.client_conns[addr] = {"socket": clientSocket}
        thread = Thread(target=recv_from_client, args=(clientSocket, addr, self.client_conns))
        thread.start()

    def __del__(self):
        #Close receiving socket for new connections
        self.receiving_socket.close()
        #Close all client sockets before destroying the Nameserver object
        for client_addr in self.client_conns.keys():
            self.client_conns[client_addr]["socket"].close()
            del self.client_conns[client_addr]

def main():
     # Create the BlockBlobService that is used to call the Blob service for the storage account
    cloud.azure_blob_service_client = BlockBlobService(
        account_name='cs237version1azure', account_key='71c5QApXXLqW0Q4dqPm8BVYrf2fR3R35aqMNcejMoUBMnx/mkIq/PNq+tgaIoz+1lzQoZF5aFZDFTSSX5B4eCA==')

    # # Create a container called 'quickstartblobs'.
    # cloud.azure_container_name = 'cs237version1'
    # cloud.azure_blob_service_client.create_container(cloud.azure_container_name)

    # # Set the permission so the blobs are public.
    # cloud.azure_blob_service_client.set_container_acl(
    #     cloud.azure_container_name, public_access=PublicAccess.Container)

    fileServer = FileServer(df.FILESERVER_PORT)
    while True:
        fileServer.accept_client_conn()


if __name__ == "__main__":
    main()

