"""
 router_class.py: A router with RIP specified protocol.

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges (11139316)
 - Chrystel Claire Quirimit (63369627)

"""

import json
import socket


class Router:
    """ Router class represents the router """

    def __init__(self, router_id, network_id):
        """ Initialize the router class."""
        self.network_id = network_id
        self.router_id = router_id
        self.links = []  # (input, output, cost, ticks since last update)
        self.f_table = {self.router_id: (0, 0)}  # forwarding table {destination: [output, cost]}
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket to send
        self.active = True  # router is running
        self.garbage_can = dict()

    def __str__(self, table):
        """ Prints out the forwarding table """
        max_cost = 16
        table_format = "=" * 18
        table_format += " RIPv2 Routing Table of " + str(self.router_id) + " "
        table_format += "=" * 18 + "\n"
        table_format += f"{'Router Id':<15}{'Port':>6}{'Cost':>20}"
        table_format += "\n" + "=" * 62 + "\n"
        for key, value in sorted(table.items()):
            port, cost = value
            if cost >= max_cost:  # if cost is more than max cost of 16
                table_format += "{:<12}{:>9}{:>20} \n".format(key, port, '*')
            else:
                table_format += "{:<12}{:>9}{:>20} \n".format(key, port, cost)
        return table_format

    def add_link(self, link):
        """ Add a link in the links list"""
        self.links.append(link)  # link = (input, output, cost)

    def toggle_activity(self):
        """Turns router on/off and resets the f_table"""
        self.active = not self.active
        print('Toggle activity to:', self.active)
        self.f_table = {self.router_id: (0, 0)}

    def recv_msg(self, msg, port):
        """ check if active and then process the message (process_msg) """
        if self.active:  # if router is active, process message as normal (taking message and port nums argument)
            self.process_msg(msg, port)
        else:  # if router is not active check to see if packet type is activity toggle and turn back on if so.
            if int(msg[6:8], 2) == 3:
                self.toggle_activity()

    def process_msg(self, msg, port):
        """ Process the message by taking the message and port number the message was received on
        first checks destination of the message and then checks message type form the msg header"""
        try:
            if str(int(msg[:6], 2)) == self.router_id or str(int(msg[:6], 2)) == '0':
                msg_dst, typ, body = self.pkt_unravel(msg)
                # Request Type 0: Update the Forwarding Table using function: update_f_table
                if typ == 0:
                    self.update_f_table(body, self.get_link(port))
                # Request 1: Prints a message stating what the router has received
                if typ == 1:
                    print('Router', self.router_id, 'received message', body)
                # Request 2: Show the Forwarding table
                if typ == 2:
                    print(self.__str__(self.f_table))
                # Request Type 3: Turn On/Off activity of router
                if typ == 3:
                    self.toggle_activity()
            else:  # ask richard for the else statement and if statement
                msg_dst = str(int(msg[:6], 2))
                print('Router', self.router_id, 'received message to forward to router', msg_dst)
                if self.f_table.__contains__(msg_dst):
                    target = self.network_id, self.f_table[msg_dst][0]
                    self.sender.sendto(msg.encode('utf8'), target)
        except ValueError:
            print('Incorrect message format received at Router ID:', self.router_id)

    def broadcast(self):
        """Sends out the forwarding information we have to our neighbors"""
        self.changes = False
        for link in self.links:
            msg_dict = dict()  # a dictionary for routing information to be sent to this link
            target = self.network_id, link[1]
            for key, value in self.f_table.items():  # this is split horizon
                if value[0] != link[1]:  # if the nexthop port is equal to the link output
                    msg_dict[key] = value
            msg = self.pkt_build(0, 0, msg_dict)
            self.sender.sendto(msg.encode('utf8'), target)

    def on_tick(self):
        """ timer responsible for periodic updates """
        if self.active:
            self.broadcast()  # every tick we broadcast our forwarding capabilities
            for link in self.links:
                link[3] += 1  # link[3] is the time since last update
                if link[3] >= 6:  # 6 ticks with no contact means we assume station is offline or unreachable
                    self.kill_link(link)
            self.garbage()

    def garbage(self):
        """updates the garbage dictionary and if times out delete item"""
        to_delete = []  # items eligible for deletion
        for key in self.garbage_can:
            value = self.garbage_can[key]
            self.garbage_can[key] = value + 1
            if value > 9:  # after 10 ticks in the garbage can we flag item as eligible for deletion
                to_delete.append(key)
        for key in to_delete:
            self.f_table.__delitem__(key)
            self.garbage_can.__delitem__(key)

    def kill_link(self, link):
        """ find the link and change the cost to 16 **"""
        for dest in self.f_table:
            if self.f_table[dest][0] == link[1]:
                self.f_table[dest] = (link[1], 16)

    def get_link(self, port):
        """ Grab the link of the port given"""
        for link in self.links:
            if link[0] == port:
                return link
        print('[ERROR]: Link not found')

    def update_f_table(self, new_info, link):
        """Updates the forwarding table.
        If a change is made to the forwarding table self.changes is toggled to True
        self.changes is used for our implementation of triggered updates
        """
        link[3] = 0  # reset last update value on link as if this reaches over 6 we assume link is dead (see on_tick)
        max_cost = 16
        base_cost = link[2]  # Get the cost of the link.
        self.changes = False  # tracks if we alter the f_table

        for dest in new_info:
            if dest in self.f_table:  # See if we have info on the router.
                current_best = self.f_table[dest][1]
                # work out new potential cost max = 16
                if new_info[dest][1] + base_cost <= max_cost:
                    new_potential_cost = new_info[dest][1] + base_cost
                else:
                    new_potential_cost = max_cost
                if new_potential_cost < current_best:  # If this is a better route we change our table entries.
                    self.f_table[dest] = (link[1], new_potential_cost)
                    self.changes = True
                    try:  # put in garbage can if the new cost is less than our current best *
                        self.garbage_can.__delitem__(dest)
                    except KeyError:
                        continue

                # if the case is that we use this link as our route we need to update the cost if it has changed
                # regardless
                if self.f_table[dest][0] == link[1]:
                    if self.f_table[dest] != (link[1], new_potential_cost):
                        self.f_table[dest] = (link[1], new_potential_cost)
                        self.changes = True
                        if new_potential_cost == max_cost:
                            self.garbage_can[dest] = 0  # add key to garbage can
            else:  # if no other info, if new cost hasnt reached max, we can change it
                cost = new_info[dest][1] + base_cost
                if cost < max_cost:
                    self.f_table[dest] = (
                    link[1], cost)  # We didn't have a route to here. So we just take any route info.
                    self.changes = True
            if self.changes:  # f_table gets changed therefore we need to update tell neighbors.
                self.broadcast()

    @staticmethod
    def pkt_build(dst, typ, body):
        """ Creates the correctly formatted packet to send between routers """
        bin_dst = bin(int(dst))[2:].zfill(6)  # first 6 digits represent destin
        bin_type = bin(int(typ))[2:].zfill(2)  # 2 digits for type = 4 possible types
        bin_body = bin(int((json.dumps(body).encode('utf8')).hex(), 16))[2:]
        return bin_dst + bin_type + bin_body

    @staticmethod
    def pkt_unravel(msg):
        """ Packet gets to be unravelled return each formatted part of the packet"""
        dst = str(int(msg[:6], 2))  # first 6 digits represent destin
        typ = int(msg[6:8], 2)  # digits 7 & 8 for type = 4 possible types
        body = json.loads(bytes.fromhex(hex(int(msg[8:], 2))[2:]))  # remainder are the body
        return dst, typ, body
