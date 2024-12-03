import requests
import json
from typing import Literal
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()

class LightTalk:
  def __init__(self, light_id):
    self._token = os.getenv("LIGHT_PAT")
    self._light_id = light_id
    self.get_headers = {
      "Authorization": f"Bearer {self._token}",
      "accept": "application/json",
    }
    self.put_headers = {
      "Authorization": f"Bearer {self._token}",
      "accept": "application/json",
      "content-type": "application/json",
    }

  def pretty_print(self, response):
    print(json.dumps(response, indent=4))
  
  def change_color_state(self, color):
    endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
    payload = {
      "color": color,
    }
    response = requests.put(endpoint, json=payload, headers=self.put_headers)
    if response.ok:
      print("color = ", color)
      return response.json()
    raise ValueError(f"Could not change the color of light with id {self.light_id} to {color}")

  def change_brightness(self, level):
    endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
    payload = {
      "brightness": level,
    }
    response = requests.put(endpoint, json=payload, headers=self.put_headers)
    if response.ok:
      print("level = ", level)
      return response.json()
    raise ValueError(f"Could not change the color of light with id {self._light_id} to {level}")


  def list_all_lights(self) -> 'JSON':
    endpoint = 'https://api.lifx.com/v1/lights/all'
    response = requests.get(endpoint, headers=self.get_headers)

    if response.ok:
      return response.json()
    raise ValueError("Could not get all lights")
  

  def turn_on(self):
    return self.change_power_state("on")


  def turn_off(self):
    return self.change_power_state("off")


  def change_power_state(self, state:Literal["on", "off"]) -> str:
    endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
    payload = {
      "power" : state,
    }
    print(state)
    response = requests.put(endpoint, headers=self.put_headers, json=payload)
    if response.ok:
      return response.json()
    raise ValueError(f"Could not change power state to {state} for light id: {self._light_id} \n{response.text} \n {response}")


light1 = LightTalk(os.getenv("LIGHT1_ID"))
jr = light1.change_color_state("blue")
light1.pretty_print(jr)
light1.turn_on()
light1.change_color_state("red saturation:0.8")
light1.change_brightness(0.5)

while 1:
  light1.turn_off()
  sleep(2)
  light1.turn_on()
  sleep(5)

