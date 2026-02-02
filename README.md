# ESP32 DAC Audio Streamer

Stream audio from your computer or phone to an ESP32 over Wi-Fi and play it through a DAC or LM386 amplifier. This project includes both a Python client and ESP32 server designed to work together reliably.

## Features

- TCP audio streaming at 22,050 Hz
- Plays MP3/WAV files from your computer
- Optional live microphone input via Python
- LM386-safe hard limiter to prevent clipping
- Adjustable playback volume from the client

## Hardware

- ESP32 Dev Board
- DAC output pin: GPIO25
- Optional amplifier: LM386 (use a coupling capacitor)
- Shared GND between ESP32 and amplifier

## Setup

### ESP32

1. Open the ESP32 code in PlatformIO or Arduino IDE
2. Set your Wi-Fi credentials
3. Upload the code. The ESP32 will print its IP on serial.

Python Client
Install dependencies:

pip install numpy pydub
Run the Python script

Choose a file or enable live mic streaming

Adjust volume with the slider

Usage Notes
Start the Python client first, then the ESP32 will receive the stream

Make sure the ESP32 DAC pin is connected properly and GND is shared with amplifier

Only one client at a time is supported over TCP

How it Works
Python client reads audio, converts it to 8-bit DAC values, and streams via TCP

ESP32 server buffers incoming bytes and outputs them through DAC at 22,050 Hz using a timer interrupt

Hard limiter prevents spikes from damaging the LM386 or speakers


Credits
Built by ZiadWin356/cicweb
