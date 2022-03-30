"""A basic router for RIP implementation
todo: Router: define f_table(forwarding table), write __str__ to print f_table, write recv_msg
todo: Main: implement config reader and use to create server and router objects"""


import socket
import select
import threading  # Probably won't be used
import sys

# import config file
import config

# https://pythontic.com/modules/socket/udp-client-server-example
"""
Class: Server
Create a UDP socket.
Bind the socket to the server address.
Wait until the datagram packet arrives from the client.
Process the datagram packet and send a reply to the client.
Go back to Step 3.
"""
class Server:
    # Initialize udp socket and grab the dictionary file
    def __init__(self, owner, address, port):
        # Create a udp socket
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket to receive
        # Bind the socket to the server address
        #self.receiver.bind(('localhost', port))

        """
        Attributes:
        Address: Input port of Sending router
        Port: Neighbor port it will send to
        Owner: Neighbor Id
        """
        self.address = address
        self.owner = owner
        self.port = port #[[1112, 1, 1]]
        #for ports in self.port:
        #   for output, id, cost in self.port:
        #       neighbor_port, neighbor_cost, neighbor_id = output, cost, id
        self.hop = 0
        self.next_hop = 1


    def fileno(self):  # required for select
        return self.receiver.fileno()

    def on_read(self):  # the method for receiving a message
        message = self.receiver.recv(1024).decode('utf-8')
        print('Send to ', self.owner)
        self.owner.recv_msg(message, self.port)


"""
Class: Router
Create a UDP socket.
Send a message to the server.
Wait until response from the server is received.
Process reply and go back to step 2, if necessary.
Close socket descriptor and exit.
"""
class Router():
    """ will initialize the configuration class. The paramaters are used since it is required"""
    # initialize the router
    def __init__(self, parsed_file):
        #self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket to send
        self.links = []
        self.forwarding_table = {}
        # router dictionary from config.py
        self.parsed_file = parsed_file
        routing_dictionary = self.parsed_file
        # grabbing the router_id of the router
        for key in routing_dictionary.keys():
            router_id = key
        self.router_id = router_id

        input_ports = []
        for value in routing_dictionary.items():
            value = value[1]
            for input, port, output in value:
                input_port = input
                input_ports.append(input)
        self.input_ports = input_port



    def add_link(self, link):
        self.links.append(link)

    # Display the information of the routing dictionary
    def __str__(self):
        table_format = "=" * 18
        table_format += " RIPv2 Routing Table of " + str(self.router_id) + " "
        table_format += "=" * 18 + "\n"
        table_format += "Router Inputs: " + str(self.input_ports) + "\n"
        table_format += f"{'Router Id':<15}{'Port':>6}{'Cost':>20}{'Next Hop':>21}"
        table_format += "\n" + "=" * 62 + "\n"
        """
        cost = Server.cost
        for key, value in sorted(self.parsed_file):
            value = value[1]
            for input, port, output in value:
                table_format += "{:<12} {:>6}  {:>20} \n".format(key, port, , cost)
        """
        print(table_format)

    def __repr(self):
       return self.__str__()

    def recv_msg(self, msg, port):
        msg_dst = msg[0:8]
        print('Data received: ', msg, port, self.router_id)
        if msg_dst == self.router_id:
            print('Message received at router', self.router_id)
        else:
            if self.f_table.__contains__(msg_dst):
                self.sender.sendto(msg, self.f_table[msg_dst][0])

    def update_forwarding_table(self, new_info):
        """todo: write me"""


# router_info ={'1': [[1112, 1116, 1117], [2221, 7777, 6666]],
#               '2': [[2221, 2223], [1112, 2223]],
#               '3': [[3332, 3334], [2223, 4443]],
#               '4': [[4443, 4445, 4447], [7774, 3334, 5554]],
#               '5': [[5554, 5556], [4445, 6665]],
#               '6':[[6661, 6665], [1116, 5556]],
#               '7': [[7771, 7774], [1117, 4447]]}

test_routers = {'1': [(5000, 5001, 8)],
               '2': [(5001, 5000, 8)]}  # dictionary format {id: [(input, output, cost], (link2))]}

def main():
    """I run the show around here!"""
    try:
        if len(sys.argv) < 2:
            sys.exit()

        router_file = sys.argv[1]
        router_id, inputs, outputs = config.read_router_file(router_file)
        config_file = config.Main(router_id, inputs, outputs)
        router_parse = config_file.parse_routing_dictionary(router_file)

        if not config_file:
            sys.exit("Invalid configuration file")
        print("Configuration has been loaded!")
        # Read the router ID from grabbing it from Main
        router = Router(router_parse)
        print("Start router:", str(router_id))
        server = Server(router_id, inputs, outputs)

    except IndexError:
        sys.exit("Argument is invalid!")

    '''
    servers = []
    routers = []
    i = 0
    for router in test_routers:
        routers.append(Router(router))
        for link in test_routers[router]:
            servers.append(Server('localhost', int(link[0]), routers[i]))
            routers[i].add_link(link)
        i += 1
    '''

main()
