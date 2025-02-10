# backend/app/main.py
import pytz
from . import models
from datetime import datetime, timedelta
from .database import get_db_connection, init_db
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import time
import asyncio

light_path = os.path.abspath("/home/ubuntu/repos/471-project/backend/scripts/auth.py")
log_data_path = os.path.abspath(
    "/home/ubuntu/repos/471-project/backend/scripts/log_data.py"
)
sys.path.insert(0, light_path)
sys.path.insert(0, log_data_path)
from scripts import auth, log_data


app = FastAPI()

init_db()
tz_LA = pytz.timezone("America/Los_Angeles")
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# stop_event = threading.Event()

@app.get("/")
def read_root():
    # auth.schedule()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return {"tables": [table[0] for table in tables]}
    
async def update_sleep_data_background():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        data = log_data.log_data()
        date, timestamp, light, temperature, motion = data
        c.execute(
            "INSERT INTO sleep_data (date, timestamp, light, temperature, motion) VALUES (?, ?, ?, ?, ?)",
            (date, timestamp, light, temperature, motion),
        )
        conn.commit()
        last_id = c.lastrowid
        conn.close()
        return {"success": True, "id": last_id}
    except Exception as e:
        print(f"Error logging sleep data: {str(e)}")
        return {"success": False, "error": str(e)}

def get_sleep_wake_times():
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    today = today.strftime("%Y-%m-%d")
    tomorrow = tomorrow.strftime("%Y-%m-%d")
    conn = get_db_connection()
    c = conn.cursor()
    print(today)
    record =c.execute(f'SELECT * FROM settings WHERE date = ?', (today,)).fetchall()
    
    sleep_time = ""
    wake_time = ""
    for row in record:
        # print(dict(row)["date"], "is today")
        # print(dict(row)["bed_time"], "is bed time")
        # print(dict(row)["wake_time"], "is wake time")
        sleep_time = str(today) + " " + dict(row)["bed_time"] + ":01"
        wake_time = str(tomorrow) + " " + dict(row)["wake_time"] + ":01"
    conn.close()
    return datetime.strptime(sleep_time, "%Y-%m-%d %H:%M:%S"), datetime.strptime(wake_time, "%Y-%m-%d %H:%M:%S")

async def log_data_in_time_window():
    while True:
        try:
            sleep_time, wake_time = get_sleep_wake_times()
            # curr_time = datetime.now()
            curr_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S") 
            if sleep_time <= curr_time <= wake_time:
                print(sleep_time <= curr_time <= wake_time)
                print(sleep_time, curr_time, wake_time)
                await update_sleep_data_background()
                await asyncio.sleep(1)
            else:
                print("Outside sleep window, waiting 1 minute")
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Error in background task {str(e)}")
            await asyncio.sleep(60)

background_task = None

def start_background_monitoring():
    global background_task
    if background_task is None:
        background_task = asyncio.create_task(log_data_in_time_window())

@app.on_event("startup")
async def startup_event():
    start_background_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    global background_task
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass

        
@app.post("/api/sleep_data")
async def update_sleep_data(sleep_data: models.SleepData):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        data = log_data.log_data()
        date, timestamp, light, temperature, motion = data
        c.execute(
        "INSERT INTO sleep_data (date, timestamp, light, temperature, motion) VALUES (?, ?, ?, ?, ?)",
        (date, sleep_data.timestamp, sleep_data.light, sleep_data.temperature, sleep_data.motion),
    )
        # print(f"Logged: {date} | {timestamp} | Light: {light} | Temp: {temperature}°C | Motion: {motion}")
        conn.commit()
        last_id = c.lastrowid
        conn.close()
        return {"success": True, "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings")
async def update_sleep_settings(settings: models.SleepSettings):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        date = datetime.now(tz=tz_LA).strftime("%Y-%m-%d")

        c.execute(
            """
            INSERT OR REPLACE INTO settings (date, bed_time, wake_time)
            VALUES (?, ?, ?);
        """,
            (date, settings.bed_time, settings.wake_time),
        )

        conn.commit()
        last_id = c.lastrowid
        conn.close()

        return {"success": True, "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings/latest")
async def get_latest_settings():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM settings ORDER BY date DESC LIMIT 1")
        record = c.fetchone()
        conn.close()

        if record:
            return {
                "id": record["id"],
                "date": record["date"],
                "bed_time": record["bed_time"],
                "wake_time": record["wake_time"],
            }
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/{table_name}")
def get_all_rows(table_name: str):
    get_sleep_wake_times()
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Query to get all rows from the specified table
        c.execute(f"SELECT * FROM {table_name};")
        rows = c.fetchall()

        # Get column names
        c.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in c.fetchall()]

        conn.close()
        result = [dict(zip(columns, row)) for row in rows]
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.on_event("startup")
# def start_background_task():
#     loop = asyncio.get_event_loop()
#     thread = threading.Thread(target=log_data_in_time_window, args=(loop,), daemon=True)
#     thread.start()

# @app.on_event("shutdown")
# def stop_background_task():
#     stop_event.set()
