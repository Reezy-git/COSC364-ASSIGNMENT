"""
 main.py: Run me with router_class.txt to start a router.

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges ()
 - Chrystel Claire Quirimit (63369627)
 """

import select
import sys
import config
import router_class
import ticker_class
import server_class


def setup():
    """set up the servers, routers and ticker/timer"""
    servers = []  # create a list to hold servers
    routers = []  # create a list
    tickers = []
    network_id = 'localhost'
    tick_duration = 1  # every tick broadcast every 6 ticks if no message kill link

    # Config reader to take the dictionary of the router file
    router_file = sys.argv[1]
    router_id, inputs, outputs = config.read_router_file(router_file)
    config_file = config.Main(router_id, inputs, outputs)
    router_parse = config_file.parse_routing_dictionary(router_file)

    # Find the router that was given in the argument and grab the link it wants to connect
    # Start the timer
    i = 0
    for router in router_parse:
        routers.append(router_class.Router(router, network_id))
        tickers.append(ticker_class.Ticker(routers[i], tick_duration))
        for link in router_parse[router]:
            link.append(0)
            servers.append(server_class.Server(network_id, int(link[0]), routers[i]))
            routers[i].add_link(link)
        i += 1
    return servers, tickers


def main():
    """Run's the program """
    servers, tickers = setup()

    for ticker in tickers:
        ticker.loop()

    while True:
        readers, _, _ = select.select(servers, [], [])  # select takes 3 lists as input we only need first one
        for reader in readers:
            reader.on_read()

# Call the program
main()

