# Recording Light for Logic Pro X

This repo contains the code I'm running in order to automate a few things when recording with Logic Pro X. Eg:
- Hitting record in Logic Pro X will turn on a light connected to a Raspberry Pi
- Hitting record in Logic Pro X will start video recording in OBS
- Hitting record in Logic Pro X will turn my Tradfri lights red. Color changes when recording is paused, or playback is on.

What you'll need:
- Raspberry Pi with internet access (I'm using a RPi3 rev B)
- Some kind of LED light / strip expecting 5V
- A breadboard
- Some jumper wires
- OBS Studio
- Optionally, I'm using a Tradfri RGB light bulb, and a Tradfri outlet.

## Setting up a recording light for Logic Pro X

In Logic Pro X, you can set up a [recording light](https://support.apple.com/guide/logicpro-css/recording-light-setup-ctls73d03c8e/mac) by going to: `Logic Pro X` > `Settings` > `Control Surfaces` > `Setup` > `New` > `Recording Light`

## Env Setup (for both rpi and mac)
```bash
conda create --name logic_recording_light python=3.11
conda activate logic_recording_light
pip install -r requirements.txt
```

On the RPi:
```bash
pip install RPi.GPIO
```

Note: if you don't want to use conda on the rpi and want to use venv instead:
```bash
mkdir ~/venvs
python3 -m venv ~/venvs/logic_recording_light_venv
source ~/venvs/logic_recording_light_venv/bin/activate
pip install -r requirements.txt
```

## Usage

First, run the env set up commands above on both the Raspberry Pi and the mac running Logic Pro X.

### On the Raspberry Pi:
```bash
python server.py
```
You should see something like
```
± python server.py
2025-01-23 14:44:20.648 | INFO     | LightController:__init__:14 - Set pin #16 to OUT in [GPIO.BOARD] mode
2025-01-23 14:44:20.653 | INFO     | __main__:<module>:78 - Listening on ('0.0.0.0', 5005)
2025-01-23 14:44:21.654 | INFO     | LightController:health_check:27 - Ready
```

### On the mac running Logic Pro X:
Open Logic Pro X and create a new project. Then, run the following command:
```bash
python client.py
```
You should see something like:
```bash
± python client.py  --record_obs
2025-02-27 13:26:03.183 | INFO     | __main__:<module>:102 - OBS recording control enabled
2025-02-27 13:26:03.195 | INFO     | OBSController:__init__:36 - OBS Version: 31.0.1
2025-02-27 13:26:03.195 | INFO     | __main__:create_osc_client:62 - Connecting to rpi.local:5005
2025-02-27 13:26:03.476 | INFO     | __main__:create_osc_client:65 - Resolved hostname rpi.local to IP address 192.168.40.28
2025-02-27 13:26:03.478 | INFO     | __main__:<module>:123 - (0).       Logic Pro Virtual Out
2025-02-27 13:26:03.478 | INFO     | __main__:<module>:127 - Opened MIDI port Logic Pro Virtual Out
2025-02-27 13:26:03.479 | INFO     | __main__:<module>:133 - OSC client set up with hostname rpi.local on port 5005
2025-02-27 13:26:03.479 | INFO     | __main__:<module>:134 - Sending MIDI messages over OSC channel /midi
```

You can (should!) change the hostname of your rpi with the flag `--rpi_hostname`:
```bash
python client.py --rpi_hostname rpi.local
```

Optionally, if you have [OBS Studio](https://obsproject.com/download) installed on your mac, you can control the video recording status of OBS with the flag `--record_obs`:
```bash
python client.py --record_obs
```

Pressing `record` in Logic Pro X should then:
- Turn on the light connected to the RPi
- Start recording in OBS (if `--record_obs` is enabled). Make sure to have OBS open and set up, and make sure to enable  the Websocket Server in OBS: `OBS` > `Tools` > `Websocket Server Settings` > `Enable Websocket Server`

### Testing the setup
In Logic Pro X, start recording by pressing the red button at the top. Your light should turn on.

![screenshot](assets/screen_shot_term.png)

## Running locally
If you want to run the server and client on the same machine (e.g. for testing), you can run the client to point to localhost:
```bash
# Terminal 1
python client.py --rpi_hostname localhost

# Terminal 2
python server.py
```
In this setup, a Dummy light will be used instead of the recording light controlled by rpi's GPIO.

## Optional: Dirigera + Tradfri lights
This section assumes you have a Dirigera hub and a Tradfri accessory (light bulb, outlet, etc) set up.
You will need to export the following environment variables:
```bash
export DIRIGERA_TOKEN=<your_token>
export DIRIGERA_IP_ADDRESS=<dirigera_ip_address>
```

## Troubleshooting
When running `client.py` on the mac, if you see something like:
```bash
± python client.py
2025-01-19 17:14:19.139 | WARNING  | __main__:<module>:47 - No MIDI ports available. Make sure
that Logic Pro X is open, and that a recording light was setup:
Logic Pro X -> Settings -> Control Surfaces -> Setup -> New
-> Recording Light
2025-01-19 17:14:19.139 | INFO     | __main__:<module>:48 - Exiting...
```
Make sure that Logic Pro X is open, and that a recording light was setup. Specifically, this code is looking for a Virtual MIDI port called `Logic Pro Virtual Out`.


When running `server.py` on the RPi, if you see something like:
```bash
  File "/usr/lib/python3.11/socketserver.py", line 456, in __init__
    self.server_bind()
  File "/usr/lib/python3.11/socketserver.py", line 472, in server_bind
    self.socket.bind(self.server_address)
OSError: [Errno 98] Address already in use
```
This means that you may already have an instance of `server.py` running on the same port (5005 by default).
To kill that process, we need to find the PID of the process:
```bash
lsof -i :5005
```
You'll see something along the lines of:
```bash
COMMAND  PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python  1651 thien    4u  IPv4  10673      0t0  UDP *:5005
```

Take note of the PID (1651 in this case) and kill the process with:
```bash
kill 1651
```
Now you should be able to run `python server.py` again.

