import socket
from dotenv import load_dotenv
import os
from scapy.all import *
from scapy.layers.inet import IP, TCP

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))



def main():
    # Create a socket to listen for incoming connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((SERVER_IP, SERVER_PORT))
        sock.listen()

        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

        # Accept client connection
        conn, addr = sock.accept()
        with conn:
            print(f"Connected by {addr}")

            while True:
                # Receive data from the client
                data = conn.recv(65535)
                if not data:
                    break

                # Extract destination IP and packet data
                destination_ip, packet_data = data.split(b' ', 1)

                # Decapsulate and re-encapsulate the packet
                packet = IP(packet_data)
                packet.src = SERVER_IP
                packet.dst = destination_ip.decode()

                # Send the packet using scapy
                send(packet)

                # Send the modified packet back to the client
                conn.sendall(bytes(packet))


if __name__ == "__main__":
    main()
