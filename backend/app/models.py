from pydantic import BaseModel


class SleepSettings(BaseModel):
    bed_time: str
    wake_time: str


class SleepData(BaseModel):
    timestamp: str
    light: int  # lx
    temperature: float  # F
    motion: bool
