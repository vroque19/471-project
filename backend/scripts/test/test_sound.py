import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Load your .wav file
pygame.mixer.music.load("birds.mp3")

# Play it
pygame.mixer.music.play()

# Wait for it to finish
# while True:
while pygame.mixer.music.get_busy():
    time.sleep(0.1)
