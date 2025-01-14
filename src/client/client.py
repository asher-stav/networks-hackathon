from pickletools import int4
import socket
import struct
import threading
import time

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
PAYLOAD_DATA_IDX = 21
# actual payload length is unknown, will be calculated in runtime.
MAX_PAYLOAD_MSG_SIZE = 1024


class Client:
    """
    A class representing a client that can connect to servers and run speed-tests on them, both with UDP and TCP connections.
    In addition, will collect interesting data about the servers and the connections.
    """
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
        print ("Client started, listening for offer requests...")
        # AF_INET - IPv4, SOCK_DGRAM - UDP
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable broadcasting on the socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Enable reusing the port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Bind the socket to the port
        sock.bind(("", self.__port))
        while not self.__shutdown:
            # data from the server
            data: bytes
            # address and port of the server
            addr: tuple[str, int]
            # purposefully set 1 byte more than the message length to check for errors
            # recvfrom is a blocking call - no busy waiting.
            data, addr = sock.recvfrom(OFFER_MSG_LEN + 1)
            # check for correct offer message structure and values.
            if(len(data) == OFFER_MSG_LEN &
                data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN] == COOKIE &
                  data[TYPE_IDX] == TYPE_OFFER):
                # H for unsigned short (2 bytes)
                # < for little endian
                self.request_file(addr[0],
                                   struct.unpack("<H", data[OFFER_UDP_IDX:OFFER_UDP_IDX+OFFER_UDP_LEN])[0],
                                   struct.unpack("<H", data[OFFER_TCP_IDX:OFFER_TCP_IDX+OFFER_TCP_LEN])[0])
            

    def shutdown(self) -> None:
        """
        Shuts down the client, preventing it from receiving further offers.
        If the client runs a task currently, it will finish it before termination.
        """
        self.shutdown = True
    
    def request_file(self, server_addr: str, server_udp_port: int, server_tcp_port: int) -> None:
        for i in range(self.__tcp_connections_num):
            threading.Thread(target=self.tcp_connect, args=(server_addr, server_tcp_port)).start()
        for i in range(self.__udp_connections_num):
            threading.Thread(target=self.udp_connect, args=(server_addr, server_udp_port)).start()
            
            
    def tcp_connect(self, server_addr: str, server_tcp_port: int) -> None:
        pass
    
    def udp_connect(self, server_addr: str, server_udp_port: int) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr: tuple[str, int] = (server_addr, server_udp_port)
        request_msg: bytes = struct.pack(COOKIE, TYPE_REQUEST, self.__data_size)
        req_data_size: int = struct.unpack("Q", self.__data_size)[0]
        data_left: int = req_data_size

        start_time: float = time.time()
        sock.sendto(request_msg, addr)
        try:
            while(data_left > 0):
                data, server = sock.recvfrom(MAX_PAYLOAD_MSG_SIZE)
                if(data[COOKIE_IDX] != COOKIE & data[TYPE_IDX] != TYPE_PAYLOAD):
                    print ("Received a non-payload message from the server.")
                    return
                # calculate the actual payload length
                payload_len: int = len(data[PAYLOAD_DATA_IDX:])
                data_left -= payload_len
            
            end_time: float = time.time()
            transfer_time: float = end_time - start_time
            transfer_rate: float = BYTE_SIZE*req_data_size / transfer_time
            print ("UDP connection to server {}:{} finished. Transfer rate: {} bits/sec."
                   .format(server_addr, server_udp_port, transfer_rate))

        except socket.timeout:
            print ("UDP connection to server {}:{} timed out.".format(server_addr, server_udp_port))
            return

        
