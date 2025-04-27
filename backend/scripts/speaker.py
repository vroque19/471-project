import pygame
import time
import asyncio

def init_speaker():
  pygame.mixer.init()
async def play_noise():
  # print("playing sound...")
  await asyncio.sleep(0.5)
  pygame.mixer.music.load("birds.mp3")
  pygame.mixer.music.play()
  await asyncio.sleep(65)

  # while pygame.mixer.music.get_busy():
  #   await asyncio.sleep(0.1)
  # print("conclude sound")


