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


    # Change the source IP address to the VPN server's IP
    packet[IP].src = SERVER_IP

    # Ensure IP and TCP checksums are calculated
    del packet[IP].chksum
    if packet.haslayer(TCP):
        del packet[TCP].chksum

    # Optionally adjust TTL
    packet[IP].ttl = 128

    print("Forwarding packet:")
    packet.show()
    # Send the packet and wait for a response
    response = sr1(packet, timeout=10)
    return bytes(response) if response else b""

def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    try:
        # Receive data from client
        data = client_socket.recv(4096)
        print(f"Received raw data: {data}")

        # Convert raw data to a Scapy IP packet
        packet = IP(data)
        print("Constructed Scapy packet from raw data:")
        packet.show()

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
    test_ip = "148.66.138.145"
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
