import requests
import json
from typing import Literal
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()


class SmartLight:
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
        self.post_headers = {
            "accept": "application/json",
            "content-type": "application/json"
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
        raise ValueError(
            f"Could not change the color of light with id {self.light_id} to {color}"
        )

    def change_brightness(self, level):
        endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        payload = {
            "brightness": level,
        }
        response = requests.put(endpoint, json=payload, headers=self.put_headers)
        if response.ok:
            print("level = ", level)
            return response.json()
        raise ValueError(
            f"Could not change the color of light with id {self._light_id} to {level}"
        )

    def list_all_lights(self) -> "JSON":
        endpoint = "https://api.lifx.com/v1/lights/all"
        response = requests.get(endpoint, headers=self.get_headers)

        if response.ok:
            return response.json()
        raise ValueError("Could not get all lights")

    def turn_on(self):
        self.change_brightness(0.5)
        return self.change_power_state("on")

    def turn_off(self):
        return self.change_power_state("off")

    def change_power_state(self, state: Literal["on", "off"]) -> str:
        endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        payload = {
            "power": state,
        }
        response = requests.put(endpoint, headers=self.put_headers, json=payload)
        print(state)
        if response.ok:
            return response.json()
        raise ValueError(
            f"Could not change power state to {state} for light id: {self._light_id} \n{response.text} \n {response}"
        )

    def sunrise(self):
        endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/effects/sunrise"
        payload = {"duration": 10, "persist": False, "fast": False}
        response = requests.post(endpoint, json=payload, headers=self.put_headers)
        # print(response)
        if response.ok:
            return response.json()
        raise ValueError(
            f"Could not initiate sunrise for light id: {self._light_id} \n {response.text} \n {response}"
        )

    def sunset(self):
        endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/effects/sunset"
        payload = {"duration": 5, "soft_off": True, "power_on": True, "fast": False}
        response = requests.post(endpoint, json=payload, headers=self.post_headers)
        if response.ok:
            print(response)
            return response.json()
        raise ValueError(
            f"Could not initiate sunset for light id: {self._light_id} \n {response.text} \n {response}"
        )

    def clouds(self):
        endpoint = f"https://api.lifx.com/v1/lights/id:{self._light_id}/effects/clouds"
        payload = {
        "period": 50,
        "duration": None,
        "power_on": True,
        "min_saturation": 0.2,
        "fast": False
        } 
        response = requests.post(endpoint, json=payload, headers=self.put_headers)
        if response.ok:
            print(response)
            return response.json()
        raise ValueError(
            f"Could not initiate sunset for light id: {self._light_id} \n {response.text} \n {response}"
        )

    def light_power_demo(self):
        colors = ["yellow", "blue", "blue saturation:0.5", "orange", "red", "pink"]
        self.change_brightness(0.3)
        for i in range(len(colors)):
            self.change_color_state(colors[i])
            self.turn_on()
            sleep(2)
            self.turn_off()
            sleep(0.3)
    def set_state(self, power, color, brightness, duration):
        endpoint = "https://api.lifx.com/v1/lights/selector/state"

        payload = {
            "duration": 1,
            "fast": False
        }
        response = requests.post(endpoint, json=payload, headers=self.put_headers)
        if response.ok:
            return response.json()
        raise ValueError(
            f"Could not set state for light id:{self._light_id }\n {response.text} \n {response}"
        )


    


def main():
    light1 = SmartLight(os.getenv("LIGHT1_ID"))
    # light1.clouds()
    light1.change_color_state("cyan")
    # light_power_demo(light1)
    # light_power_demo(light1)

    # jr = light1.change_color_state("blue")
    # light1.pretty_print(jr)
    # light1.turn_on()
    # light1.change_color_state("red saturation:0.8")
    # light1.change_brightness(0.5)
    ...


if __name__ == "__main__":
    main()
