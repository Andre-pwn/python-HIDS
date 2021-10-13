import hashlib
import csv

TOKEN = "28rh28hr84f48fn3498fn3984fn34f98n34f3inf"

def client_validation():

    h = hashlib.sha256()
    # list of modified files
    mod = list()
    all_ok = True

    with open('response.csv','r') as file:
        server_read = csv.reader(file, delimiter=',')
        lines = file.readlines()
    with open('tuple.csv','r') as host_file:
        host_read = csv.reader(host_file)
        lines_host = host_file.readlines()
    with open('MAClog.txt', 'a') as f:
        i = 0
        for i in range(len(lines)):
            # Now we are on the response.csv
            if lines[i] != '\n':
                data = lines[i].split(",")
                if len(data)!=4:
                    raise Exception("Invalid CSV format - four elements is required")
                else:
                    original_hash, mac, its_ok, its_new = data[0], data[1], data[2], data[3][:-1]

                # Now we are on the tuple.csv
                if lines_host[i] != '\n':
                    data_host = lines_host[i].split(",")
                    if len(data_host) !=2: 
                        raise Exception("Invalid CSV format - a tuple of elements is required")
                    else:
                        path, host_original_hash = data_host[0], data_host[1][:-1]

                    h.update(host_original_hash.encode())
                    h.update(TOKEN.encode())
                    host_mac = h.hexdigest()

                    # Now is validation time
                    if host_original_hash != original_hash:
                        print("Some file is lost")

                    elif host_mac != mac:
                        print(path + " file has been modified, not the same mac")
                        f.write(path + " file has been modified, not the same mac   ---  at " + str(datetime.now(pytz.utc)) + '\n')
                        all_ok = False
                    elif its_ok != "True":
                        print(path + " file has been modified, server statement")
                        f.write(path + " file has been modified, server statement   ---  at " + str(datetime.now(pytz.utc)) + '\n')
                        all_ok = False
                    elif its_new == "True":
                        print(path + " is new on the file system, server statement")
                        f.write(path + " is new on the file system, server statement   ---  at " + str(datetime.now(pytz.utc)) + '\n')
                    else:
                        f.write(path + " is ok!!!   ---  at " + str(datetime.now(pytz.utc)) + '\n')
                        print(path + " it ok!!!")
                    h = hashlib.sha256()

    return all_ok




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
