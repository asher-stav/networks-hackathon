from math import log
import socket
import struct
import threading
import time

import logger

BYTE_SIZE = 8

# message structure constants:
COOKIE = 0xabcddcba
COOKIE_IDX = 0
COOKIE_LEN = 4

TYPE_OFFER = 0x2
TYPE_REQUEST = 0x3
TYPE_PAYLOAD = 0x4
TYPE_IDX = 4
TYPE_LEN = 1
# OFFER message
OFFER_UDP_IDX = 5
OFFER_UDP_LEN = 2
OFFER_TCP_IDX = 7
OFFER_TCP_LEN = 2
OFFER_MSG_LEN = 9
# REQUEST message
REQUEST_FILE_SIZE_IDX = 5
REQUEST_FILE_LEN = 8
REQUEST_MSG_LEN = 13
# PAYLOAD message
PAYLOAD_SEGMENT_COUNT_IDX = 5
PAYLOAD_SEGMENT_COUNT_LEN = 8
PAYLOAD_CURRENT_SEGMENT_IDX = 13
PAYLOAD_CURRENT_SEGMENT_LEN = 8
CURR_SEGMENT_IDX = 13
CURR_SEGMENT_LEN = 8
PAYLOAD_DATA_IDX = 21
# actual payload length is unknown, will be calculated in runtime.
MAX_PAYLOAD_MSG_SIZE = 1024
MAX_PAYLOAD_SIZE = 1000

