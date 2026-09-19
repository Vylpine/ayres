import socket
import numpy as np
import json
import threading

from faster_whisper import WhisperModel


AUDIO_HOST = "127.0.0.1"
AUDIO_PORT = 6000

VAD_HOST = "127.0.0.1"
VAD_PORT = 6100

SAMPLE_RATE = 16000

MODEL_SIZE = "base"


# -------------------------
# STT state
# -------------------------

speaking = False

audio_buffer = np.array(
    [],
    dtype=np.float32
)

buffer_lock = threading.Lock()


# -------------------------
# Whisper
# -------------------------

print("Loading Whisper...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded")


# -------------------------
# VAD connection
# -------------------------

vad_server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

vad_server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

vad_server.bind(
    (VAD_HOST, VAD_PORT)
)

vad_server.listen(1)

print("Waiting for VAD...")

vad_client, addr = vad_server.accept()

print(f"VAD connected: {addr}")


# -------------------------
# Whisper processing
# -------------------------

def process_audio():

    global audio_buffer

    with buffer_lock:

        if len(audio_buffer) == 0:
            return

        audio = audio_buffer.copy()

        audio_buffer = np.array(
            [],
            dtype=np.float32
        )

    duration = len(audio) / SAMPLE_RATE

    print(
        f"Transcribing {duration:.2f}s"
    )

    segments, info = model.transcribe(
        audio,
        language="en"
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    if text:
        print(f"STT: {text}")


# -------------------------
# VAD event receiving
# -------------------------

def vad_loop():

    global speaking

    receive_buffer = b""

    while True:

        data = vad_client.recv(4096)

        if not data:

            print("VAD disconnected")

            break

        receive_buffer += data

        while b"\n" in receive_buffer:

            message_bytes, receive_buffer = (
                receive_buffer.split(
                    b"\n",
                    1
                )
            )

            if not message_bytes:
                continue

            event = json.loads(
                message_bytes.decode()
            )

            event_type = event.get("type")

            if event_type == "speech_start":

                speaking = True

                print("STT: speech started")


            elif event_type == "speech_end":

                speaking = False

                print("STT: speech ended")

                process_audio()


# Start VAD listener

threading.Thread(
    target=vad_loop,
    daemon=True
).start()


# -------------------------
# Audio connection
# -------------------------

audio_client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

audio_client.connect(
    (AUDIO_HOST, AUDIO_PORT)
)


# -------------------------
# Audio receiving
# -------------------------

def recv_exactly(sock, amount):

    data = b""

    while len(data) < amount:

        packet = sock.recv(
            amount - len(data)
        )

        if not packet:
            return None

        data += packet

    return data


def receive_frame():

    length_bytes = recv_exactly(
        audio_client,
        4
    )

    if length_bytes is None:
        return None

    length = int.from_bytes(
        length_bytes,
        "big"
    )

    return recv_exactly(
        audio_client,
        length
    )


# -------------------------
# Main audio loop
# -------------------------

print("STT service started")

while True:

    frame = receive_frame()

    if frame is None:

        print(
            "Audio service disconnected"
        )

        break

    samples = np.frombuffer(
        frame,
        dtype=np.float32
    )

    if not speaking:
        continue

    with buffer_lock:

        audio_buffer = np.concatenate(
            (
                audio_buffer,
                samples
            )
        )