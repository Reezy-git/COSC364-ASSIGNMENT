import sys
import re


# input port instance router listen to
# output how to reach rich neighbor
# send data to neighbor poisoined reverse
# listen to if the neighbor sends data to the router and update roouting table


class Main:
    # execute when the class is being initiated
    def __init__(self, router_id, input_ports, outputs):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs
        self.routing_dictionary = {}
        # For loop to get information of output port in a dictionary template
        for neighbor_port, cost, neighbor_id in outputs:
            self.routing_dictionary[neighbor_id] = (int(cost), int(neighbor_port))
        #self.routing_table = [self.router_id, self.routing_dictionary]
        #[1, {2: (1, 2221), 7: (8, 7771), 6: (5, 6661)}]

    # Human-readable routing table returned that can be printed in terminal
    def print_routing_table(self):
        table_format = "="*18
        table_format += " RIPv2 Routing Table of " + str(self.router_id) + " "
        table_format += "="*18 + "\n"
        table_format += "Router Inputs: " + str(self.input_ports) + "\n"
        table_format += f"{'Router Id':<15}{'Port':>6}{'Cost':>20}{'Next Hop':>21}"
        table_format += "\n" + "="*62 + "\n"
        for key, value in sorted(self.routing_dictionary.items()):
            port, cost = value
            table_format += "{:<12} {:>6}  {:>20} \n".format(key, port, cost)
        print(table_format)


# Read the router config file
def read_router_file(filename):
    router_num = 1
    input_list = []
    output_list = []

    content_list = []
    # open the file and read the lines
    router_file = open(filename, 'r')
    router_contents = router_file.readlines()

    # for the contents in the file, get the router_id, input_ports and output ports
    for router_content in router_contents:
        router_content = re.split(", | |\n", router_content)
        content_list.append(router_content)
        # print(content_list)

    for contents in content_list:
        # Taking the router id
        if "router-id" in contents:
            try:
                router_num = int(contents[1])
                # print(router_num)
            except ValueError:
                print("Invalid router id")
                sys.exit()

        # Taking the input ports
        if "input-ports" in contents:
            try:
                input_list = contents[1:-1]
                input_list = list(map(int, input_list))
                if len(input_list) == 0:
                    print("No input ports found")
                    sys.exit()
            except ValueError:
                print("Invalid input ports/ No input ports found")
                sys.ext()

        # Taking the output ports
        if "outputs" in contents:
            try:
                output_nums = []
                output_list = contents[1:]
                # print(output_list)
                for outputs in output_list:
                    split_output = outputs.split("-")
                    output_nums.append(split_output)
                # print("hello", output_nums)
                for output in output_nums:
                    output[0], output[1], output[2] = int(output[0]), int(output[1]), int(output[2])
                    neighbor_port, cost, neighbor_id = output[0], output[1], output[2]
                print(neighbor_port, cost, neighbor_id)
            except ValueError:
                print("Invalid outputs")
                sys.exit()
    return router_num, input_list, output_nums


def main():

    # Take the system argument 1 for txt file
    try:
        router_file = sys.argv[1]
    except IndexError:
        print("You did not specify a file")
        sys.exit(1)

    # read config file
    router_id, input_ports, outputs = read_router_file(router_file)

    # print(router_id, '0000')
    router = Main(router_id, input_ports, outputs)

    # Print the routing table of the router
    router.print_routing_table()

if __name__ == "__main__":
    main()


