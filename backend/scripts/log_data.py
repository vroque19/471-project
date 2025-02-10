# logging real time data and insert into db
import sqlite3
import time
import os
import pytz
import random
from datetime import datetime
from .light_sensor import read_light
from .temp_sensor import read_temp
from .motion_sensor import read_motion


# script_dr = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(script_dr, "../instance/sleeptracker.db")
# conn = sqlite3.connect(db_path, check_same_thread=False)
# cursor = conn.cursor()
tz_LA = pytz.timezone("America/Los_Angeles")


lux_max = 1300


def log_data():
    timestamp = time.strftime("%H:%M:%S")
    # temperature = round(random.uniform(20, 30), 2)  # Replace with actual temp sensor
    temperature = read_temp()
    motion = read_motion()
    light = read_light()
    date = datetime.now(tz_LA).strftime("%a")
    # cursor.execute(
    #     "INSERT INTO sleep_data (date, timestamp, light, temperature, motion) VALUES (?, ?, ?, ?, ?)",
    #     (date, timestamp, light, temperature, motion),
    # )
    # conn.commit()
    output = (date, timestamp, light, temperature, motion)
    d = f"Logged: {date} | {timestamp} | Light: {light} | Temp: {temperature}°C | Motion: {motion}"
    print(
        d
    )
    return output


