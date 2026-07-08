import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import socket

SERVICE_NAME = "spotify"

scope = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-read-recently-played "
    "user-top-read "
    "user-library-read "
    "user-library-modify "
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-private "
    "playlist-modify-public "
    "user-follow-read "
    "user-follow-modify "
    "user-read-private "
    "user-read-email"
)
with open("credentials.json", "r") as file:
        credentials = json.load(file)

CLIENT_ID = credentials["clientid"]
CLIENT_SECRET = credentials["clientsecret"]
REDIRECT_URL = credentials["redirect"]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL))

def search_liked(song):
        offset = 0
        while True: 
                results = sp.current_user_saved_tracks(
                        limit=50,
                        offset=offset
                )
                tracks = results["items"]

                if not tracks:
                        return None
        
                for item in tracks:
                        track = item["track"]
                        if song.lower() in track["name"].lower():
                                return track
                offset += 50

def play_song(song):
        liked_results = search_liked(song=song)
        if not liked_results:
                results = sp.search(
                        q=song,
                        limit=1,
                        type="track"
                )
                if not results:
                        print("Song not found")
                        return None
                for track in results["tracks"]["items"]:
                        sp.start_playback(
                                uris=[track["uri"]]
                        )
                        return {
                                "song": track["name"],
                                "artist": track["artists"][0]["name"]
                        }
        else:
                sp.start_playback(
                        uris=[liked_results["uri"]]
                )
                return {
                        "song": liked_results["name"],
                        "artist": liked_results["artists"][0]["name"]
                        }

def play_playlist(query):
        playlists = sp.current_user_playlists()

        for playlist in playlists["items"]:
                if playlist["name"].lower() == query.lower():
                        sp.start_playback(
                                context_uri=playlist["uri"]
                        )
                        return None
        print("Playlist not found")

def start_playback():
        sp.start_playback()

def stop_playback():
        sp.pause_playback()

def fast_forward():
        sp.next_track()

def rewind():
        sp.previous_track()

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

def handle_message(query):
        query_type = query["type"]
        query_data = query["data"]
        
        if query_type == "play_song":
                song_data = play_song(query_data["song"])
                send_message(target="core", source=SERVICE_NAME, msg_type="success", data={
                        "command": query_type,
                        "song": song_data,
                        "artist": song_data["artist"]
                        })
        
        elif query_type == "play_playlist":
                play_playlist(query_data["playlist"])
        
        elif query_type == "start_playback":
                start_playback()

        elif query_type == "stop_playback":
                stop_playback()

        elif query_type == "fast_forward":
                fast_forward()

        elif query_type == "rewind":
                rewind()
        else:
                send_message(
                        target="core",
                        source=SERVICE_NAME,
                        msg_type="success",
                        data={
                                "command": query_type
                        }
                )

        client.send(
                (json.dumps(response) + "\n").encode()
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