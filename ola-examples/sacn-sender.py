#!/usr/bin/python3

import sacn
import time

sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
sender[1].multicast = True  # set multicast to True
# sender[1].destination = "192.168.1.20"  # or provide unicast information.
# Keep in mind that if multicast is on, unicast is not used
#sender[1].dmx_data = (1, 2, 3, 4)  # some test DMX data

fixture1 = (0, 0, 255, 0, 255, 0) #Blau maximum
fixture2 = (0, 255, 0, 0, 255, 0) #Grün maximum
fixture3 = (255, 0, 0, 0, 255, 0) #Rot maximum
fixture4 = (0, 0, 255, 0, 255, 0) #Blau maximum
fixture5 = (0, 255, 0, 0, 255, 0) #Grün maximum
fixture6 = (255, 0, 0, 0, 255, 0) #Rot maximum
sender[1].dmx_data = fixture1 + fixture2 + fixture3 + fixture4 + fixture5 + fixture6

time.sleep(60)  # send the data for 10 seconds
sender.stop()  # do not forget to stop the sender