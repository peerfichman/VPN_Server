import socket
from Crypto.Cipher import AES
from dotenv import load_dotenv
import os
from scapy.all import IP

load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode('raw_unicode_escape').decode('unicode_escape').encode(
    "raw_unicode_escape")
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))


def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(100)
    return server_socket


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    try:
        # Receive encrypted data from client
        nonce = client_socket.recv(16)
        tag = client_socket.recv(16)
        encrypted_data = client_socket.recv(4096)

        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)

        print(f"Received from Client: {decrypted_data}")

        # Extract destination IP address and port using scapy
        ip_packet = IP(decrypted_data)
        destination_ip = ip_packet.dst
        destination_port = ip_packet.dport
        print(f"Extracted Destination IP: {destination_ip} and Port: {destination_port}")

        # Forward the decrypted data
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward_socket.settimeout(10)  # Set a timeout for the connection
        forward_socket.connect((destination_ip, destination_port))
        forward_socket.sendall(decrypted_data)

        # Receive response and send back to client
        response_data = forward_socket.recv(4096)
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
        encrypted_response, tag = cipher.encrypt_and_digest(response_data)
        client_socket.sendall(cipher.nonce + tag + encrypted_response)

        forward_socket.close()

    except socket.timeout:
        print(f"Connection to {destination_ip}:{destination_port} timed out.")
    except Exception as e:
        print(f"An error occurred: {e}")
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
