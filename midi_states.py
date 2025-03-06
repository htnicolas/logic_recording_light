# Business logic for translating midi messages to legible actions
# This should be modified to work with your specific MIDI controller

from enum import Enum

from loguru import logger


CONTROL_CHANGE_STATUS_ALL_CHANNELS = [x for x in range(176, 192)]

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
    # To be used when user closes the project in LPX and All Notes Off is sent to external MIDI controller
    # This assumes that you setup reset messages in LPX to send Control 123 (All Notes Off) and that you have
    # a MIDI controller that can receive this message
    ALL_NOTES_OFF = "all_notes_off"
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

    # You can set LPX to send reset MIDI messages to your controller upon closing the project
    # Preferences -> MIDI -> Reset Messages -> External MIDI -> Select Control 123 (All Notes Off)
    elif status in CONTROL_CHANGE_STATUS_ALL_CHANNELS:
        if data1 == 123 and data2 == 0:
            return MidiActions.ALL_NOTES_OFF

    # Roland TD-07 drum kit snare
    elif data1 == 38:
        if status == 153:
            return MidiActions.SNARE_ON
        elif status == 137:
            return MidiActions.SNARE_OFF
    else:
        logger.info(f"Unknown MIDI message: {midi_data}")
        return None
