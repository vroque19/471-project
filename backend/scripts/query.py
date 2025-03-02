import sqlite3
import os
from datetime import datetime

DATABASE_PATH = "../instance/sleeptracker.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


query = """
SELECT * 
FROM sensor_data 
WHERE 
    (date = '2025-02-27' AND timestamp >= '23:00:00') 
    OR 
    (date = '2025-02-28' AND timestamp <= '07:50:00')
ORDER BY date, timestamp;

"""


def get_sensor_data():
    conn = get_db_connection()
    data = conn.execute(query).fetchall()
    conn.close()
    return data


def main():
    print(get_sensor_data())


if __name__ == "__main__":
    main()
