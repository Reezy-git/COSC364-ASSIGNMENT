
"""A basic router for RIP implementation
todo: Router: write __str__ to print f_table, write broadcasting function
todo: Main: implement config reader and use to create server and router objects"""


import socket
import select
import threading
import sys
import json
import config

class Ticker:
    """Ticks every duration"""
    def __init__(self, duration, owner):
        self.thread = None
        self.duration = duration
        self.owner = owner

    def loop(self):
        self.owner.on_tick()  # the true action
        self.thread = threading.Timer(self.duration, self.loop)  # sets a timer with function to call self.on_tick
        self.thread.start()  # starts that timer

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
        self.owner.recv_msg(message, self.port)

class Router:
    def __init__(self, router_id):
        self.router_id = router_id
        self.links = []
        self.f_table = {self.router_id: (0, 0)}  # forwarding table
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send
        self.active = True

    def __str__(self, table):
        """Prints out the forwarding table """
        max_cost = 16
        table_format = "=" * 18
        table_format += " RIPv2 Routing Table of " + str(self.router_id) + " "
        table_format += "=" * 18 + "\n"
        table_format += f"{'Router Id':<15}{'Port':>6}{'Cost':>20}"
        table_format += "\n" + "=" * 62 + "\n"
        for key, value in sorted(table.items()):
            port, cost = value
            if cost >= max_cost:
                table_format += "{:<12}{:>9}{:>20} \n".format(key, port, '*')
            else:
                table_format += "{:<12}{:>9}{:>20} \n".format(key, port, cost)
        return table_format

    def add_link(self, link):
        self.links.append(link)  # link = (input, output, cost, time since update)

    def toggle_activity(self):
        """Turns router on/off and resets the f_table"""
        self.active = not self.active
        self.f_table = {self.router_id: (0, 0)}
    # check if active and then process_msg


    def recv_msg(self, msg, port):
        """If we are active send the message to process message if not check for activity toggle packet"""
        if self.active:  # if router is active, process message as normal
            self.process_msg(msg, port)
        else:  # if router is not active check to see if packet type is activity toggle and turn back on if so.
            if int(msg[6:8], 2) == 3:
                self.toggle_activity()

    def broadcast(self):
        """Sends out the forwarding information we have to our neighbors"""
        for link in self.links:
            target = self.network_id, link[1]
            msg = self.pkt_build(0, 0, self.f_table)
            self.sender.sendto(msg.encode('utf8'), target)


    def process_msg(self, msg, port):
        try:
            if str(int(msg[:6], 2)) == self.router_id or str(int(msg[:6], 2)) == '0':
                msg_dst, typ, body = self.pkt_unravel(msg)
                # Request Type 0: Updating Forward Table
                if typ == 0:
                    print('Update forwarding table with', body)
                    self.update_f_table(body, self.get_link(port))
                # Request 1: Receive periodic update
                if typ == 1:
                    print('Router', self.router_id, 'received message', body)
                # Request 2: Show Forwarding table
                if typ == 2:
                    print(self.__str__(self.f_table))
                # Request Type 3: Turn On/Off activity of router
                if typ == 3:
                    self.toggle_activity()
            else:
                msg_dst = str(int(msg[:6], 2))
                print('Router', self.router_id, 'received message to forward to router', msg_dst)
                if self.f_table.__contains__(msg_dst):
                    target = 'localhost', self.f_table[msg_dst][0]
                    self.sender.sendto(msg.encode('utf8'), target)
        except ValueError:
            print('Incorrect message format received at Router ID:', self.router_id)

    def get_link(self, port):
        for link in self.links:
            if link[0] == port:
                return link
        print('[ERROR]: Link not found')

    def update_f_table(self, new_info, link):
        link[3] = 0  # update ticks since last message
        base_cost = link[2]  # Get the cost of the link.
        for dest in new_info:
            if dest in self.f_table:  # See if we have info on the router.
                current_best = self.f_table[dest][1]
                new_potential_cost = new_info[dest][1] + base_cost
                if current_best > new_potential_cost:  # If this is a better route we change our table entries.
                    self.f_table[dest] = (link[1], new_potential_cost)  # output port, new cost
            else:
                cost = new_info[dest][1] + base_cost
                self.f_table[dest] = (link[1], cost)  # We didn't have a route to here. So we just take any route info.

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

    def on_tick(self):
        """responsible for periodic updates"""
        self.broadcast()
        for link in self.links:
            link[3] += 1
            if link[3] >= 6:
                self.kill_link(link)

    def kill_link(self, link):
        for dest in self.f_table:
            if self.f_table[dest][0] == link[1]:
                self.f_table[dest] = (link[1], 16)


def setup():
    servers = []  # create a list to hold servers
    routers = []  # create a list
    tickers = []
    i = 0
    network_id = 'localhost'
    for router in test_routers:
        routers.append(Router(router, network_id))
        for link in test_routers[router]:
            link.append(0)
            servers.append(Server(network_id, int(link[0]), routers[i]))
            routers[i].add_link(link)
        tickers.append(Ticker(3, routers[i]))
        i += 1
    return servers, tickers

def main():
    """I run the show around here!"""
    servers = []  # create a list to hold servers
    routers = []  # create a list
    i = 0

    # Config reader to take the dictionary of the router file
    router_file = sys.argv[1]
    router_id, inputs, outputs = config.read_router_file(router_file)
    config_file = config.Main(router_id, inputs, outputs)
    router_parse = config_file.parse_routing_dictionary(router_file)

    for router in router_parse:
        routers.append(Router(router))
        route = Router(router)
        for link in router_parse[router]:
            servers.append(Server('localhost', int(link[0]), routers[i]))
            routers[i].add_link(link)
        i += 1

    while True:
        readers, _, _ = select.select(servers, [], [])  # select takes 3 lists as input we only need first one
        for reader in readers:
            reader.on_read()


main()
