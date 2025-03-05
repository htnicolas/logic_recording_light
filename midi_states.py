# Business logic for translating midi messages to legible actions
# This should be modified to work with your specific MIDI controller

from enum import Enum

from loguru import logger


class MidiActions(Enum):
    """
    Enum to represent MIDI actions
    """
    RECORD_START = "record_start"
    RECORD_STOP = "record_stop"
    PLAY = "play"
    STOP = "stop"
    TRACK_LEFT = "track_left"
    TRACK_RIGHT = "track_right"
    SNARE_ON = "snare_on"
    SNARE_OFF = "snare_off"
    UNKNOWN = "unknown"

def get_midi_action(midi_data: list) -> MidiActions | None:
    """
    Translate MIDI messages to actions enum.
    Midi messages may come from various sources, such as LPX virtual MIDI port or a keyboard.
    Args:
        midi_data: List, MIDI message from OSC consisting of status,
                    data1, data2
    Returns:
        Enum: MIDI message type
    """
    status, data1, data2 = midi_data

    # Record button on Nektar LX61: 16 107 127 for press, 16 107 0 for release
    # When rec light is set up, LPX Virtual MIDI sends 2 25 127; stopping recording sends 2 25 0
    if data1 == 25:
        if data2 == 127:
            return MidiActions.RECORD_START
        elif data2 == 0:
            return MidiActions.RECORD_STOP

    # Play button on Nektar LX61: 16 106 127 for press, 16 106 0 for release
    elif data1 == 106:
        if data2 == 127:
            return MidiActions.PLAY

    # Stop button on Nektar LX61: 16 105 127 for press, 16 105 0 for release
    elif data1 == 105:
        if data2 == 127:
            return MidiActions.STOP

    # Track Left button on Nektar LX61: 16 109 127 for press, 16 109 0 for release
    elif data1 == 109:
        if data2 == 127:
            return MidiActions.TRACK_LEFT

    # Track Left button on Nektar LX61: 16 110 127 for press, 16 110 0 for release
    elif data1 == 110:
        if data2 == 127:
            return MidiActions.TRACK_RIGHT

    # Roland TD-07 drum kit snare
    elif data1 == 38:
        if status == 153:
            return MidiActions.SNARE_ON
        elif status == 137:
            return MidiActions.SNARE_OFF
    else:
        logger.info(f"Unknown MIDI message: {midi_data}")
        return None
