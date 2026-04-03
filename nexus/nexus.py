from google import genai
from google.genai import types
API_KEY = open("./NexusKey.txt", "r").read()

client = genai.Client(api_key=API_KEY)

#define functions
check_mem_function = {
        "name": "check_mem",
        "description": "checks short and long term memory for potential information if required",
        "parameters": {},
        }
save_memory_function = {
        "name": "save_memory",
        "description": "saves important or notable memory to short-term. important enough memories will be transferred to long-term",
        "parameters": {
            "type": "object",
            "properties": {
                "significance": {
                    "type": "integer",
                    "description": "the importance of the memory on a scale of 1-8",
                    },
                "content": {
                    "type": "string",
                    "description": "a short description of the memory to be saved. Example: 'the user programs in python'"
                    },
                },
                "required": ["significance", "content"],
            },
        }
save_event_function = {
        "name": "save_event",
        "description": "saves an event for later notification",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "the name of the saved event",
                    },
                "value": {
                    "type": "integer",
                    "description": "a rating of 1-10 on how important the event is",
                    },
                },
                "required": ["name", "value"],
            },
        }
save_alarm_function = {
        "name": "save_alarm",
        "description": "saves an alarm for later notification",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "the name of the alarm",
                    },
                "time": {
                    "type": "integer",
                    "description": f""}}}}
