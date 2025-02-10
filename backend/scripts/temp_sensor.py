import board
import busio
import adafruit_ms8607
import time

# Initialize I2C with the correct bus (change to bus 12 if needed)
# i2c = busio.I2C(board.SCL, board.SDA)  # Use I2C-11
# If it's on I2C-12, use: i2c = busio.I2C(board.SCL2, board.SDA2)
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

# while True:
#   read_data()
#   time.sleep(1)
