import select
import socket


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


server = Server('localhost', 5010)


while True:
    readers, _, _ = select.select([server], [], [])  # select takes 3 lists as input we only need first one
    for reader in readers:
        reader.on_read()





