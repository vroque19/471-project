import sqlite3
import os
import pandas as pd
from datetime import datetime

DATABASE_PATH = "instance/sleeptracker.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_sensor_data():
    query = """
SELECT * 
FROM sensor_data 
WHERE 
    (date = '2025-02-27' AND timestamp >= '23:00:00') 
    OR 
    (date = '2025-02-28' AND timestamp <= '05:50:00')
ORDER BY date, timestamp;

"""
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(
        df["date"] + " " + df["timestamp"], format="%Y-%m-%d %H:%M:%S"
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Now extract the date part of the 'timestamp' column
    # df["date_part"] = df["timestamp"].dt.date

    # Print the result
    # print(df[["timestamp", "date_part"]])
    df["hour_bin"] = df["timestamp"].dt.floor("h")
    # print(df["timestamp"])
    return df


def main():
    print(get_sensor_data())


if __name__ == "__main__":
    main()
