#!/usr/bin/python3
import client_lib as cl
import definitions as df

def main():
    client = cl.Client(df.NAMESERVER_PORT, df.FILESERVER_PORT)
    # client.read("dummy")
    client.write("tmp.txt")

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