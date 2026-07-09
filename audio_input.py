import json
import socket
import sounddevice as sd
import time
import threading
import queue

HOST = "127.0.0.1"
PORT = 6000

subscribers = []

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))
server.listen()

audio_queue = queue.Queue()

def callback(indata, frames, time, status):

    audio_queue.put(indata.copy())

def audio_loop():

    with sd.InputStream(
        callback=callback,
        channels=1,
        samplerate=16000
    ):
        while True:
            time.sleep(1)

threading.Thread(
    target=audio_loop,
    daemon=True
).start()


while True:
    conn, addr = server.accept()
    print(f"subscriber connected {addr}")
    subscribers.append(conn)