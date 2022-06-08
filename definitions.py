
from enum import IntEnum

NAMESERVER_PORT = int(10008)
FILESERVER_PORT = int(10007)
HOST = "127.0.0.1"
MAX_MSG_SIZE = int(4096)

class MSG_TYPES(IntEnum):
    REQUEST_FILE_UPLOAD_C_2_N        = 1
    REPLY_FILE_UPLOAD_N_2_C          = 2
    REPLY_EXISTING_FILE_UPLOAD_N_2_C = 3
    REQUEST_FILE_UPLOAD_C_2_F        = 4
    REPLY_FILE_UPLOAD_F_2_C          = 5

    #While reading files, the client directly talks to cloud and not through file server
    REQUEST_FILE_DOWNLOAD_C_2_N      = 6
    REPLY_FILE_DOWNLOAD_N_2_C        = 7
    
    REQUEST_FILE_DELETE_C_2_N        = 8
    REPLY_FILE_DELETE_N_2_C          = 9
