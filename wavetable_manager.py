import os

import adafruit_wave
import ulab.numpy as np

WAVETABLE_DIR = "wavetables"

WAVE_LEN = 256
WAVES_PER_TABLE = 64


def read_wavetables() -> list[tuple[str, adafruit_wave.Wave_read]]:
    wavetables = []

    for filename in sorted(os.listdir(WAVETABLE_DIR)):
        if not filename.lower().endswith(".wav"):
            continue

        path = WAVETABLE_DIR + "/" + filename
        name = filename[:-4]

        wave_read = adafruit_wave.open(path)

        wavetables.append((name, wave_read))

    return wavetables


WAVETABLES = read_wavetables()


def get_names_list():
    return [name for name, _ in WAVETABLES]


def get_read_from_name(wavetable_name: str):
    for name, wave_read in WAVETABLES:
        if wavetable_name == name:
            return wave_read
    return None


def get_waveform(wavetable_name: str, position: float):
    position = min(max(position, 0), WAVES_PER_TABLE - 1)

    wave_read = get_read_from_name(wavetable_name)
    samp_pos = int(position) * WAVE_LEN

    wave_read.setpos(samp_pos)
    wave_a = np.frombuffer(wave_read.readframes(WAVE_LEN), dtype=np.int16)

    # multiplying wave_a by an empty wave_b returns an empty waveform altogether
    if position == WAVES_PER_TABLE - 1:
        return wave_a

    wave_read.setpos(samp_pos + WAVE_LEN)
    wave_b = np.frombuffer(wave_read.readframes(WAVE_LEN), dtype=np.int16)

    pos_frac = position - int(position)

    waveform = np.zeros(WAVE_LEN, dtype=np.int16)
    waveform[:] = (1 - pos_frac) * wave_a + pos_frac * wave_b
    return waveform
