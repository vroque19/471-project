from gpiozero import MotionSensor
import time

PIN = 17
pir = MotionSensor(PIN)

def read_motion():
  return pir.is_active
while True:
  print(read_motion())
  time.sleep(0.5)
