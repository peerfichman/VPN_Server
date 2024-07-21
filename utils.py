from scapy.all import *


import time
import socket
import os
import hashlib

SERVER_UDP_PORT = 5050  # Random port
SERVER_UDP_IP = "10.0.2.5"  # prashant.at

users = {"10.10.0.2": hashlib.md5(b'pw1').digest(),
         "10.10.0.3": hashlib.md5(b'pw2').digest()}  # Keeps track of usernames and passwords. I know MD5 is bad!
addresses = {"10.0.2.5": (SERVER_UDP_IP, SERVER_UDP_PORT), "10.10.0.2": None,
             "10.10.0.3": None}  # Keeps track of current communicating person
messages = {"10.10.0.1": [], "10.10.0.2": [], "10.10.0.3": []}


# get a message for another client
def receive_non_auth_message(data):
    packet = IP(data)
    print(packet.summary())


# get client message queue object
def get_message_queue(addr):
    for k, v in messages.items():
        if k == addr:
            return k
    return None


# received a message for the client
def message_for_client(addr, message):
    address = get_message_queue(addr)

    if address != None:
        print('appending ' + str(message) + ' for ' + address)
        messages[address].append(message)


def get_messages_for_client(addr):
    address = get_message_queue(addr)
    if address != None:
        return messages[address]
    else:
        return None


def clear_messages(addr):
    print('public ip is ' + str(addr[0]))
    lan_addr = check_if_addr_exists(addr)
    print('clearing messages for ' + str(lan_addr))
    if lan_addr != None:
        messages[lan_addr] = []


# Server authenticates user
def validate_user(username, pw):
    if users[username] == pw:
        return True
    else:
        return False


# Client sends authentication message
def send_auth_packet(sock, username, pw):
    print("Client -> Server : Sending poll packet")
    message = "username:" + username + ":" + pw + ":" + str(time.time())

    # amitcrypto.enc(sock, message, (SERVER_UDP_IP, 5050))
    sock.sendto(message, (SERVER_UDP_IP, 5050))
    return


# Server receives message and decides if its an auth message
def recv_auth(sock, addr, encmessage):
    # xor = XOR.XORCipher(key)
    # message = xor.decrypt(encmessage)
    message = encmessage
    # message = amitcrypto.dec(sock, encmessage, addr)
    # print "Recv auth method entered"
    try:
        username = message.split(':')[1]
        pw = message.split(':')[2]
        # print username
        # print pw, len(pw)
        # print users[username], len(users[username])
        # print users[username] == pw
        if validate_user(username, pw):
            print("Valid poll received from " + username)
            print('pushing addr ' + str(addr) + ' for ' + username)
            addresses[username] = addr
            return True
        else:
            return False
    except:
        return False


# get public ip for user
def get_public_ip(addr):
    for k, v in addresses.items():
        if k == addr:
            return v
    return None



# Check if addr exists in dictionary
def check_if_addr_exists(addr):
    for k, v in addresses.items():
        # print 'value type : ' + str(type(v)) + 'value addr: '+ str(type(addr))
        # print 'address key '+str(k)+' public ip '+str(v) + 'addr ' + str(addr)
        if v != None and v[0] == addr[0] and v[1] == addr[1]:
            return k
    return None