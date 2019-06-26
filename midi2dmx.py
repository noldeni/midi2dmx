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
  hsvRangeStart = 0
  hsvRangeEnd = 360
  hsvOffset = 240
  hsvSaturation = 1
  hsvValue = 1
  fixtures = 6
  fixtureOffset = 30
  dimmer = 255
  operationMode = "test"
  olaserverip = "192.168.178.12"
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
            mappedColorValue = self.mapToneToColor(note)
            self.__sendDMX__(mappedColorValue)
            print("Keyboard: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, mappedColorValue))
        if message[0] & 0xF0 == CONTROL_CHANGE:
            status, note, velocity = message
            if note == 2:
                param.dimmer = velocity
            elif note == 20:
                channel = (status & 0xF) + 1
                mappedColorValue = self.mapToneToColor(velocity)
                self.__sendDMX__(mappedColorValue)
                print("Theremin: Channel[%s] Note[%s] Velocity[%s] Color[%s]" % (channel, note, velocity, mappedColorValue))
        #print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

    def __sendDMX__(self, mappedColorValue):
        if param.operationMode == "equal":
            print('Color wheel')
        elif param.operationMode == "wheel":
            print('Zero')
        elif param.operationMode == "wheel":
            print('Single')
        else:
            print('Testmode')
            defaultValue = (0, param.dimmer, 0) # white off, dimmer 100%, effect off
            fixture1 = (0, 0, 255) + defaultValue #Blau maximum
            fixture2 = (0, 255, 0) + defaultValue #Grün maximum
            fixture3 = (255, 0, 0) + defaultValue #Rot maximum
            fixture4 = (0, 0, 255) + defaultValue #Blau maximum
            fixture5 = (0, 255, 0) + defaultValue #Grün maximum
            fixture6 = mappedColorValue + defaultValue
            sender[1].dmx_data = fixture1 + fixture2 + fixture3 + fixture4 + fixture5 + fixture6

    def __sendOffsetColor__(self, mappedColorValue):
        defaultValue = (0, param.dimmer, 0) # white off, dimmer 100%, effect off
        rgb = self.__hsvToRgb__(mappedColorValue, param.hsvSaturation, param.hsvValue)
        data = ()
        for i in range(1, param.fixtures + 1):
            data += rgb + defaultValue
            rgb = self.__hsvToRgb__(mappedColorValue + param.fixtureOffset, param.hsvSaturation, param.hsvValue)
        sender[1].dmx_data = data

    def __sendEqualColor__(self, mappedColorValue):
        defaultValue = (0, param.dimmer, 0) # white off, dimmer 100%, effect off
        rgb = self.__hsvToRgb__(mappedColorValue, param.hsvSaturation, param.hsvValue)
        data = ()
        for i in range(1, param.fixtures + 1):
            data += rgb + defaultValue
        sender[1].dmx_data = data

    def mapToneToColor(self, note):
        colorvalue = self.map(note, param.thereminRangeStart, param.thereminRangeEnd, param.hsvRangeStart, param.hsvRangeEnd)
        colorvalue += param.hsvOffset
        if colorvalue > param.hsvRangeEnd:
            colorvalue -= param.hsvRangeEnd
        return colorvalue

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def __hsvToRgb__(self, h, s, v):
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
#sender[1].multicast = True  # set multicast to True
sender[1].destination = param.olaserverip  # or provide unicast information.
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

