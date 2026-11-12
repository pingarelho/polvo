from picogui_picogame import App
from picogui_records import RecordList

import control_bindings
import synth
import trigger_bindings
from models import Preset
from preset_manager import get_loaded_preset
from preset_reader import DEFAULT_NOTE
from property_screen import PropertyScreen


class NoteScreen(RecordList):
    ADD_NOTE = ("+ Add note", "")

    def __init__(self, preset: Preset):
        self.preset = preset
        self.notes = self.preset.notes
        self.rows: list[tuple[str, str]] = []
        self.build_rows()

        super().__init__(self.preset.name, self.rows, on_select=self.new_or_edit_note)

    def build_rows(self):
        self.rows.clear()
        self.rows.extend((f"Note {i + 1}", "...") for i in range(len(self.notes)))
        self.rows.append(self.ADD_NOTE)

    def new_or_edit_note(self, app: App, i: int):
        if self.is_add_selected():
            note = DEFAULT_NOTE.clone()
            self.notes.append(note)
            loaded_preset = get_loaded_preset()
            synth.add_note(note, loaded_preset)
            trigger_bindings.add(note, loaded_preset)
            control_bindings.add_all(note, loaded_preset)
            self.build_rows()
            return

        property_screen = PropertyScreen(self.notes[i], f"Note {i + 1}")
        app.push(property_screen)

    def is_add_selected(self):
        return self.rows[self.sel] == self.ADD_NOTE
