import sys
import pygame
from pygame.locals import *
import threading
import queue
import time
import subprocess
import os

# Import your API call function
from test_game.api_npc.api_npc import run

with open(r'..\requirements.txt', 'r', encoding='utf-16') as f:
    requirements = f.read().splitlines()
    for package in requirements:
        subprocess.run(['pip', 'install', package])
    print(requirements)

# For local streaming, the websockets are hosted without ssl - http://
HOST = '127.0.0.1:5001'
URI = f'http://{HOST}/api/v1/generate'

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/chat'

print("Running command")

# Define the command to run
command = [
    'koboldcpp\\koboldcpp_nocuda.exe',
    'koboldcpp\\models\\mistral-7b-instruct-v0.1.Q4_K_M.gguf',
    '--skiplauncher'
]

def start_server(comand):
    process = subprocess.run(command, capture_output=True, text=True)
    print("Return Code:", process.returncode)
    if process.stderr:
        print("Error Output:", process.stderr)

# Start the server
threading.Thread(target=start_server, args=(command,)).start()

history = []

# Initialize the game engine
pygame.init()

# Set the height and width of the screen [width, height]
size = [640, 480]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Condescending Narrator")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)

# Initialize the game variables
done = False
clock = pygame.time.Clock()
x, y = 50, 320
speedx, speedy = 0, 0
font = pygame.font.Font(None, 24)
text_surface = []
api_call_in_progress = False
text_queue = queue.Queue()

# Initialize last_generate before the loop
last_generate = time.monotonic()


def generate_text(user_input):
    global api_call_in_progress
    global history
    response = run(user_input, history)
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]
    response = response.strip()
    history.append(response)
    text_queue.put(response)
    api_call_in_progress = False


def wrap_text(text, font, max_width):
    """
    Wrap text to fit within a given width when rendered.
    :param text: The text to be wrapped.
    :param font: The font to be used when rendering the text.
    :param max_width: The maximum width in pixels for the text.
    :return: A list of lines that make up the wrapped text.
    """
    words = text.split(' ')
    lines = []
    while words:
        line = ''
        while words and font.size(line + words[0])[0] <= max_width:
            line += (words.pop(0) + " ")
        lines.append(line)
    return lines


# Main loop of the game
while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                speedx = -3
            elif event.key == K_RIGHT:
                speedx = 3
            elif event.key == K_UP:
                speedy = -3
            elif event.key == K_DOWN:
                speedy = 3
        elif event.type == KEYUP:
            if event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                speedx, speedy = 0, 0

    x += speedx
    y += speedy
    x = max(0, min(size[0] - 20, x))
    y = max(0, min(size[1] - 30, y))

    # Fill the screen with black background
    screen.fill(black)

    # Draw the white block (player)
    pygame.draw.rect(screen, white, (x, y, 20, 30))

    # Check for text to display and wrap it on the screen
    if not text_queue.empty():
        try:
            response = text_queue.get()
            wrapped_text = wrap_text(response, font, size[0] - 20)  # Adjust the width as needed
            text_surface = [font.render(line, True, white) for line in wrapped_text]
        except AttributeError:
            pass
        except TypeError:
            pass

    # Blit the text surfaces onto the screen
    y_offset = 10  # Starting Y position to blit text. Adjust as needed.
    for surface in text_surface:
        screen.blit(surface, (10, y_offset))
        y_offset += font.get_linesize()  # Move Y position for next line

    # Trigger a new API call if needed
    if not api_call_in_progress and (time.monotonic() - last_generate) > 5:
        user_input = ("[INST]"
                      "The player is inside a game. He is a white block moving around in an empty black background.\n"
                      "Generate a one-sentence response in an extremely passive-aggressive manner. Make sure your response is always unique.\n"
                      "[/INST]")
        #history = {'internal': [], 'visible': []}
        # Set the flag to True immediately before starting the thread
        api_call_in_progress = True
        threading.Thread(target=generate_text, args=(user_input,)).start()
        last_generate = time.monotonic()

    # Refresh the screen
    pygame.display.flip()

    # Set the time delay to keep game running at a consistent speed
    clock.tick(20)

# End the game and clean up
pygame.quit()
sys.exit()

