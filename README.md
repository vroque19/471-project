# CatNap
A Smart Sleep System designed to align with your circadian rhythm. 

A Raspberry Pi screen displays a home page, daily sleep data, and weekly sleep scores.

Configuring you sleep and wake times on the touch screen will automatically be sent to the database and be considered in sleep data collection
Sleep data is collected during your personal sleep window via motion, light, and temperature sensors.
A LIFX wifi light is tuned to align with your circadian rhythm.

# Automation scripts to start the application on-boot:
open-local.sh: 
``` bash
#!/bin/bash
export DISPLAY=:0 


firefox -kiosk -private-window "http://localhost:5173" &
# Wait for Firefox
sleep 10
# Send the F11 key to enter fullscreen mode
xdotool search --sync --onlyvisible --name firefox key F11

```
~/.config/autostart/open-firefox.desktop file: 
```bash
[Desktop Entry]
Name=Open Firefox to localhost
Exec=/home/rpi5/open-local.sh
Type=Application
X-GNOME-Autostart-enabled=true
```

## Systemd Service Files

### Frontend Services:
```
/etc/systemd/system/npmrun.service 
```

- defines how to manage the Node.js application as a background service on the RaspberryPi 5
## Backend Services:
```
/etc/systemd/system/backend.service
```

- defines how to manage the FastAPI application as a background service on the RaspberryPi 5

> don't forget to install node modules, enviroment variables, virtual enviroment

# Resources
[FastAPI](https://fastapi.tiangolo.com/) <br>
[Svelte](https://svelte.dev/docs) <br>
[LIFX](https://api.developer.lifx.com/reference/introduction) <br>
[Raspberry Pi Pinout](https://pinout.xyz/pinout/) <br>
[FastAPI](https://fastapi.tiangolo.com/) <br>
[Adafruit MS8607](https://learn.adafruit.com/adafruit-te-ms8607-pht-sensor/python-circuitpython) <br>
[PIR motion sensor](https://projects.raspberrypi.org/en/projects/physical-computing/11) <br>
[Adafruit TSL2591](https://www.adafruit.com/product/1980) <br>
