import socket
import pyotp
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv("./.env")
 
class MySocket:
    max_request_len = int(os.getenv('MAX_REQUEST_LEN'))

    def __init__(self):
        encryption_key = os.getenv('FERNET_KEY')
        host_name = os.getenv('HOST_NAME')
        server_port = int(os.getenv('SERVER_PORT'))
        totp_key = os.getenv('TOTP_KEY')
        
        self.totp = pyotp.TOTP(totp_key)        
        self.cipher = Fernet(encryption_key)

        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cleint_socket.bind((host_name, server_port))
        self.cleint_socket.listen(10)

    def run(self):
        # Establish the connection
        print("Ready to serve...")
        (clientSocket, client_address) = self.cleint_socket.accept()
        print(clientSocket, client_address)

        verify_totp = clientSocket.recv(1024)
        print("before decryption", verify_totp)
        decrypted_data = self.cipher.decrypt(verify_totp)
        print("before decoding", decrypted_data)
        decoded_data = decrypted_data.decode('utf-8')
        print("verify_totp", decrypted_data.decode('utf-8'))

        if (not self.totp.verify(decoded_data)):
            print("Invalid TOTP")
            clientSocket.close()
            return
            
        while True:
            request = clientSocket.recv(self.max_request_len) 
            if len(request) == 0:
                continue

            print("request_before_decription", request)
            request = self.cipher.decrypt(request)
            print("request", request)
            

            # parse the first line
            first_line = request.split(b'\n')[0]
            # print("first_line", first_line)

            # get url
            url = first_line.split(b' ')[1]
            # print("url", url)

            http_pos = url.find(b"://") # find pos of ://
            # print("http_pos", http_pos)
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):] # get the rest of url
            # print("temp", temp)

            port_pos = temp.find(b":") # find the port pos (if any)
            # print("port_pos", port_pos)

            # find end of web server
            webserver_pos = temp.find(b"/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos < port_pos): 

                # default port 
                port = 80 
                webserver = temp[:webserver_pos] 

            else: # specific port 
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos] 
            
            print("Connect to:", webserver, port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            try:
                s.connect((webserver, port))
                s.sendall(request)
                while 1:
                    # receive data from web server
                    data = s.recv(self.max_request_len)
                    print("data", data)
                    data_encrypted = self.cipher.encrypt(data)
                    print("data_encrypted", data_encrypted)
                    clientSocket.send(data_encrypted) # send to browser/client
                    if (len(data) > 0):
                        print("data sent")
                    else:
                        print("no data")
                        break
            except socket.error as e:
                print("Socket error", e)


x = MySocket()

x.run()