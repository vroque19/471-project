# senior design project
## Developing

# TODO
1. add sleep data view
2. add swipe feature
3. send sleep data to a database (.csv or db)
4. interface website with LIFX light 

## Running
start a development server:

```bash
npm run dev
```

# or start the server and open the app in a new browser tab
```
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

### 11/15/24
/etc/systemd/system/npmrun.service to spin up service on boot
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
# Resources
[Layer Cake](https://layercake.graphics/) <br>
