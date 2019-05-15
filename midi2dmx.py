#!/usr/bin/env python
#
# test_midiin_callback.py
#
"""Show how to receive MIDI input by setting a callback function."""

from __future__ import print_function

import logging
import sys
import time
import math
import sacn

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)

# Global parameter class
class param:
  thereminRangeStart = 0
  thereminRangeEnd = 127
  hsvRangeStart = 50
  hsvRangeEnd = 310
  hsvOffset = 240
  hsvSaturation = 1
  hsvValue = 1
  fixtures = 6
  fixtureOffset = 30
  dimmer = 255
  channels =	{
    "R": 0,
    "G": 1,
    "B": 2,
    "W": 3,
    "D": 4,
    "S": 5
  }

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        if message[0] & 0xF0 == NOTE_ON:
            status, note, velocity = message
            channel = (status & 0xF) + 1
            hsvColor = self.__getColor__(note)
            self.__sendDMX__(hsvColor)
            print("Keyboard: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, hsvColor))
        if message[0] & 0xF0 == CONTROL_CHANGE:
            status, note, velocity = message
            if note == 20:
                channel = (status & 0xF) + 1
                hsvColor = self.__getColor__(velocity)
                self.__sendDMX__(hsvColor)
                print("Theremin: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, hsvColor))
        #print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

    def __sendDMX__(self, hsvColor):
        defaultValue = (0, 255, 0) # white off, dimmer 100%, effect off
        fixture1 = (0, 0, 255, 0, 255, 0) #Blau maximum
        fixture2 = (0, 255, 0, 0, 255, 0) #Grün maximum
        fixture3 = (255, 0, 0, 0, 255, 0) #Rot maximum
        fixture4 = (0, 0, 255, 0, 255, 0) #Blau maximum
        fixture5 = (0, 255, 0, 0, 255, 0) #Grün maximum
        fixture6 = hsvColor + defaultValue
        sender[1].dmx_data = fixture1 + fixture2 + fixture3 + fixture4 + fixture5 + fixture6

    def getHsvColor(note):
        colorvalue = map(note, param.thereminRangeStart, param.thereminRangeEnd, param.hsvRangeStart, param.hsvRangeEnd)
        colorvalue += param.hsvOffset
        if colorvalue > param.hsvRangeEnd:
        colorvalue -= param.hsvRangeEnd
        return colorvalue

    def map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def __getColor__(self, note):
        rangeStart = 0
        rangeEnd = 127
        saturation = 1
        value = 1
        colorvalue = int((note - rangeStart) * 360/((rangeEnd - rangeStart) + 1))
        rgb = self.__hsv_color__(colorvalue, saturation, value)
        return rgb

    def __hsv_color__(self, h, s, v):
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
midiin.set_callback(MidiInputHandler(port_name))

sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
sender[1].multicast = True  # set multicast to True
# sender[1].destination = "192.168.1.20"  # or provide unicast information.
# Keep in mind that if multicast is on, unicast is not used
#sender[1].dmx_data = (1, 2, 3, 4)  # some test DMX data

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
    sender.stop()  # do not forget to stop the sender

