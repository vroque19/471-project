from pydantic import BaseModel


class SleepSettings(BaseModel):
    bed_time: str
    wake_time: str


class SleepData(BaseModel):
    light: int  # lx
    temp: float  # F
    motion: bool
