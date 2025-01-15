import sys
import threading
import signal

from server import Server

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
        print("Invalid command line arguments. Format: <udp_port> <tcp_port> <broadcast_port>")
        return
    
    s: Server = Server(udp_port, tcp_port, broadcast_port)
    print('Starting server. Press any key to terminate')
    threading.Thread(target=s.listening).start()
    threading.Thread(target=shutdown, args=(s, )).start()

def shutdown(s: Server) -> None:
    input()
    s.shutdown()


if __name__ == '__main__':
    main()
