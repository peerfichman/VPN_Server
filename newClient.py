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
        self.totp = pyotp.TOTP('base32secret3232')
        self.cipher = Fernet(encryption_key.encode())

        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.cleint_socket.bind((host_name, int(client_port)))
        self.cleint_socket.listen(10)  # become a server socket

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((host_name, int(server_port)))
        token = self.totp.now()
        print("token", token)
        token = bytes(token, encoding='utf-8')
        print("token_encoded", token)
        encrypted_token = self.cipher.encrypt(token)
        print("token_encrypted", encrypted_token)

        self.server_socket.send(encrypted_token)
        

    def run(self):
        self.server_socket.settimeout(2)
        while True:
            # print("Ready to serve...")
            (clientSocket, client_address) = self.cleint_socket.accept()
            print(clientSocket, client_address)
            print("wait for browser")
            request = clientSocket.recv(self.max_request_len)
            print("request", request)
            print("sending request to server")
            try:
                request = self.cipher.encrypt(request)
                self.server_socket.send(request)
                while 1:
                    print("waiting for server response")
                    data = self.server_socket.recv(self.max_request_len)
                    data = self.cipher.decrypt(data)

                    if (len(data) > 0):
                        print("data received from server:", data)
                        clientSocket.send(data)
                        print("data sent to browser")
                    else:
                        break
            except socket.error as e:
                print("Socket error", e)


    # def __init__(self, config):
    #     # Create a TCP socket
    #     self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     # Re-use the socket
    #     self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     # bind the socket to a public host, and a port
    #     self.cleint_socket.bind((config['HOST_NAME'], config['CLIENT_PORT']))
    #     self.cleint_socket.listen(10)  # become a server socket
    #
    # def send_packet(self, data):
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_socket.connect((config['HOST_NAME'], config['SERVER_PORT']))
    #     print("sending")
    #     server_socket.sendall(data)
    #     # Receive response
    #     print("sent, now receiving...")
    #     server_socket.settimeout(5.0)
    #     response = server_socket.recv(4096)
    #     print("received")
    #     server_socket.close()
    #     return response
    #
    # def run(self):
    #     while True:
    #         # Establish the connection
    #         print("Ready to serve...")
    #         (clientSocket, client_address) = self.cleint_socket.accept()
    #         print(clientSocket, client_address)
    #         clientSocket.settimeout(5.0)
    #         request = clientSocket.recv(config['MAX_REQUEST_LEN'])
    #         print("request", request)
    #
    #         try:
    #             # self.server_socket.connect((config['HOST_NAME'], config['SERVER_PORT']))
    #             # self.server_socket.sendall(request)
    #             #while 1:
    #                 # receive data from web server
    #                 # data = self.server_socket.recv(config['MAX_REQUEST_LEN'])
    #             data = self.send_packet(request)
    #                 # if (len(data) > 0):
    #             print("data received from server:", data)
    #             clientSocket.send(data)  # send to browser/client
    #                 # else:
    #                 #     break
    #         except socket.error  as e:
    #             print("Socket error", e)
    #         except socket.timeout as e:
    #             print("Socket timeout error", e)




x = MySocket()

x.run()
