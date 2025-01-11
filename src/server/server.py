import socket
import struct
import threading


COOKIE = 0xabcddcba
UDP_OFFER_MSG_CODE = 0x2
UDP_REQUEST_MSG_CODE = 0x3
UDP_PAYLOAD_MSG_CODE = 0x4


class Server:
    """
    Server class that listens for incoming connections from clients in either UDP or TCP.
    When a client requests, the server sends an amount of data as requested.
    """
    __shutdown: bool
    __udp_port: int
    __tcp_port: int
    
    def __init__(self, udp_port: int, tcp_port: int):
        self.__shutdown = False
        self.__udp_port = udp_port
        self.__tcp_port = tcp_port
    
    def listening(self):
        ip: str = ''
        offer_sock: socket.socket = None
        # TODO - start listening to clients
        print(f'Server started, listening on IP address {'TODO'}') 
        self.announcer(offer_sock)

    def shutdown(self) -> None:
        """
        Shuts down the server, preventing it from receiving further new client connections.
        Finishes handling existing connections before termination
        """
        pass        
            
    def announcer(self, sock: socket.socket):
        while not self.__shutdown:
            # TODO - send offers every 1 second.
            pass
        
    def listen_udp(self):
        pass

    def listen_tcp(self):
        pass

    def handle_udp_connection(self):
        pass

    def handle_tcp_connection(self):
        pass
