"""
  config.py: Takes a router's information.

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges (11139316)
 - Chrystel Claire Quirimit (63369627)

"""

import sys
import re

class Main:
    """ Executed when a router file has been selected."""
    # execute when the class is being initiated
    def __init__(self, router_id, input_ports, outputs):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs
        self.routing_dictionary = {}

    def parse_routing_dictionary(self, file):
        """ Create a dictionary from given file"""
        each_pair = []
        router_dictionary = {}
        neighbor_ports = []
        cost_list = []

        # Grabbing the router id, new input and output list
        router_num, new_input_list, output_slice = read_router_file(file)
        self.router_id = str(router_num)
        self.input_ports = new_input_list
        self.outputs = output_slice

        # For loop for grabbing all the list and putting it individual list
        # For each list, their output are turned into an int.
        for output in self.outputs:
            output[0], output[1], output[2] = int(output[0]), int(output[1]), int(output[2])
            neighbor_port, cost, neighbor_id = output[0], output[1], output[2]
            neighbor_ports.append(neighbor_port)
            cost_list.append(cost)
        a = 0
        # Using zip to use three list in one loop.
        for i, c, n in zip(new_input_list, neighbor_ports, cost_list):
            each_pair.append([i, c, n])
            a += 1

        # Dictionary format as {id: [[inputs, port, cost]]
        router_dictionary[str(router_num)] = each_pair
        self.routing_dictionary = router_dictionary
        return(self.routing_dictionary)

def read_router_file(filename):
    """ Read the router configuration file to grab everything for the router """
    router_num = 1
    content_list = []
    output_slice = []

    # open the file and read the lines
    try:
        router_file = open(filename, 'r')
        router_contents = router_file.readlines()
    except FileNotFoundError as e:
        print(f"File not found!", file=sys.stderr)
        sys.exit()

    # for the contents in the file, get the router_id, input_ports and output ports
    for router_content in router_contents:
        router_content = re.split(", | |\n", router_content)
        content_list.append(router_content)

    # take the router id, input and output fom the list
    for contents in content_list:
        if "router-id" in contents: #take the router id if it exist
            try:
                router_num = int(contents[1])
            except ValueError:
                print("Invalid router id")
                sys.exit()
        if "input-ports" in contents: # take ports if it exist
            try:
                input_list = contents[1:-1]
                new_input_list = [int(i) for i in input_list]
                if len(input_list) == 0:
                    print("No input ports found")
                    sys.exit()
            except ValueError:
                print("Invalid input ports/ No input ports found")
                sys.ext()
        if "outputs" in contents: # take output ports if it exists
            try:
                output_list = contents[1:]
                for outputs in output_list:
                    output_slice.append(outputs.split("-"))

                # for the output, slice it to get the neighbor port, cost and id
                for output in output_slice:
                    output[0], output[1], output[2] = int(output[0]), int(output[1]), int(output[2])
            except ValueError:
                print("Invalid outputs")
                sys.exit()
    return router_num, new_input_list, output_slice


def main():
    """ Runs the config. Takes one router file only."""
    try:
        router_file = sys.argv[1]
    except IndexError:
        print("You did not specify a file")
        sys.exit(1)
    # read config file
    router_id, input_ports, outputs = read_router_file(router_file)
    # calling the main class
    router = Main(router_id, input_ports, outputs)
    # Print the routing table of the router
    router.parse_routing_dictionary(router_file)

# Run
if __name__ == "__main__":
    main()


