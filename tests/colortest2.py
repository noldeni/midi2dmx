#!/usr/bin/env python
import time
import math

def mapToneToColor(note):
    # Maps every Note regardless of octave to a fixed color
    #Chromatische Farbtabelle aus Virtual MIDI Piano Keyboard
    colordict = {
        0:(0,0,255),
        1:(127,0,255),
        2:(255,0,255),
        3:(255,0,127),
        4:(255,0,0),
        5:(255,127,0),
        6:(255,255,0),
        7:(127,255,0),
        8:(0,255,0),
        9:(0,255,127),
        10:(0,255,255),
        11:(0,127,255),
    }
    while True:
        if note in range(0,12):
            return colordict[note]
        note -= 12

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    for i in range(0, 128):
        mappedColorValue = mapToneToColor(i)
        print("Colorvalue: %s Data[%s]" % (i, mappedColorValue))
        time.sleep(1)
    #mappedColorValue = mapToneToColor(random.randint(0, 127))
    #sendOffsetColor(mappedColorValue)
    #time.sleep(1)
except KeyboardInterrupt:
    print('Interrupted.')
finally:
    print("Exit.")
