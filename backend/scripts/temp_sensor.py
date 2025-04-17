import board
import busio
import adafruit_ms8607
import time

i2c = board.I2C()
# Create sensor object
sensor = adafruit_ms8607.MS8607(i2c)

# Read data from sensor
def read_temp():
  temp = sensor.temperature
  return temp
# Print values
def read_data():
  pressure = sensor.pressure
  humidity = sensor.relative_humidity
  temperature = sensor.temperature
  print(f"Temperature: {temperature:.2f} °C")
  print(f"Pressure: {pressure:.2f} hPa")
  print(f"Humidity: {humidity:.2f} %")
  time.sleep(1)

