from consts import NUMBER_OF_MODULES
from models import Control, Note, Preset, Property, PropertyType


class ControlBinding:
    def __init__(self, note: Note, property_type: PropertyType):
        self.note = note
        self.property_type = property_type

    def __eq__(self, other):
        return (
            isinstance(other, ControlBinding)
            and self.note == other.note
            and self.property_type == other.property_type
        )

    def __hash__(self):
        return hash((self.note, self.property_type))


_bindings: dict[int, set[ControlBinding]] = {i: set() for i in range(NUMBER_OF_MODULES)}


def unload_preset():
    for bindings in _bindings.values():
        bindings.clear()


def load_preset(preset: Preset):
    unload_preset()
    for note in preset.notes:
        for property_type in PropertyType.ALL:
            property: Property = getattr(note, property_type)
            if property.use_control:
                get_bindings(property.control.module).add(
                    ControlBinding(note, property_type)
                )


def move(new_module: int, control: Control, property_type: PropertyType):
    binding = binding_from_control(control, property_type)
    if binding is None:
        return

    get_bindings(control.module).remove(binding)
    get_bindings(new_module).add(binding)


def add(note: Note, property_type: PropertyType, loaded_preset: Preset):
    property: Property = getattr(note, property_type)
    if property.use_control and loaded_preset and note in loaded_preset.notes:
        get_bindings(property.control.module).add(ControlBinding(note, property_type))


def add_all(note: Note, loaded_preset: Preset):
    for property_type in PropertyType.ALL:
        if property_type in (PropertyType.PITCH, PropertyType.WAVETABLE):
            continue

        add(note, property_type, loaded_preset)


def remove(note: Note, property_type: PropertyType):
    property: Property = getattr(note, property_type)
    binding = ControlBinding(note, property_type)
    get_bindings(property.control.module).discard(binding)


def remove_all(note: Note):
    for property_type in PropertyType.ALL:
        if property_type in (PropertyType.PITCH, PropertyType.WAVETABLE):
            continue

        remove(note, property_type)


def binding_from_control(control: Control, property_type: PropertyType):
    for binding in get_bindings(control.module):
        if binding.property_type != property_type:
            continue

        property: Property = getattr(binding.note, binding.property_type)

        if property.control != control:
            continue

        return binding

    return None


def get_bindings(module: int):
    return _bindings[module]


def get_active_bindings():
    return {key: value for key, value in _bindings.items() if value}
