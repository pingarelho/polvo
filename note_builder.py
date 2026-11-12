import synthio

import wavetable_manager

try:
    from models import Note, Property
except ImportError:
    pass


def build(note: Note):
    return synthio.Note(
        frequency=calc_frequency(note=note, build=True),
        panning=calc_panning(panning=note.panning, build=True),
        waveform=get_waveform(note=note, build=True),
        envelope=build_envelope(note=note, build=True),
        amplitude=calc_amplitude(amplitude=note.amplitude, build=True),
    )


def calc_frequency(
    note: Note,
    new_pitch: int | None = None,
    new_fine_tune: float | None = None,
    build=False,
):
    if new_pitch is None:
        new_pitch = note.pitch.value

    if new_fine_tune is None:
        new_fine_tune = note.fine_tune.value

    return synthio.midi_to_hz(
        note.pitch.value + calc_fine_tune(note.fine_tune, new_fine_tune, build)
    )


def calc_fine_tune(fine_tune: Property, new_fine_tune: float, build=False):
    return midi_to_ft_range(prop_min_or_fixed(fine_tune, new_fine_tune, build))


def calc_amplitude(
    amplitude: Property, new_amplitude: float | None = None, build=False
):
    if new_amplitude is None:
        new_amplitude = amplitude.value

    return prop_min_or_fixed(amplitude, new_amplitude, build) / 127


def get_waveform(
    note: Note,
    new_wavetable: str | None = None,
    new_position: float | None = None,
    build=False,
):
    if new_wavetable is None:
        new_wavetable = note.wavetable.value

    if new_position is None:
        new_position = note.position.value

    return wavetable_manager.get_waveform(
        new_wavetable, calc_position(note.position, new_position, build)
    )


def calc_position(position: Property, new_position: float, build=False):
    return prop_min_or_fixed(position, new_position, build) * 63 / 1023


def calc_panning(panning: Property, new_panning: float | None = None, build=False):
    if new_panning is None:
        new_panning = panning.value

    return midi_to_pan_range(prop_min_or_fixed(panning, new_panning, build))


def calc_attack(attack: Property, new_attack: float, build=False):
    return prop_min_or_fixed(attack, new_attack, build) / 10


def calc_decay(decay: Property, new_decay: float, build=False):
    return prop_min_or_fixed(decay, new_decay, build) / 10


def calc_sustain(sustain: Property, new_sustain: float, build=False):
    return prop_min_or_fixed(sustain, new_sustain, build) / 127


def calc_release(release: Property, new_release: float, build=False):
    return prop_min_or_fixed(release, new_release, build) / 10


def build_envelope(
    note: Note,
    new_attack: float | None = None,
    new_decay: float | None = None,
    new_sustain: float | None = None,
    new_release: float | None = None,
    build=False,
):
    if new_attack is None:
        new_attack = note.attack.value

    if new_decay is None:
        new_decay = note.decay.value

    if new_sustain is None:
        new_sustain = note.sustain.value

    if new_release is None:
        new_release = note.release.value

    return synthio.Envelope(
        attack_time=calc_attack(note.attack, new_attack, build),
        decay_time=calc_decay(note.decay, new_decay, build),
        sustain_level=calc_sustain(note.sustain, new_sustain, build),
        release_time=calc_release(note.release, new_release, build),
    )


def midi_to_pan_range(value: float):  # 0 = -1; 64 = 0; 127 = 1
    if value <= 64:
        return value / 64 - 1
    else:
        return (value - 64) / 63


def midi_to_ft_range(value: float):  # 0 = -16; 64 = 0; 127 = 15.75
    return value * 0.25 - 16


def prop_min_or_fixed(property: Property, value: float, build=False):
    return property.control.property_min if (property.use_control and build) else value
