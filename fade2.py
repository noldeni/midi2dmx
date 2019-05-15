#!/usr/bin/python

from __future__ import print_function
import argparse
import sys
import array
from ola.ClientWrapper import ClientWrapper
from time import sleep

import math

wrapper = None


def dmxsent(status):
    if status.Succeeded():
        pass
        # print('Success!')
    else:
        print('Error: %s' % status.message, file=sys.stderr)

    global wrapper
    if wrapper:
        wrapper.Stop()


def senddmx(data_in):
    universe = 1
    global wrapper
    wrapper = ClientWrapper()
    client = wrapper.Client()
    # send 1 dmx frame with values for channels 1-6
    client.SendDmx(universe, data_in, dmxsent)
    wrapper.Run()


# def senddmx(rgb_in):
#     universe = 1
#     data = array.array('B')
#     # first fixture
#     data.append(rgb_in['rot'])     # channel 1 rot
#     data.append(rgb_in['gruen'])   # channel 2 gruen
#     data.append(rgb_in['blau'])    # channel 3 blau
#     data.append(0)              # channel 4 weiss
#     data.append(255)            # channel 5 dimmer
#     data.append(0)              # channel 6 strobe
#     # second fixture
#     data.append(rgb_in['rot'])     # channel 7 rot
#     data.append(rgb_in['gruen'])   # channel 8 gruen
#     data.append(rgb_in['blau'])    # channel 9 blau
#     data.append(0)              # channel 10 weiss
#     data.append(255)            # channel 11 dimmer
#     data.append(0)              # channel 12 strobe
#     # third fixture
#     data.append(rgb_in['rot'])     # channel 13 rot
#     data.append(rgb_in['gruen'])   # channel 14 gruen
#     data.append(rgb_in['blau'])    # channel 15 blau
#     data.append(0)              # channel 16 weiss
#     data.append(255)            # channel 17 dimmer
#     data.append(0)              # channel 18 strobe
#     # fourth fixture
#     data.append(rgb_in['rot'])     # channel 19 rot
#     data.append(rgb_in['gruen'])   # channel 20 gruen
#     data.append(rgb_in['blau'])    # channel 21 blau
#     data.append(0)              # channel 22 weiss
#     data.append(255)            # channel 23 dimmer
#     data.append(0)              # channel 24 strobe
#     # fifth fixture
#     data.append(rgb_in['rot'])     # channel 25 rot
#     data.append(rgb_in['gruen'])   # channel 26 gruen
#     data.append(rgb_in['blau'])    # channel 27 blau
#     data.append(0)              # channel 28 weiss
#     data.append(255)            # channel 29 dimmer
#     data.append(0)              # channel 30 strobe
#     # sixth fixture
#     data.append(rgb_in['rot'])     # channel 31 rot
#     data.append(rgb_in['gruen'])   # channel 32 gruen
#     data.append(rgb_in['blau'])    # channel 33 blau
#     data.append(0)              # channel 34 weiss
#     data.append(255)            # channel 35 dimmer
#     data.append(0)              # channel 36 strobe
#     global wrapper
#     wrapper = ClientWrapper()
#     client = wrapper.Client()
#     # send 1 dmx frame with values for channels 1-6
#     client.SendDmx(universe, data, dmxsent)
#     wrapper.Run()


def hsv_color(h, s, v):
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
    return {'rot': r, 'gruen': g, 'blau': b}


def sine_color(angle, shift=120):
    amplitude = 255 / 2
    center = 255 / 2
    r = round(math.sin(math.radians(angle)) * amplitude + center)
    g = round(math.sin(math.radians(angle + shift)) * amplitude + center)
    b = round(math.sin(math.radians(angle + (2 * shift))) * amplitude + center)
    return {'rot': int(r), 'gruen': int(g), 'blau': int(b)}


def wheel_color(position):
    """Get color from wheel value (0 - 384)."""

    if position < 0:
        position = 0
    if position > 384:
        position = 384

    if position < 128:
        r = 127 - position % 128
        g = position % 128
        b = 0
    elif position < 256:
        g = 127 - position % 128
        b = position % 128
        r = 0
    else:
        b = 127 - position % 128
        r = position % 128
        g = 0

    return {'rot': r, 'gruen': g, 'blau': b}


def getOffset(high, curr, off):
    res = curr+off
    if res > high:
        res = res-high
    return res


