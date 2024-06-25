import os
import machine
from machine import RTC, SDCard, Pin

"""
This simple tool can be used for importing an app from the SD card (or anywhere else) just like the app loader in main.py does.
Good for testing and debugging app behaviour on SDCard apps especially.

"""

try:
    sd = SDCard(slot=2, sck=Pin(40), miso=Pin(39), mosi=Pin(14), cs=Pin(12))
    os.mount(sd, '/sd')
except OSError as e:
    print(e)
    print("Could not mount SDCard!")

# app to launch from SD
app_path = "/sd/apps/Catacombs/catacombs.py"

try:
    __import__(app_path)
except ImportError as e:
    print(e)
    print(f"Tried to launch {app_path}, but failed!")

app_path = "/apps/Catacombs/catacombs.py"

try:
    __import__(app_path)
except ImportError as e:
    print(e)
    print(f"Tried to launch {app_path}, but failed!")
