from gpiozero import MotionSensor

PIN = 17
pir = MotionSensor(PIN)

def read_motion():
  return pir.is_active




