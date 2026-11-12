NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_note(midi: int) -> str:
    octave = (midi // 12) - 1
    note = NOTES[midi % 12]
    return f"{note}{octave}"


MIDI_NOTES = [midi_to_note(midi) for midi in range(128)]


def pan_to_string(pan: int) -> str:
    if pan == 64:
        return "C"

    if pan < 64:
        amount = 64 - pan
        return f"L{amount}"
    else:
        amount = pan - 64
        return f"R{amount}"


PAN_STRINGS = [pan_to_string(pan) for pan in range(128)]
