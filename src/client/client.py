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
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting on the socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Enable reusing the port
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(('', self.__port))
        while not self.__shutdown:
            data: bytes
            addr: tuple[str, int]
            # purposefully set 1 byte more than the message length to check for errors
            data, addr = sock.recvfrom(OFFER_MSG_LEN)

            # check for correct offer message structure and values.
            if len(data) == OFFER_MSG_LEN:
                cookie = struct.unpack("I", data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN])[0]
                type = struct.unpack("B", data[TYPE_IDX:TYPE_IDX+TYPE_LEN])[0]
                if cookie == COOKIE and type == TYPE_OFFER:
                    # H for unsigned short (2 bytes)
                    self.request_file(addr[0],
                                    struct.unpack("H", data[OFFER_UDP_IDX:OFFER_UDP_IDX+OFFER_UDP_LEN])[0],
                                    struct.unpack("H", data[OFFER_TCP_IDX:OFFER_TCP_IDX+OFFER_TCP_LEN])[0])
                else:
                    print("Received invalid cookie or msg type")
            else:
                print("Received msg of unexpected length")
        sock.close()
            

    def shutdown(self) -> None:
        """
        Shuts down the client, preventing it from receiving further offers.
        If the client runs a task currently, it will finish it before termination.
        """
        self.__shutdown = True
    
    def request_file(self, server_addr: str, server_udp_port: int, server_tcp_port: int) -> None:
        for i in range(self.__tcp_connections_num):
            threading.Thread(target=self.tcp_connect, args=(server_addr, server_tcp_port)).start()
        for i in range(self.__udp_connections_num):
            threading.Thread(target=self.udp_connect, args=(server_addr, server_udp_port)).start()
            
            
    def tcp_connect(self, server_addr: str, server_tcp_port: int) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr: tuple[str, int] = (server_addr, server_tcp_port)
        # Prepare the request message
        cookie = struct.pack('I', COOKIE)
        type_offer = struct.pack('H', TYPE_REQUEST)
        request_msg: bytes = cookie + type_offer + self.__data_size
        req_data_size: int = struct.unpack("Q", self.__data_size)[0]
        data_left: int = req_data_size

        try:
            # Connect to the server
            sock.connect(addr)
            print(f"Connected to server {server_addr}:{server_tcp_port} via TCP.")

            # Send the request message
            sock.sendall(request_msg)
            print(f"Sent request message of {req_data_size} bytes to the connected server.")

            # Receive data
            start_time: float = time.time()
            while data_left > 0:
                data: bytes = sock.recv(MAX_PAYLOAD_MSG_SIZE)
                if not data:
                    print("Server closed the connection.")
                    return

                cookie: int = struct.unpack('I', data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN])
                if cookie != COOKIE:
                    print(f'Error: received invalid cookie: {cookie}')
                    print('Closing socket...')
                    sock.close()
                    return
                    
                message_type: int = struct.unpack('B', data[TYPE_IDX:TYPE_IDX+TYPE_LEN])
                if message_type != TYPE_PAYLOAD:
                    print(f'Error: received invalid message type: {message_type}. Expected: {TYPE_REQUEST}')
                    print('Closing socket...')
                    sock.close()
                    return
                
                # Calculate the actual payload length
                payload_len: int = len(data[PAYLOAD_DATA_IDX:])
                data_left -= payload_len

            end_time: float = time.time()
            transfer_time: float = end_time - start_time
            transfer_rate: float = BYTE_SIZE * req_data_size / transfer_time

            print(f"TCP connection to server {server_addr}:{server_tcp_port} finished. "
                f"Transfer rate: {transfer_rate} bits/sec.")

        except socket.error as e:
            print(f"TCP connection error: {e}")

        finally:
            sock.close()
            print("Connection closed.")
    
    def udp_connect(self, server_addr: str, server_udp_port: int) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr: tuple[str, int] = (server_addr, server_udp_port)
        cookie = struct.pack('I', COOKIE)
        type_offer = struct.pack('H', TYPE_REQUEST)
        request_msg: bytes = cookie + type_offer + self.__data_size
        req_data_size: int = struct.unpack("Q", self.__data_size)[0]
        data_left: int = req_data_size

        try:
            sock.sendto(request_msg, addr)
            print("Sent request message of {} bytes to server {}:{} via UDP.".format(req_data_size, server_addr, server_udp_port))
            start_time: float = time.time()

            while(data_left > 0):
                data, server = sock.recvfrom(MAX_PAYLOAD_MSG_SIZE)
                if not data:
                    print ("Did not receive data from the server.")
                    continue
                cookie: int = struct.unpack('I', data[COOKIE_IDX:COOKIE_IDX+COOKIE_LEN])
                if cookie != COOKIE:
                    print(f'Error: received invalid cookie: {cookie}')
                    continue
                
                message_type: int = struct.unpack('B', data[TYPE_IDX:TYPE_IDX+TYPE_LEN])
                if message_type != TYPE_PAYLOAD:
                    print(f'Error: received invalid message type: {message_type}. Expected: {TYPE_REQUEST}')
                    continue

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

        
