import sys
import threading

from client import Client

PORT_IDX = 1

def main() -> None:
    port: int
    data_size: int
    tcp_connections_num: int
    udp_connections_num: int
    try:
        port = int(sys.argv[PORT_IDX])
    except Exception:
        print("Invalid command line argument, missing port number.")
        return

    # Gets the data size, TCP connections number and UDP connections number from the user
    data_size = get_data_size()
    tcp_connections_num = get_connections_num("TCP")
    udp_connections_num = get_connections_num("UDP")

    # Initializes the client
    client = Client(port, data_size, tcp_connections_num, udp_connections_num)
    # Runs the client
    print('Starting client. Press any key to terminate')
    threading.Thread(target=client.run, args=()).start()
    threading.Thread(target=shutdown, args=(client, )).start()

def shutdown(client: Client) -> None:
    """
    Listens for user input and then shuts down the client
    """
    input()
    client.shutdown()
    
def get_data_size() -> int:
    """
    Gets the amount of data the client wants to request the server, according to the unit
    (bytes, kilobytes, megabytes and gigabytes)
    """
    data_size: int
    user_choice: int = input("""what unit would you like to enter the file size in?
1) bytes
2) kilobytes
3) megabytes
4) gigabytes
Input: """)
    data_req_str: str = "Enter file size (in {unit}): "
    match user_choice:
        case '1':
            data_size = int(input(data_req_str.format(unit="bytes")))
        case '2':
            data_size = int(input(data_req_str.format(unit="kilobytes"))) * 1024
        case '3':
            data_size = int(input(data_req_str.format(unit="megabytes"))) * 1024 * 1024
        case '4':
            data_size = int(input(data_req_str.format(unit="gigabytes"))) * 1024 * 1024 * 1024
        case _:
            print("Invalid choice, please try again")
            data_size = get_data_size()
    return data_size
    
def get_connections_num(connection_type: str) -> int:
    """
    Gets the amount of connections the client wants to make to the server
    for the given type (TCP or UDP)
    """
    connections_num: str = input(f"Enter amount of {connection_type} connections: ")
    if not connections_num.isnumeric():
        print("Invalid input, please enter a number")
        connections_num = get_connections_num(connection_type)
    return int(connections_num)
    
if __name__ == '__main__':
    main()
