import socket
from Crypto.Cipher import AES
import base64
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode('raw_unicode_escape').decode('unicode_escape').encode(
    "raw_unicode_escape")
SERVER_IP = '10.0.2.15'
SERVER_PORT = 9999


def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(100)
    return server_socket


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    # Receive encrypted data from client
    nonce = client_socket.recv(16)
    encrypted_data = client_socket.recv(4096)
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt(encrypted_data)
    print(f"Received from Clien: {decrypted_data}")
    # Forward the decrypted data
    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # forward_socket.connect(("destination_server_ip", 80))  # Forward to actual destination -- remove quate
    # forward_socket.sendall(decrypted_data) --  rmove quate

    # Receive response and send back to client
    # response_data = forward_socket.recv(4096) --remove quate
    # encrypted_response = cipher.encrypt(response_data) #-- remove quate
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    encrypted_response = cipher.encrypt(b'hello back')  # remove line
    client_socket.sendall(cipher.nonce + encrypted_response)
    forward_socket.close()
    client_socket.close()


def main():
    server_socket = create_server_socket()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        handle_client(client_socket, addr)


if __name__ == "__main__":
    main()
