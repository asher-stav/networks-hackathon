import sys
import threading

import logger
from server import Server

# command line arguments indexes
UDP_PORT_INDEX = 1
TCP_PORT_INDEX = 2
BROADCAST_PORT_INDEX = 3


def main() -> None:
    udp_port: int
    tcp_port: int
    broadcast_port: int

    try:
        udp_port = int(sys.argv[UDP_PORT_INDEX])
        tcp_port = int(sys.argv[TCP_PORT_INDEX])
        broadcast_port = int(sys.argv[BROADCAST_PORT_INDEX])
    except Exception:
        logger.error("Invalid command line arguments. Format: <udp_port> <tcp_port> <broadcast_port>")
        return
    
    server: Server = Server(udp_port, tcp_port, broadcast_port)
    logger.info('Starting server. Press any key to terminate')
    threading.Thread(target=server.run).start()
    threading.Thread(target=shutdown, args=(server, )).start()

def shutdown(s: Server) -> None:
    """
    Listens for user input and then shuts down the server
    """
    input()
    s.shutdown()


if __name__ == '__main__':
    main()
