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

tz_LA = pytz.timezone("America/Los_Angeles")

lux_max = 1300

def log_data():
    timestamp = time.strftime("%H:%M:%S")
    temperature = read_temp()
    motion = read_motion()
    light = read_light()
    day = datetime.now(tz_LA).strftime("%a")
    date = datetime.now(tz_LA).strftime("%Y-%m-%d")
    output = (day, date, timestamp, light, temperature, motion)
    d = f"Logged: {day} | {date} | {timestamp} | Light: {light} | Temp: {temperature}°C | Motion: {motion}"
    print(
        d
    )
    return output

