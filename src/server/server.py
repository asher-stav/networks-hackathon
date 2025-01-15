import socket
import struct
import threading
import time

import teapot_gen
import logger


COOKIE = 0xabcddcba
UDP_OFFER_MSG_CODE = 0x2
UDP_REQUEST_MSG_CODE = 0x3
UDP_PAYLOAD_MSG_CODE = 0x4
# Constants for UDP request message type
REQUEST_MESSAGE_LEN = 13
REQUEST_COOKIE_INDEX = 0
REQUEST_TYPE_INDEX = 4
REQUEST_FILE_SIZE_INDEX = 5

MAX_UDP_MESSAGE_LEN = 1024
MAX_PAYLOAD_SIZE = 1000

BROADCAST_IP = '255.255.255.255'

class Server:
    """
    Server class that listens for incoming connections from clients in either UDP or TCP.
    When a client requests, the server sends an amount of data as requested.
    """
    __udp_port: int
    __tcp_port: int
    __broadcast_port: int

    __offer_sock: socket.socket
    __udp_sock: socket.socket
    __tcp_sock: socket.socket
    
    def __init__(self, udp_port: int, tcp_port: int, broadcast_port: int):
        self.__shutdown = False
        self.__udp_port = udp_port
        self.__tcp_port = tcp_port
        self.__broadcast_port = broadcast_port
    
    def run(self) -> None:
        """
        Runs the server: starts UDP and TCP servers, and starts broadcasting
        offer messages
        """
        # Open UDP server
        self.__udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.__udp_sock.bind(('', self.__udp_port))
        except:
            logger.error(f'Error: failed to bind UDP server to port {self.__udp_port}')
            self.__udp_sock.close()
            return

        udp_thread: threading.Thread = threading.Thread(target=self.listen_udp)
        udp_thread.start()

        # Open TCP serer
        self.__tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__tcp_sock.bind(('', self.__tcp_port))
        except:
            logger.error(f'Error: failed to bind TCP server to port {self.__tcp_port}')
            self.__udp_sock.close()
            self.__tcp_sock.close()
            return

        tcp_thread: threading.Thread = threading.Thread(target=self.listen_tcp)
        tcp_thread.start()

        # Open offer thread
        self.__offer_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.__offer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # self.__offer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            logger.error(f'Error: failed to bind broadcast to port {self.__broadcast_port}')
            self.__udp_sock.close()
            self.__tcp_sock.close()
            self.__offer_sock.close()
            return
        offer_thread: threading.Thread = threading.Thread(target=self.announce_offers)
        offer_thread.start()

        logger.info(f'Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}')
        teapot_gen.init()
        threading.Thread(target=teapot_gen.start).start()

    def shutdown(self) -> None:
        """
        Shuts down the server, preventing it from receiving further new client connections.
        Finishes handling existing connections before termination
        """
        logger.info('Terminating server...')
        self.__shutdown = True

        self.__offer_sock.close()
        # Enable UDP & TCP listeners to wrap up connections - close only reading from socket
        self.__tcp_sock.close()
        self.__udp_sock.close()
        teapot_gen.stop()

    def announce_offers(self) -> None:
        """
        Sends offers to connect to the server every one second
        """
        while not self.__shutdown:
            self.send_udp_offer()
            time.sleep(1)
        logger.debugging('Stopped sending offers')

    def send_udp_offer(self) -> None:
        """
        Sends an broadcast offer to connect to the server.
        Message structure:
            - magic cookie, 4 bytes
            - message code, 2 bytes
            - server UDP port, 2 bytes
            - server TCP port, 2 bytes
        """
        message: bytes
        message = struct.pack('I', COOKIE)
        message += struct.pack('B', UDP_OFFER_MSG_CODE)
        message += struct.pack('H', self.__udp_port)
        message += struct.pack('H', self.__tcp_port)
        self.__offer_sock.sendto(message, (BROADCAST_IP, self.__broadcast_port))
        
    def listen_udp(self) -> None:
        """
        Listens for UDP requests from clients
        """
        try:
            while not self.__shutdown:
                data, address = self.__udp_sock.recvfrom(MAX_UDP_MESSAGE_LEN)
                teapot_gen.stop()
                logger.debugging(f'Accepted UDP client {address}')
                threading.Thread(target=self.handle_udp_connection, args=(data, address)).start()
        except:
            logger.error('Error: failed to receive new UDP message. Wrapping up UDP server...')
            self.__udp_sock.close()
        logger.debugging('Closed UDP server')

    def listen_tcp(self):
        """
        Listens for TCP connections from clients
        """
        try:
            self.__tcp_sock.listen()

            while not self.__shutdown:
                client_sock, address = self.__tcp_sock.accept()
                teapot_gen.stop()
                logger.debugging(f'Accepted TCP client {address}')
                threading.Thread(target=self.handle_tcp_connection, args=(client_sock, )).start()
        except:
            logger.error('Error: failed to accept new TCP client. Wrapping up TCP server...')
            self.__tcp_sock.close()
        logger.debugging('Closed TCP server')

    def handle_udp_connection(self, data: bytes, address) -> None:
        """
        Handles a UDP client request
        After processing the request, sends UDP packets according to the requested
        file size
        """
        if(len(data) < REQUEST_MESSAGE_LEN):
            logger.error('Error: received invalid message length from UDP client!')
            return
        
        cookie: int = struct.unpack('I', data[REQUEST_COOKIE_INDEX:REQUEST_TYPE_INDEX])[0]
        if cookie != COOKIE:
            logger.error(f'Error: received invalid cookie: {cookie}')
            return
        
        message_type: int = struct.unpack('B', data[REQUEST_TYPE_INDEX:REQUEST_FILE_SIZE_INDEX])[0]
        if message_type != UDP_REQUEST_MSG_CODE:
            logger.error(f'Error: received invalid message type: {message_type}. Expected: {UDP_REQUEST_MSG_CODE}')
            return
        
        file_size: int = struct.unpack('Q', data[REQUEST_FILE_SIZE_INDEX:REQUEST_MESSAGE_LEN])[0]

        segments_amount: int = (file_size // MAX_PAYLOAD_SIZE) + 1
        message_start: bytes = struct.pack('I', COOKIE) + struct.pack('B', UDP_PAYLOAD_MSG_CODE) + \
            struct.pack('Q', segments_amount)

        data_sent: int = 0
        curr_segment = 0

        logger.debugging(f'Sending {file_size} bytes to client in {segments_amount} segments over UDP...')
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while data_sent < file_size:
            message: bytes = b''
            message += message_start
            message += struct.pack('Q', curr_segment)
            curr_payload: int = min(MAX_PAYLOAD_SIZE, file_size - data_sent)
            message += ('a' * curr_payload).encode()
            try:
                sock.sendto(message, address)
            except Exception as e:
                logger.error(f'Error: failed to send segment number {curr_segment} to udp client: {e}')

            curr_segment += 1
            data_sent += curr_payload
        logger.debugging(f'Finished sending data in UDP connection ${address}')

    def handle_tcp_connection(self, client_sock: socket.socket) -> None:
        """
        Handles a TCP client request
        After processing the request, sends bytes as the requested file size
        """
        bytes_amount: int = 0
        curr_char: str = ''
        while curr_char != '\n':
            try:
                curr_char = client_sock.recv(1).decode()
            except Exception as e:
                logger.error(f'Error: TCP client failed to receive next char {e}')
                client_sock.close()
                return
            
            if not curr_char.isdigit() and curr_char != '\n':
                logger.error('Error: received a non-digit char from client in TCP connection!')
                client_sock.close()
                return
            if curr_char != '\n':
                bytes_amount = (10 * bytes_amount) + int(curr_char)

        logger.debugging(f'Sending {bytes_amount} bytes to client over TCP...')
        sent_data: int = 0
        while sent_data < bytes_amount:
            try:
                sent_data += client_sock.send(('a' * min(1024, bytes_amount - sent_data)).encode())
            except Exception:
                logger.error(f'Error: failed to send data to tcp client!')
                client_sock.close()
                return
            
        client_sock.close()
        logger.debugging(f'Finished sending data in TCP connection')
