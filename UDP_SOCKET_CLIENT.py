import socket


# Open a socket
open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Hardcoded host change me if needed
host = 'localhost', 5010

while True:
    message = bytes(input('Enter message to send : '), 'utf-8')  # Get input for message and encode as UTF-8
    open_socket.sendto(message, host)  # Send message to server

