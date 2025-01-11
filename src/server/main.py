import sys

from server import Server

UDP_PORT_INDEX = 1
TCP_PORT_INDEX = 2


def main() -> None:
    udp_port: int
    tcp_port: int

    try:
        udp_port = int(sys.argv[UDP_PORT_INDEX])
        tcp_port = int(sys.argv[TCP_PORT_INDEX])
    except Exception:
        print("Invalid command line arguments. Format: <udp_port> <tcp_port>")
        return
    
    # Get the port numbers from the user
    server: Server = Server(udp_port, tcp_port)

if __name__ == '__main__':
    main()
