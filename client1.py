#!/usr/bin/python3
import client_lib as cl

NAMESERVER_PORT = int(10001)
FILESERVER_PORT = int(10002)

def main():
    client = cl.Client(NAMESERVER_PORT, FILESERVER_PORT)
    client.read("dummy")

    while True:
        # Sample commands:
        #  - read <filename>
        #  - write <filename> 
        #  - delete <filename>
        user_cmd = input()
        user_cmd = user_cmd.split(" ")
        if len(user_cmd) != 2:
            print("Incorrect request, valid requests are:\n\t read/write/delete <filename>\n")
            continue
        else:
            if user_cmd[0] == "read":
                client.read(user_cmd[1])
            elif user_cmd[0] == "write":
                client.write(user_cmd[1])
            elif user_cmd[0] == "delete":
                client.delete(user_cmd[1])

if __name__ == "__main__":
    main()