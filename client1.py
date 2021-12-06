import socket
from tqdm import tqdm
import math
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from fernet import Fernet
import pickle
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 49157  # Reserve a port for your service.


def decrypt(filename, key):
    print("Decrypting...")
    f = Fernet(key)
    with open(filename, "rb") as fr:
        # read the encrypted data
        encrypted_data = fr.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    # write the original file
    with open(filename, "wb") as fl:
        fl.write(decrypted_data)

    print("Finished")
    sys.exit()
    
    
try:
    s.connect((host, 49151))
    print(s.recv(1024).decode("ascii"))
    msg=input()
    s.send(msg.encode("ascii"))
    msg1=s.recv(1024).decode("ascii")
    
    if(msg1 == "False"):
        print("Password is incorrect !! Try again later")
    else:
        print("Connection established successfully with server!!...")
        def sendData(file):
            s.send(file)
            
        print("\nWhat do you want from the server")
        Answer = input("1.Download File\n2.Upload File\nEnter an option:")
            
        if Answer == "1":
            
            mssg = "download"
            s.send(mssg.encode())
            data=s.recv(1024)
            print(pickle.loads(data))
            FileName = input("Enter Filename to Download from server : ")
            Data = "Temp"
            # flag=False
            
            s.send(FileName.encode())
            SEPARATOR="|"
            details = s.recv(1024).decode('ascii')
            file_n, file_s, file_size = details.split(SEPARATOR)
            file_s = int(file_s)
            file_size = int(file_size)
    
            with open("t_" + file_n, "wb") as fw:
                byte_read = s.recv(file_s)
                fw.write(byte_read)

            keys = open("t_key.key", "rb").read()
            with open(FileName, "wb") as f:
                while True:
               # read 1024 bytes from the socket (receive)
                   bytes_read = s.recv(1024)
                   if not bytes_read:
                       print("\nFile recieved sent for decrypting.....")
                       s.close()
                       f.close()
                       decrypt(FileName, keys)
                       break
                   f.write(bytes_read)
                f.close()
            
        elif Answer == "2":
            mssg = "upload"
            s.send(mssg.encode())
            print(os.listdir("./"))
            FileName = input("Enter Filename to Upload On server : ")
            s.send(FileName.encode())
            # flag=False
            
            while True:
                no = int(s.recv(1024).decode())
                print(no, " Bytes is to be sent.")
                res = input("Enter 'OK' if okay else enter 'NO':")
                s.send(res.encode())
                resp = s.recv(1024)
                if resp.decode() == "OK":
                    break
            
            dataList = []
            UploadFile = open("./" + FileName, "rb")
            Read = UploadFile.read()
            x = math.ceil(sys.getsizeof(Read) / (no-10))
            
            ones, twos, threes, fours = "", "", "", ""
            deli = 0
            if x < 100:
                ones = str(0)
                twos = ""
                deli = 5
                s.send("5".encode())
            elif x < 1000:
                ones = str(00)
                twos = str(0)
                threes = ""
                deli = 6
                s.send("6".encode())
            elif x < 10000:
                ones = str(000)
                twos = str(00)
                threes = str(0)
                fours = ""
                deli = 7
                s.send("7".encode())
            
            UploadFile = open("./" + FileName, "rb")
            Read = UploadFile.read(no-deli)
            i = 1
            while Read:
                string = ""
                if i < 10:
                    string = ones + "%d&/-" % i
                elif 10 <= i < 100:
                    string = twos + "%d&/-" % i
                elif 100 <= i < 1000:
                    string = threes + "%d&/-" % i
                elif 1000 <= i < 10000:
                    string = fours + "%d&/-" % i
                by = bytes(string, 'utf-8')
                dataList.append(by + Read)
                Read = UploadFile.read(no-deli)
                i += 1
                break
            
            executor = ThreadPoolExecutor(5)
            print("Sending...")
            tqdm(executor.map(sendData, dataList))
            sleep(2)
            print("Done Sending")
            UploadFile.close()
        s.close()

    
except Exception as e:
    print("\nSomething's wrong with %s:%d. Exception is %s" % (host, 49159, e))



