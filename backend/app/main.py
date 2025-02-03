# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
from . import models
from .database import get_db_connection, init_db

app = FastAPI()

# Initialize database
init_db()
tz_LA = pytz.timezone("America/Los_Angeles")
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/data/{table_name}")
def get_all_rows(table_name: str):
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


@app.get("/")
def read_root():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        conn.close()
        return {"tables": [table[0] for table in tables]}
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
