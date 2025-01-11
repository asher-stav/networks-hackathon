import socket
import struct
import threading

class Client:
    """
    A class representing a client that can connect to servers and run speed-tests on them, both with UDP and TCP connections.
    In addition, will collect interesting data about the servers and the connections.
    """
    __shutdown: bool
    __data_size: int
    __tcp_connections_num: int
    __udp_connections_num: int
    
    def __init__(self, data_size: int, tcp_connections_num: int, udp_connections_num: int):
        self.__shutdown = False
        self.__data_size = data_size
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
        # Bind the socket to the port - route -> 1 up in the keyboard ;)
        sock.bind(("", 49753))
        while not self.__shutdown:
            # data from the server
            data: bytes
            # address and port of the server
            addr: tuple[str, int]
            # receive data from the server, 10 bytes - length of the message,
            # purposefully set 1 byte more than the message length to check for errors
            # recvfrom is a blocking call - no busy waiting.
            data, addr = sock.recvfrom(10)
            # 9 bytes is the expected size of the offer message.
            # 0xabcddcba is the magic cookie
            # 0x2 is the offer message type
            if(len(data) == 9 & data[0:4] == 0xabcddcba & data[4] == 0x2):
                # H for unsigned short (2 bytes)
                # < for little endian
                self.request_file(addr[0], struct.unpack("<H", data[6:8])[0], struct.unpack("<H", data[8:10])[0])
            

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
        pass
