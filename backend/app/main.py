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
graphs_path = os.path.abspath(
    "/home/ubuntu/repos/471-project/backend/scripts/graph.py"
)
score_graph_path = os.path.abspath(
    "/home/ubuntu/repos/471-project/backend/scripts/score_graph.py"
)
score_path = os.path.abspath(
    "/home/ubuntu/repos/471-project/backend/scripts/calc_score.py"
)
sys.path.insert(0, light_path)
sys.path.insert(0, log_data_path)
sys.path.insert(0, graphs_path)
sys.path.insert(0, score_graph_path)
sys.path.insert(0, score_path)
from scripts import auth, log_data, score_graph, graph, query, calc_score


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

async def update_sleep_score_background():
    try:
        date, day, score = calc_score.main()
        print("score: ", score)
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
        print(f"Error updating sleep score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



async def run_at_wake_time():
    while True:
        try:
            sleep_time, wake_time = get_sleep_wake_times()  # Fetch wake_time from DB
            # wake_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            # time.sleep(2)
            curr_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            today = (curr_time.date())
            start_time = wake_time.replace(year=today.year, month=today.month, day=today.day)
            two_minutes_later = start_time + timedelta(minutes=2)
            # allow 2 minutes for graphs to upload
            if curr_time >= start_time and curr_time <= two_minutes_later:
                print("time to get graphs... calculating")
                await update_sleep_score_background()
                await asyncio.sleep(1)
                graph.main()
                await asyncio.sleep(1)
                score_graph.main()
                await asyncio.sleep(3600)
            else:
                print("not wake time... waiting...")
                sleep_time, wake_time = get_sleep_wake_times()  # Fetch wake_time from DB
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Error in wake-up script task: {str(e)}")
            await asyncio.sleep(30)  # Retry after 30 seconds

    


async def log_data_in_time_window():
    sleep_time, wake_time = get_sleep_wake_times()
    while True:
        try:
            curr_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S") 

            if sleep_time <= curr_time <= wake_time:
                # print("In sleep window - logging data")
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
background_task2 = None

def start_background_tasks():
    global background_task, background_task2
    if background_task is None:
        background_task = asyncio.create_task(log_data_in_time_window())
    if background_task2 is None:
        background_task2 = asyncio.create_task(run_at_wake_time())

@app.on_event("startup")
async def startup_event():
    start_background_tasks()

@app.on_event("shutdown")
async def shutdown_event():
    global background_task, background_task2
    for task in [background_task, background_task2]:
        if task:
            task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass 

@app.post("/api/sleepscores")
async def update_sleep_scores(scores: models.SleepScores):
    try:
        date, day, score = calc_score.main()
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
        print(settings.bed_time)
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

