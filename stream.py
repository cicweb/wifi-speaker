import socket
import threading
import time
import tkinter as tk
from tkinter import filedialog
import numpy as np
from pydub import AudioSegment

# config

ESP32_IP = "YOUR_IP_HERE"
ESP32_PORT = 1234

RATE = 22050
CHUNK = 512
VOLUME = 1.2   # 0.0 – 5.0

running = False
sock = None

# core

def soft_limiter(samples, threshold=0.9):
    peak = np.max(np.abs(samples))
    if peak > threshold:
        samples *= threshold / peak
    return samples


def pcm16_to_dac8(samples):
    
    samples = samples.astype(np.float32) / 32768.0

    # volume
    samples *= (VOLUME / 5.0)

    # limiter
    samples = soft_limiter(samples)

    # clamp
    samples = np.clip(samples, -1.0, 1.0)

    
    return ((samples + 1.0) * 127.5).astype(np.uint8)

# streaming the file

def stream_audiosegment(audio):
    global running, sock

    running = False
    time.sleep(0.05)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(RATE)
        .set_sample_width(2)
    )

    samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ESP32_IP, ESP32_PORT))

    running = True
    idx = 0

    while running and idx < len(samples):
        chunk = samples[idx:idx + CHUNK]
        data = pcm16_to_dac8(chunk)
        sock.sendall(data.tobytes())
        idx += CHUNK
        time.sleep(CHUNK / RATE)

    sock.close()
    running = False


def choose_file():
    path = filedialog.askopenfilename(
        filetypes=[("Audio files", "*.mp3 *.wav")]
    )
    if not path:
        return

    audio = AudioSegment.from_file(path)
    threading.Thread(
        target=stream_audiosegment,
        args=(audio,),
        daemon=True
    ).start()


def stop():
    global running
    running = False


def set_volume(v):
    global VOLUME
    VOLUME = float(v)

root = tk.Tk()
root.title("ZiadWin356's Audio Streamer")

tk.Button(root, text="Play File", command=choose_file).pack(pady=5)
tk.Button(root, text="STOP", command=stop).pack(pady=5)

vol = tk.Scale(
    root,
    from_=0,
    to=5,
    resolution=0.1,
    orient="horizontal",
    label="Volume",
    command=set_volume
)
vol.set(VOLUME)
vol.pack(pady=10)

root.mainloop()
