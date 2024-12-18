#Distributed Image Client - Omer Kfir, Yuval Mendel
import sys, protocol, random, pickle, time
import numpy as np

dest_address = "127.0.0.1"
dest_port = 12345

RANDOM_PIXEL_COUNT = 40

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

        # Define the boundaries for the client's region
        if self.quarter == 1:  # Top-left
            client_start_x, client_start_y = 0, 0
        elif self.quarter == 2:  # Top-right
            client_start_x, client_start_y = self.IMAGE_WIDTH, 0
        elif self.quarter == 3:  # Bottom-left
            client_start_x, client_start_y = 0, self.IMAGE_HEIGHT
        elif self.quarter == 4:  # Bottom-right
            client_start_x, client_start_y = self.IMAGE_WIDTH, self.IMAGE_HEIGHT

        client_end_x = client_start_x + self.IMAGE_WIDTH
        client_end_y = client_start_y + self.IMAGE_HEIGHT

        # Calculate the boundaries of the requested block
        block_end_x = absolute_x + self.SCREEN_SIZE
        block_end_y = absolute_y + self.SCREEN_SIZE

        # Find the overlapping region between the block and the client
        overlap_start_x = max(absolute_x, client_start_x)
        overlap_end_x = min(block_end_x, client_end_x)

        overlap_start_y = max(absolute_y, client_start_y)
        overlap_end_y = min(block_end_y, client_end_y)

        # Check if there is no overlap
        if overlap_start_x >= overlap_end_x or overlap_start_y >= overlap_end_y:
            return np.empty((0, 0, 3), dtype=self.color_array.dtype)  # No part of the block is in the client's region

        # Calculate local coordinates within the client's image
        local_start_x = overlap_start_x - client_start_x
        local_end_x = overlap_end_x - client_start_x

        local_start_y = overlap_start_y - client_start_y
        local_end_y = overlap_end_y - client_start_y

        # Extract and return the overlapping part of the image
        return self.color_array[local_start_y:local_end_y, local_start_x:local_end_x]


def send_chunks(client_socket, client_image : Image) -> None:
    """
        Send image chunks to server
    """
    
    random_pixel_cnt = 0
    while True:
        try:
            # Client receives an request from server
            msg_type, place = protocol.recv_message(client_socket)
            if msg_type == protocol.SERVER_DISCONNECT:
                raise Exception
            
            if random_pixel_cnt == 0:
                client_image.replace_random_pixel()

            # Calculate place of cube on map
            x, y = map(int, place.decode().split("~"))
            image_chunk = pickle.dumps(client_image.get_part_of_image(x, y))

            # Client sends the image chunk
            protocol.send_message(client_socket, (protocol.IMAGE_CHUNK_SEND, image_chunk))
            random_pixel_cnt = (random_pixel_cnt + 1) % RANDOM_PIXEL_COUNT
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
    