import sys
import re

# load in the dictionary
# list of tuple

class Main:
    # execute when the class is being initiated
    def __init__(self, router_id, input_ports, outputs):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs
        self.routing_dic = {}
        for neighbor_port, cost, neighbor_id in outputs:
            self.routing_dic[neighbor_id] = (int(cost), int(neighbor_port))

    # print the dictionary for now.
    def print_routing_table(self):
        table_format = "RIPv2 Routing Table of: " + str(self.router_id) + "\n"
        table_format += "="*40
        table_format += "\n" + str(self.routing_dic)
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
        #print(content_list)

    for contents in content_list:
        # Taking the router id
        if "router-id" in contents:
            try:
                router_num = int(contents[1])
                #print(router_num)
            except ValueError:
                print("Invalid router id")

        # Taking the input ports
        if "input-ports" in contents:
            try:
                input_list = contents[1:-1]
                input_list = list(map(int, input_list))
                if len(input_list) == 0:
                    print("No input ports found")
                else:
                    print("Valid Inputs")
                    #print(input_list)
            except ValueError:
                print("Invalid input ports")

        # Taking the output ports
        if "outputs" in contents:
            try:
                output_nums = []
                output_list = contents[1:]
                #print(output_list)
                for outputs in output_list:
                    split_output = outputs.split("-")
                    output_nums.append(split_output)
                #print("hello", output_nums)
                for output in output_nums:
                    output[0], output[1], output[2] = int(output[0]), int(output[1]), int(output[2])
                    neighbor_port, cost, neighbor_id =  output[0], output[1], output[2]
                print(neighbor_port, cost, neighbor_id)
            except ValueError:
                print("Invalid outputs")
    return router_num, input_list, output_nums

# input port instance router listen to
# output how to reach rich neighbor

# send data to neighbor poisoined reverse
# listen to if the neighbor sends data to the router and update roouting table


def main():
    # read config file
    router_id, input_ports, outputs = read_router_file("router2.txt")
    # print(router_id, '0000')
    router = Main(router_id, input_ports, outputs)
    #print(router.routing_dic)
    router.print_routing_table()


if __name__ == "__main__":
    main()
