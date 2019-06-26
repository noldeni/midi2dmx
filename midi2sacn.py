#!/usr/bin/env python
import sys
import sacn
import time
import math
import random
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE

# Global parameter class
class param:
  thereminRangeStart = 0
  thereminRangeEnd = 127
  hsvRangeStart = 0
  hsvRangeEnd = 360
  hsvOffset = 240
  hsvSaturation = 1
  hsvValue = 1
  fixtures = 12
  fixtureOffset = 30
  dimmer = 255
  olaserverip = "192.168.178.39"
  #operationMode = "equal"
  operationMode = "offset"
  #operationMode = "test"
  channels =	{
    "R": 0,
    "G": 1,
    "B": 2,
    "W": 3,
    "D": 4,
    "S": 5
  }

def MidiInputHandler(event, data=None):
    message, deltatime = event
    if message[0] & 0xF0 == NOTE_ON:
        status, note, velocity = message
        channel = (status & 0xF) + 1
        mappedColorValue = mapToneToColor(note)
        sendColor(mappedColorValue)
        print("Keyboard: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, mappedColorValue))
    if message[0] & 0xF0 == CONTROL_CHANGE:
        status, note, velocity = message
        if note == 2:
            param.dimmer = velocity
        elif note == 20:
            channel = (status & 0xF) + 1
            mappedColorValue = mapToneToColor(velocity)
            sendColor(mappedColorValue)
            print("Theremin: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, mappedColorValue))

def sendColor(hsvColor):
    if param.operationMode == "equal":
        print('Equal (Color wheel)')
        sendEqualColor(hsvColor)
    elif param.operationMode == "offset":
        print('Offset')
        sendOffsetColor(hsvColor)
    elif param.operationMode == "test":
        print('Single')
    else:
        print('Testmode')

def sendEqualColor(hsvColor):
    defaultValue = (0, 255, 0) # white off, dimmer 100%, effect off
    rgb = hsvToRgb(hsvColor, param.hsvSaturation, param.hsvValue)
    data = ()
    for i in range(1, param.fixtures + 1):
        data += rgb + defaultValue
    sender[1].dmx_data = data

def sendOffsetColor(hsvColor):
    defaultValue = (0, 255, 0) # white off, dimmer 100%, effect off
    rgb = hsvToRgb(hsvColor, param.hsvSaturation, param.hsvValue)
    data = ()
    for i in range(1, param.fixtures + 1):
        data += rgb + defaultValue
        rgb = hsvToRgb(hsvColor + param.fixtureOffset, param.hsvSaturation, param.hsvValue)
    sender[1].dmx_data = data

def mapToneToColor(note):
    colorvalue = map(note, param.thereminRangeStart, param.thereminRangeEnd, param.hsvRangeStart, param.hsvRangeEnd)
    colorvalue += param.hsvOffset
    if colorvalue > param.hsvRangeEnd:
        colorvalue -= param.hsvRangeEnd
    return colorvalue

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def hsvToRgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return (r, g, b)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler)

sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
# sender[1].multicast = True  # set multicast to True
# sender[1].destination = "192.168.56.1"  # or provide unicast information.
#sender[1].destination = "127.0.0.1"  # or provide unicast information.
#sender[1].destination = "192.168.178.39"  # or provide unicast information.
sender[1].destination = param.olaserverip  # or provide unicast information.
# Keep in mind that if multicast is on, unicast is not used
#sender[1].dmx_data = (1, 2, 3, 4)  # some test DMX data

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        #mappedColorValue = mapToneToColor(random.randint(0, 127))
        #sendOffsetColor(mappedColorValue)
        time.sleep(5)
except KeyboardInterrupt:
    print('Interrupted.')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
    sender.stop()  # do not forget to stop the sender