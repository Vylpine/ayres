import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 5000

services = {}

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))
server.listen()

print(f"AYRES Core listening on {HOST}:{PORT}")

def handle_client(conn):

    buffer = ""

    while True:

        data = conn.recv(1024)

        if not data:
            break

        buffer += data.decode()

        while "\n" in buffer:

            line, buffer = buffer.split("\n", 1)

            message = json.loads(line)

            process_message(
                conn,
                message
            )

def process_message(conn, message):

    if message["type"] == "register":

        service_name = message["service"]

        services[service_name] = {
            "conn": conn
        }

        print(
            f"{service_name} registered"
        )

        return

    target = message.get("target")

    if target not in services:

        print(
            f"Unknown target: {target}"
        )

        return

    target_conn = services[target]["conn"]

    target_conn.send(
        (
            json.dumps(message)
            + "\n"
        ).encode()
    )

while True:

    conn, addr = server.accept()

    print(
        f"Connection from {addr}"
    )

    threading.Thread(
        target=handle_client,
        args=(conn,),
        daemon=True
    ).start()