class Client:
    """
    A class representing a client that can connect to servers and run speed-tests on them, 
    both with UDP and TCP connections.
    In addition, collects data about the servers and the connections.
    """
    __offer_sock: socket.socket
    __port: int
    __shutdown: bool
    __data_size: bytes
    __tcp_connections_num: int
    __udp_connections_num: int
    
    def __init__(self, port: int, data_size: int, tcp_connections_num: int, udp_connections_num: int):
        self.__port = port
        self.__shutdown = False
        self.__data_size = struct.pack("Q", data_size)
        self.__tcp_connections_num = tcp_connections_num
        self.__udp_connections_num = udp_connections_num
    
    def run(self) -> None:
        """
        Runs the client until stopped, constantly looking for servers to run a speedtest on.
        """
        self.__offer_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable broadcasting on the socket
        self.__offer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Enable reusing the port
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.__offer_sock.bind(('', self.__port))

        logger.info("Client started, listening for offer requests...")
        
        try:
            while not self.__shutdown:
                data: bytes
                addr: tuple[str, int]
                # purposefully set 1 byte more than the message length to check for errors
                data, addr = self.__offer_sock.recvfrom(OFFER_MSG_LEN)

                # check for correct offer message structure and values.
                if len(data) == OFFER_MSG_LEN:
                    cookie: int = struct.unpack("I", data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN])[0]
                    type: int = struct.unpack("B", data[TYPE_IDX:TYPE_IDX+TYPE_LEN])[0]
                    if cookie == COOKIE and type == TYPE_OFFER:
                        udp_port: int = struct.unpack("H", data[OFFER_UDP_IDX:OFFER_UDP_IDX+OFFER_UDP_LEN])[0]
                        tcp_port: int = struct.unpack("H", data[OFFER_TCP_IDX:OFFER_TCP_IDX+OFFER_TCP_LEN])[0]
                        request_thread = threading.Thread(target=self.request_file, args=(addr[0],
                                        udp_port, tcp_port, ))
                        request_thread.start()
                        request_thread.join()
                        logger.info('All transfers complete, listening to offer requests')
                    else:
                        logger.error("Received invalid cookie or message type")
                else:
                    logger.error("Received message of unexpected length")
        except:
            logger.error('Failed to receive offer')

        self.__offer_sock.close()

    def shutdown(self) -> None:
        """
        Shuts down the client, preventing it from receiving further offers.
        If the client runs a task currently, it will finish it before termination.
        """
        logger.info('Terminating client...')
        self.__shutdown = True
        self.__offer_sock.close()
    
    def request_file(self, server_addr: str, server_udp_port: int, server_tcp_port: int) -> None:
        tcp_threads: list[threading.Thread] = []
        for i in range(self.__tcp_connections_num):
            t = threading.Thread(target=self.tcp_connect,
                                args=(server_addr, server_tcp_port, i + 1, ))
            t.start()
            tcp_threads.append(t)
        udp_threads: list[threading.Thread] = []
        for i in range(self.__udp_connections_num):
            t = threading.Thread(target=self.udp_connect, 
                                 args=(server_addr, server_udp_port, i + 1, ))
            t.start()
            udp_threads.append(t)

        for t in tcp_threads:
            t.join()
        for t in udp_threads:
            t.join()
            
    def tcp_connect(self, server_addr: str, server_tcp_port: int, connection_num: int) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr: tuple[str, int] = (server_addr, server_tcp_port)
        
        req_data_size: int = struct.unpack("Q", self.__data_size)[0]
        request_msg: bytes = (str(req_data_size) + '\n').encode()
        data_left: int = req_data_size

        try:
            # Connect to the server
            sock.connect(addr)
            logger.info(f"Connected to server {server_addr}:{server_tcp_port} via TCP.")

            # Send the request message
            sock.sendall(request_msg)
            logger.debugging(f"Sent request message of {req_data_size} bytes to the connected server.")

            # Receive data
            start_time: float = time.time()
            while data_left > 0:
                data: bytes = sock.recv(MAX_PAYLOAD_MSG_SIZE)
                if not data:
                    logger.error("Server closed the connection.")
                    return
                
                # Calculate the actual payload length
                payload_len: int = len(data)
                data_left -= payload_len

            end_time: float = time.time()
            transfer_time: float = end_time - start_time
            transfer_rate: float = float('inf') if transfer_time == 0 else BYTE_SIZE * req_data_size / transfer_time
            Client.print_tcp_connection_metrics(connection_num, transfer_time, transfer_rate)

        except socket.error as e:
            logger.error(f"TCP connection error: {e}")

        finally:
            sock.close()
            logger.debugging("Connection closed.")

    @staticmethod
    def print_tcp_connection_metrics(connection_num: int, transfer_time: float,
                                     transfer_rate: float) -> None:
        """
        Prints TCP connection metrics: connection number, total transfer time
        and transfer rate
        """
        logger.info(f'TCP transfer #{connection_num} finished, '
                f'total time: {transfer_time:.4f} seconds, '
                f'total speed: {transfer_rate:.4f} bits/second')
        
    
    def udp_connect(self, server_addr: str, server_udp_port: int, connection_num: int) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr: tuple[str, int] = (server_addr, server_udp_port)
        cookie: bytes = struct.pack('I', COOKIE)
        type_offer: bytes = struct.pack('B', TYPE_REQUEST)
        request_msg: bytes = cookie + type_offer + self.__data_size
        req_data_size: int = struct.unpack("Q", self.__data_size)[0]
        data_left: int = req_data_size

        try:
            sock.sendto(request_msg, addr)
            logger.debugging(f'Sent request message of {req_data_size} bytes to server '
                  f'{server_addr}:{server_udp_port} via UDP.')
            segments_amount: int = (req_data_size // MAX_PAYLOAD_SIZE) + 1
            received_segments_count: int = 0
            curr_segment_id: int = 0

            start_time: float = time.time()

            while curr_segment_id < segments_amount - 1:
                data, _ = sock.recvfrom(MAX_PAYLOAD_MSG_SIZE)
                if not data:
                    logger.error("Did not receive data from the server.")
                    continue
                cookie: int = struct.unpack('I', data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN])[0]
                if cookie != COOKIE:
                    logger.error(f'Error: received invalid cookie: {hex(cookie)}')
                    continue
                
                message_type: int = struct.unpack('B', data[TYPE_IDX:TYPE_IDX+TYPE_LEN])[0]
                if message_type != TYPE_PAYLOAD:
                    logger.error(f'Error: received invalid message type: {message_type}. Expected: {TYPE_REQUEST}')
                    continue
                
                curr_segment_id = struct.unpack('Q', data[CURR_SEGMENT_IDX:CURR_SEGMENT_IDX + CURR_SEGMENT_LEN])[0]

                # calculate the actual payload length
                payload_len: int = len(data[PAYLOAD_DATA_IDX:])
                data_left -= payload_len
                received_segments_count += 1
            
            end_time: float = time.time()
            transfer_time: float = end_time - start_time

            transfer_rate: float = float('inf') if transfer_time == 0 else BYTE_SIZE * req_data_size / transfer_time
            Client.print_udp_connection_metrics(connection_num, transfer_time,
                        transfer_rate, (received_segments_count / segments_amount) * 100)

        except socket.timeout:
            logger.error(f'UDP connection to server {server_addr}:{server_udp_port} timed out.')
            return
        
    @staticmethod
    def print_udp_connection_metrics(connection_num: int, transfer_time: float,
                                     transfer_rate: float, success_percent: float) -> None:
        """
        Prints UDP connection metrics: connection number, total transfer time,
        transfer rate and what percent of packets received
        """
        logger.info(f'UDP transfer #{connection_num} finished, '
                f'total time: {transfer_time:.4f} seconds, '
                f'total speed: {transfer_rate:.4f} bits/second, '
                f'percentage of packets received successfully: {success_percent:.4f}%')
