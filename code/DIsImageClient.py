#Distributed Image Client - Omer Kfir, Yuval Mendel
import sys, protocol, random
import numpy as np

dest_address = "127.0.0.1"
dest_port = 12345
class Image:
    
    IMAGE_HEIGHT = 100
    IMAGE_WIDTH = 100


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
    def get_part_of_image(self, absolute_x, absolute_y, width, height):
        if self.quarter == 1:
            return self.color_array[absolute_y:min(absolute_y+height, self.IMAGE_HEIGHT), absolute_x:min(absolute_x+width, self.IMAGE_WIDTH)]
        elif self.quarter == 2:
            pass
        elif self.quarter == 3:
            pass
        elif self.quarter == 4:
            pass


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
    #connection made

    #generate client image
    client_image = Image(client_image_quarter)

    

if __name__ == "__main__":
    main()
    