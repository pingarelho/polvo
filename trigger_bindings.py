from consts import NUMBER_OF_MODULES
from models import Note, Preset, Trigger

_bindings: dict[int, set[Note]] = {i: set() for i in range(NUMBER_OF_MODULES)}


def unload_preset():
    for notes in _bindings.values():
        notes.clear()


def load_preset(preset: Preset):
    unload_preset()
    for note in preset.notes:
        trigger = note.trigger
        if trigger.use_control:
            get_notes(trigger.module).add(note)


def move(new_module: int, trigger: Trigger):
    note = note_from_trigger(trigger)
    if note is None:
        return

    get_notes(trigger.module).remove(note)
    get_notes(new_module).add(note)


def add(note: Note, loaded_preset: Preset):
    trigger = note.trigger
    if trigger.use_control and loaded_preset and note in loaded_preset.notes:
        get_notes(trigger.module).add(note)


def remove(note: Note):
    get_notes(note.trigger.module).discard(note)


def note_from_trigger(trigger: Trigger):
    for note in get_notes(trigger.module):
        if note.trigger == trigger:
            return note

    return None


def get_notes(module: int):
    return _bindings[module]


def get_active_bindings():
    return {key: value for key, value in _bindings.items() if value}
