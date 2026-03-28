import datetime
import json
from time import time
import os

def save_event(name, time, value):
    with open(f"./events/{time}.json", "w") as file:
        eventdata = {"name": name, "value": value} #   stores name and importance of event
        json.dump(eventdata, file, indent=4) # as a .json file

def check_events():
    seconds = int(time()) # seconds since last epoch
    seconds -= 86400 # minus one day
    for f in os.listdir("./events/"):
        f = f[:-5]
        if (int(f) >= seconds): # consider an event within one day soon
            with open(f"./events/{f}.json", "r") as file:
                event = json.load(file)
                os.remove(f"./events/{f}.json")
                return event

def save_alarm(name, time):
    with open(f"./alarms/{time}.json", "w") as file:
        alarmdata = {"name": name} #           stores name of alarm as a 
        json.dump(alarmdata, file, indent=4) # .json file

def check_alarms():
    seconds = int(time()) # seconds since last epoch
    for f in os.listdir("./alarms/"):
        f = f[:-5]
        if (int(f) >= seconds): # if an alarm is set for now, detect it
            with open(f"./alarms/{f}.json", "r") as file:
                alarm = json.load(file)
                os.remove(f"./alarms/{f}.json")
                return alarm
