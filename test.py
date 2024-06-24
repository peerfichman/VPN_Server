import socket
from Cryptodome.Cipher import AES
from dotenv import load_dotenv
import os

load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode('raw_unicode_escape').decode('unicode_escape').encode(
    "raw_unicode_escape")
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))


def create_client_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    return client_socket


def send_request(client_socket, request_data):
    # Encrypt the request data
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    encrypted_data, tag = cipher.encrypt_and_digest(request_data)

    # Send nonce, tag, and encrypted data to the server
    client_socket.sendall(nonce)
    client_socket.sendall(tag)
    client_socket.sendall(encrypted_data)

    # Receive response from server
    nonce = client_socket.recv(16)
    tag = client_socket.recv(16)
    encrypted_response = client_socket.recv(4096)

    # Decrypt the response data
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted_response = cipher.decrypt_and_verify(encrypted_response, tag)

    return decrypted_response


def main():
    client_socket = create_client_socket()
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

    # Create a mock request data (example: HTTP GET request to example.com)
    mock_request = b'E\x00\x00<\x00\x00\x40\x00\x40\x06\x00\x00\xc0\xa8\x01\x19\x5d\xb8\xd8\x22\x00\x50\xd1\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x50\x02\x20\x00\x72\x10\x00\x00'

    try:
        response = send_request(client_socket, mock_request)
        print(f"Response from server: {response.decode()}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
