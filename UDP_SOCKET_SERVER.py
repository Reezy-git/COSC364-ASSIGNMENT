import socket

# Server address (hard-coded)
SERVER = 'localhost', 5001
# SERVER= socket.gethostbyname(socket.gethostname()), 5000

open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Open a UDP socket
open_socket.bind(SERVER)  # Bind socket to server address details
print("waiting on port:", SERVER)

while True:
    data, addr = open_socket.recv(1024)  # wait for data
    print(data.decode('utf-8'))  # decode and print data
