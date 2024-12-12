#Distributed Image Client - Omer Kfir, Yuval Mendel
import sys, protocol

dest_address = "IP"
dest_port = 0


def main():

    # Check if correct arguments passed in command line
    if len(sys.argv) != 2:
        print("Incorrect Usage - python DisImageClient.py <Client Number>")
        return
    
    client_image_quarter = int(sys.argv[1])
    if client_image_quarter > 4 or client_image_quarter < 1:
        print("Incorrect Usage - Client number range is 1-4")
        return
    
    # Create client socket
    client_socket = protocol.connect(dest_address, dest_port, client_image_quarter)
    if not client_socket:
        return
    
    
    
    

if __name__ == "__main__":
    main()