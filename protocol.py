#Distributed Image Protocol - Omer Kfir, Yuval Mendel
import socket

# Messages types -> Client to server
IMAGE_CHUNK_SEND = b"IMS"
CLIENT_DISCONNECT = b"CLD"

CLIENT_ID = b"CCI"

# Server to Client
IMAGE_CHUNK_RECV = b"IMR"
SERVER_DISCONNECT = b"SLD"

SERVER_ACK = b"ACK"
SERVER_REJECT = b"REJ"

MSG_TYPE_INDEX = 0
MSG_DATA_INDEX = 1

MSG_TYPE_LEN = 3
MSG_LEN_LEN = 8

DEBUG_FLAG = True

def construct_message_send(msg_type : bytes, msg_data : bytes) -> bytes:
    """
        Builds message to send
        by protocol rules
    """
    msg_to_send = msg_type
    msg_to_send += msg_data
    
    return msg_to_send


def deconstruct_message_recv(msg_recv : bytes) -> tuple[bytes, bytes]:
    """
        Deconstruct message received
        By protocol rules
    """
    
    msg_type = msg_recv[MSG_LEN_LEN:MSG_LEN_LEN + MSG_TYPE_LEN]
    msg_data = msg_recv[MSG_LEN_LEN + MSG_TYPE_LEN:]
    
    return msg_type,msg_data


def send_message(sock : socket.socket, msg : tuple[bytes, bytes]) -> None:
    """
        Send constructed message
    """
    
    msg = construct_message_send(*msg)
    send_with_size(sock, msg)


def recv_message(sock : socket.socket) -> tuple[bytes, bytes]:
    """
        Recv constructed message
    """

    msg = __recv_by_size(sock)
    msg = deconstruct_message_recv(msg)
    
    return msg


def connect(dest_addr : str, dest_port : int, client_quarter : int) -> socket.socket:
    """
        Client Socket connect to destination
        Sends Client ID
    """
    
    sock = socket.socket()
    sock.connect((dest_addr, dest_port))
    
    # Send ID of client to the server
    client_quarter = str(client_quarter).encode()
    send_message(sock, (CLIENT_ID, client_quarter))
    
    server_ans = recv_message(sock)[MSG_TYPE_INDEX]
    if server_ans == SERVER_ACK:
        print(f"Client Connect to {dest_addr}:{dest_port}, quarter - {client_quarter}")
    
    else:
        print("BLOCKED BY JAMES!!!!!!!☹")
        
        sock.close()
        sock = None
    
    return sock


def recv_client(sock : socket.socket, empty_quartes : list[int]) -> socket.socket:
    """
        Server Receives new client
    """
    
    return_code = SERVER_REJECT
    
    # Accept new client
    client_socket, _ = sock.accept()
    msg_type, msg_data = recv_message(client_socket)
    
    if msg_type == CLIENT_ID:
        msg_data = int(msg_data.decode())
        
        # Check if client quarter is not already used
        if msg_data in empty_quartes:
            empty_quartes.remove(msg_data)
            return_code = SERVER_ACK
        
    
    send_message(client_socket, (return_code, b""))
    
    # If data was not valid close socket
    if return_code == SERVER_REJECT:
        client_socket.close()
        client_socket = None
    
    # Return client socket
    return client_socket


def create_server(addr : str, port : int) -> socket.socket:
    """
        Creates server socket
    """
    
    sock = socket.socket()
    sock.bind((addr, port))
    sock.listen(4)
    
    return sock
    
    

"""
    TCP by size
"""

def __log(prefix, data, max_to_print=100):
    if not DEBUG_FLAG:
        return
    data_to_log = data[:max_to_print]
    if type(data_to_log) == bytes:
        try:
            data_to_log = data_to_log.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
    print(f"\n{prefix}({len(data)})>>>{data_to_log}")


def __recv_amount(sock, size=4):
    buffer = b''
    while size:
        new_bufffer = sock.recv(size)
        if not new_bufffer:
            return b''
        buffer += new_bufffer
        size -= len(new_bufffer)
    return buffer


def __recv_by_size(sock, return_type="bytes"):
    try:
        data = b''
        data_len = int(__recv_amount(sock, MSG_LEN_LEN))
        # code handle the case of data_len 0
        data = __recv_amount(sock, data_len)
        __log("Receive", data)
        if return_type == "string":
            return data.decode()
    except:
        data = '' if return_type == "string" else b''
    return data


def __send_with_size(sock, data):
    if len(data) == 0:
        return
    try:
        if type(data) != bytes:
            data = data.encode()
        len_data = str(len(data)).zfill(MSG_LEN_LEN).encode()
        data = len_data + data
        sock.sendall(data)
        __log("Sent", data)
    except OSError:
        print('ERROR: send_with_size with except OSError')