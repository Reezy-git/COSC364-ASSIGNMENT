"""
  Client.py: client for testing
  How to use: run in command line with arguments PORT, ROUTER_ID, TYPE, MESSAGE
  e.g. python3 Client.py 1112 1 1 'Your message here'
           this will send a message to router 1 via injection port 1112 requesting router1 to print message (type 1)
  if MESSAGE == 1 it will send the example forwarding table dictionary below
  if ID = 0 any router will accept the message
  type 0 = update f_table
  type 1 = standard message (will print)
  type 2 = output f_table
  type 3 = turn the router on/off

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges (11139316)
 - Chrystel Claire Quirimit (63369627)

"""

import json
import socket
import sys

open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = 'localhost', int(sys.argv[1])


def pkt_build(dst, typ, body):
    """ Creates the correctly formatted packet to send between routers """
    bin_dst = bin(int(dst))[2:].zfill(6)  # first 6 digits represent destination = 64 possible routers
    bin_type = bin(int(typ))[2:].zfill(2)  # 2 digits for type = 4 possible transmissions
    bin_body = bin(int((json.dumps(body).encode('utf8')).hex(), 16))[2:]
    return bin_dst + bin_type + bin_body


def pkt_unravel(msg):
    """ Packet gets to be unravelled return each formatted part of the packet"""
    dst = str(int(msg[:6], 2))
    typ = str(int(msg[6:8], 2))
    body = json.loads(bytes.fromhex(hex(int(msg[8:], 2))[2:]))
    return dst, typ, body


def create_message(f_table):
    if sys.argv[4] == '1':
        msg = f_table
    else:
        msg = sys.argv[4]
    return msg


example_forwarding_table = {2: (3332, 1), 7: (7771, 8), 6: (6661, 5)}
message = create_message(example_forwarding_table)
message = pkt_build(sys.argv[2], sys.argv[3], message).encode('utf8')
open_socket.sendto(message, host)