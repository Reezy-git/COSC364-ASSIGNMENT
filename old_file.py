
"""A basic router for RIP implementation
todo: Router: define f_table(forwarding table), write __str__ to print f_table, write recv_msg
todo: Main: implement config reader and use to create server and router objects"""


import socket
import select
import threading  # Probably won't be used
import sys
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
        #print('Send to ', self.owner)
        self.owner.recv_msg(message, self.port)


class Router:
    def __init__(self, router_id):
        self.router_id = router_id
        self.links = []
        self.forwarding_table = {router_id: (0, 0)}  # forwarding table port, cost
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send

    def __str__(self):
        """Prints out the forwarding table """
        table_format = "="*18
        table_format += " RIPv2 Routing Table of " + str(self.router_id) + " "
        table_format += "="*18 + "\n"
        table_format += "Router Inputs: " + str(self.links) + "\n"
        table_format += f"{'Router Id':<15}{'Port':>6}{'Cost':>20}{'Next Hop':>21}"
        table_format += "\n" + "="*62 + "\n"
        for key, value in sorted(self.forwarding_table.items()):
            port, cost = value
            table_format += "{:<12} {:>6}  {:>20} \n".format(key, port, cost)
        print(table_format)

    def add_link(self, link):
        links = self.links
        links.append(link)  # link = (input, output, cost)
        #print(links) [[1112, 1, 2221], [1117, 8, 7771], [1116, 5, 6661]]

    def update_forwarding_table(self):
        """todo: write me"""
        # check if forwarding table has the dictionary in it -  link from link function and new info
        # check if ID in dictionary, if not add to dictionary with port and cost from link + cost listed
        # if in dictionary see if cost is lower and update appropriately

        for link in self.links:
            print(link)
        # for router, contents in self.forwarding_table.items():
        #    router = self.router_id
        #   contents = self.links
        # for router, contents in self.forwarding_table.items():
        # if router == self.router_id:
        # continue)
        # elif router not in self.forwarding_table[1].keys():
        #    self.forwarding_table[1][router] = [contents[0], contents[1], link+contents[2]]

    def recv_msg(self, msg, port):
        try:
            if str(int(msg[:6], 2)) == self.router_id or str(int(msg[:6], 2)) == '0':
                print(str(int(msg[:6], 2)))
                msg_dst, typ, body = self.pkt_unravel(msg)
                if typ == 0:
                    print('Update f_table with', body)
                if typ == 1:
                    print('Router', self.router_id, 'received message', body)
                if typ == 2:
                    # print the f_table
                    pass
                if typ == 3:
                    # maybe disable router?
                    pass
            else:
                msg_dst = str(int(msg[:6], 2))
                print('Router', self.router_id, 'received message to forward to router', msg_dst)
                if self.f_table.__contains__(msg_dst):
                    self.sender.sendto(msg, self.f_table[msg_dst][0])
        except ValueError:
            print('Incorrect message format received at Router ID:', self.router_id)

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


# router_info ={'1': [[1112, 1116, 1117], [2221, 7777, 6666]],
#               '2': [[2221, 2223], [1112, 2223]],
#               '3': [[3332, 3334], [2223, 4443]],
#               '4': [[4443, 4445, 4447], [7774, 3334, 5554]],
#               '5': [[5554, 5556], [4445, 6665]],
#               '6':[[6661, 6665], [1116, 5556]],
#               '7': [[7771, 7774], [1117, 4447]]}

#test_routers = {'1': [(5000, 5001, 8), (5011, 41241, 8)]}  # dictionary format {id: [(input, output, cost), (link2))]}


def main():
    """I run the show around here!"""
    servers = []  # create a list to hold servers
    routers = []  # create a list whose routes in the forwarding table
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
        route.__str__()
        i += 1




    while True:
        readers, _, _ = select.select(servers, [], [])  # select takes 3 lists as input we only need first one
        for reader in readers:
            reader.on_read()


main()

