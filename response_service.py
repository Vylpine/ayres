import json
import socket
import threading

SERVICE_NAME = "response"

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


def handle_message(message):
        print(message)