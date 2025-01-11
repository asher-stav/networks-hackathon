from client import Client

def main() -> None:
    data_size: int
    tcp_connections_num: int
    udp_connections_num: int
    # Asks the user for the file size, the amount of
    # TCP connections and the amount of UDP connections
    # Creates a new Client object with the given values
    # TODO: Implement the user input
    client = Client(data_size, tcp_connections_num, udp_connections_num) # Initializes the client
    # Runs the client
    client.run()

if __name__ == '__main__':
    main()
