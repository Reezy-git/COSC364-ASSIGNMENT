"""
 server_class.py: A bare-bones UDP socket server

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges ()
 - Chrystel Claire Quirimit (63369627)

"""

import socket

class Server:
    """ Creates a UDP socket. """
    def __init__(self, network_id, port, owner):
        self.network_id = network_id
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket to receive
        host = self.network_id, port
        self.port = port
        self.receiver.bind(host)
        self.owner = owner  # the router which owns this port

    def fileno(self):  # required for select
        return self.receiver.fileno()

    def on_read(self):  # the method for receiving a message
        message = self.receiver.recv(1024).decode('utf-8')
        self.owner.recv_msg(message, self.port)
