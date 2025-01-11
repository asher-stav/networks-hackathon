from logging import shutdown
import socket
import struct
import threading
import time


COOKIE = 0xabcddcba
UDP_OFFER_MSG_CODE = 0x2
UDP_REQUEST_MSG_CODE = 0x3
UDP_PAYLOAD_MSG_CODE = 0x4

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
        ip: str = ''
        # TODO - start listening to clients
        offer_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        offer_thread: threading.Thread = threading.Thread(target=self.announcer, args=(offer_sock, ))
        offer_thread.start()

        print(f'Server started, listening on IP address {'TODO'}')
        self.announcer(offer_sock)

    def shutdown(self) -> None:
        """
        Shuts down the server, preventing it from receiving further new client connections.
        Finishes handling existing connections before termination
        """
        pass        
            
    def announcer(self, sock: socket.socket) -> None:
        """
        Sends offers to connect to the server every second
        """
        while not self.is_shutdown():
            self.send_upd_offer(sock)
            time.sleep(1)

    def send_upd_offer(self, sock: socket.socket) -> None:
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
        message += struct.pack('>H', UDP_OFFER_MSG_CODE, self.__udp_port, self.__tcp_port)
        sock.sendto(message, (BROADCAST_IP, self.__broadcast_port))
        
    def listen_udp(self):
        pass

    def listen_tcp(self):
        pass

    def handle_udp_connection(self):
        pass

    def handle_tcp_connection(self):
        pass
