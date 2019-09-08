#!/usr/bin/env python3

"""JACK client that prints all received MIDI events."""

import os
import math
import jack
import binascii
import struct
import sacn

# Global parameter class
class param:
    # IP address of sacn server
    #OLA_SERVER_IP = "192.168.178.39" #gilgalad
    OLA_SERVER_IP = "192.168.178.41" #colorwheel

    # MIDI definitions
    NOTE_ON = 0x90
    NOTE_OFF = 0x80
    CONTROL_CHANGE = 0xB0

    # Input selector (PAD 5)
    INPUT_THEREMIN = True
    INPUT_ARDOUR = False
    INPUT_OXYGEN = False

    # Theremin settings and values
    THERMIN_RANGE_START = 0
    THERMIN_RANGE_END = 127
    THERMIN_VELOCITY = 0
    THERMIN_PITCH = 0

    # Lighting selector (PAD 6)
    EQUAL_LIGHTS = False

    # OXYGEN mode selector (PAD 6)
    KEY_TOGGLE = False

    # All fixtures off (PAD 7)
    ALL_OFF = False

    # All fixtures white (PAD 8)
    ALL_WHITE = False

    # OXYGEN Keboard start note
    START_NOTE = 60

    # Fixtures
    FIXTURES = 12
    FIXTURE_OFFSET = 30

    # Fixture state (True = On / False = Off)
    FXTURE_1 = False
    FXTURE_2 = False
    FXTURE_3 = False
    FXTURE_4 = False
    FXTURE_5 = False
    FXTURE_6 = False
    FXTURE_7 = False
    FXTURE_8 = False
    FXTURE_9 = False
    FXTURE_10 = False
    FXTURE_11 = False
    FXTURE_12 = False

    # Keys to turn fixtures on and off
    # Key 60 = <SonicPi::Note :C4>
    # Key 61 = <SonicPi::Note :Cs4>
    # Key 62 = <SonicPi::Note :D4>
    # Key 63 = <SonicPi::Note :Eb4>
    # Key 64 = <SonicPi::Note :E4>
    # Key 65 = <SonicPi::Note :F4>
    # Key 66 = <SonicPi::Note :Fs4>
    # Key 67 = <SonicPi::Note :G4>
    # Key 68 = <SonicPi::Note :Ab4>
    # Key 69 = <SonicPi::Note :A4>
    # Key 70 = <SonicPi::Note :Bb4>
    # Key 71 = <SonicPi::Note :B4>

    # Keys to set colors on and off
    # Key 72 = <SonicPi::Note :C5>
    # Key 73 = <SonicPi::Note :Cs5>
    # Key 74 = <SonicPi::Note :D5>
    # Key 75 = <SonicPi::Note :Eb5>
    # Key 76 = <SonicPi::Note :E5>
    # Key 77 = <SonicPi::Note :F5>
    # Key 78 = <SonicPi::Note :Fs5>
    # Key 79 = <SonicPi::Note :G5>
    # Key 80 = <SonicPi::Note :Ab5>
    # Key 81 = <SonicPi::Note :A5>
    # Key 82 = <SonicPi::Note :Bb5>
    # Key 83 = <SonicPi::Note :B5>

    DEFAULT_COLOR = 0 #red
    HSV_SATURATION = 1
    HSV_VALUE = 1
    HSV_RANGE_START = 0
    HSV_RANGE_END = 360
    HSV_OFFSET = 240

    FIXTURE_COLORS = {
        'C': 0,
        'Cs': 30,
        'D': 60,
        'Ds': 90,
        'E': 120,
        'F': 150,
        'Fs': 180,
        'G': 210,
        'Gs': 240,
        'A': 270,
        'As': 300,
        'B': 330,
    }
    COLOR_1_C = False
    COLOR_2_Cs = False
    COLOR_3_D = False
    COLOR_4_Ds = False
    COLOR_5_E = False
    COLOR_6_F = False
    COLOR_7_Fs = False
    COLOR_8_G = False
    COLOR_9_Gs = False
    COLOR_10_A = False
    COLOR_11_As = False
    COLOR_12_B = False
    
    # OXYGEN25 PAD status
    PAD_1 = False
    PAD_2 = False
    PAD_3 = False
    PAD_4 = False
    #PAD_5 = False
    #PAD_6 = False
    PAD_7 = False
    PAD_8 = False

client = jack.Client('ThereLightArt')
port = client.midi_inports.register('input')


