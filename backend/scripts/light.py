import os
import asyncio
import requests
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz

load_dotenv()
LIFX_TOKEN = os.getenv("TOKEN")
LIFX_ID = os.getenv("ID")
TEST_ID = os.getenv("TEST_ID")
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

tz_LA = pytz.timezone("America/Los_Angeles")

class Light:
    def __init__(self):
        # self.wake_funcs = [self.wake_1, self.wake_2, self.wake_3, self.wake_4, self.wake_5]
        # self.sleep_funcs = [self.sleep_1, self.sleep_2, self.sleep_3, self.sleep_4, self.sleep_5]
        self.wake_funcs = [getattr(self, f"wake_{i}") for i in range(1, 6)] # scope/ variable introspection
        self.sleep_funcs = [getattr(self, f"sleep_{i}") for i in range(1, 7)]
        # self._light_id = os.getenv("ID")
        self._light_id = os.getenv("TEST_ID")
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
        payload = {"power": "on"}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            # print("Light turned on")
            return response.json()
        raise ValueError(f"Could not turn on light with id: {self._light_id}")

    def turn_off(self):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        print(self._light_id)
        payload = {"power": "off"}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            # print("Light turned off")
            return response.json()
        raise ValueError(f"Could not turn on light with id: {self._light_id}")

    def change_color(self, color):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"color": color}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            # print("Light color changed")
            return response.json()
        raise ValueError(f"Could not change color of light with id: {self._light_id}")

    def change_hue(self, hue):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 1, "hue": hue}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            # print("Light hue changed")
            return response.json()
        raise ValueError(f"Could not change hue of light with id: {self._light_id}")

    def change_saturation(self, saturation):
        url = f"https://api.lifx.com/v1/lights/id:{self._light_id}/state"
        headers = self.put_headers
        payload = {"duration": 1, "saturation": saturation}
        response = requests.put(url, headers=headers, json=payload)
        if response.ok:
            # print("Light saturation changed")
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
            # print("Light brightness changed")
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
            # print("Light temperature changed")
            return response.json()
        raise ValueError(
            f"Could not change temperature of light with id: {self._light_id}"
        )

    def get_step(self, wake_time, sleep_time, current_time):
        if wake_time > current_time and sleep_time > current_time:
            wake_time = wake_time - timedelta(days=1)
        wake_end = wake_time + timedelta(minutes=75)  # Wake cycle active period
        sleep_start = sleep_time - timedelta(minutes=75)  # Sleep cycle start
        # current_time = datetime.now(tz_LA)
        next_wake_time = wake_time + timedelta(days=1)
        print("wake", wake_time, "wake end", wake_end, "curr", current_time)

        # Check if current time is in the wake cycle (steps 0-4)
        if wake_time <= current_time < wake_end:
            # print("wake", wake_time, "wake end", wake_end, "curr", current_time)
            minutes_since_wake = (current_time - wake_time).total_seconds() / 60
            step = int(minutes_since_wake // 15)  # 15-minute increments
            step = min(step, 4)  # Cap at step 4
            # print(wake_time, current_time, wake_end, minutes_since_wake)
            return ("wake", step)
        # Check if current time is in the wake step 4 persistence period (wake_end to sleep_start)
        if wake_end <= current_time < sleep_start:
            return ("wake", 4)  # Persist wake step 4
         # Check if current time is in the sleep cycle (steps 0-5)
        if sleep_start <= current_time <= next_wake_time:
            minutes_until_sleep = (sleep_time - current_time).total_seconds() / 60
            step = int((75 - minutes_until_sleep) // 15)  # 75 minutes total, 15-minute increments
            step = min(step, 5)  # Cap at step 5
            return ("sleep", step)
        # Check if current time is in the sleep step 5 persistence period (sleep_datetime to next_wake_datetime)
        if sleep_time < current_time < next_wake_time:
            return ("sleep", 5)  # Persist sleep step 5
  

    def wake_1(self):
        self.turn_on()
        self.change_brightness(0.15)
        self.change_color(MORNING1)
        self.change_color(MORNING1)
        self.change_brightness(0.15)
        self.change_temperature(1800)
        time.sleep(1)
        return

    def wake_2(self):
        self.change_brightness(0.4)
        self.change_color(MORNING2)
        self.change_color(MORNING2)
        self.change_brightness(0.4)
        self.change_temperature(5000)
        time.sleep(1)
        return

    def wake_3(self):
        self.change_brightness(0.7)
        self.change_color(MORNING3)
        self.change_color(MORNING3)
        self.change_brightness(0.7)
        time.sleep(1)
        return

    def wake_4(self):
        self.change_brightness(0.8)
        self.change_temperature(5500)
        self.change_brightness(0.8)
        self.change_color(MORNING4)
        time.sleep(1)
        return

    def wake_5(self):
        print("Brightest")
        self.change_brightness(1)
        time.sleep(2)
        self.change_temperature(5500)
        self.change_color(MORNING5)
        time.sleep(1)
        return


    def sleep_1(self):
        self.change_brightness(0.95)
        self.change_color(EVENING1)
        self.change_color(EVENING1)
        self.change_brightness(0.95)
        self.change_temperature(5000)
        time.sleep(1)
        return

    def sleep_2(self):
        self.change_color(EVENING3)
        self.change_brightness(0.7)
        self.change_color(EVENING4)
        self.change_color(EVENING4)
        self.change_brightness(0.7)
        self.change_temperature(3000)
        time.sleep(1)
        return

    def sleep_3(self):
        self.change_brightness(0.5)
        self.change_temperature(2000)
        time.sleep(1)
        return

    def sleep_4(self):
        self.change_brightness(0.2)
        self.change_temperature(1500)
        time.sleep(3)
        return

    def sleep_5(self):
        self.change_brightness(0.1)
        self.change_temperature(1200)
        time.sleep(3)

        return

    def sleep_6(self):
        self.turn_off()
        return

    async def cycle(self):
        print("cycling light")
        # await asyncio.sleep(3)
        self.wake_1()
        await asyncio.sleep(2)
        self.wake_2()
        await asyncio.sleep(2)
        self.wake_3()
        await asyncio.sleep(2)
        self.wake_4()
        await asyncio.sleep(2)
        self.wake_5()
        await asyncio.sleep(2)
        self.sleep_1()
        await asyncio.sleep(2)
        self.sleep_2()
        await asyncio.sleep(2)
        self.sleep_3()
        await asyncio.sleep(2)
        self.sleep_4()
        await asyncio.sleep(2)
        self.sleep_5()
        await asyncio.sleep(2)
        self.sleep_6()
    
    async def run_cycle(self):
        print("running light")
        for step in self.wake_funcs:
            step()
            await asyncio.sleep(1)
        for step in self.sleep_funcs:
            step()
        for step in self.wake_funcs:
            step()
            await asyncio.sleep(1)
        for step in self.sleep_funcs:
            step()
            await asyncio.sleep(1)

    def wake_cycle(self):
        self.run_cycle(self.wake_funcs)

    def sleep_cycle(self):
        self.run_cycle(self.sleep_funcs)
    # TODO (vroque19) : create the step functions for light
    # hint: use integer division with step size to index funcs
    def step(self, step_number, cycle_type="wake"):
        print("stepping...")
        # Select the appropriate function list based on cycle_type
        if cycle_type.lower() == "wake":
            funcs = self.wake_funcs
        elif cycle_type.lower() == "sleep":
            funcs = self.sleep_funcs
        else:
            raise ValueError("cycle_type must be 'wake' or 'sleep'")

        # Calculate the index and map it to the function list
        num_funcs = len(funcs)
        if num_funcs == 0:
            raise ValueError(f"No functions available for {cycle_type} cycle")

        index = step_number % num_funcs  # Use modulo to wrap around if step_number exceeds num_funcs
        print(funcs[index])
        # Check if the index is valid
        if index >= num_funcs:
            raise ValueError(f"Step number {step_number} results in an invalid index for {cycle_type} cycle")

        # Execute the function at the calculated index
        print(f"Executing {cycle_type} step {step_number} (function index {index})")
        funcs[index]()

def get_sleep_wake_times():
    today = datetime.today()
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    today = today.strftime("%Y-%m-%d")
    bed_time = "21:45"
    wake_time = "8:30"
    if datetime.strptime(bed_time, "%H:%M") < datetime.strptime(wake_time, "%H:%M"):
        # past midnight
        sleep_time = datetime.strptime(f"{tomorrow} {bed_time}:00", "%Y-%m-%d %H:%M:%S")
        wake_time = datetime.strptime(f"{tomorrow} {wake_time}:00", "%Y-%m-%d %H:%M:%S")
    else:
        sleep_time = datetime.strptime(f"{today} {bed_time}:00", "%Y-%m-%d %H:%M:%S")
        wake_time = datetime.strptime(f"{today} {wake_time}:00", "%Y-%m-%d %H:%M:%S")
    return sleep_time, wake_time



def main():
    light = Light()
    sleep_time, wake_time = get_sleep_wake_times()
    # test_get_step(light, wake_time, sleep_time, datetime.now())
    # light.sleep_1()
    # light.turn_on()
    light.run_cycle()



    

  
    

if __name__ == "__main__":
    main()
