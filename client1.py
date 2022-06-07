#!/usr/bin/python3
import client_lib as cl
import definitions as df

def main():
    client = cl.Client(df.NAMESERVER_PORT, df.FILESERVER_PORT)
    client.write("tmp2.txt")
    file_content = client.read("tmp2.txt")
    print(file_content)

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
                file_content = client.read(user_cmd[1])
                print(file_content)
            elif user_cmd[0] == "write":
                file_content = client.write(user_cmd[1])
                print(file_content)
            elif user_cmd[0] == "delete":
                client.delete(user_cmd[1])

if __name__ == "__main__":
    main()