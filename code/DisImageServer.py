#Distributed Image Server - Omer Kfir, Yuval Mendel
import pygame, threading, protocol
import numpy as np

client_objects = []
empty_quartes = [1, 2, 3, 4]

ADRESS = "0.0.0.0"
PORT = 12345

lock = threading.Lock()
task_running = True

# Screen dimensions
CUBE_SIZE = 50 
SCREEN_WIDTH = CUBE_SIZE * 8
SCREEN_HEIGHT = CUBE_SIZE * 8

SCALE = 4
BLACK = (0, 0, 0)

FPS = 20
SPEED = 2

constructed_image = np.full((50, 50, 3), (255, 255, 255), dtype=np.uint8)

def initialize_screen():
    """
        Initialize the screen before starting
    """

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Distributed image")
    return screen

def handle_movement(keys, x, y) -> tuple[int, int]:
    """
        Moves cube accroding to player
    """

    global task_running

    if keys[pygame.K_UP] and y > 0:
        y -= SPEED
    if keys[pygame.K_DOWN] and y < SCREEN_HEIGHT - CUBE_SIZE * SCALE:
        y += SPEED
    if keys[pygame.K_LEFT] and x > 0:
        x -= SPEED
    if keys[pygame.K_RIGHT] and x < SCREEN_WIDTH - CUBE_SIZE * SCALE:
        x += SPEED
    if keys[pygame.K_ESCAPE]:
        task_running = False
    return x, y

def draw_cube(surface, array, offset_x, offset_y) -> None:
    """
        Draws numpy 2d array on screen
    """

    for row in range(CUBE_SIZE):
        for col in range(CUBE_SIZE):
            color_value = tuple(array[row, col])  # Grayscale value from NumPy array

            x = (col * SCALE) + offset_x
            y = (row * SCALE) + offset_y
            
            pygame.draw.rect(
                surface,  # Surface to draw on
                color_value,  # Color for the rectangle
                pygame.Rect(x, y, SCALE, SCALE)  # Rectangle position and size
            )

def calc_chunk_index(quarter : int, height : int, width : int) -> tuple[int, int]:
    """
        Calculates right index for chunk quarter in 2d array
    """

    h, w = 0, 0
    if quarter == 2 or quarter == 4:
        w = 50 - width
    if quarter == 3 or quarter == 4: 
        h = 50 - height
    
    return h, w
        

def recv_chunks() -> None:
    """
        Receive image chunks for each quarter.
    """

    global client_objects, empty_quartes, task_running, constructed_image

    while task_running:
        temp_image = np.full((50, 50, 3), (0, 0, 0), dtype=np.uint8)
        
        for client_object in client_objects:
            try:
                client_socket, client_quarter = client_object
                # Server requests an image chunk
                protocol.send_message(client_socket, (protocol.IMAGE_CHUNK_RECV, b""))

                # Server receives an image chunk
                msg_type, image_chunk = protocol.recv_message(client_socket)
                if msg_type == protocol.CLIENT_DISCONNECT:
                    raise Exception

                chunk_height, chunk_width = image_chunk.shape
                h, w = calc_chunk_index(client_quarter, chunk_height, chunk_width)
            
                temp_image[h:h + chunk_height, w:w+chunk_width] = image_chunk
            except:

                # If got an exception close the connection and erase clear the quarter
                with lock:
                    protocol.remove_client(client_object)
                
                print(f">>>Client chunk {client_object[1]} has disconnected>>>")
        
        # Update global image
        constructed_image = temp_image


def recv_clients() -> None:
    """
        Receive clients for avaliable quarters.
    """

    global client_objects, empty_quartes, task_running
    server_socket = protocol.create_server(ADRESS, PORT)

    print(">>>Server running>>>")

    # Receive Clients
    while task_running:
        client_object = protocol.recv_client(server_socket, empty_quartes)

        if not client_socket:

            # Clients can also disconnect and so list client_objects can be changed
            # From other functions, so a lock is needed

            with lock:
                client_objects.append(client_object)
            print(f">>>Received new client, chunk {client_object[1]}>>>")

        else:
            print(f">>>Rejected client, chunk {client_object[1]} is already taken>>>")
    
    # Close sockets
    for client_socket, _ in client_objects:
        protocol.send_message(client_socket, (protocol.SERVER_DISCONNECT, b""))
        protocol.close(client_socket)
    
    protocol.close(server_socket)
    print(">>>Closed all sockets>>>")


def main():

    global task_running

    # Create thread which receives clients and a thread which receives the image chunks
    #clients_recv_thread = threading.Thread(target=recv_clients, args=())
    #chunks_recv_thread = threading.Thread(target=recv_chunks, args=()) 

    screen = initialize_screen()
    x = (SCREEN_WIDTH - CUBE_SIZE) // 2
    y = (SCREEN_HEIGHT - CUBE_SIZE) // 2
    clock = pygame.time.Clock()

    while task_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                task_running = False

        # Handle any movement or key actions
        keys = pygame.key.get_pressed()
        x, y = handle_movement(keys, x, y)

        # Fill the screen with black before drawing
        screen.fill(BLACK)

        # Draw the constructed image at the new position
        draw_cube(screen, constructed_image, x, y)

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(FPS)

    pygame.quit()

    # Close threads
    #chunks_recv_thread.join()
    #clients_recv_thread.join()
    print(">>>Closed all threads>>>")

if __name__ == "__main__":
    main()