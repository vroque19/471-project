# backend/app/main.py
import os
import sys
import pytz
import asyncio
import subprocess
from . import models
from dotenv import load_dotenv
from datetime import datetime, timedelta
from .database import get_db_connection, init_db
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
ENV_PATH = "/home/ubuntu/repos/471-project/backend/scripts/.env"
BACKLIGHT_PATH = "/sys/class/backlight/10-0045/bl_power"

light_path = os.path.abspath("/home/ubuntu/repos/471-project/backend/scripts/light.py")
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
from scripts import auth, log_data, score_graph, graph, query, calc_score, light

load_dotenv(ENV_PATH)
LIFX_TOKEN = os.getenv("TOKEN")
LIFX_ID = os.getenv("ID")
graphs_uploaded = False

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

@app.get("/")
def read_root():
    # auth.schedule()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return {"tables": [table[0] for table in tables]}

def get_backlight_path():
    """Find the correct backlight control path"""
    return BACKLIGHT_PATH
    raise FileNotFoundError("Could not find display backlight control file")

async def turn_display_off():
    """Turn the display off"""
    print("turn display off")
    try:
        subprocess.run(
    ['sudo', 'tee', BACKLIGHT_PATH],
    input='1\n',
    text=True,
    check=True
    )
    except Exception as e:
        print(f"Error turning display off: {str(e)}")
        try:
            # backlight_path = get_backlight_path()  # make sure this returns a valid path string
            with open(BACKLIGHT_PATH, 'w') as f:
                f.write('1')
        except subprocess.CalledProcessError as e:
            print(f"Fallback also failed: {str(e)}")

async def turn_display_on():
    """Turn the display on by enabling backlight"""
    print("turn display on")
    try:
        subprocess.run(
    ['sudo', 'tee', BACKLIGHT_PATH],
    input='0\n',
    text=True,
    check=True
    )
    except Exception as e:
        print(f"Error turning display on: {str(e)}")
        try:
            # backlight_path = get_backlight_path()  # make sure this returns a valid path string
            with open(BACKLIGHT_PATH, 'w') as f:
                f.write('0')
        except subprocess.CalledProcessError as e:
            print(f"Fallback also failed: {str(e)}")

    
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
    today = datetime.today()
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
            INSERT OR REPLACE INTO sleep_scores (date, day, score)
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
    # check and upload graphs at wake time
    global graphs_uploaded
    while True:
        try:
            await turn_display_on()
            sleep_time, wake_time = get_sleep_wake_times()  # Fetch wake_time from DB

            curr_time = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            today = (curr_time.date())
            start_time = wake_time.replace(year=today.year, month=today.month, day=today.day)
            # allow 2 minutes for graphs to upload
            two_minutes_later = start_time + timedelta(minutes=2)
            if curr_time >= start_time and not graphs_uploaded:
                print("time to get graphs... calculating")
                await update_sleep_score_background()
                await asyncio.sleep(1)
                graph.main()
                await asyncio.sleep(1)
                score_graph.main()
                graphs_uploaded = True
                await asyncio.sleep(600)
            if curr_time < start_time:
                graphs_uploaded = False
                print("sleep time... waiting...")
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
            # within sleep window
            if sleep_time <= curr_time <= wake_time or (curr_time.time() < wake_time.time()):

                await update_sensor_data_background()
                await turn_display_off()
                await asyncio.sleep(1)
            # outside sleep window
            else:
                sleep_time, wake_time = get_sleep_wake_times()
                # debugging
                print(f"Outside sleep window, waiting 1 minute\nCurrent: {curr_time}\nSleep: {sleep_time}\nWake: {wake_time}")
                # await turn_display_on()
                await asyncio.sleep(60)
    
        except Exception as e:
            print(f"Error in background task {str(e)}")
            await asyncio.sleep(60)

async def run_light_schedule():
    print("Running light schedule")
    while True:
        light1 = light.Light()
        sleep_time, wake_time = get_sleep_wake_times()
        wake_time = wake_time.replace(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day)
        schedule = [
            (wake_time, light.wake_1),
            (wake_time + timedelta(minutes=15), light.wake_2),
            (wake_time + timedelta(minutes=30), light.wake_3),
            (wake_time + timedelta(minutes=45), light.wake_4),
            (wake_time + timedelta(minutes=60), light.wake_5),
            (sleep_time - timedelta(minutes=90), light.bed_1),
            (sleep_time - timedelta(minutes=60), light.bed_2),
            (sleep_time - timedelta(minutes=45), light.bed_3),
            (sleep_time - timedelta(minutes=30), light.bed_4),
            (sleep_time - timedelta(minutes=15), light.bed_5),
            (sleep_time, light.bed_6),
        ]
        now = datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S") 
        for i in range(len(schedule)):
            if i == len(schedule) - 1:
                # sleep_time, wake_time = get_sleep_wake_times()
                wake_time = wake_time + timedelta(days=1)
                print("new wake: ", wake_time)
                schedule = [
            (wake_time, light.wake_1),
            (wake_time + timedelta(minutes=15), light.wake_2),
            (wake_time + timedelta(minutes=30), light.wake_3),
            (wake_time + timedelta(minutes=45), light.wake_4),
            (wake_time + timedelta(minutes=60), light.wake_5),
            (sleep_time - timedelta(minutes=90), light.bed_1),
            (sleep_time - timedelta(minutes=60), light.bed_2),
            (sleep_time - timedelta(minutes=45), light.bed_3),
            (sleep_time - timedelta(minutes=30), light.bed_4),
            (sleep_time - timedelta(minutes=15), light.bed_5),
            (sleep_time, light.bed_6),
        ]
            event = schedule[i]
            trigger_time, light_func = event[0], event[1]
            next_time = schedule[(i+1)%(len(schedule))][0]
            print(f"Now: {now}, Trigger: {trigger_time}, Next: {next_time}, Now >= Trigger? {next_time > now >= trigger_time}")
            if trigger_time <= now < next_time:
                # print(f"Now: {now}, Trigger: {trigger_time}, Next: {next_time}, Trigger? {next_time > now >= trigger_time}")
                print("Light function: ", light_func)
                await light_func(light1)
                print("Waiting until", next_time)
                await asyncio.sleep(1)  # Prevent rapid re-triggering
            # elif sleep_time <= now <= get_sleep_wake_times()[1]:
            #     print(f"Now: {now}, Sleep time: {sleep_time}, Next: {next_time}, Trigger? {sleep_time <= now < get_sleep_wake_times()[1]}")
            #     print("Light function: ", light_func)
            #     await light_func(light1)
            #     print("Waiting until", get_sleep_wake_times()[1])
            #     await asyncio.sleep(1)  # Prevent rapid re-triggering

        # await asyncio.sleep(max((next_time - now).total_seconds(), 1))
        await asyncio.sleep(60)

background_task = None
background_task2 = None
background_task3 = None

def start_background_tasks():
    global background_task, background_task2, background_task3
    if background_task is None:
        background_task = asyncio.create_task(log_data_in_time_window())
    if background_task2 is None:
        background_task2 = asyncio.create_task(run_at_wake_time())
    if background_task3 is None:
        background_task3 = asyncio.create_task(run_light_schedule())



@app.on_event("startup")
async def startup_event():
    start_background_tasks()

@app.on_event("shutdown")
async def shutdown_event():
    global background_task, background_task2, background_task3
    tasks = [background_task, background_task2, background_task3]
    for task in tasks:
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

