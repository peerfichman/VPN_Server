import os
import socket
from dotenv import load_dotenv
import pydivert
from scapy.all import IP, TCP, Raw
import psutil

load_dotenv()

# Configuration
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))



def send_packet(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    client_socket.sendall(data.tobytes())

    # Receive response
    response = client_socket.recv(4096)
    client_socket.close()

    return response


def main():

    # Send the mock packet
    # response = send_packet(mock_data)
    # print(f"Client received response: {response}")
    # with pydivert.WinDivert("tcp.DstPort == 80 or tcp.DstPort == 443") as w:
    with pydivert.WinDivert("ip.DstAddr == 148.66.138.145") as w:
        for packet in w:
            data = packet.raw
            interface = packet.interface
            response = send_packet(data)
            print(response)
            new_packet = pydivert.Packet(raw=response, direction=pydivert.Direction.INBOUND, interface=interface)
            w.send(new_packet)


if __name__ == "__main__":
    main()
