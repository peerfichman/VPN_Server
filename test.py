import os
import socket
from Cryptodome.Cipher import AES
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode('raw_unicode_escape').decode('unicode_escape').encode("raw_unicode_escape")
# Configuration
SERVER_IP = '127.0.0.1'  # Replace with your server's IP address
SERVER_PORT = 9999


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # Prepare and send the encrypted "hello" message
    message = b'hello'
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    encrypted_message = cipher.encrypt(message)

    # Send nonce and encrypted message
    client_socket.sendall(nonce + encrypted_message)

    # Receive the encrypted response from the server
    nonce = client_socket.recv(16)
    encrypted_response = client_socket.recv(4096)

    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted_response = cipher.decrypt(encrypted_response)

    print(f"Received from server: {decrypted_response.decode('utf-8')}")

    client_socket.close()


if __name__ == "__main__":
    main()
