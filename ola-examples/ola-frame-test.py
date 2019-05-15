#!/usr/bin/python3
# -*- coding: utf-8 -*-

import array
#from ola.ClientWrapper import ClientWrapper

wrapper = None
loop_count = 0
TICK_INTERVAL = 100  # in ms
DMX_MIN_SLOT_VALUE = 0

channels =	{
  "R": 0,
  "G": 1,
  "B": 2,
  "W": 3,
  "D": 4,
  "S": 5
}

# compute frame here
fixtures = 6
fixtureChannels = 6
initialValue = 0
data = array.array('B', [DMX_MIN_SLOT_VALUE] * (fixtures * fixtureChannels))

# set(fixture, channel, value)
# set(4, "G", 125)
address = ((4 - 1) * fixtureChannels) + channels["G"]
print('Länge: %i Address: %i' % (len(data), address))

                                                                        

