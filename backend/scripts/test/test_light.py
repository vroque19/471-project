import os
import requests
import json
import time
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()
LIFX_TOKEN = os.getenv("TOKEN")
LIFX_ID = os.getenv("ID")
# WAKE UP
MORNING1 = "orange"
MORNING2 = "#be934e"
MORNING3 = "#d8b26a"
MORNING4 = "#f2d08b"
MORNING5 = "#F7F7F7"

# WIND DOWN
EVENING1 = "#be934e"
EVENING2 = "#986c40"
EVENING3 = "#e44318"
EVENING4 = "E6411A"
EVENING5 = "#986c40"



class Light:
    def __init__(self):
        self._light_id = os.getenv("ID")
        self._token = os.getenv("TOKEN")
        self.get_headers = {
            "Authorization": f"Bearer {self._token}",
            "accept": "application/json",
        }
        self.put_headers = {
            "Authorization": f"Bearer {self._token}",
            "accept": "text/json",
            "content-type": "application/json",
        }
        self.post_headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

    def turn_on(self):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        print(self._light_id)
        payload = {"power": "on"}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light turned on")
            return response.json()
        raise ValueError(f"Could not turn on light with id: {self._light_id}")

    def turn_off(self):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        print(self._light_id)
        payload = {"power": "off"}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light turned on")
            return response.json()
        raise ValueError(f"Could not turn on light with id: {self._light_id}")

    def change_color(self, color):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"color": color}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light color changed")
            return response.json()
        raise ValueError(f"Could not change color of light with id: {self._light_id}")

    def change_hue(self, hue):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 1, "hue": hue}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light hue changed")
            return response.json()
        raise ValueError(f"Could not change hue of light with id: {self._light_id}")

    def change_saturation(self, saturation):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 1, "saturation": saturation}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light saturation changed")
            return response.json()
        raise ValueError(
            f"Could not change saturation of light with id: {self._light_id}"
        )

    def change_brightness(self, brightness):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 0.2, "brightness": brightness}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light brightness changed")
            return response.json()
        raise ValueError(
            f"Could not change brightness of light with id: {self._light_id}"
        )
    

    
    def change_temperature(self, kelvin):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 0.2, "kelvin": kelvin}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            print("Light temperature changed")
            return response.json()
        raise ValueError(
            f"Could not change temperature of light with id: {self._light_id}"
        )

def wake_1(light):
    light.turn_on()
    light.change_brightness(0.15)
    light.change_color(MORNING1)
    light.change_color(MORNING1)
    light.change_brightness(0.15)

    light.change_temperature(1800)
    time.sleep(1)
    return

def wake_2(light):
    light.change_brightness(0.4)
    light.change_color(MORNING2)
    light.change_color(MORNING2)
    light.change_brightness(0.4)
    light.change_temperature(5000)
    time.sleep(1)
    return

def wake_3(light):
    light.change_brightness(0.7)
    light.change_color(MORNING3)
    light.change_color(MORNING3)
    light.change_brightness(0.7)
    time.sleep(1)
    return

def wake_4(light):
    light.change_brightness(0.8)
    light.change_temperature(5500)
    light.change_brightness(0.8)
    light.change_color(MORNING4)
    time.sleep(1)
    return

def wake_5(light):
    light.change_brightness(1)
    time.sleep(2)
    light.change_temperature(5500)
    light.change_color(MORNING5)
    time.sleep(1)
    return


def bed_1(light):
    light.change_brightness(0.95)
    light.change_color(EVENING1)
    light.change_color(EVENING1)
    light.change_brightness(0.95)
    light.change_temperature(5000)
    time.sleep(1)
    return

def bed_2(light):

    light.change_color(EVENING3)
    light.change_brightness(0.7)
    light.change_color(EVENING4)
    light.change_color(EVENING4)
    light.change_brightness(0.7)
    light.change_temperature(3000)
    time.sleep(1)
    return

def bed_3(light):
    light.change_brightness(0.5)
    # light.change_color(EVENING4)
    # light.change_brightness(0.5)
    light.change_temperature(2000)
    time.sleep(1)
    return

def bed_4(light):
    light.change_brightness(0.2)
    light.change_temperature(1500)
    time.sleep(3)
    return

def bed_5(light):
    light.change_brightness(0.1)
    light.change_temperature(1200)
    time.sleep(3)

    return

def bed_6(light):
    light.turn_off()

def cycle(light):
    time.sleep(1)
    wake_1(light)
    wake_2(light)
    wake_3(light)
    wake_4(light)
    wake_5(light)
    bed_1(light)
    bed_2(light)
    bed_3(light)
    bed_4(light)
    bed_5(light)
    # light.turn_off()

def main():
    light = Light()
    # light.turn_on()
    # cycle(light)
    light.turn_off()
    
    # light.change_temperature(1500)
    # light.change_color(MORNING1)
    # time.sleep(1)
    # light.change_color(EVENING2)
    # time.sleep(1)

    # light.change_color(EVENING4)
    # light.change_brightness(0.15)


    

  
    

if __name__ == "__main__":
    main()
