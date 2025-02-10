from gpiozero import MotionSensor
import time

pir = MotionSensor(17)
motion = 0
def motion():
    motion = 1



while True:
    # if pir.is_active:
    #     print("you moved")
    print(pir.is_active)
    time.sleep(1)

def cleanup():
    pir.close()

atexit.register(cleanup)

# Your motion detection code here
pause()  # Keep the script running

