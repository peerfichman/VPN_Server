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
        print("Ready to serve...")
        (clientSocket, client_address) = self.cleint_socket.accept()
        print(clientSocket, client_address)

        verify_totp = clientSocket.recv(1024)
        decrypted_data = self.cipher.decrypt(verify_totp)
        decoded_data = decrypted_data.decode('utf-8')

        if (not self.totp.verify(decoded_data)):
            print("Invalid TOTP")
            clientSocket.close()
            return
            
        while True:
            request = clientSocket.recv(self.max_request_len) 
            if len(request) == 0:
                continue

            request = self.cipher.decrypt(request)            

            first_line = request.split(b'\n')[0]
            
            url = first_line.split(b' ')[1]

            http_pos = url.find(b"://") 
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):] 

            port_pos = temp.find(b":") 
            
            webserver_pos = temp.find(b"/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos < port_pos): 
                port = 80 
                webserver = temp[:webserver_pos] 
            else: 
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos] 
            
            print("Connect to:", webserver, port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            try:
                s.connect((webserver, port))
                print("packet forwarded to web server")
                s.sendall(request)
                while 1:
                    data = s.recv(self.max_request_len)
                    if (len(data) > 0):
                        print("packet recieved from web server")
                        data_encrypted = self.cipher.encrypt(data)
                        clientSocket.send(data_encrypted)
                        print("data sent back to client")
                    else:
                        break
            except socket.error as e:
                print("Socket error", e)


x = MySocket()

x.run()