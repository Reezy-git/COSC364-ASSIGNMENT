import socket
import threading
import sys
import select
import datetime


class Server:
    def __init__(self, name, port, socket_type):
        self.name = name
        self.server = socket.socket()
        self.port = port
        self.type = socket_type
        self.port_binder()
        self.server.listen()

    def fileno(self):
        """Returns fileno, required for select()"""
f        return self.server.fileno()
f
    def on_read(self):
        """What to do when the socket is accessed."""
        print(f'[CONNECTION] Connection request received on {self.name} socket.')
        self.acceptor()

    def acceptor(self):
        """Executes socket_name.accept() allows use of threads or multiprocessing."""
        try:
            conn, addr = self.server.accept()
            # open a thread to deal with the new connection
            thread_name = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread_name.start()
        except:
            print('Error accepting connection')

    def handle_client(self, conn, addr):
        """Receives and handles client connections."""
        print(f"[CONNECTION] {addr} connected on port: {self.server.getsockname()[1]}.")
        data = conn.recv(128)
        msg = ''
        for byte in data:
            msg += bin(byte)[2:].zfill(8)
        accepted, action = self.check(msg)
        if accepted:
            self.respond(action, conn)
        if not accepted:
            self.send_error(action)
        conn.close()

    @staticmethod
    def send_error(num):
        """Prints an appropriate error message for the operator."""
        if num == 1:
            print('[ERROR] Erroneous packet received: Incorrect magic_number.')
        if num == 2:
            print('[ERROR] Erroneous packet received: Incorrect packet_type.')
        if num == 0:
            print('[ERROR] Erroneous packet received: Request type error.')
        if num == 5:
            print('[ERROR] Erroneous packet received: Packet too large.')

    @staticmethod
    def check(packet):
        """Checks packet for validity and provides output for next protocol."""
        magic_number = int(packet[:16], 2)
        packet_type = int(packet[16:32], 2)
        request_type = int(packet[32:48], 2)
        if len(packet) > 48:
            return False, 5
        if magic_number != 0x497E:
            return False, 1
        if packet_type != 0x0002:
            return False, 2
        if request_type == 0x0001:
            return True, 3
        if request_type == 0x0002:
            return True, 4
        return False, 0

    def respond(self, action, conn):
        """Formulates and sends the response packet."""
        response = Packet(self.type, action)
        conn.send(response.form())

    def port_binder(self):
        """gets potential ports and tries to bind them if in correct range [min, max]."""
        min_port = 1024
        max_port = 64000
        potential_port = self.port
        try:
            self.port = int(potential_port)
            if min_port <= self.port <= max_port:
                try:
                    self.server.bind((socket.gethostbyname(socket.gethostname()), self.port))
                    print(f'Bound: {self.name} to port: {self.port}')
                except OSError:
                    print(f'Port {self.port} already in use')
                    exit()
            else:
                print('Integer entered is out of the acceptable range of ports '
                      f'[{min_port}, {max_port}]')
                exit()
        except ValueError:
            print('You must input integers for your port numbers...')
            exit()


