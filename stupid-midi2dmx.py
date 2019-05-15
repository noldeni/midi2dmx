from lib.StupidArtnet import StupidArtnet
import time
import random
import logging
import math

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)

# Global parameter class
class param:
    # Artnet parameter
    target_ip = '192.168.56.1'		# typically in 2.x or 10.x range
    universe = 0 					# see docs
    packet_size = 100				# it is not necessary to send whole universe
    thereminRangeStart = 0
    thereminRangeEnd = 127
    hsvRangeStart = 50
    hsvRangeEnd = 310
    hsvOffset = 240
    hsvSaturation = 1
    hsvValue = 1
    fixtures = 6
    fixtureChannels = 6
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

def getHsvColor(note):
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

for x in range(0, 128):
  colorvalue = getHsvColor(x)
  rgb = hsvToRgb(colorvalue, param.hsvSaturation, param.hsvValue)
  print("Theremin value: %i HSV value: %9.5f RGB: %s" % (x, colorvalue, rgb))
  packet_size = param.fixtures * param.fixtureChannels
  a = StupidArtnet(param.target_ip, param.universe, packet_size)
  packet = bytearray(packet_size)		# create packet for Artnet
