import os
import socket
from Cryptodome.Cipher import AES
from dotenv import load_dotenv
import pydivert

load_dotenv()

# Configuration
SERVER_IP = '127.0.0.1'
SERVER_PORT = 1194
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')


def send_encrypted_packet(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    encrypted_data, tag = cipher.encrypt_and_digest(data)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    client_socket.sendall(cipher.nonce + tag + encrypted_data)

    # Receive encrypted response
    encrypted_response = client_socket.recv(4096)
    nonce, tag, encrypted_message = encrypted_response[:16], encrypted_response[16:32], encrypted_response[32:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted_response = cipher.decrypt_and_verify(encrypted_message, tag)

    client_socket.close()
    return decrypted_response


def main():
    with pydivert.WinDivert() as w:
        for packet in w:
            data = packet.raw
            decrypted_response = send_encrypted_packet(data)
            packet.raw = decrypted_response
            w.send(packet)


if __name__ == "__main__":
    main()