class Packet:
    """The packet class."""
    def __init__(self, socket_lang, request_type):
        self.socket_lang = socket_lang
        self.request_type = request_type
        self.pkt = bytearray()
        self.response = ''
        self.header_string = ''

    def response_header(self):
        """Posts back the date_time packet requested."""
        self.date_time = datetime.datetime.now()
        magic_number = bin(0x497E)[2:].zfill(16)
        packet_type = bin(0x0002)[2:].zfill(16)
        lang = bin(self.socket_lang + 1)[2:].zfill(16)
        year = bin(int(self.date_time.year))[2:].zfill(16)
        month = bin(int(self.date_time.month))[2:].zfill(8)
        day = bin(int(self.date_time.day))[2:].zfill(8)
        hour = bin(int(self.date_time.hour))[2:].zfill(8)
        minute = bin(int(self.date_time.minute))[2:].zfill(8)
        self.header_string = magic_number + packet_type + lang + year + month + day + hour + minute

    def pkt_constructor(self, i=0, j=0):
        """Creates a bytearray object from a string of bits."""
        j += 8
        if len(self.response) <= j:
            self.pkt.append(int(self.response[i:len(self.response)], 2))
        else:
            self.pkt.append(int(self.response[i:j], 2))
            i += 8
            self.pkt_constructor(i, j)

    def form(self):
        """Forms and returns requested packet."""
        self.response_header()
        text_bits = ''
        if self.request_type == 3:
            text_bytes = self.get_date_string()
        else:
            text_bytes = self.get_time_string()
        for byte in text_bytes:
            text_bits += (bin(byte)[2:].zfill(8))
        length = bin(len(text_bytes))[2:].zfill(8)
        self.response = self.header_string + length + text_bits
        self.pkt_constructor()
        return self.pkt

    def get_date_string(self):
        """Returns appropriate date string."""

        def get_month(lang, month):
            """Returns the appropriate month representation for given language.
            the version of Te Reo/German months using macrons causes issues with the output and so
            have been simplified.
            """
            english_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                              'August', 'September', 'October', 'November', 'December']
            te_reo_months = ['Kohitatea', 'Hui-tanguru', 'Poutu-te-rangi', 'Paenga-whawha',
                             'Haratua', 'Pipiri', 'Hongongoi', 'Here-turi-koka', 'Mahuru',
                             'Whiringa-a-nuku', 'Whiringa-a-rang', 'Hakihea']
            german_months = ['Januar', 'Februar', 'Marz', 'April', 'Mai', 'Juni', 'Juli', 'August',
                             'September', 'Oktober', 'November', 'Dezember']
            all_months = [english_months, te_reo_months, german_months]
            return all_months[lang][month - 1]

        if self.socket_lang == 0:
            print('[REQUEST] Client requested: English date.')
            response = f"Today's date is {get_month(0, self.date_time.month)} {self.date_time.day}," \
                       f" {self.date_time.year}"
        elif self.socket_lang == 1:
            print('[REQUEST] Client requested: Te Reo date.')
            response = f"Ko te ra o tenei ra ko {get_month(1, self.date_time.month)}" \
                       f" {self.date_time.day}, {self.date_time.year}"
        else:
            print('[REQUEST] Client requested: German date.')
            response = f"Heute ist der {get_month(2, self.date_time.month)} {self.date_time.day}," \
                       f" {self.date_time.year}"
        return response.encode('utf8')

    def get_time_string(self):
        """returns byte object representing """
        if self.socket_lang == 0:
            print('[REQUEST] Client requested: English time.')
            text_bytes = f'The current time is {self.date_time.hour}:{self.date_time.minute}'
        elif self.socket_lang == 1:
            print('[REQUEST] Client requested: Te Reo time.')
            text_bytes = f'Ko te wa o tenei wa {self.date_time.hour}:{self.date_time.minute}'
        else:
            print('[REQUEST] Client requested: German time.')
            text_bytes = f'Die Uhrzeit ist {self.date_time.hour}:{self.date_time.minute}'
        return text_bytes.encode('utf8')


def main():
    """I run the show around here!"""
    print("[STARTING] Server is starting...")

    def run_sockets(sockets_list):
        """Run the sockets!"""
        while True:  # infinite loop
            readers, _, _ = select.select(sockets_list, [], [], 10)
            for reader in readers:
                reader.on_read()

    try:
        _ = sys.argv[3]
    except IndexError:
        print('Not enough arguments given, please provide three appropriate port numbers.')
        exit()
    print('[STARTING] Establishing server sockets...')
    server1 = Server('English', sys.argv[1], 0)
    server2 = Server('Te Reo', sys.argv[2], 1)
    server3 = Server('German', sys.argv[3], 2)

    print(f"[LISTENING] Server is listening on IP: {socket.getfqdn(socket.gethostname())}")

    run_sockets([server1, server2, server3])


main()
