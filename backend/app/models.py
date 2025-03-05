from pydantic import BaseModel


class SleepSettings(BaseModel):
    bed_time: str
    wake_time: str


class SensorData(BaseModel):
    timestamp: str
    light: int  # lx
    temperature: float  # F
    motion: bool

class SleepScores(BaseModel):
    date: str
    day: str
    score: int
