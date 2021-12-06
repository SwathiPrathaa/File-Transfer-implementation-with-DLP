import socket
import threading
import os
import re
import tqdm
from time import sleep
import pickle
from fernet import Fernet
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def encrypt(filename, filename_encrpt, keys):
     f = Fernet(keys)
     with open(filename, "rb") as file:
         # read all file data
         file_data = file.read()
     # encrypt data
     encrypted_data = f.encrypt(file_data)
     # write the encrypted file
     with open(filename_encrpt, "wb") as file:
         file.write(encrypted_data)
         
class ThreadedServer():
    
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 49151
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # the SO_REUSEADDR flag tells the kernel to
        self.s.bind((self.host, self.port))  # reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.


    def listen(self):
        self.s.listen(5)  #max 5 client connections r allowed
        while True:
            c, addr = self.s.accept()
            c.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(c, addr)).start()     
    a=1
    def listenToClient(self, c, addr):
        print('\nServer> Client Requested :', addr)
        c.send("\nEnter the password :".encode("ascii"))
        pswd=c.recv(1024).decode('ascii')
        if pswd != "pswrd123":
                print("Server> Password entered by the client is incorrect!!")
                c.send("False".encode("ascii"))
                
        else:
                print("Password is correct !! Connection established with the client")
                c.send("True".encode("ascii"))
            
                list1=[]
                data = c.recv(1024)
            
                if data.decode() == "download":
                    FileFound = 0   
            
                    print(os.listdir("./"))  # Shows all the files at server side
                    list1=os.listdir("./")
                    data=pickle.dumps(list1)
                    c.send(data)
                    
                    FileName = c.recv(1024)
                    print("\nServer> Client wants to download :",FileName)
                    print("Server> Checking the list of files ...")
                    for file in os.listdir("./"):
                        
                        if file == FileName.decode():
                            
                            FileFound = 1
                            break
            
                    if FileFound == 0:
                        print("Server> File Not Found in the Server!!")
            
                    else:
                        print("Server> File Found in the Server!!")
                        file_name = FileName.decode()
                        upfile = FileName.decode()
                        file_size = os.path.getsize(upfile)
                        SEPARATOR="|"
                        gen_key = Fernet.generate_key()
                
                        with open("key.key", "wb") as key_file:
                            key_file.write(gen_key)
                    
                        file_name1 = "key.key"
                        file_size1 = os.path.getsize(file_name1)
                
                        c.send(f"{file_name1}{SEPARATOR}{file_size1}{SEPARATOR}{file_size}".encode('ascii'))
                        with open(file_name1, "rb") as f: ##sending the key file
                            bytes_read = f.read()

                            if bytes_read:
                                c.sendall(bytes_read)
                        f.close()
                        key = open("key.key", "rb").read()
                
                        file_name_encrypt = "encrypt_" + file_name
                        print("Encrypting and sending!!!")
                        print("Please wait for few seconds.")
                        size = os.path.getsize('key.key')
                        encrypt(file_name, file_name_encrypt, key)
                        progress = tqdm.tqdm(range(file_size), f"Sending {upfile}", unit="B", unit_scale=True,
                                      unit_divisor=1024)
                        UploadFile = open("./" + file_name_encrypt, "rb")##
                        for _ in progress:
                    
                            Read = UploadFile.read(1024)
                            while Read:
                        
                                c.send(Read)      # sends 1KB
                                Read = UploadFile.read(1024)
                           # update the progress bar
                        
                            progress.update(len(Read))
                    
                    
                        print("\nServer> File Sent Successfully!!")
                        UploadFile.close()
                        c.close()
         
                
                elif data.decode() == "upload":
                            FileName = c.recv(1024)
                            
                            print("Server> Client wants to upload :",FileName)
                            downfile = FileName.decode()
                
                            while True:
                                no = input("Server> Enter the number of bytes to be sent: ")
                                c.send(no.encode())
                                res = c.recv(1024)
                                if res.decode() == "OK":
                                    c.send("OK".encode())
                                    break
                                c.send("NO".encode())
                
                            deli = int(c.recv(1024))
                
                            no = int(no)
                
                            DownloadFile = open(downfile, "wb")
                            Data = c.recv(no) 
                            i = 1
                            li = []
                            print("Server> Receiving File...")
                            while Data:
                                li.append(Data)
                                Data = c.recv(no)
                                i = i + 1
                
                            dict = {}
                            for i in li:
                                try:
                                    x = re.match(b"(.*)&/-(.*)", i)
                                    id = int(x.group(1).decode(encoding="utf-8"))
                                    data = i[deli:]
                                    dict[id] = data
                                except:
                                    print(i, "Error")
                
                            keys = list(dict.keys())
                            keys.sort()
                
                            for k in keys:
                                DownloadFile.write(dict[k])
                
                            print("Server> File Received Successfully!!")
                            DownloadFile.close()
                            c.close()


if __name__ == "__main__":
    ThreadedServer().listen()
