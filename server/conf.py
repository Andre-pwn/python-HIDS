import socket
import tqdm
import os
import pickle
import csv
import hashlib
import schedule
import time

from rbt import *

# Token to make a MAC, we should hide this in some way?

TOKEN = "28rh28hr84f48fn3498fn3984fn34f98n34f3inf"

# Modified
# Now this makes a csv to be sent to the client, this csv contains:
# hash_file, hash(hash_file + TOKEN), hash provided was ok?, this file is new for previous file system?

def scan(rbt):
    with open('tuple.csv') as filecsv:
        lines = filecsv.readlines()

    # Make new csv
    with open('response.csv', 'a') as filecsv:
        # Clear csv
        open('response.csv', 'w+')
        writer = csv.writer(filecsv, delimiter=',')

        for line in lines:
            if line != "\n":
                path_hash = line.split(",")
                
                if len(path_hash)!=2:
                    raise Exception("Invalid CSV format - a tuple of elements is required")
                else:
                    is_ok, is_new, hash_from_search = rbt.search_and_validation((path_hash[0],path_hash[1]),actual_node=rbt.root)
                    hash_from_search = hash_from_search[:-1]
                    print(hash_from_search)
                    # Make the hash and add data to csv
                    h = hashlib.sha256()
                    h.update(hash_from_search.encode())
                    h.update(TOKEN.encode())
                    writer.writerow([path_hash[1][:-1]] + [h.hexdigest()] + [is_ok] + [is_new])

def hash_file(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha256()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

def connection(SERVER_HOST,SERVER_PORT,BUFFER_SIZE,SEPARATOR):
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    client_socket, address = s.accept() 
    print(f"[+] {address} is connected.")

    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    filesize = int(filesize)

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))
    client_socket.close()
    s.close()

def initializate_data():
    with open('tuple.csv') as fp:
        lines = fp.readlines()

    rbt = RedBlackTree()

    for line in lines:
        print(line)

    for line in lines:
        if line != "\n":
            path_hash = line.split(",")
            if len(path_hash)!=2:
                raise Exception("Bad format of csv")
            else:
                rbt.insert((path_hash[0],path_hash[1]))

    # Serialize

    with open('RBTbyteStream', 'wb') as f:
        pickle.dump(rbt,f)

def generate_response():

    # Deserialize

    with open('RBTbyteStream', 'rb') as f:
        t = pickle.load(f)

    # Maybe we can delete this
    a = deepcopy(t)

    scan(t)

    # Serialize again
    with open('RBTbyteStream', 'wb') as f:
        pickle.dump(a,f)

def connect_and_response():
    connection(SERVER_HOST,SERVER_PORT,BUFFER_SIZE,SEPARATOR)
    generate_response()
    send_reply(CLIENT_IP,CLIENT_PORT)
    print("Entering in waiting mode...")
    print("Another connection will be enstablished in 24 hours...")

def send_reply(CLIENT_IP,CLIENT_PORT):
    filename = "response.csv"
    filesize = os.path.getsize(filename)
    s = socket.socket()
    print(f"[+] Opening connection with the client")
    print(f"[+] Connecting to {CLIENT_IP}:{CLIENT_PORT}")
    s.connect((CLIENT_IP, CLIENT_PORT))
    print("[+] Connected.")
    s.send(f"{filename}{SEPARATOR}{filesize}".encode('utf-8'))
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
    s.close()

def __init__ ():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 22222
    BUFFER_SIZE = 4096 # receive 4096 bytes each time
    SEPARATOR = "<SEPARATOR>"
    connection(SERVER_HOST,SERVER_PORT,BUFFER_SIZE,SEPARATOR)
    print("[*] The first connection has been enstablished")
    print("[*] Initializing data...")
    initializate_data()
    print("[*] Sending the reply back")
    generate_response()
    send_reply(CLIENT_IP,CLIENT_PORT)


#default settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 22222
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 22221

__init__()

schedule.every(9).seconds.do(connect_and_response)

while(1):
    schedule.run_pending()
    time.sleep(1)
