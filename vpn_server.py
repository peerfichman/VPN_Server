import socket
from Crypto.Cipher import AES
from dotenv import load_dotenv
import os
from scapy.all import *


load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode('raw_unicode_escape').decode('unicode_escape').encode(
    "raw_unicode_escape")
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))


def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    return server_socket


def forward_packet(packet):
    """Forward a packet using Scapy."""
    send(packet)


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    try:
        # Receive nonce and encrypted data from client
        nonce = client_socket.recv(16)
        encrypted_data = client_socket.recv(4096)

        # Decrypt data
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
        decrypted_data = cipher.decrypt(encrypted_data)

        print(f"Received data: {decrypted_data}")

        # Convert decrypted data to a Scapy packet
        packet = IP(decrypted_data)

        # Forward the packet using Scapy
        forward_packet(packet)

        # Prepare the response
        response_message = b'hello back'
        response_cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
        encrypted_response = response_cipher.encrypt(response_message)

        # Send nonce and encrypted response
        client_socket.sendall(response_cipher.nonce + encrypted_response)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def main():
    server_socket = create_server_socket()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        handle_client(client_socket, addr)


if __name__ == "__main__":
    main()