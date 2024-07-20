import socket
from dotenv import load_dotenv
import os
from scapy.all import *
from scapy.layers.inet import IP, TCP, Ether

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))


def decapsulate_packet(packet):
    # Decapsulate the original packet to get the necessary layers
    original_ip = packet[IP]
    original_tcp = packet[TCP]
 # Test connectivity with an ICMP packet
    # Define the IP layer
    ip_layer = IP(
        src=SERVER_IP,  # Source IP
        dst="148.66.138.145",  # Destination IP
        ttl=128,  # Time to live
        id=18441,  # Identification
        flags="DF"  # Don't Fragment
    )

    # Define the TCP layer
    tcp_layer = TCP(
        sport=SERVER_PORT,  # Source port
        dport=80,  # Destination port
        seq=3362635848,  # Sequence number
        flags="S",  # SYN flag
        window=64240,  # Window size
        dataofs=8  # Data offset
    )
    
    http_payload = "GET / HTTP/1.1\r\nHost: 148.66.138.145\r\nConnection: close\r\n\r\n"

    # Combine the layers into a single packet
    packet = ip_layer / tcp_layer / http_payload
    packet.show()
    # Send the packet
    response = sr1(packet)

    if response:
        print("ICMP test packet received response:")
        response.show()
    else:
        print("ICMP test packet received no response")

    return response


def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    return server_socket


def forward_packet(packet):
    """Forward a packet using Scapy and return the response."""

    # Change the source IP address to the VPN server's IP
    response = decapsulate_packet(packet)
    
    # Send the packet and wait for a response
    # ans, unans = sr(new_packet, iface='enp0s3')
    # print("ans", ans)
    # print("unans", unans)
    # return ans if len(ans) > 0 else b""
    
    # Send the packet
    # response = sr1(new_packet)
    # if response:
    #     print("packet received response:")
    #     response.show()
    # else:
    #     print("packet received no response")

    return response if response else b""


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")

    try:
        # Receive data from client
        data = client_socket.recv(4096)
        print(f"Received raw data: {data}")

        # Convert raw data to a Scapy IP packet
        packet = Ether(data)
        print("Constructed Scapy packet from raw data:")
        packet.show()

        # Forward the packet using Scapy and get the response
        response = forward_packet(packet)
        print(f"Sent Response packets: {response}")

        # Send the response back to the client
        [client_socket.sendall(res[1].build()) for res in response]
        # client_socket.sendall(response)

    except Exception as e:
        print(f"Error handling client: {e}, {e.with_traceback()}")
    finally:
        client_socket.close()


def main():
    server_socket = create_server_socket()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    # Test connectivity with an ICMP packet
    # Define the IP layer
    ip_layer = IP(
        src=SERVER_IP,  # Source IP
        dst="148.66.138.145",  # Destination IP
        ttl=128,  # Time to live
        id=18441,  # Identification
        flags="DF"  # Don't Fragment
    )

    # Define the TCP layer
    tcp_layer = TCP(
        sport=SERVER_PORT,  # Source port
        dport=80,  # Destination port
        seq=3362635848,  # Sequence number
        flags="S",  # SYN flag
        window=64240,  # Window size
        dataofs=8  # Data offset
    )
    http_payload = "GET / HTTP/1.1\r\nHost: 148.66.138.145\r\nConnection: close\r\n\r\n"

    # Combine the layers into a single packet
    packet = ip_layer / tcp_layer / http_payload
    packet.show()
    # Send the packet
    # response = sr1(packet)

    # if response:
    #     print("ICMP test packet received response:")
    #     response.show()
    # else:
    #     print("ICMP test packet received no response")

    while True:
        client_socket, addr = server_socket.accept()
        print("here")
        handle_client(client_socket, addr)


if __name__ == "__main__":
    main()
