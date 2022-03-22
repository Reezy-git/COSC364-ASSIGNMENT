"""A basic router for RIP implementation
todo: Router: define f_table(forwarding table), write __str__ to print f_table, write recv_msg
todo: Main: implement config reader and use to create server and router objects"""


import socket
import select
import threading  # Probably won't be used
import sys

# import config file
import config

class Server:
    def __init__(self, address, port, owner):
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket to receive
        host = 'localhost', port
        self.port = port
        self.receiver.bind(host)
        self.owner = owner  # the router which owns this port

    def fileno(self):  # required for select
        return self.receiver.fileno()

    def on_read(self):  # the method for receiving a message
        message = self.receiver.recv(1024).decode('utf-8')
        print('Send to ', self.owner)
        self.owner.recv_msg(message, self.port)


class Router:
    def __init__(self, router_id):
        self.router_id = router_id
        self.links = []
        self.f_table = {1: (5000, 8), 2: (5001, 2)}  # forwarding table
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send

    def add_link(self, link):
        self.links.append(link)

    def __str__(self):
        # Your routing table prints here

    def recv_msg(self, msg, port):
        msg_dst = msg[0:8]
        print('Data received: ', msg, port, self.router_id)
        if msg_dst == self.router_id:
            print('Message received at router', self.router_id)
        else:
            if self.f_table.__contains__(msg_dst):
                self.sender.sendto(msg, self.f_table[msg_dst][0])

    def update_f_table(self, new_info):
        """todo: write me"""


# router_info ={'1': [[1112, 1116, 1117], [2221, 7777, 6666]],
#               '2': [[2221, 2223], [1112, 2223]],
#               '3': [[3332, 3334], [2223, 4443]],
#               '4': [[4443, 4445, 4447], [7774, 3334, 5554]],
#               '5': [[5554, 5556], [4445, 6665]],
#               '6':[[6661, 6665], [1116, 5556]],
#               '7': [[7771, 7774], [1117, 4447]]}

test_routers = {'1': [(5000, 5001, 8)],
                '2': [(5001, 5000, 8)]}  # dictionary format {id: [(input, output, cost), (link2))]}

def main():
    """I run the show around here!"""
    try:
        if len(sys.argv) < 2:
            sys.exit()

        with open(sys.argv[1]) as router_file:
            config_file = Config()
            config_file.read_router_file(router_file)

            pass

    servers = []
    routers = []
    i = 0
    for router in test_routers:
        routers.append(Router(router))
        for link in test_routers[router]:
            servers.append(Server('localhost', int(link[0]), routers[i]))
            routers[i].add_link(link)
        i += 1

    while True:
        readers, _, _ = select.select(servers, [], [])  # select takes 3 lists as input we only need first one
        for reader in readers:
            reader.on_read()

main()
