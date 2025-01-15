import sys
import threading

from client import Client

PORT_IDX = 1

def main() -> None:
    __port: int
    __data_size: int
    __tcp_connections_num: int
    __udp_connections_num: int
    try:
        __port = int(sys.argv[PORT_IDX])
    except Exception:
        print("Invalid command line argument, missing port number.")
        return

    # Gets the data size, TCP connections number and UDP connections number from the user
    __data_size = get_data_size()
    __tcp_connections_num = get_connections_num("TCP")
    __udp_connections_num = get_connections_num("UDP")

    # Initializes the client
    client = Client(__port, __data_size, __tcp_connections_num, __udp_connections_num)
    # Runs the client
    threading.Thread(target=client.run(), args=()).start()
    input("Press any key to shutdown the client, this will prevent further connections")
    client.shutdown()
    
def get_data_size() -> int:
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
    connections_num: str = input(f"Enter amount of {connection_type} connections: ")
    if (not connections_num.isnumeric()):
        print("Invalid input, please enter a number")
        connections_num = get_connections_num(connection_type)
    return connections_num
    
if __name__ == '__main__':
    main()
