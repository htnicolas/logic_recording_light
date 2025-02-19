# Recording Light for Logic Pro X

What you'll need:
- Raspberry Pi with internet access (I'm using a RPi3 rev B)
- Some kind of LED light / strip expecting 5V
- A breadboard
- Some jumper wires

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
± python client.py 
2025-01-19 17:21:49.484 | INFO     | __main__:<module>:45 - Opened MIDI port Logic Pro Virtual Out
2025-01-19 17:21:49.484 | INFO     | __main__:<module>:51 - OSC client set up on 127.0.0.1:5005
2025-01-19 17:21:49.484 | INFO     | __main__:<module>:52 - Sending MIDI messages over OSC channel /midi
```

### Testing the setup
In Logic Pro X, start recording by pressing the red button at the top. Your light should turn on.

![screenshot](assets/screen_shot_term.png)


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
Make sure that Logic Pro X is open, and that a recording light was setup.


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

