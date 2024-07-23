import os
import socket
import pyotp
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv("./.env")

class MySocket:
    max_request_len = int(os.getenv('MAX_REQUEST_LEN'))
    
    def __init__(self):
        encryption_key = os.getenv('FERNET_KEY')
        host_name = os.getenv('HOST_NAME')
        server_port = int(os.getenv('SERVER_PORT'))
        client_port = int(os.getenv('CLIENT_PORT'))
        totp_key = os.getenv('TOTP_KEY')
        self.totp = pyotp.TOTP(totp_key)
        self.cipher = Fernet(encryption_key.encode())

        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.cleint_socket.bind((host_name, int(client_port)))
        self.cleint_socket.listen(10)  # become a server socket

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((host_name, int(server_port)))

        token = self.totp.now()
        token = bytes(token, encoding='utf-8')
        encrypted_token = self.cipher.encrypt(token)
        self.server_socket.send(encrypted_token)
        

    def run(self):
        self.server_socket.settimeout(8)
        while True:
            print("new connection from browser")
            (clientSocket, client_address) = self.cleint_socket.accept()
            print(clientSocket, client_address)

            request = clientSocket.recv(self.max_request_len)
            if (len(request) > 0):
                request = self.cipher.encrypt(request)
                print("sending request to server")
            else:
                continue
            try:
                self.server_socket.send(request)
                while 1:
                    print("waiting for server response")
                    data = self.server_socket.recv(self.max_request_len)

                    if (len(data) > 0):
                        data = self.cipher.decrypt(data)
                        clientSocket.send(data)
                        print("data sent to browser")
                    else:
                        break
            except socket.error as e:
                print("Socket error", e)


x = MySocket()

x.run()
