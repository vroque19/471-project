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
DEMO_MODE = False
ENV_PATH = "/home/ubuntu/repos/471-project/backend/scripts/.env"
BACKLIGHT_PATH = "/sys/class/backlight/10-0045/bl_power"

speaker_path = os.path.abspath("/home/ubuntu/repos/471-project/backend/scripts/speaker.py")
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
sys.path.insert(0, speaker_path)
from scripts import auth, log_data, score_graph, graph, query, calc_score, light, speaker

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
        # past midnight
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
        # print("score: ", score)
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
    
def get_curr_time():
    return datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")

async def run_at_wake_time():
    # check and upload graphs at wake time
    global graphs_uploaded
    while True:
        try:
            # await turn_display_on()
            sleep_time, wake_time = get_sleep_wake_times()  # Fetch wake_time from DB
            curr_time = get_curr_time()
            today = (curr_time.date())
            start_time = wake_time.replace(year=today.year, month=today.month, day=today.day)
            # allow 2 minutes for graphs to upload
            
            if curr_time >= start_time and not graphs_uploaded:
                # print("time to get graphs... calculating")
                await update_sleep_score_background()
                await asyncio.sleep(1)
                graph.main()
                await asyncio.sleep(5)
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
                await turn_display_on()
                await asyncio.sleep(60)
    
        except Exception as e:
            print(f"Error in background task {str(e)}")
            await asyncio.sleep(60)

async def run_light_schedule():
    curr_time = get_curr_time()
    print(f"Running light schedule at {curr_time}")
    sleep_time, wake_time = get_sleep_wake_times()

    light1 = light.Light()
    print(f"got light{light1}")
    while True:
        # light1.turn_on()
        cycle, step = light1.get_step(wake_time, sleep_time, curr_time)
        print(f"got {step} from {cycle}")
        if cycle is not None:
            print(f"Executing {cycle} cycle, step {step}")
            await light1.step(step, cycle)
        else:
            print("No cycle active")
        
        await asyncio.sleep(10)
        
async def light_demo():
    wake_time, sleep_time = get_sleep_wake_times()
    light1 = light.Light()
    while True:
        await light1.run_cycle()

async def speaker_demo():
    speaker.init_speaker()
    while True:
        await speaker.play_noise()

async def sensor_demo():
    while True:
        await log_data.demo_data()

async def demo():
    print("Running demo...")
    await turn_display_on()
    wake_time, sleep_time = get_sleep_wake_times()

    light_task = asyncio.create_task(light_demo())
    speaker_task = asyncio.create_task(speaker_demo())
    log_task = asyncio.create_task(log_data.demo_data())

    await speaker_task
    await log_task
    await light_task


background_task = None
background_task2 = None
background_task3 = None


def start_background_tasks():
    global background_task, background_task2, background_task3
    if not DEMO_MODE:
        if background_task is None:
            background_task = asyncio.create_task(log_data_in_time_window())
        if background_task2 is None:
            background_task2 = asyncio.create_task(run_at_wake_time())
        if background_task3 is None:
            background_task3 = asyncio.create_task(run_light_schedule())
    if DEMO_MODE:
        if background_task2 is None:
            background_task2 = asyncio.create_task(run_at_wake_time())
        if background_task3 is None:
            background_task3 = asyncio.create_task(demo())


@app.on_event("startup")
async def startup_event():
    start_background_tasks()

@app.on_event("shutdown")
async def shutdown_event():
    global background_task, background_task2, background_task3
    tasks = [background_task, background_task2, background_task3]
    if not DEMO_MODE:
        for task in tasks:
            if task:
                task.cancel()
    else:
        if background_task3:
            background_task3.cancel()
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

