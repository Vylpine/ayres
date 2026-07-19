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

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen()

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):

    if status:
        print(status)

    audio_queue.put(indata.copy())

def audio_loop():

    with sd.InputStream(
        callback=callback,
        channels=1,
        samplerate=16000,
        blocksize=320
    ):
        while True:
            time.sleep(1)

def send_frames():
    while True:
        
        frame = audio_queue.get()
        frame_bytes = frame.tobytes()

        for subscriber in subscribers.copy():

            try:

                length = len(frame_bytes).to_bytes(4, "big")

                subscriber.sendall(length + frame_bytes)

            except (BrokenPipeError, ConnectionResetError, OSError):
                subscriber.close()
                subscribers.remove(subscriber)

threading.Thread(
    target=audio_loop,
    daemon=True
).start()

threading.Thread(
    target=send_frames,
    daemon=True
).start()

while True:
    conn, addr = server.accept()
    print(f"subscriber connected {addr}")
    subscribers.append(conn)