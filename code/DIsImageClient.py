#Distributed Image Client - Omer Kfir, Yuval Mendel
import sys, protocol, random, pickle
import numpy as np

dest_address = "127.0.0.1"
dest_port = 12345

class Image:
    
    IMAGE_HEIGHT = 100
    IMAGE_WIDTH = 100
    
    SCREEN_SIZE = 50

    # static mathod for generating a random color
    def get_random_color():
        return [random.randrange(256), random.randrange(256), random.randrange(256)]
    
    def __init__(self, quarter):
        self.color = Image.get_random_color()
        shape = (self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3)
        self.color_array = np.full(shape, self.color, dtype=np.uint8)
        self.quarter = quarter
    
    # replace a random pixel to a random color
    def replace_random_pixel(self):
        rand_x = random.randrange(self.IMAGE_WIDTH)
        rand_y = random.randrange(self.IMAGE_HEIGHT)
        self.color_array[rand_y, rand_x] = Image.get_random_color()
    
    #gives the part of the image that is relevet
    def get_part_of_image(self, absolute_x, absolute_y):
        if self.quarter == 1:
            return self.color_array[absolute_y:min(absolute_y+self.SCREEN_SIZE, self.IMAGE_HEIGHT), absolute_x:min(absolute_x+self.SCREEN_SIZE, self.IMAGE_WIDTH)]
        elif self.quarter == 2:
            pass
        elif self.quarter == 3:
            pass
        elif self.quarter == 4:
            pass


def send_chunks(client_socket, client_image : Image) -> None:
    """
        Send image chunks to server
    """
    
    while True:
        try:
            # Client receives an request from server
            msg_type, place = protocol.recv_message(client_socket)
            if msg_type == protocol.SERVER_DISCONNECT:
                raise Exception

            # Calculate place of cube on map
            x, y = map(int, place.decode().split("~"))
            image_chunk = pickle.dumps(client_image.get_part_of_image(x, y))

            # Client sends the image chunk
            protocol.send_message(client_socket, (protocol.IMAGE_CHUNK_SEND, image_chunk))
        except Exception as error:
            
            protocol.close(client_socket)
            print(f"{error}\nDisconnecting from server.")
            
            break
    


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
    print("Connected Succesfully to server")

    #generate client image
    client_image = Image(client_image_quarter)
    send_chunks(client_socket, client_image)

    

if __name__ == "__main__":
    main()
    