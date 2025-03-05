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
    
async def update_sensor_data_background():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        data = log_data.log_data()
        day, date, timestamp, light, temperature, motion = data
        c.execute(
            "INSERT INTO sensor_data (day, date, timestamp, light, temperature, motion) VALUES (?, ?, ?, ?, ?, ?)",
            (day, date, timestamp, light, temperature, motion),
        )
        conn.commit()
        last_id = c.lastrowid
        conn.close()
        return {"success": True, "id": last_id}
    except Exception as e:
        print(f"Error logging sleep data: {str(e)}")
        return {"success": False, "error": str(e)}

def get_sleep_wake_times():
    today = (datetime.today())
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    today = today.strftime("%Y-%m-%d")
    conn = get_db_connection()
    c = conn.cursor()
    record = c.execute('SELECT * FROM settings').fetchall()
    row = dict(record[0])
    bed_time = row["bed_time"]
    wake_time = row["wake_time"]
    if datetime.strptime(bed_time, "%H:%M") < datetime.strptime(wake_time, "%H:%M"):
        sleep_time = datetime.strptime(f"{tomorrow} {bed_time}:00", "%Y-%m-%d %H:%M:%S")
        wake_time = datetime.strptime(f"{tomorrow} {wake_time}:00", "%Y-%m-%d %H:%M:%S")
    else:
        sleep_time = datetime.strptime(f"{today} {bed_time}:00", "%Y-%m-%d %H:%M:%S")
        wake_time = datetime.strptime(f"{tomorrow} {wake_time}:00", "%Y-%m-%d %H:%M:%S")
    
    conn.close()
    return sleep_time, wake_time

async def calc_sleep_score():
    ...


async def log_data_in_time_window():
    print("initiate data logging")
    sleep_time, wake_time = get_sleep_wake_times()
    while True:
        try:
            curr_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S") 
            # Log current times for debugging
            # print(f"Current time: {curr_time}")
            # print(f"Sleep time: {sleep_time}")
            # print(f"Wake time: {wake_time}")
            if sleep_time <= curr_time <= wake_time:
                print("In sleep window - logging data")
                await update_sensor_data_background()
                await asyncio.sleep(1)
            else:
                sleep_time, wake_time = get_sleep_wake_times()
                print(f"Outside sleep window, waiting 1 minute\nCurrent: {curr_time}\nSleep: {sleep_time}\nWake: {wake_time}")
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

@app.post("/api/settings")
async def update_sleep_scores(scores: models.SleepScores):
    try:
        day = datetime.now(tz_LA).strftime("%a")
        date = datetime.now(tz=tz_LA).strftime("%Y-%m-%d")
        score = calc_sleep_score()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO sleep_scores (date, day, score)
            VALUES (?, ?, ?)
            """,  (date, day, score),
            )
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
        # date = datetime.now(tz=tz_LA).strftime("%Y-%m-%d")

        c.execute(
            """
            REPLACE INTO settings (id, bed_time, wake_time)
            VALUES (?, ?, ?);
        """,
            (1, settings.bed_time, settings.wake_time),
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

