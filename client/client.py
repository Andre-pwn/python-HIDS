import csv
import glob
import socket
import hashlib
import os
import tqdm
import schedule
import time
from MAC import client_validation

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

#append data into the csv file
def writing(path):
    with open('tuple.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for data in path:
            writer.writerow([data] + [hash_file(data)])

#clear the csv file or create if does not exist
def csvclear():
    f = open('tuple.csv', 'w+')
    
#recursive way to walk thrugh folders and scan files    
def walk_on_paths(path):
    file_paths = [i for i in (os.path.join(path, f) for f in os.listdir(path)) if os.path.isfile(i)]
    dir_paths = [i for i in (os.path.join(path, f) for f in os.listdir(path)) if os.path.isdir(i)]
    writing(file_paths)
    if dir_paths!=None:
        for next_path in dir_paths:
            walk_on_paths(next_path)

def rev_connection(CLIENT_HOST,CLIENT_PORT,BUFFER_SIZE,SEPARATOR):
    s = socket.socket()
    s.bind((CLIENT_HOST, CLIENT_PORT))
    s.listen(1)
    print(f"[*] Opening the connection for receiving the response...")
    print(f"[*] Listening as {CLIENT_HOST}:{CLIENT_PORT}")
    client_socket, address = s.accept() 
    print(f"[+] {address} is connected.")

    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
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

def file_definition():
    csvclear()
    path1="/etc/"
    #path1="/Users/M/Desktop/US/Cuarto/SSII/PAI1/pruebas/SSII/"
    walk_on_paths(path1)
    filesize = os.path.getsize(filename)

def server_connection():
    s = socket.socket()
    print(f"[+] Connecting to {SERVER_HOST}:{SERVER_PORT}")
    s.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")
    s.send(f"{filename}{SEPARATOR}{filesize}".encode('utf-8'))
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            # we use sendall to assure transimission in busy networks
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
    s.close()


def execution():
    file_definition()
    server_connection()
    rev_connection(CLIENT_HOST,CLIENT_PORT,BUFFER_SIZE,SEPARATOR)
    print(client_validation())

SERVER_HOST = '127.0.0.1'        
SERVER_PORT = 22222             
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
CLIENT_HOST = '127.0.0.1'        
CLIENT_PORT = 22221
filename = "tuple.csv" 
filesize = 0  

execution()
schedule.every(10).seconds.do(execution)

while(1):
    schedule.run_pending()
    time.sleep(1)