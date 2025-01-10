import socket
import struct
import threading

class Client:
    shutdown: bool = False
    data_size: int
    tcp_connections_num: int
    udp_connections_num: int

    
    def __init__(self, data_size: int, tcp_connections_num: int, udp_connections_num: int):
        self.data_size = data_size
        self.tcp_connections_num = tcp_connections_num
        self.udp_connections_num = udp_connections_num
        
    # Runs the client until stopped, constntly looking for servers to run a speedtest on.
    def run(self):
        while(not self.shutdown):
            sock : socket
            # TODO - Look for a server, and connect to it
            self.request_file(sock)
    
    def request_file(self, sock: socket):
        for i in range(self.tcp_connections_num):
            # TODO - Create a new thread for each tcp connection with the method tcp_connect
            pass
        for i in range(self.udp_connections_num):
            # TODO - Create a new thread for each udp connection with the method udp_connect
            pass
        pass

    def tcp_connect():
        pass
    
    def udp_conenct():
        pass