import smbus2
import time

# Light Sensor
# Constants for BH1750
DEVICE = 0x23  # Default I2C address for BH1750
POWER_ON = 0x01
RESET = 0x07
CONTINUOUS_H_RES_MODE = 0x10  # Start in continuous high-res mode

bus = smbus2.SMBus(1)  # Initialize I2C bus (1 for Pi 5)


def read_light():
    data = bus.read_i2c_block_data(DEVICE, CONTINUOUS_H_RES_MODE, 2)
    return (data[0] << 8) + data[1]


# Thresholds and state tracking
threshold = 5  # Adjust this for sensitivity
previous_reading = None

print("Monitoring for light changes...")
try:
    while True:
        current_reading = read_light()
        print(f"Current light level: {current_reading} lx")

        if previous_reading is not None:
            # Detect a change in light intensity
            if abs(current_reading - previous_reading) > threshold:
                print("Light motion detected")

        previous_reading = current_reading
        time.sleep(0.5)  # Adjust polling rate as needed

except KeyboardInterrupt:
    print("Stopping program")
