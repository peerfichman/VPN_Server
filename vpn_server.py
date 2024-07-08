import socket
from dotenv import load_dotenv
import os
from scapy.all import *

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))

def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    return server_socket

def forward_packet(packet):
    """Forward a packet using Scapy and return the response."""
    response = sr1(packet, timeout=30)
    return bytes(response) if response else b""

def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    try:
        # Receive data from client
        data = client_socket.recv(4096)
        print(f"Received data: {data}")

        # Convert raw data to a Scapy IP packet
        packet = IP(data)

        # Forward the packet using Scapy and get the response
        response = forward_packet(packet)
        print(f"Sent Response: {response}")

        # Send the response back to the client
        client_socket.sendall(response)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def main():
    server_socket = create_server_socket()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    # Test connectivity with an ICMP packet
    test_ip = "8.8.8.8"
    icmp_packet = IP(dst=test_ip)/ICMP()
    response = sr1(icmp_packet, timeout=30)
    if response:
        print("ICMP test packet received response:")
        response.show()
    else:
        print("ICMP test packet received no response")

    while True:
        client_socket, addr = server_socket.accept()
        handle_client(client_socket, addr)

if __name__ == "__main__":
    main()
