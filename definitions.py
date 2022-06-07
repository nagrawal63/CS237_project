
from enum import IntEnum

NAMESERVER_PORT = int(10001)
FILESERVER_PORT = int(10003)
HOST = "127.0.0.1"
MAX_MSG_SIZE = int(4096)

class MSG_TYPES(IntEnum):
    REQUEST_FILE_UPLOAD_C_2_N   = 1
    REPLY_FILE_UPLOAD_N_2_C     = 2
    REQUEST_FILE_UPLOAD_C_2_F   = 3
    REPLY_FILE_UPLOAD_F_2_C     = 4

    #While reading files, the client directly talks to cloud and not through file server
    REQUEST_FILE_DOWNLOAD_C_2_N = 5
    REPLY_FILE_DOWNLOAD_N_2_C   = 6
    
    REQUEST_FILE_DELETE_C_2_N   = 9
    REPLY_FILE_DELETE_N_2_C     = 10
    REQUEST_FILE_DELETE_C_2_F   = 11
    REPLY_FILE_DELETE_F_2_C     = 12
