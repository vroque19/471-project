import time
import os
import pytz
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import numpy as np
tz_LA = pytz.timezone("America/Los_Angeles")
times_path = os.path.abspath(
    "/home/ubuntu/repos/471-project/backend/app/main.py"
)
from .query import get_sleep_settings, get_score_data

def compute_sleep_score(df, sleep_time, wake_time):
    if df.empty:
        print("No data found for the given time range. ( calc_score.py )")
        return 0
    
    """Compute sleep score based on various sleep metrics."""
    print("computing sleep score...\n\n")
    """
    get the correct days and times
    """
    
    wake_periods = []
    num_wake_events = detect_sleep_periods(df, sleep_time=sleep_time, wake_time=wake_time, wake_events=wake_periods)
    if num_wake_events == 0:
        wake_periods.append({
                'timestamp': df['timestamp'][0],
                'light': 0,
                'motion': 0
            })
        wake_periods.append({
                'timestamp': df['timestamp'][0],
                'light': 0,
                'motion': 0
            })
        # print(len(wake_periods))

    # # Total Time in Bed (TIB) and Total Sleep Time (TST)
    TIB = abs((wake_time - sleep_time).total_seconds()) / 60  # in minutes
    TST = TIB - ((num_wake_events)/2)

    # # Sleep Latency 20%
    sleep_start_time = get_sleep_latency(wake_periods) # if perfect sleep latency
    sleep_time = df['timestamp'][0]
    sleep_latency = (sleep_start_time - sleep_time).total_seconds() / 60
    latency_score = 20 * max(0, (TIB - sleep_latency) / TIB)
    
    # # Sleep Efficiency 30%
    sleep_efficiency = (TST / TIB) * 100
    efficiency_score = 30 * max(0, 1 - ((85 - sleep_efficiency) / 100))
    
    # # Sleep Interruptions 10% 
    interruptions_score = max(0, 10 - (TIB/ len(wake_periods)))
    
    # # Sleep Duration 30% (ideally 8 hours)
    duration_score = 30 * max(0, 1 - abs(8 - (TST / 60)) / 3)
  
    # # Environmental Stability (light/temp fluctuations) 10%
    temp_variance = np.std(df['temperature'])
    light_variance = np.std(df['light'])
    env_stability_score = max(0, 10 - (0.5 * temp_variance) - (0.5 * light_variance))
    
    # # Final Sleep Score
    sleep_score = (latency_score + efficiency_score + interruptions_score +
                   duration_score + env_stability_score)
    return sleep_score

def get_sleep_latency(wake_events):
    l, r = 1, 2 # dont count first one
    while r < len(wake_events):
        time_diff = abs((wake_events[l]['timestamp'] - wake_events[r]['timestamp']).total_seconds())
        if time_diff > 20*60: # about 40 minutes
            # print(time_diff)
            break
        l += 1
        r += 1
    # print("last wake before sleep:", l, wake_events[l])
    return wake_events[l]['timestamp']


def detect_sleep_periods(df, sleep_time, wake_time, wake_events):
    """Detect wake periods in sleep data based on two heuristics:
    1. Consistent motion for 1+ minutes
    2. Light level > threshold """
    light_thresh = 10 # lux
    motion_thresh = 0.3 # avg over 30s  ~ 1 movement every 10 seconds
    consecutive_motion = 0
    prev_time = df['timestamp'][0] # keep track of last time wake detected
    ten_sec_ago = False
    is_awake = False           
    
    df_resampled = df.resample('30S', on='timestamp').mean().reset_index()
    # print(df_resampled)
    for i, row in df_resampled.iterrows():
        current_time = row['timestamp']
        if prev_time is None:
            time_diff = 0
        else:
            time_diff = (current_time - prev_time).total_seconds()
        if row['motion'] > motion_thresh or row['light'] > light_thresh:
            is_awake = True
            wake_events.append({
                'timestamp': current_time,
                'light': row['light'],
                'motion': row['motion']
            })
        else:
            is_awake = False
        
        prev_time = current_time
    # print(("wake events: ", len(wake_events)))
    
    return len(wake_events)

def get_sleep_times(sleep_day, today, bed_time, wake_time):
    """Get the correct sleep and wake times based on the current day and settings."""
    bed_time = datetime.strptime(sleep_day + " " + bed_time, "%Y-%m-%d %H:%M")
    wake_time = datetime.strptime(today + " " + wake_time, "%Y-%m-%d %H:%M")
    return bed_time, wake_time

def main():
    df, sleep_day, today, bed_time, wake_time = get_score_data()
    sleep_time, wake_time = get_sleep_times(sleep_day, today, bed_time, wake_time)
    date = datetime.now().strftime("%Y-%m-%d")
    day = datetime.now().strftime("%a")
    score = compute_sleep_score(df, sleep_time, wake_time)
    output = (date, day, score)
    return output

if __name__ == "__main__":
    main()
