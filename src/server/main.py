from server.server import Server

def main() -> None:
    udp_port: int
    tcp_port: int
    
    # Get the port numbers from the user
    server: Server = Server(udp_port, tcp_port)

if __name__ == '__main__':
    main()
