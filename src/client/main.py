from client import Client

def main() -> None:
    data_size: int
    tcp_connections_num: int
    udp_connections_num: int

    # Gets the data size, TCP connections number and UDP connections number from the user
    data_size = get_data_size()
    tcp_connections_num = get_connections_num("TCP")
    udp_connections_num = get_connections_num("UDP")

    # Initializes the client
    client = Client(data_size, tcp_connections_num, udp_connections_num)
    # Runs the client
    client.run()
    
def get_data_size() -> int:
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
