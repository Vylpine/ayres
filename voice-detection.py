
import socket
import numpy as np
import torch
import json

from silero_vad import load_silero_vad


HOST = "127.0.0.1"
PORT = 6000

STT_HOST = "127.0.0.1"
STT_PORT = 6100

SAMPLE_RATE = 16000

WINDOW_SIZE = 512
HOP_SIZE = 320

START_THRESHOLD = 0.75
STOP_THRESHOLD = 0.20

START_FRAMES = 3
STOP_FRAMES = 10


# -------------------------
# Audio connection
# -------------------------

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    (HOST, PORT)
)


# -------------------------
# VAD model
# -------------------------

model = load_silero_vad()

model.reset_states()


# -------------------------
# VAD state
# -------------------------

sample_buffer = np.array(
    [],
    dtype=np.float32
)

currently_speaking = False

speech_counter = 0
silence_counter = 0


# -------------------------
# STT connection
# -------------------------

stt_client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

stt_client.connect(
    (STT_HOST, STT_PORT)
)


# -------------------------
# Send VAD event
# -------------------------

def send_event(event_type):

    message = {
        "source": "vad",
        "target": "stt",
        "type": event_type
    }

    data = (
        json.dumps(message) + "\n"
    ).encode()

    stt_client.sendall(data)


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
        client,
        4
    )

    if length_bytes is None:
        return None

    length = int.from_bytes(
        length_bytes,
        "big"
    )

    return recv_exactly(
        client,
        length
    )


# -------------------------
# Main VAD loop
# -------------------------

print("VAD service started")

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

    sample_buffer = np.concatenate(
        (
            sample_buffer,
            samples
        )
    )

    while len(sample_buffer) >= WINDOW_SIZE:

        chunk = sample_buffer[:WINDOW_SIZE]

        sample_buffer = sample_buffer[HOP_SIZE:]

        audio_tensor = torch.from_numpy(
            chunk
        )

        confidence = model(
            audio_tensor,
            SAMPLE_RATE
        ).item()



        # -------------------------
        # Speech detection
        # -------------------------

        if confidence >= START_THRESHOLD:

            speech_counter += 1
            silence_counter = 0


        elif confidence <= STOP_THRESHOLD:

            silence_counter += 1
            speech_counter = 0


        # Between thresholds:
        # leave counters unchanged


        # -------------------------
        # Speech started
        # -------------------------

        if (
            not currently_speaking
            and speech_counter >= START_FRAMES
        ):

            currently_speaking = True

            speech_counter = 0

            print(
                "Speech started"
            )

            send_event(
                "speech_start"
            )


        # -------------------------
        # Speech ended
        # -------------------------

        elif (
            currently_speaking
            and silence_counter >= STOP_FRAMES
        ):

            currently_speaking = False

            silence_counter = 0

            print(
                "Speech ended"
            )

            send_event(
                "speech_end"
            )
