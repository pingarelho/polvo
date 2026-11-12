import control_bindings
import synth
import trigger_bindings
from models import Preset
from preset_reader import read_all_presets
from utils import slugify

presets: list[Preset] = read_all_presets()
_loaded_preset: Preset | None = None


def add(name: str) -> bool:
    if preset_exists(name):
        return False

    presets.append(Preset(name, slugify(name), []))
    return True


def rename(preset: Preset, new_name: str):
    if preset_exists(new_name):
        return False

    preset.name = new_name
    return True


def duplicate(preset: Preset, name: str):
    if preset_exists(name):
        return False

    presets.append(Preset(name, slugify(name), [note.clone() for note in preset.notes]))
    return True


def delete(preset: Preset):
    global _loaded_preset

    if is_loaded(preset):
        synth.unload_preset()
        trigger_bindings.unload_preset()
        control_bindings.unload_preset()
        _loaded_preset = None

    presets.remove(preset)


def load_preset(preset: Preset):
    global _loaded_preset

    synth.unload_preset()
    if is_loaded(preset):
        trigger_bindings.unload_preset()
        control_bindings.unload_preset()
        _loaded_preset = None
    else:
        _loaded_preset = preset
        synth.load_preset(preset)
        trigger_bindings.load_preset(preset)
        control_bindings.load_preset(preset)


def get_loaded_preset():
    return _loaded_preset


def is_loaded(preset: Preset):
    return preset == _loaded_preset


def preset_exists(name: str):
    return any(preset.name == name for preset in presets)
