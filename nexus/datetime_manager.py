import datetime
import json
from time import time
import os

def save_event(name, time, value):
    with open(f"./events/{time}.json", "w") as file:
        eventdata = {"name": name, "value": value} #   stores name and importance of event
        json.dump(eventdata, file, indent=4) # as a .json file

def check_events():
    milliseconds = int(time()) # milliseconds since last epoch
    milliseconds -= 86400 # minus one day
    for f in os.listdir("./events/"):
        f = f[:-5]
        if (int(f) >= milliseconds): # consider an event within one day soon
            with open(f"./events/{f}.json", "r") as file:
                event = json.load(file)
                os.remove(f"./events/{f}.json")
                return event
