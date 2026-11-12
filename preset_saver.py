import json
import os

from consts import PRESET_DIR
from models import Control, Note, Preset, Property
from preset_manager import presets


def control_to_dict(control: Control) -> dict:
    return {
        "module": control.module,
        "module_min": control.module_min,
        "module_max": control.module_max,
        "property_min": control.property_min,
        "property_max": control.property_max,
        "curve": control.curve,
    }


def property_to_dict(property: Property) -> dict:
    data = {
        "value": property.value,
    }

    if property.control is not None:
        data["control"] = control_to_dict(property.control)
        data["use_control"] = property.use_control

    return data


def note_to_dict(note: Note) -> dict:
    properties = (
        note.pitch,
        note.fine_tune,
        note.amplitude,
        note.wavetable,
        note.position,
        note.panning,
        note.attack,
        note.decay,
        note.sustain,
        note.release,
    )

    data = {
        "trigger": {
            "module": note.trigger.module,
            "attack_threshold": note.trigger.attack_threshold,
            "release_threshold": note.trigger.release_threshold,
            "use_control": note.trigger.use_control,
        }
    }

    for property in properties:
        data[property.type] = property_to_dict(property)

    return data


def preset_to_dict(preset: Preset) -> dict:
    return {
        "name": preset.name,
        "notes": [note_to_dict(note) for note in preset.notes],
    }


def save_preset(preset: Preset) -> None:
    path = PRESET_DIR + "/" + preset.file_name + ".json"
    data = preset_to_dict(preset)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)


def save_all_presets():
    existing_file_names = {f for f in os.listdir(PRESET_DIR) if f.endswith(".json")}
    preset_file_names = {preset.file_name + ".json" for preset in presets}

    for file_name in existing_file_names - preset_file_names:
        os.remove(PRESET_DIR + "/" + file_name)

    for preset in presets:
        save_preset(preset)
