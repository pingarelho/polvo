from picogui_picogame import App

import control_bindings
import note_builder
import picogui as ui
import synth
import trigger_bindings
import wavetable_manager
from control_screen import ControlScreen
from custom_widgets import CoolLabel, EllipsisLink, SteppedChoice
from models import Note, Property, PropertyType, Trigger
from preset_manager import get_loaded_preset
from property_notation import MIDI_NOTES, PAN_STRINGS
from trigger_screen import TriggerScreen
from utils import get_property_max, sanitize


class PropertyWidget:
    def __init__(self, property: Property, on_change):
        self.property = property
        self.on_change = on_change

    @property
    def widget(self) -> ui.Widget:
        property_type = self.property.type
        label = sanitize(property_type)

        if self.property.use_control:
            return EllipsisLink(
                label,
                lambda _: ControlScreen(self.property.control, property_type),
            )
        else:
            value = self.property.value
            if property_type == PropertyType.WAVETABLE:
                wavetable_names = wavetable_manager.get_names_list()
                return SteppedChoice(
                    label=label,
                    options=wavetable_names,
                    index=wavetable_names.index(value),
                    on_change=lambda v: self.on_change(self.property, v),
                )
            elif property_type == PropertyType.PITCH:
                return SteppedChoice(
                    label=label,
                    options=MIDI_NOTES,
                    index=value,
                    on_change=lambda v: self.on_change(self.property, v),
                )
            elif property_type == PropertyType.PANNING:
                return SteppedChoice(
                    label=label,
                    options=PAN_STRINGS,
                    index=value,
                    on_change=lambda v: self.on_change(self.property, v),
                )
            else:
                return ui.IntField(
                    label=label,
                    value=value,
                    hi=get_property_max(property_type),
                    on_change=lambda v: self.on_change(self.property, v),
                )


class TriggerWidget:
    def __init__(self, trigger: Trigger):
        self.trigger = trigger

    @property
    def widget(self) -> ui.Widget:
        if self.trigger.use_control:
            return EllipsisLink("Trigger", lambda _: TriggerScreen(self.trigger))
        else:
            return CoolLabel("Trigger", "disabled")


class PropertyScreen(ui.Screen):
    def __init__(self, note: Note, title: str):
        self.note = note
        self.wrapper_widgets: list[TriggerWidget | PropertyWidget] = [
            TriggerWidget(note.trigger),
            PropertyWidget(note.pitch, self.on_change),
            PropertyWidget(note.fine_tune, self.on_change),
            PropertyWidget(note.amplitude, self.on_change),
            PropertyWidget(note.wavetable, self.on_change),
            PropertyWidget(note.position, self.on_change),
            PropertyWidget(note.panning, self.on_change),
            PropertyWidget(note.attack, self.on_change),
            PropertyWidget(note.decay, self.on_change),
            PropertyWidget(note.sustain, self.on_change),
            PropertyWidget(note.release, self.on_change),
        ]
        super().__init__(title, [widget.widget for widget in self.wrapper_widgets])

    def on_change(self, property: Property, value: int | str):
        property_type = property.type
        synth_note = self.note.synth_note
        if property_type == PropertyType.PITCH:
            property.value = MIDI_NOTES.index(value)
            synth_note.frequency = note_builder.calc_frequency(
                note=self.note,
                new_pitch=MIDI_NOTES.index(value),
            )
        elif property_type == PropertyType.FINE_TUNE:
            property.value = value
            synth_note.frequency = note_builder.calc_frequency(
                note=self.note,
                new_fine_tune=value,
            )
        elif property_type == PropertyType.AMPLITUDE:
            property.value = value
            synth_note.amplitude = note_builder.calc_amplitude(property, value)
        elif property_type == PropertyType.WAVETABLE:
            property.value = value
            synth_note.waveform = note_builder.get_waveform(
                note=self.note,
                new_wavetable=value,
            )
        elif property_type == PropertyType.POSITION:
            property.value = value
            synth_note.waveform = note_builder.get_waveform(
                note=self.note,
                new_position=value,
            )
        elif property_type == PropertyType.PANNING:
            property.value = PAN_STRINGS.index(value)
            synth_note.panning = note_builder.calc_panning(
                property, PAN_STRINGS.index(value)
            )
        elif property_type == PropertyType.ATTACK:
            property.value = value
            synth_note.envelope = note_builder.build_envelope(
                note=self.note,
                new_attack=value,
            )
        elif property_type == PropertyType.DECAY:
            property.value = value
            synth_note.envelope = note_builder.build_envelope(
                note=self.note,
                new_decay=value,
            )
        elif property_type == PropertyType.SUSTAIN:
            property.value = value
            synth_note.envelope = note_builder.build_envelope(
                note=self.note,
                new_sustain=value,
            )
        elif property_type == PropertyType.RELEASE:
            property.value = value
            synth_note.envelope = note_builder.build_envelope(
                note=self.note,
                new_release=value,
            )

    def toggle_sel_control(self, app: App):
        sel_wrapper = self.wrapper_widgets[self.sel]

        if isinstance(sel_wrapper, TriggerWidget):
            trigger = sel_wrapper.trigger
            trigger.toggle_control()
            loaded_preset = get_loaded_preset()
            if trigger.use_control:
                synth.delete_note(self.note)
                trigger_bindings.add(self.note, loaded_preset)
            else:
                synth.add_note(self.note, loaded_preset)
                trigger_bindings.remove(self.note)

        elif isinstance(sel_wrapper, PropertyWidget):
            property = sel_wrapper.property
            if property.control is None:
                return

            property_type = property.type
            property.toggle_control()
            if property.use_control:
                control_bindings.add(self.note, property_type, get_loaded_preset())
            else:
                control_bindings.remove(self.note, property_type)
                self.on_change(property, sel_wrapper.widget.value)

        self.widgets[self.sel] = sel_wrapper.widget
        app.invalidate()
