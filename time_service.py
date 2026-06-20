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

def start_timer(duration):
    time.sleep(duration)
    print("Timer done!")
    fin_message = {
        "target": "ayres",
        "source": SERVICE_NAME,
        "type": "timer_done",
        "duration": duration
    }
    client.send(
        (json.dumps(fin_message) + "\n").encode()
    )

def start_alarm(end_time):
    while True:
        if f"{hour}:{minute}" == end_time:
            print("Alarm done!")
            fin_message = {
                "target": "ayres",
                "source": SERVICE_NAME,
                "type": "alarm_done",
                "end_time": end_time
            }
            client.send(
                (json.dumps(fin_message) + "\n").encode()
            )

        else:
            time.sleep(30)

def handle_message(query):

    query_type = query["type"]

    if query_type == "start_timer":

        duration = query["duration"]

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