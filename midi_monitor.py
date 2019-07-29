#!/usr/bin/env python3

"""JACK client that prints all received MIDI events."""

import jack
import binascii
import struct

# Global parameter class
class param:
    # MIDI definitions
    NOTE_ON = 0x90
    NOTE_OFF = 0x80
    CONTROL_CHANGE = 0xB0

    # Input selector
    INPUT_THEREMIN = True
    INPUT_ARDOUR = False
    INPUT_OXYGEN = False

    # OXYGEN25 PAD status
    PAD_1 = False
    PAD_2 = False
    PAD_3 = False
    PAD_4 = False
    PAD_5 = False
    PAD_6 = False
    PAD_7 = False
    PAD_8 = False

client = jack.Client('MIDI-Monitor')
port = client.midi_inports.register('input')


@client.set_process_callback
def process(frames):
    for offset, data in port.incoming_midi_events():
        if len(data) == 3:
            status, pitch, velocity = bytes(data)
            channel = (status & 0xF) + 1
            if status & 0xF0 == param.CONTROL_CHANGE and velocity == 0 and pitch in(64, 123):
                # Ardour track end -> ignore these
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
                    elif status & 0xF0 == param.NOTE_OFF:
                        print('{0}: 0x{1} OXYGEN25 NOTE_OFF ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
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
                        # PAD 1 turns different inputs on and off
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
                        param.PAD_6 = not param.PAD_6
                        print('PAD 6 {}'.format(param.PAD_6))
                    elif pitch == 51:
                        param.PAD_7 = not param.PAD_7
                        print('PAD 7 {}'.format(param.PAD_7))
                    elif pitch == 49:
                        param.PAD_8 = not param.PAD_8
                        print('PAD 8 {}'.format(param.PAD_8))
                elif status & 0xF0 == param.NOTE_OFF:
                    # Ignore NOTE_OFF because we toggle boolean
                    pass
                else:
                    print('{0}: 0x{1} OXYGEN25 PAD UNKNOWN ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                            binascii.hexlify(data).decode(),
                                            channel, pitch, velocity))
            elif channel == 1:
                # Theremin
                if param.INPUT_THEREMIN:
                    if status & 0xF0 == param.CONTROL_CHANGE:
                        print('{0}: 0x{1} THEREMIN CONTROL_CHANGE ch={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
                                                binascii.hexlify(data).decode(),
                                                channel, pitch, velocity))
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

        #status, pitch, velocity = struct.unpack('3B', data)
        #print('{0}: 0x{1} st={2} pitch={3} velocity={4}'.format(client.last_frame_time + offset,
        #                          binascii.hexlify(data).decode(),
        #                          status, pitch, velocity))
        #print('{0}: 0x{1} len:{2}'.format(client.last_frame_time + offset,
        #                          binascii.hexlify(data).decode(),
        #                          len(data)))

with client:
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()
