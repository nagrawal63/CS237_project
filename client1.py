#!/usr/bin/python3
import client_lib as cl

NAMESERVER_PORT = int(10001)
FILESERVER_PORT = int(10002)

def main():
    client = cl.Client(NAMESERVER_PORT, FILESERVER_PORT)
    client.read("dummy")

if __name__ == "__main__":
    main()