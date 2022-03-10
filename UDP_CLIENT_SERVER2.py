import socket

SERVER = 'localhost', 5001
#SERVER= socket.gethostbyname(socket.gethostname()), 5000

in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
in_socket.bind(SERVER)
print("waiting on port:", SERVER[1])

try:
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('socket.error')

host = 'localhost', 5002

while True:
    data, addr = in_socket.recv(1024)
    print(data.decode('utf-8'))
    message = bytes(input('Enter message to send : '), 'utf-8')
    out_socket.sendto(message, host)

