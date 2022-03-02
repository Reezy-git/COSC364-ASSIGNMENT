import sys


class Main:
    # execute when the class is being initiated
    def __init__(self, router_id, input_ports, outputs):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs

    # Return in readable information
    def __str__(self):
        router_format = "Router-Id: " + self.router_id[9:]
        router_format += "=" * len(self.outputs) + '\n'
        router_format += "Input Ports: " + self.input_ports[12:]
        router_format += "Outputs: " + self.outputs[8:]
        return router_format


# check router id
def check_router(router_id):
    if router_id >= 1 and router_id <= 64000:
        return True
    print("Router doesn't exist")


# check input ports
def check_input_ports(input_ports):
    duplicated_ports = []
    for port in input_ports:
        if port >= 1024 and port <= 64000:
            if port in duplicated_ports:
                return True
            duplicated_ports.append(port)
        print("Port is too small/big to exist!")
    return duplicated_ports


# check the outputs
# def check_outputs(input_ports, outputs):
#
#    for output in outputs:
#        if output[0] in input_ports:


# Read the router config file
def read_router_file(filename):
    content = open(filename, 'r')
    router_contents = content.readlines()
    content_list = []
    for router_content in router_contents:
        router_content.split(",")
        content_list.append(router_content)
        content.close()
    return content_list


# Input for what router file is needed
def input_router():
    router_file = input("Input a router: ")
    router, ports, outputs = read_router_file(router_file)
    return router, ports, outputs


def main():
    # read config file
    router_id, input_ports, outputs = input_router()
    router = Main(router_id, input_ports, outputs)
    print(router)


if __name__ == "__main__":
    main()
