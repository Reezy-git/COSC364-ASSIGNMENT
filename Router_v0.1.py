"""A basic router for RIP implementation
todo: define destination class
todo: implement Server class to listen and act as a router
todo: implement config reader"""


import socket
import select
import threading  # Probably won't be used
import sys


class Server:
    def __init__(self, address, port):
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket to receive
        host = address, port
        self.receiver.bind(host)
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send

    def fileno(self):  # required for select
        return self.receiver.fileno()

    def on_read(self):  # the method for receiving a message
        """todo: process message into something useful i.e. receive new address data"""
        message = self.receiver.recv(1024).decode('utf-8')
        print(message)


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
    server = Server('localhost', 5010)

    while True:
        readers, _, _ = select.select([server], [], [])  # select takes 3 lists as input we only need first one
        for reader in readers:
            reader.on_read()

#test push