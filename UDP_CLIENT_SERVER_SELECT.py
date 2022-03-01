import socket
import select
import sys


# Setup server address
SERVER = 'localhost', 5000
#SERVER= socket.gethostbyname(socket.gethostname()), 5000

# Bind a UDP socket with server details to listen on
in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
in_socket.bind(SERVER)
print("waiting on port:", SERVER)


# the destination details (where we are sending data to)
host = 'localhost', 5000
print('sending data to', host)

# Bind a UDP socket to send data through
out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    readers, _, _ = select.select([sys.stdin, in_socket], [], [])  # select takes 3 lists as input we only need first one
    for reader in readers:
        if reader is in_socket:  # if we get a message do this
            data = in_socket.recv(1024)
            print(data.decode('utf-8'))
        else:  # if we don't have a message take input
            message = bytes(sys.stdin.readline(), 'utf-8')
            out_socket.sendto(message, host)





