import math

import adafruit_mcp3xxx.mcp3008 as mcp
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn

import control_bindings
import note_builder
import trigger_bindings
from consts import NUMBER_OF_MODULES
from models import Curve, Property, PropertyType
from synth import synth

spi = busio.SPI(clock=board.GP18, MISO=board.GP16, MOSI=board.GP19)
cs = digitalio.DigitalInOut(board.GP17)
mcp3008 = mcp.MCP3008(spi, cs)

module_readings: dict[int, float] = {}

SMOOTHING_FACTOR = 0.1


def read_adc(channel: int):
    return AnalogIn(mcp3008, channel).value >> 6


def smooth_out_reading(channel: int, value: int):
    if channel not in module_readings:
        module_readings[channel] = value
    else:
        previous = module_readings[channel]
        module_readings[channel] = previous + SMOOTHING_FACTOR * (value - previous)

    smoothed = module_readings[channel]

    return smoothed


def map_range(value, old_min, old_max, new_min, new_max, curve: Curve):
    # Normalize old range to 0..1
    x = (value - old_min) / (old_max - old_min)

    # Apply curve
    if curve == Curve.LINEAR:
        y = x
    elif curve == Curve.EXP:
        y = math.pow(2, x) - 1
    elif curve == Curve.LOG:
        y = math.log(1 + x) / math.log(2)

    # Map 0..1 to new range
    return new_min + y * (new_max - new_min)


def handle_modules():
    active_triggers = trigger_bindings.get_active_bindings()
    active_controls = control_bindings.get_active_bindings()

    active_modules = [
        module
        for module in range(NUMBER_OF_MODULES)
        if module in active_triggers or module in active_controls
    ]

    # check if a module is no longer active and remove it from module_readings, so
    # that the current reading is used by default when it becomes active again later
    for module in module_readings:
        if module not in active_modules:
            module_readings.pop(module)

    for module in active_modules:
        reading = read_adc(module)
        reading = smooth_out_reading(module, reading)

        if module in active_triggers:
            for note in active_triggers[module]:
                synth_note = note.synth_note
                trigger = note.trigger

                if synth_note in synth.pressed:
                    if reading >= trigger.release_threshold:
                        synth.release(synth_note)
                else:
                    if reading <= trigger.attack_threshold:
                        synth.press(synth_note)

        if module in active_controls:
            for binding in active_controls[module]:
                note = binding.note
                property_type = binding.property_type
                property: Property = getattr(note, property_type)
                control = property.control

                # clamping input
                if reading < control.module_min or reading > control.module_max:
                    continue

                mapped_reading = map_range(
                    reading,
                    control.module_min,
                    control.module_max,
                    control.property_min,
                    control.property_max,
                    control.curve,
                )

                synth_note = note.synth_note
                if property_type == PropertyType.FINE_TUNE:
                    synth_note.frequency = note_builder.calc_frequency(
                        note=note, new_fine_tune=mapped_reading
                    )
                elif property_type == PropertyType.AMPLITUDE:
                    synth_note.amplitude = note_builder.calc_amplitude(
                        amplitude=note.amplitude, new_amplitude=mapped_reading
                    )
                elif property_type == PropertyType.POSITION:
                    synth_note.waveform = note_builder.get_waveform(
                        note=note, new_position=mapped_reading
                    )
                elif property_type == PropertyType.PANNING:
                    synth_note.panning = note_builder.calc_panning(
                        panning=note.panning, new_panning=mapped_reading
                    )
                elif property_type == PropertyType.ATTACK:
                    synth_note.envelope = note_builder.build_envelope(
                        note=note, new_attack=mapped_reading
                    )
                elif property_type == PropertyType.DECAY:
                    synth_note.envelope = note_builder.build_envelope(
                        note=note, new_decay=mapped_reading
                    )
                elif property_type == PropertyType.SUSTAIN:
                    synth_note.envelope = note_builder.build_envelope(
                        note=note, new_sustain=mapped_reading
                    )
                elif property_type == PropertyType.RELEASE:
                    synth_note.envelope = note_builder.build_envelope(
                        note=note, new_release=mapped_reading
                    )
