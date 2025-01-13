from email import message
from logging import shutdown
import socket
import struct
import threading
import time


COOKIE = 0xabcddcba
UDP_OFFER_MSG_CODE = 0x2
UDP_REQUEST_MSG_CODE = 0x3
UDP_PAYLOAD_MSG_CODE = 0x4

REQUEST_MESSAGE_LEN = 13
REQUEST_COOKIE_INDEX = 0
REQUEST_TYPE_INDEX = 4
REQUEST_FILE_SIZE_INDEX = 5

BROADCAST_IP = '255.255.255.255'


class Server:
    """
    Server class that listens for incoming connections from clients in either UDP or TCP.
    When a client requests, the server sends an amount of data as requested.
    """
    __shutdown: bool
    __udp_port: int
    __tcp_port: int
    __broadcast_port: int

    __offer_sock: socket.socket
    __udp_sock: socket.socket
    __tcp_sock: socket.socket

    __shutdown_lock: threading.Lock
    
    def __init__(self, udp_port: int, tcp_port: int, broadcast_port: int):
        self.__shutdown = False
        self.__udp_port = udp_port
        self.__tcp_port = tcp_port
        self.__broadcast_port = broadcast_port
        self.__shutdown_lock = threading.Lock()

    def is_shutdown(self) -> bool:
        shutdown: bool
        self.__shutdown_lock.acquire()
        shutdown = self.__shutdown
        self.__shutdown_lock.release()

        return shutdown
    
    def listening(self):
        # Open UDP server
        self.__udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__udp_sock.bind(('', self.__udp_port))

        udp_thread: threading.Thread = threading.Thread(target=self.listen_udp)
        udp_thread.start()

        # Open TCP serer
        self.__tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_sock.bind(('', self.__tcp_port))

        tcp_thread: threading.Thread = threading.Thread(target=self.listen_tcp)
        tcp_thread.start()

        # Open offer thread
        self.__offer_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        offer_thread: threading.Thread = threading.Thread(target=self.announcer)
        offer_thread.start()

        print(f'Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}')

    def shutdown(self) -> None:
        """
        Shuts down the server, preventing it from receiving further new client connections.
        Finishes handling existing connections before termination
        """
        self.__shutdown_lock.acquire()
        self.__shutdown = True
        self.__shutdown_lock.release()        
            
    def announcer(self) -> None:
        """
        Sends offers to connect to the server every second
        """
        while not self.is_shutdown():
            self.send_upd_offer()
            time.sleep(1)

    def send_upd_offer(self) -> None:
        """
        Sends an broadcast offer to connect to the server.
        Message structure:
            - magic cookie, 4 bytes
            - message code, 2 bytes
            - server UDP port, 2 bytes
            - server TCP port, 2 bytes
        """
        message: bytes
        message = struct.pack('>I', COOKIE)
        message += struct.pack('>B', UDP_OFFER_MSG_CODE)
        message += struct.pack('>H', self.__udp_port, self.__tcp_port)
        self.__offer_sock.sendto(message, (BROADCAST_IP, self.__broadcast_port))
        
    def listen_udp(self):
        while not self.is_shutdown():
            data, address = self.__udp_sock.recvfrom(REQUEST_MESSAGE_LEN)
            threading.Thread(target=self.handle_udp_connection, args=(data, address)).start()

    def listen_tcp(self):
        self.__tcp_sock.listen()

        while not self.is_shutdown():
            client_sock: socket.socket = self.__tcp_sock.accept()
            threading.Thread(target=self.handle_tcp_connection, args=(client_sock, )).start()

    def handle_udp_connection(self, data: bytes, address) -> None:
        cookie: int = struct.unpack('>I', data[REQUEST_COOKIE_INDEX:REQUEST_TYPE_INDEX])
        if cookie != COOKIE:
            print(f'Error: received invalid cookie: {cookie}')
            return
        
        message_type: int = struct.unpack('>B', data[REQUEST_TYPE_INDEX:REQUEST_FILE_SIZE_INDEX])
        if message_type != UDP_REQUEST_MSG_CODE:
            print(f'Error: received invalid message type: {message_type}. Expected: {UDP_REQUEST_MSG_CODE}')
            return
        
        file_size: int = struct.unpack('>L', data[REQUEST_FILE_SIZE_INDEX:REQUEST_MESSAGE_LEN])

        segments_amount: int = Server.get_udp_segments_amount(file_size)
        single_segment_payload: int = file_size // segments_amount
        message_start: bytes = struct.pack('>I', COOKIE) + struct.pack('>B', UDP_PAYLOAD_MSG_CODE) + \
            struct.pack('>L', segments_amount)

        for curr_segment in range(segments_amount):
            message: bytes = b''
            message += message_start
            message += struct.pack('>L', curr_segment)
            message += ('a' * single_segment_payload).encode()
            try:
                self.__udp_sock.sendto(message, address)
            except Exception:
                print(f'Error: failed to send segment number {curr_segment} to udp client!')

    @staticmethod
    def get_udp_segments_amount(file_size: int) -> int:
        """
        TODO: return number of segments to send based on file size
        """
        pass

    def handle_tcp_connection(self, client_sock: socket.socket) -> None:
        bytes_amount: int = 0
        curr_char: str = ''
        while curr_char != '\n':
            curr_char = client_sock.recv(1).decode()
            if not curr_char.isdigit():
                print('Error: received a non-digit char from client in TCP connection!')
                client_sock.close()
                return
            bytes_amount = (10 * bytes_amount) + int(curr_char)

        for i in range(bytes_amount):
            try:
                client_sock.send('a')
            except Exception:
                print(f'Error: failed to send byte number {i} to tcp client!')
                break
        client_sock.close()
