# Recording Light for Logic Pro X

What you'll need:
- Raspberry Pi with internet access (I'm using a RPi3 rev B)
- Some kind of LED light / strip expecting 5V
- A breadboard
- Some jumper wires

## Setting up a recording light for Logic Pro X

In Logic Pro X, you can set up a [recording light](https://support.apple.com/guide/logicpro-css/recording-light-setup-ctls73d03c8e/mac) by going to:
- Logic Pro X
- Settings
- Control Surfaces
- Setup
- New
- Recording Light

## Env Setup (for both rpi and mac)
```bash
conda create --name logic_recording_light python=3.11
conda activate logic_recording_light
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
2025-01-19 17:12:55.887 | INFO     | __main__:<module>:69 - Listening on ('127.0.0.1', 5005)
```

### On the mac running Logic Pro X:
Open Logic Pro X and create a new project. Then, run the following command:
```bash
python client.py
```
You should see something like:
```bash
```

## Troubleshooting
When running `client.py` on the mac, if you see something like:
```bash
± python client.py
2025-01-19 17:14:19.139 | WARNING  | __main__:<module>:47 - No MIDI ports available. Make sure that Logic Pro X is open, and t
hat a recording light was setup:
Logic Pro X -> Settings -> Control Surfaces -> Setup -> New -> Recording Light
2025-01-19 17:14:19.139 | INFO     | __main__:<module>:48 - Exiting...
```
Make sure that Logic Pro X is open, and that a recording light was setup.


