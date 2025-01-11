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
        while not self.__shutdown:
            sock: socket.socket = None
            # TODO - Look for a server
            self.request_file()

    def shutdown(self) -> None:
        """
        Shuts down the client, preventing it from receiving further offers.
        If the client runs a task currently, it will finish it before termination.
        """
        pass
    
    def request_file(self, server_addr: str, server_udp_port: int, server_tcp_port: int) -> None:
        for i in range(self.__tcp_connections_num):
            # TODO - Create a new thread for each tcp connection with the method tcp_connect
            pass
        for i in range(self.__udp_connections_num):
            # TODO - Create a new thread for each udp connection with the method udp_connect
            pass
        pass

    def tcp_connect(self, server_addr: str, server_tcp_port: int) -> None:
        pass
    
    def udp_connect(self, server_addr: str, server_udp_port: int) -> None:
        pass
