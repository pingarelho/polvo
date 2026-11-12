import json
import os

from consts import MAX_PRESET_NAME_LENGTH, PRESET_DIR
from models import (
    Control,
    Note,
    Preset,
    Property,
    PropertyType,
    Trigger,
)
from wavetable_manager import WAVETABLES

DEFAULT_NOTE_PATH = "default_note.json"


def read_note(note_data) -> Note:
    trigger_data = note_data["trigger"]

    trigger = Trigger(
        trigger_data["module"],
        trigger_data["attack_threshold"],
        trigger_data["release_threshold"],
        trigger_data["use_control"],
    )

    properties: dict[PropertyType, Property] = {}

    for property_type in PropertyType.ALL:
        property_data = note_data[property_type]

        skip_control = property_type in (PropertyType.PITCH, PropertyType.WAVETABLE)
        control = None

        if not skip_control:
            control_data = property_data["control"]
            control = Control(
                control_data["module"],
                control_data["module_min"],
                control_data["module_max"],
                control_data["property_min"],
                control_data["property_max"],
                control_data["curve"],
            )

        value = property_data["value"]
        if property_type == PropertyType.WAVETABLE and value == "":
            value = WAVETABLES[0][0]

        property = Property(
            property_type,
            value,
            control,
            None if skip_control else property_data["use_control"],
        )
        properties[property_type] = property

    pitch = properties[PropertyType.PITCH]
    fine_tune = properties[PropertyType.FINE_TUNE]
    amplitude = properties[PropertyType.AMPLITUDE]
    wavetable = properties[PropertyType.WAVETABLE]
    position = properties[PropertyType.POSITION]
    panning = properties[PropertyType.PANNING]
    attack = properties[PropertyType.ATTACK]
    decay = properties[PropertyType.DECAY]
    sustain = properties[PropertyType.SUSTAIN]
    release = properties[PropertyType.RELEASE]

    return Note(
        trigger,
        pitch,
        fine_tune,
        amplitude,
        wavetable,
        position,
        panning,
        attack,
        decay,
        sustain,
        release,
    )


def read_default_note() -> Note:
    with open(DEFAULT_NOTE_PATH, "r", encoding="utf-8") as file:
        note_data = json.load(file)
    return read_note(note_data)


DEFAULT_NOTE = read_default_note()


def read_preset(file_name) -> Preset | None:
    path = PRESET_DIR + "/" + file_name
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    name = data["name"]
    if len(name) > MAX_PRESET_NAME_LENGTH:
        return None

    notes: list[Note] = []

    for note_data in data["notes"]:
        notes.append(read_note(note_data))

    file_name = file_name[:-5]
    return Preset(data["name"], file_name, notes)


def read_all_presets() -> list[Preset]:
    presets = []

    file_names = [f for f in os.listdir(PRESET_DIR) if f.endswith(".json")]
    file_names.sort()

    for file_name in file_names:
        preset = read_preset(file_name)
        if preset:
            presets.append(preset)

    return presets