def blackout(count):
    data = array.array('B')
    for fix in range(0, count):
        # first fixture
        data.append(0)  # channel 1 rot
        data.append(0)  # channel 2 gruen
        data.append(0)  # channel 3 blau
        data.append(0)  # channel 4 weiss
        data.append(0)  # channel 5 dimmer
        data.append(0)  # channel 6 strobe
    return data


def white(count):
    data = array.array('B')
    for fix in range(0, count):
        # first fixture
        data.append(0)  # channel 1 rot
        data.append(0)  # channel 2 gruen
        data.append(0)  # channel 3 blau
        data.append(255)  # channel 4 weiss
        data.append(255)  # channel 5 dimmer
        data.append(0)  # channel 6 strobe
    return data


parser = argparse.ArgumentParser(description='Output fading colors to dmx devices.')
parser.add_argument('-f', '--fixtures',
                    type=int,
                    default=1,
                    help='specify the number of fixtures (default 1)')
parser.add_argument('-o', '--offset',
                    type=int,
                    default=0,
                    help='specify the offset between fixtures (default 0)')
parser.add_argument('-t', '--type',
                    default='hsv',
                    choices=['hsv', 'sine', 'wheel'],
                    help='select type of fader (default hsv)')
parser.add_argument('-d', '--delay',
                    type=float,
                    default=0.1,
                    help='delay between colors (default 0.1)')

parser.add_argument('-p', '--phaseshift',
                    type=int,
                    default=90,
                    help='phaseshift between sine waves (default 90)')

parser.add_argument('-s', '--saturation',
                    type=float,
                    default=1,
                    help='saturation for hsv colors (default 1)')

parser.add_argument('-v', '--value',
                    type=float,
                    default=1,
                    help='value for hsv colors (default 1)')

args = parser.parse_args()
delay = args.delay
offset = args.offset
if args.type == 'hsv':
    start = 0
    end = 360
    saturation = args.saturation
    value = args.value
    try:
        while True:
            for pos in range(start, end):
                data = array.array('B')
                for fix in range(0, args.fixtures):
                    rgb = hsv_color(pos, saturation, value)
                    # first fixture
                    data.append(rgb['rot'])  # channel 1 rot
                    data.append(rgb['gruen'])  # channel 2 gruen
                    data.append(rgb['blau'])  # channel 3 blau
                    data.append(0)  # channel 4 weiss
                    data.append(255)  # channel 5 dimmer
                    data.append(0)  # channel 6 strobe
                    pos = getOffset(end, pos, offset)
                senddmx(data)
                sleep(delay)

    except KeyboardInterrupt:
        senddmx(white(args.fixtures))
        print('Finish!')
elif args.type == 'sine':
    start = 0
    end = 361
    phaseshift = args.phaseshift
    try:
        while True:
            for pos in range(start, end):
                data = array.array('B')
                for fix in range(0, args.fixtures):
                    rgb = sine_color(pos, phaseshift)
                    # first fixture
                    data.append(rgb['rot'])  # channel 1 rot
                    data.append(rgb['gruen'])  # channel 2 gruen
                    data.append(rgb['blau'])  # channel 3 blau
                    data.append(0)  # channel 4 weiss
                    data.append(255)  # channel 5 dimmer
                    data.append(0)  # channel 6 strobe
                    pos = getOffset(end, pos, offset)
                senddmx(data)
                sleep(delay)

    except KeyboardInterrupt:
        senddmx(white(args.fixtures))
        print('Finish!')
elif args.type == 'wheel':
    start = 0
    end = 385
    try:
        while True:
            for pos in range(start, end):
                data = array.array('B')
                for fix in range(0, args.fixtures):
                    rgb = wheel_color(pos)
                    # first fixture
                    data.append(rgb['rot'])  # channel 1 rot
                    data.append(rgb['gruen'])  # channel 2 gruen
                    data.append(rgb['blau'])  # channel 3 blau
                    data.append(0)  # channel 4 weiss
                    data.append(255)  # channel 5 dimmer
                    data.append(0)  # channel 6 strobe
                    pos = getOffset(end, pos, offset)
                senddmx(data)
                sleep(delay)

    except KeyboardInterrupt:
        senddmx(white(args.fixtures))
        print('Finish!')
else:
    print('Nothing!')
