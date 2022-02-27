import socket
import sys
import select


class DTRequestPacket:
    def __init__(self, request_type):
        self.magic_number = bin(0x497E)[2:].zfill(16)
        self.packet_type = bin(0x0002)[2:].zfill(16)
        self.bit_string = ''
        self.pkt = bytearray()
        try:
            self.type = bin(int(request_type))[2:].zfill(16)
        except TypeError:
            print('[ERROR] Request type must be integer; 1 for date, 2 for time.')
            exit()

    def form(self):
        """Creates and returns the request packet."""
        self.bit_string = self.magic_number + self.packet_type + self.type
        self.pkt_constructor()
        return self.pkt

    def pkt_constructor(self, i=0, j=0):
        """Creates a bytearray object from a string of bits."""
        j += 8
        if len(self.bit_string) <= j:
            self.pkt.append(int(self.bit_string[i:len(self.bit_string)], 2))
        else:
            self.pkt.append(int(self.bit_string[i:j], 2))
            i += 8
            self.pkt_constructor(i, j)


class ReceivedPacket:
    def __init__(self, msg):
        self.msg = msg
        self.bit_string = ''
        self.text = ''
        self.txt = bytearray()
        self.bitify()
        self.process()

    def bitify(self):
        """Converts bytes into bits."""
        for byte in self.msg:
            self.bit_string += bin(byte)[2:].zfill(8)

    def process(self):
        """Processes the packet."""
        accepted, action = self.check()
        if not accepted:
            self.send_error(action)
        else:
            self.print_text()

    def check(self):
        """checks packet for validity and provides output for next protocol."""
        magic_number = int(self.bit_string[:16], 2)
        packet_type = int(self.bit_string[16:32], 2)
        lang_code = int(self.bit_string[32:48], 2)
        year = int(self.bit_string[48:64], 2)
        month = int(self.bit_string[64:72], 2)
        day = int(self.bit_string[72:80], 2)
        hour = int(self.bit_string[80:88], 2)
        minute = int(self.bit_string[88:96], 2)
        length = int(self.bit_string[96:104], 2)
        if len(self.bit_string) < 13:
            return False, 0
        if magic_number != 0x497E:
            return False, 1
        if packet_type != 0x0002:
            return False, 2
        if lang_code not in [0x0001, 0x0002, 0x0003]:
            return False, 3
        if year >= 2100:
            return False, 4
        if month not in range(1, 13):
            return False, 5
        if day not in range(1, 32):
            return False, 6
        if hour not in range(24):
            return False, 7
        if minute not in range(60):
            return False, 8
        if len(self.msg) != 13 + length:
            print(length, len(self.bit_string) // 8)
            return False, 9
        return True, 10

    @staticmethod
    def send_error(num):
        """Handler for errors in dt_receive."""
        if num == 0:
            print('[ERROR] Erroneous packet received: Packet too small.')
            exit()
        if num == 1:
            print('[ERROR] Erroneous packet received: Incorrect magic_number.')
            exit()
        if num == 2:
            print('[ERROR] Erroneous packet received: Incorrect packet_type.')
            exit()
        if num == 3:
            print('[ERROR] Erroneous packet received: Incorrect LanguageCode.')
            exit()
        if num == 4:
            print('[ERROR] Erroneous packet received: Year out of range.')
            exit()
        if num == 5:
            print('[ERROR] Erroneous packet received: Month out of range.')
            exit()
        if num == 6:
            print('[ERROR] Erroneous packet received: Day out of range.')
            exit()
        if num == 7:
            print('[ERROR] Erroneous packet received: Hour out of range.')
            exit()
        if num == 8:
            print('[ERROR] Erroneous packet received: Minute out of range.')
            exit()
        if num == 9:
            print('[ERROR] Erroneous packet received: Length incorrect.')
            exit()

    def print_text(self):
        """Prints the output expected by the user."""
        self.pkt_constructor(104, 104)
        for val in self.txt:
            self.text += chr(val)
        return self.text

    def pkt_constructor(self, i=0, j=0):
        """Creates a bytearray object from a string of bits."""
        j += 8
        if len(self.bit_string) <= j:
            self.txt.append(int(self.bit_string[i:len(self.bit_string)], 2))
        else:
            self.txt.append(int(self.bit_string[i:j], 2))
            i += 8
            self.pkt_constructor(i, j)


class Connection:
    def __init__(self, server, port):
        self.client = socket.socket()
        try:
            self.client.connect((server, port))
        except ConnectionRefusedError:
            print(f'[ERROR] Host {server} refused connection on port: {port}')
            exit()

    def fileno(self):
        return self.client.fileno()

    def on_read(self):
        received = self.client.recv(128)
        return ReceivedPacket(received).text

    def send(self, request_type):
        msg = DTRequestPacket(request_type)
        packet = msg.form()
        self.client.send(packet)


def main():
    """I run the show around here."""

    def setup():
        """retrieves the details from the input arguments returns 3 arguments."""
        min_port = 1024
        max_port = 64000
        server = None
        try:
            request_type = sys.argv[1]
        except IndexError:
            print('[ERROR] No request type given.')
            exit()
        try:
            server = socket.getaddrinfo(sys.argv[2], sys.argv[3])[0][4][0]
        except socket.gaierror:
            print('[ERROR] Input for host address invalid.')
            exit()
        except IndexError:
            print('[ERROR] Incorrect host details given.')
            exit()
        try:
            port = int(sys.argv[3])
            if min_port <= port <= max_port:
                return sys.argv[1], server, port
            else:
                print('[ERROR] Integer entered is out of the acceptable range of ports.'
                      f'[{min_port}, {max_port}]')
                exit()
        except ValueError:
            print('You must input integers for your port numbers...')
            exit()

    request_type, server, port = setup()
    client = Connection(server, port)
    client.send(request_type)
    text = ''
    readers, _, _ = select.select([client], [], [], 1)
    for reader in readers:
        text = reader.on_read()
    if len(text):
        print(text)
    else:
        print('[ERROR] No packet received within 1 second.')


main()
