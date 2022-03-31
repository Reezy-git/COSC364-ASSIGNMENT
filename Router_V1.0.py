
"""A basic router for RIP implementation
todo: Router: define f_table(forwarding table), write __str__ to print f_table, write recv_msg
todo: Main: implement config reader and use to create server and router objects"""


import socket
import select
import threading  # Probably won't be used
import sys
import json


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
        self.f_table = {self.router_id: (0, 0)}  # forwarding table
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send
        self.active = True

    def add_link(self, link):
        self.links.append(link)  # link = (input, output, cost)

    def toggle_activity(self):
        """Turns router on/off and resets the f_table"""
        self.active = not self.active
        self.f_table = {self.router_id: (0, 0)}

    def recv_msg(self, msg, port):
        if self.active:  # if router is active, process message as normal
            self.process_msg(msg, port)
        else:  # if router is not active check to see if packet type is activity toggle and turn back on if so.
            if int(msg[6:8], 2) == 3:
                self.toggle_activity()

    def process_msg(self, msg, port):
        try:
            if str(int(msg[:6], 2)) == self.router_id or str(int(msg[:6], 2)) == '0':
                print(str(int(msg[:6], 2)))
                msg_dst, typ, body = self.pkt_unravel(msg)
                if typ == 0:
                    print('Update f_table with', body)
                    self.update_f_table(body, self.get_link(port))
                if typ == 1:
                    print('Router', self.router_id, 'received message', body)
                if typ == 2:
                    print(self.f_table)
                if typ == 3:
                    self.toggle_activity()
            else:
                msg_dst = str(int(msg[:6], 2))
                print('Router', self.router_id, 'received message to forward to router', msg_dst)
                # if self.f_table.__contains__(msg_dst):
                #     self.sender.sendto(msg, self.f_table[msg_dst][0])
        except ValueError:
            print('Incorrect message format received at Router ID:', self.router_id)

    def get_link(self, port):
        for link in self.links:
            if link[0] == port:
                return link
        print('link not found')

    def update_f_table(self, new_info, link):
        """todo: write me"""
        base_cost = link[2]
        for dest in new_info:
            if dest in self.f_table:
                current_best = self.f_table[dest][1]
                new_potential_cost = new_info[dest][1] + base_cost
                if current_best > new_potential_cost:
                    self.f_table[dest] = (link[1], new_potential_cost)
            else:
                cost = new_info[dest][1] + base_cost
                self.f_table[dest] = (link[1], cost)

    @staticmethod
    def pkt_build(dst, typ, body):
        """Creates the correctly formatted packet to send between routers"""
        bin_dst = bin(int(dst))[2:].zfill(6)  # first 6 digits represent destin
        bin_type = bin(int(typ))[2:].zfill(2)  # 2 digits for type = 4 possible types
        bin_body = bin(int((json.dumps(body).encode('utf8')).hex(), 16))[2:]
        return bin_dst + bin_type + bin_body

    @staticmethod
    def pkt_unravel(msg):
        dst = str(int(msg[:6], 2))
        typ = int(msg[6:8], 2)
        body = json.loads(bytes.fromhex(hex(int(msg[8:], 2))[2:]))
        return dst, typ, body


test_routers = {'1': [(5000, 5001, 8), (5011, 41241, 8)]}  # dictionary format {id: [(input, output, cost), (link2))]}


def main():
    """I run the show around here!"""
    servers = []  # create a list to hold servers
    routers = []  # create a list
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
