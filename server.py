#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 prashant <prashant@prashant>
#
# Distributed under terms of the MIT license.


# Adapted:
# https://github.com/montag451/pytun/blob/master/test/test_tun.py and
# https://github.com/sergeybratus/netfluke/blob/master/tcp.py

import sys
import optparse
import socket
import select
import errno
import pytun
import utils
from scapy.all import IP, UDP, Raw


def swap_src_and_dst(pkt, layer):
    pkt[layer].dst, pkt[layer].src = pkt[layer].src, pkt[layer].dst


class TunnelServer(object):

    def __init__(self, taddr, tdstaddr, tmask, tmtu, laddr, lport):

        self._tun = pytun.TunTapDevice("eran", flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self._tun.addr = taddr
        self._tun.dstaddr = tdstaddr
        self._tun.netmask = tmask
        self._tun.mtu = tmtu
        self._tun.up()
        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        self._sock.bind(("enp0s3", 0))

    def run(self):
        mtu = self._tun.mtu
        r = [self._tun, self._sock];
        w = [];
        x = []
        send_info = ''
        recv_packet = ''
        send_packet = ''

        while True:
            r, w, x = select.select(r, w, x)

            if self._tun in r:
                print('tun read triggered')
                send_packet = self._tun.read(mtu)
                print('read' + str(send_packet) + 'from tunnel')

            if self._sock in r:
                recv_packet, addr = self._sock.recvfrom(65535)
                print("recived packet", recv_packet)
                auth = utils.recv_auth(self._sock, addr, recv_packet)
                print("auth value:", auth)
                exists = utils.check_if_addr_exists(addr)
                print("exists:", exists)
                print("adress existst:", addr)
                #if exists != None:
                    # first get client address
                clientIP = IP(recv_packet)
                print("clientIP:", clientIP)
                    # authorization packet
                    # if auth == True:
                    #     print("auth true")
                    #     if clientIP:
                    #         print("In CLient IP and IP src:", clientIP.src)
                    #         # get message queue and send one by one
                    #         recv_packets = utils.get_messages_for_client(clientIP.src)
                    #         print("recived packet for client:", recv_packet)
                    #         if recv_packets != None and (addr[0] != utils.SERVER_UDP_IP):
                    #             for send_pkt in recv_packets:
                    #                 self._sock.sendto(send_pkt, addr)
                    #             utils.clear_messages(addr)
                    #         recv_packet = ''
                    #         recv_packets = ''
                    # else:
                utils.receive_non_auth_message(recv_packet)
                if clientIP:
                    print('sender: ' + str(clientIP.src) + ' receiver: ' + str(clientIP.dst))
                    # add to queue for client
                    utils.message_for_client(clientIP.dst, recv_packet)
                    recv_packets = utils.get_messages_for_client(clientIP.dst)
                    print('recv packets - ' + str(recv_packets))
                    if recv_packets != None and str(clientIP.dst) != '10.10.0.1':
                        for send_pkt in recv_packets:
                            dest = utils.get_public_ip(clientIP.dst)
                            self._sock.sendto(send_pkt, dest)
                        utils.clear_messages(addr)
                    if str(clientIP.dst) != '10.10.0.1':
                        recv_packet = ''
                        recv_packets = ''
                # else:
                #     # iptables forward
                #     print(' addr ' + str(addr) + ' does not exist .. iptables will forward the data:' + str(recv_packet) + 'if it could')
                #     raddr = addr[0]
                #     rport = addr[1]
                #     # aesobj = amitcrypto.AESCipher(key)
                #     # self._sock.sendto(aesobj.encrypt(data),(raddr,rport))
                #     self._sock.sendto(recv_packet, (raddr, rport))

            if self._tun in w:
                print('no encryption yet, writing to tunnel')
                # Encryption ?
                print("writing packet to tunne:", recv_packet)
                self._tun.write(str(recv_packet))
                recv_packet = ''

            if self._sock in w:
                ip_pkt = IP(send_packet)
                print(ip_pkt)
                # send_addr = utils.get_public_ip(ip_pkt.dst)
                send_addr = ("10.0.2.15", 5050)
                self._sock.sendto(send_packet, send_addr)
                send_packet = ''

            r = [];
            w = []

            if recv_packet:
                print('tun appended to w')
                w.append(self._tun)
            else:
                r.append(self._sock)

            if send_packet:
                w.append(self._sock)
            else:
                print('appending self._tun to r')
                r.append(self._tun)


def main():
    tun_mtu = 1500

    ptp_addr = "10.10.0.1"
    ptp_dst = "10.10.0.1"
    ptp_mask = "255.255.255.0"
    sock_addr = "10.0.2.15"
    sock_port = 5050

    server = TunnelServer(ptp_addr, ptp_dst, ptp_mask, tun_mtu,
                          sock_addr, sock_port)
    server.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())