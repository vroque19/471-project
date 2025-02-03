# logging real time data and insert into db
import sqlite3
import time
import os
import random  # Replace with actual sensor reading

script_dr = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dr, "../data/sleepData.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

lux_max = 1300


def log_data():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    motion = random.randint(0, 1)  # Replace with actual light sensor reading
    temperature = round(random.uniform(20, 30), 2)  # Replace with actual temp sensor
    light = str(random.randint(0, lux_max))

    cursor.execute(
        "INSERT INTO sleep_data (timestamp, light, temperature, motion) VALUES (?, ?, ?, ?)",
        (timestamp, light, temperature, motion),
    )
    conn.commit()
    print(
        f"Logged: {timestamp} | Light: {light} | Temp: {temperature}°C | Motion: {motion}"
    )


while True:
    log_data()
    time.sleep(1)  # Log every second
