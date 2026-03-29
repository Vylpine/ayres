import os
import time
import json

sig_cuttoff = 5  # memory is rated from 1-10 based on significance, if the rated
                          # significance is higher than the cuttoff, then the memory is
                          # transferred to long-term memory

def check_short_term_memory():
    for f in os.listdir("./mem/short_term"):
        f = f[:2]
        if int(f) >= sig_cuttoff:
            os.rename(f"./mem/short_term/{f}.json", f"./mem/long_term/{f}.json")

def clear_short_term_memory():
    for f in os.listdir("./mem/short_term"):
        f = f[:-5]
        if int(f[1:]) >= (int(time.time()) - 604800): # consider a short-term memory within a
                                                  # week obsolete and delete to save space
            os.remove(f"./mem/short_term/{f}.json")

def check_mem():
    memory = []
    listdir = os.listdir("./mem/short_term/")
    for i in range(0, 7):
        f = listdir[i]
        with open(f"./mem/short_term/{f}", "r") as file:
            short_term_mem = json.load(file)
            short_term_mem = short_term_mem["content"]
            memory += short_term_mem