@client.set_process_callback
def process(frames):
    for offset, data in port.incoming_midi_events():
        if len(data) == 3:
            status, pitch, velocity = bytes(data)
            channel = (status & 0xF) + 1
            if status & 0xF0 == param.CONTROL_CHANGE and velocity == 0 and pitch in(64, 123):
                # Ardour track start/end resets all channels -> ignore these
                pass 
            elif channel == 6:
                # Ardour track
                if param.INPUT_ARDOUR:
                    if status & 0xF0 == param.NOTE_ON:
                        print('{0}: 0x{1} ARDOUR NOTE_ON ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
                    elif status & 0xF0 == param.NOTE_OFF:
                        print('{0}: 0x{1} ARDOUR NOTE_OFF ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
            elif channel == 12:
                # OXYGEN25 keys
                if param.INPUT_OXYGEN:
                    if status & 0xF0 == param.NOTE_ON:
                        print('{0}: 0x{1} OXYGEN25 NOTE_ON ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
                        # Fixture selection
                        if pitch == param.START_NOTE:
                            param.FXTURE_1 = not param.FXTURE_1 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+1:
                            param.FXTURE_2 = not param.FXTURE_2 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+2:
                            param.FXTURE_3 = not param.FXTURE_3 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+3:
                            param.FXTURE_4 = not param.FXTURE_4 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+4:
                            param.FXTURE_5 = not param.FXTURE_5 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+5:
                            param.FXTURE_6 = not param.FXTURE_6 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+6:
                            param.FXTURE_7 = not param.FXTURE_7 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+7:
                            param.FXTURE_8 = not param.FXTURE_8 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+8:
                            param.FXTURE_9 = not param.FXTURE_9 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+9:
                            param.FXTURE_10 = not param.FXTURE_10 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+10:
                            param.FXTURE_11 = not param.FXTURE_11 if param.KEY_TOGGLE else True
                        elif pitch == param.START_NOTE+11:
                            param.FXTURE_12 = not param.FXTURE_12 if param.KEY_TOGGLE else True
                        # Color selection
                        elif pitch == param.START_NOTE+12:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_1_C = not param.COLOR_1_C
                            else:
                                param.COLOR_1_C = True
                        elif pitch == param.START_NOTE+13:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_2_Cs = not param.COLOR_2_Cs
                            else:
                                param.COLOR_2_Cs = True
                        elif pitch == param.START_NOTE+14:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_3_D = not param.COLOR_3_D
                            else:
                                param.COLOR_3_D = True
                        elif pitch == param.START_NOTE+15:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_4_Ds = not param.COLOR_4_Ds
                            else:
                                param.COLOR_4_Ds = True
                        elif pitch == param.START_NOTE+16:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_5_E = not param.COLOR_5_E
                            else:
                                param.COLOR_5_E = True
                        elif pitch == param.START_NOTE+17:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_6_F = not param.COLOR_6_F
                            else:
                                param.COLOR_6_F = True
                        elif pitch == param.START_NOTE+18:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_7_Fs = not param.COLOR_7_Fs
                            else:
                                param.COLOR_7_Fs = True
                        elif pitch == param.START_NOTE+19:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_8_G = not param.COLOR_8_G
                            else:
                                param.COLOR_8_G = True
                        elif pitch == param.START_NOTE+20:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_9_Gs = not param.COLOR_9_Gs
                            else:
                                param.COLOR_9_Gs = True
                        elif pitch == param.START_NOTE+21:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_10_A = not param.COLOR_10_A
                            else:
                                param.COLOR_10_A = True
                        elif pitch == param.START_NOTE+22:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_11_As = not param.COLOR_11_As
                            else:
                                param.COLOR_11_As = True
                        elif pitch == param.START_NOTE+23:
                            if param.KEY_TOGGLE:
                                resetColors()
                                param.COLOR_12_B = not param.COLOR_12_B
                            else:
                                param.COLOR_12_B = True
                    elif status & 0xF0 == param.NOTE_OFF:
                        print('{0}: 0x{1} OXYGEN25 NOTE_OFF ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
                        if not param.KEY_TOGGLE:
                            # Fixture selection
                            if pitch == param.START_NOTE:
                                param.FXTURE_1 = False
                            elif pitch == param.START_NOTE+1:
                                param.FXTURE_2 = False
                            elif pitch == param.START_NOTE+2:
                                param.FXTURE_3 = False
                            elif pitch == param.START_NOTE+3:
                                param.FXTURE_4 = False
                            elif pitch == param.START_NOTE+4:
                                param.FXTURE_5 = False
                            elif pitch == param.START_NOTE+5:
                                param.FXTURE_6 = False
                            elif pitch == param.START_NOTE+6:
                                param.FXTURE_7 = False
                            elif pitch == param.START_NOTE+7:
                                param.FXTURE_8 = False
                            elif pitch == param.START_NOTE+8:
                                param.FXTURE_9 = False
                            elif pitch == param.START_NOTE+9:
                                param.FXTURE_10 = False
                            elif pitch == param.START_NOTE+10:
                                param.FXTURE_11 = False
                            elif pitch == param.START_NOTE+11:
                                param.FXTURE_12 = False
                            # Color selection
                            elif pitch == param.START_NOTE+12:
                                param.COLOR_1_C = False
                            elif pitch == param.START_NOTE+13:
                                param.COLOR_2_Cs = False
                            elif pitch == param.START_NOTE+14:
                                param.COLOR_3_D = False
                            elif pitch == param.START_NOTE+15:
                                param.COLOR_4_Ds = False
                            elif pitch == param.START_NOTE+16:
                                param.COLOR_5_E = False
                            elif pitch == param.START_NOTE+17:
                                param.COLOR_6_F = False
                            elif pitch == param.START_NOTE+18:
                                param.COLOR_7_Fs = False
                            elif pitch == param.START_NOTE+19:
                                param.COLOR_8_G = False
                            elif pitch == param.START_NOTE+20:
                                param.COLOR_9_Gs = False
                            elif pitch == param.START_NOTE+21:
                                param.COLOR_10_A = False
                            elif pitch == param.START_NOTE+22:
                                param.COLOR_11_As = False
                            elif pitch == param.START_NOTE+23:
                                param.COLOR_12_B = False
            elif channel == 10:
                # OXYGEN25 Pads
                if status & 0xF0 == param.NOTE_ON:
                    # Toggle booleans on NOTE_ON
                    print('{0}: 0x{1} OXYGEN25 PAD NOTE_ON/OFF ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                            binascii.hexlify(data).decode(),
                                            channel, pitch, velocity))
                    if pitch == 36:
                        param.PAD_1 = not param.PAD_1
                        print('PAD 1 {}'.format(param.PAD_1))
                    elif pitch == 38:
                        param.PAD_2 = not param.PAD_2
                        print('PAD 2 {}'.format(param.PAD_2))
                    elif pitch == 42:
                        param.PAD_3 = not param.PAD_3
                        print('PAD 3 {}'.format(param.PAD_3))
                    elif pitch == 46:
                        param.PAD_4 = not param.PAD_4
                        print('PAD 4 {}'.format(param.PAD_4))
                    elif pitch == 50:
                        # PAD 5 turns different inputs on and off
                        if param.INPUT_THEREMIN:
                            param.INPUT_THEREMIN = False
                            param.INPUT_ARDOUR = True
                            param.INPUT_OXYGEN = False
                        elif param.INPUT_ARDOUR:
                            param.INPUT_THEREMIN = False
                            param.INPUT_ARDOUR = False
                            param.INPUT_OXYGEN = True
                        elif param.INPUT_OXYGEN:
                            param.INPUT_THEREMIN = True
                            param.INPUT_ARDOUR = False
                            param.INPUT_OXYGEN = False
                        print('INPUT: Theremin {0} Ardour {1} Oxygen {2}'.format(param.INPUT_THEREMIN, param.INPUT_ARDOUR, param.INPUT_OXYGEN))
                    elif pitch == 45:
                        if param.INPUT_THEREMIN:
                            # In Theremin mode PAD 6 switches between equal lights and offset
                            param.EQUAL_LIGHTS = not param.EQUAL_LIGHTS
                            print('MODE: Equal lights {}'.format(param.EQUAL_LIGHTS))
                        elif param.INPUT_OXYGEN:
                            # In Oxygen mode PAD 6 switches between key toggle and key on/off
                            param.KEY_TOGGLE= not param.KEY_TOGGLE
                            print('MODE: Key toggle {}'.format(param.KEY_TOGGLE))
                    elif pitch == 51:
                        # All fixtures off (PAD 7)
                        param.ALL_OFF = not param.ALL_OFF
                        print('PANIC: All Off {}'.format(param.ALL_OFF))
                    elif pitch == 49:
                        # All fixtures white (PAD 8)
                        param.ALL_WHITE = not param.ALL_WHITE
                        print('PANIC: All white {}'.format(param.ALL_WHITE))
                elif status & 0xF0 == param.NOTE_OFF:
                    # Ignore NOTE_OFF because we toggle boolean
                    pass
                else:
                    print('{0}: 0x{1} OXYGEN25 PAD UNKNOWN ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                            binascii.hexlify(data).decode(),
                                            channel, pitch, velocity))
                printStatus()
            elif channel == 1:
                # Theremin
                if param.INPUT_THEREMIN:
                    if status & 0xF0 == param.CONTROL_CHANGE:
                        print('{0}: 0x{1} THEREMIN CONTROL_CHANGE ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
                        if pitch == 2:
                            param.THERMIN_VELOCITY = velocity
                        elif pitch == 20:
                            param.THERMIN_PITCH = velocity
                    else:
                        print('{0}: 0x{1} THEREMIN UNKNOWN ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
            else:
                #pass  # ignore
                print('UNKNOWN-1 {0}: 0x{1} len:{2}'.format(client.last_frame_time + offset,
                                          binascii.hexlify(data).decode(),
                                          len(data)))
        else:
            #pass  # ignore
            print('UNKNOWN-2 {0}: 0x{1} len:{2}'.format(client.last_frame_time + offset,
                                      binascii.hexlify(data).decode(),
                                      len(data)))
        sendDmxData()
        #status, pitch, velocity = struct.unpack('3B', data)
        #print('{0}: 0x{1} st={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
        #                          binascii.hexlify(data).decode(),
        #                          status, pitch, velocity))
        #print('{0}: 0x{1} len:{2}'.format(client.last_frame_time + offset,
        #                          binascii.hexlify(data).decode(),
        #                          len(data)))

def sendDmxData():
    if param.ALL_OFF:
        allFixturesOff()
    elif param.ALL_WHITE:
        allFixturesWhite()
    elif param.INPUT_THEREMIN:
        mappedColorValue = mapToneToColor(param.THERMIN_PITCH)
        if param.EQUAL_LIGHTS:
            print('Equal (Color wheel)')
            sendEqualColor(mappedColorValue)
        else:
            print('Offset')
            sendOffsetColor(mappedColorValue)
    elif param.INPUT_ARDOUR:
        pass
    elif param.INPUT_OXYGEN:
        color = 0
        color = param.DEFAULT_COLOR
        if param.KEY_TOGGLE:
            color = param.FIXTURE_COLORS['C'] if param.COLOR_1_C else color
            color = param.FIXTURE_COLORS['Cs'] if param.COLOR_2_Cs else color
            color = param.FIXTURE_COLORS['D'] if param.COLOR_3_D else color
            color = param.FIXTURE_COLORS['Ds'] if param.COLOR_4_Ds else color
            color = param.FIXTURE_COLORS['E'] if param.COLOR_5_E else color
            color = param.FIXTURE_COLORS['F'] if param.COLOR_6_F else color
            color = param.FIXTURE_COLORS['Fs'] if param.COLOR_7_Fs else color
            color = param.FIXTURE_COLORS['G'] if param.COLOR_8_G else color
            color = param.FIXTURE_COLORS['Gs'] if param.COLOR_9_Gs else color
            color = param.FIXTURE_COLORS['A'] if param.COLOR_10_A else color
            color = param.FIXTURE_COLORS['As'] if param.COLOR_11_As else color
            color = param.FIXTURE_COLORS['B'] if param.COLOR_12_B else color
        else:
            color += param.FIXTURE_COLORS['C'] if param.COLOR_1_C else 0
            color += param.FIXTURE_COLORS['Cs'] if param.COLOR_2_Cs else 0
            color += param.FIXTURE_COLORS['D'] if param.COLOR_3_D else 0
            color += param.FIXTURE_COLORS['Ds'] if param.COLOR_4_Ds else 0
            color += param.FIXTURE_COLORS['E'] if param.COLOR_5_E else 0
            color += param.FIXTURE_COLORS['F'] if param.COLOR_6_F else 0
            color += param.FIXTURE_COLORS['Fs'] if param.COLOR_7_Fs else 0
            color += param.FIXTURE_COLORS['G'] if param.COLOR_8_G else 0
            color += param.FIXTURE_COLORS['Gs'] if param.COLOR_9_Gs else 0
            color += param.FIXTURE_COLORS['A'] if param.COLOR_10_A else 0
            color += param.FIXTURE_COLORS['As'] if param.COLOR_11_As else 0
            color += param.FIXTURE_COLORS['B'] if param.COLOR_12_B else 0
        while color > 360:
            color -= 360
        #print('SEND: color {}'.format(color))
        dmxcolor = hsvToRgb(color, param.HSV_SATURATION, param.HSV_VALUE)
        #print('SEND: dmxcolor {}'.format(dmxcolor))

        data = ()
        # (0, 255, 0) white off, dimmer 100%, effect off
        # (0, 0, 0) white off, dimmer 0%, effect off
        data += dmxcolor + (0, 255, 0) if param.FXTURE_1 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_2 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_3 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_4 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_5 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_6 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_7 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_8 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_9 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_10 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_11 else dmxcolor + (0, 0 ,0)
        data += dmxcolor + (0, 255, 0) if param.FXTURE_12 else dmxcolor + (0, 0 ,0)
        #print('SEND: Data {}'.format(data))
        sender[1].dmx_data = data

def allFixturesOff():
    data = ()
    # (0, 0, 0) R off, G off, B off
    # (0, 0, 0) white off, dimmer 0%, effect off
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    data += (0, 0 ,0) + (0, 0, 0)
    #print('SEND: Data {}'.format(data))
    sender[1].dmx_data = data

def allFixturesWhite():
    data = ()
    # (0, 0, 0) R off, G off, B off
    # (255, 255, 0) white on, dimmer 100%, effect off
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    data += (0, 0 ,0) + (255, 255, 0)
    #print('SEND: Data {}'.format(data))
    sender[1].dmx_data = data

def printStatus():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    if param.INPUT_ARDOUR:
        print('INPUT: Ardour')
    elif param.INPUT_OXYGEN:
        print('INPUT: Oxygen')
        if param.KEY_TOGGLE:
            print('MODE: Toggle')
        else:
            print('MODE: Continuous')
    elif param.INPUT_THEREMIN:
        print('INPUT: Theremin')
        if param.EQUAL_LIGHTS:
            print('MODE: Equal lights')
        else:
            print('MODE: Offset')
    if param.ALL_OFF:
        print('PANIC 1: All Off')
    else:
        print('PANIC 1: Normal')
    if param.ALL_WHITE:
        print('PANIC 2: All White')
    else:
        print('PANIC 2: Normal')

def sendEqualColor(hsvColor):
    defaultValue = (0, 255, 0) # white off, dimmer 100%, effect off
    rgb = hsvToRgb(hsvColor, param.HSV_SATURATION, param.HSV_VALUE)
    data = ()
    for i in range(1, param.FIXTURES + 1):
        data += rgb + defaultValue
    sender[1].dmx_data = data

def sendOffsetColor(hsvColor):
    defaultValue = (0, 255, 0) # white off, dimmer 100%, effect off
    rgb = hsvToRgb(hsvColor, param.HSV_SATURATION, param.HSV_VALUE)
    data = ()
    for i in range(1, param.FIXTURES + 1):
        data += rgb + defaultValue
        hsvColor += param.FIXTURE_OFFSET
        rgb = hsvToRgb(hsvColor, param.HSV_SATURATION, param.HSV_VALUE)
    sender[1].dmx_data = data

def mapToneToColor(note):
    colorvalue = map(note, param.THERMIN_RANGE_START, param.THERMIN_RANGE_END, param.HSV_RANGE_START, param.HSV_RANGE_END)
    colorvalue += param.HSV_OFFSET
    if colorvalue > param.HSV_RANGE_END:
        colorvalue -= param.HSV_RANGE_END
    return colorvalue

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def hsvToRgb(h, s, v):
    #print("Color[%s]" % (h))
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

def resetColors():
    param.COLOR_1_C = False
    param.COLOR_2_Cs = False
    param.COLOR_3_D = False
    param.COLOR_4_Ds = False
    param.COLOR_5_E = False
    param.COLOR_6_F = False
    param.COLOR_7_Fs = False
    param.COLOR_8_G = False
    param.COLOR_9_Gs = False
    param.COLOR_10_A = False
    param.COLOR_11_As = False
    param.COLOR_12_B = False

sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
# sender[1].multicast = True  # set multicast to True
# sender[1].destination = "192.168.56.1"  # or provide unicast information.
#sender[1].destination = "127.0.0.1"  # or provide unicast information.
#sender[1].destination = "192.168.178.39"  # or provide unicast information.
sender[1].destination = param.OLA_SERVER_IP  # or provide unicast information.
# Keep in mind that if multicast is on, unicast is not used
#sender[1].dmx_data = (1, 2, 3, 4)  # some test DMX data

with client:
    printStatus()
    input()

sender.stop()  # do not forget to stop the sender