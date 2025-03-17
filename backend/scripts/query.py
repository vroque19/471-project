import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta

DATABASE_PATH = "instance/sleeptracker.db"
# DATABASE_PATH = "../instance/sleeptracker.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_sleep_settings():
    query = """
SELECT * FROM settings
"""
    conn = get_db_connection()
    settings = conn.execute(query).fetchall()
    row = dict(settings[0])
    wake_time = row["wake_time"]
    bed_time = row["bed_time"]
    conn.close()
    return wake_time, bed_time


def get_sensor_data():
    today = datetime.today()
    sleep_day = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    today = today.strftime("%Y-%m-%d")
    print(sleep_day)    
    wake_time, bed_time = get_sleep_settings()
    if datetime.strptime(bed_time, "%H:%M") < datetime.strptime(wake_time, "%H:%M"):
        sleep_day = today
    
    query = """
SELECT * 
FROM sensor_data 
WHERE 
    (date = '{}' AND timestamp >= '{}') 
    OR 
    (date = '{}' AND timestamp <= '{}')
ORDER BY date, timestamp;

"""

    conn = get_db_connection()
    # df = pd.read_sql_query(query, conn)
    
    df = pd.read_sql_query(query.format(sleep_day, bed_time, today, wake_time), con=conn)
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

def get_score_data():
    today = datetime.today()
    sleep_day = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    today = today.strftime("%Y-%m-%d")
    print(sleep_day)    
    wake_time, bed_time = get_sleep_settings()
    if datetime.strptime(bed_time, "%H:%M") < datetime.strptime(wake_time, "%H:%M"):
        sleep_day = today
    
    query = """
SELECT * 
FROM sensor_data 
WHERE 
    (date = '{}' AND timestamp >= '{}') 
    OR 
    (date = '{}' AND timestamp <= '{}')
ORDER BY date, timestamp;

"""

    conn = get_db_connection()
    # df = pd.read_sql_query(query, conn)
    
    df = pd.read_sql_query(query.format(sleep_day, bed_time, today, wake_time), con=conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(
        df["date"] + " " + df["timestamp"], format="%Y-%m-%d %H:%M:%S"
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df, sleep_day, today, bed_time, wake_time


def get_weekly_scores():
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    data = {"Day": days_of_week, "Sleep Score": [None] * 7}  # Initialize with None
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = today.weekday()
    start_of_week = today - timedelta(days=(weekday + 1) % 7)
    today = today.strftime("%Y-%m-%d")
    start_of_week = start_of_week.strftime("%Y-%m-%d")
    query = """
SELECT s.day, s.score
    FROM sleep_scores s
    INNER JOIN (
        SELECT date, MAX(if) as max_id  -- Assuming 'id' is an auto-incrementing column
        FROM sleep_scores
        WHERE date >= '{}' AND date <= '{}'
        GROUP BY date
    ) latest ON s.if = latest.max_id
    ORDER BY s.date;
"""
    conn = get_db_connection()
    print("start of week and today: ", start_of_week, today)
    db_scores = pd.read_sql_query(query.format(start_of_week, today), con=conn)
    conn.close()
    
    # Populate scores into the data dictionary
    for _, row in db_scores.iterrows():
        day_index = days_of_week.index(row['day'])
        print(day_index)
        data["Sleep Score"][day_index] = row['score']  # Ensure score is a float for consistency
        print(data)
    return data

def main():
    # print(get_sensor_data())
    # get_sleep_settings()
    get_sensor_data()


if __name__ == "__main__":
    main()
