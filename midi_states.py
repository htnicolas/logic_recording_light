# Business logic for translating midi messages to legible actions
# This should be modified to work with your specific MIDI controller

from enum import Enum

class MidiActions(Enum):
    """
    Enum to represent MIDI actions
    """
    RECORD_START = "record_start"
    RECORD_STOP = "record_stop"
    PLAY = "play"
    STOP = "stop"
    SNARE_ON = "snare_on"
    SNARE_OFF = "snare_off"
    UNKNOWN = "unknown"

def get_midi_action(midi_data: list) -> MidiActions | None:
    """
    Translate MIDI messages to actions enum.
    Args:
        midi_data: List, MIDI message from OSC consisting of status,
                    data1, data2
    Returns:
        Enum: MIDI message type
    """
    status, data1, data2 = midi_data

    # Record button on Logic Pro X
    if data1 == 25:
        if data2 == 127:
            return MidiActions.RECORD_START
        elif data2 == 0:
            return MidiActions.RECORD_STOP

    # Play and stop buttons on Logic Pro X

    # Roland TD-07 drum kit snare
    elif data1 == 38:
        if status == 153:
            return MidiActions.SNARE_ON
        elif status == 137:
            return MidiActions.SNARE_OFF
    else:
        return None
