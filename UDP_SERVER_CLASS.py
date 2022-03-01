import select
import socket


class Server:
    def __init__(self, address, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = address, port
        self.s.bind(host)

    def fileno(self):  # required for select
        return self.s.fileno()

    def on_read(self):  # the method for receiving a message
        """todo: process message into something useful i.e. receive new address data"""
        message = self.s.recv(1024).decode('utf-8')
        print(message)


server = Server('localhost', 5010)


while True:
    readers, _, _ = select.select([server], [], [])  # select takes 3 lists as input we only need first one
    for reader in readers:
        reader.on_read()





