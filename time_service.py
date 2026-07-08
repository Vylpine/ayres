import time
import json
import socket
import threading
from datetime import datetime

now = datetime.now()

hour = now.hour
minute = now.minute

SERVICE_NAME = "timer"

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
)

client.connect((HOST, PORT))

register_message = {
        "type": "register",
        "service": SERVICE_NAME
}

client.send(
        (json.dumps(register_message) + "\n").encode()
)

def send_message(target, msg_type, data):

    message = {
        "source": SERVICE_NAME,
        "target": target,
        "type": msg_type,
        "data": data
    }

    client.send(
        (json.dumps(message) + "\n").encode()
    )

def start_timer(duration):
    time.sleep(duration)
    print("Timer done!")
    send_message(target="ayres",
    source=SERVICE_NAME,
    msg_type="timer_done",
    data={
        "duration": duration
    })

def start_alarm(end_time):
    while True:
        hour = now.hour
        minute = now.minute

        if f"{hour}:{minute}" == end_time:
            print("Alarm done!")
            send_message(
                target="ayres",
                source=SERVICE_NAME,
                msg_type="alarm_done",
                data={
                    "end_time": end_time
                }
            )
            return

        else:
            time.sleep(30)

def handle_message(query):

    query_type = query["type"]
    query_data = query["data"]

    if query_type == "start_timer":

        duration = query_data["duration"]

        threading.Thread(
            target=start_timer,
            args=(duration,),
            daemon=True
        ).start()


buffer = ""

while True:

        data = client.recv(1024)

        if not data:
                print("Disconnected from Core")
                break

        buffer += data.decode()

        while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                message = json.loads(line)

                handle_message(message)