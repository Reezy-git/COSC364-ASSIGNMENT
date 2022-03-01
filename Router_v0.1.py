"""A basic router for RIP implementation
todo: define destination class
todo: implement Server class to listen and act as a router
todo: implement config reader"""


import socket
import select
import threading  # Probably won't be used
import sys


def server(host_name, port):
    SERVER = host_name, port
    # SERVER= socket.gethostbyname(socket.gethostname()), 5000

    open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    open_socket.bind(SERVER)
    print("waiting on port:", SERVER[1])

    while True:
        data, addr = open_socket.recvfrom(1024)
        print(data.decode('utf-8'))


class Destination:
    """
    Route description database for destination on network
    todo: complete init, write distance algorithm
    """

    def __init__(self, address, router, interface, metric, time):
        self.address = address  # the address/ID of the destination.
        self.router = router  # address of next hop to reach destination
        self.metric = metric  # integer indicating distance
        self.time = time  # time since last communication, needs to count to 180seconds then timeout as unreachable


def main():
    """I run the show around here!
    todo: implement send/recv via udp and select"""
