from picogui_dialog import Dialog
from picogui_picogame import App

import control_bindings
import picogui as ui
import synth
import trigger_bindings
from note_screen import NoteScreen
from preset_manager import get_loaded_preset


class NoteMgmtScreen(ui.Screen):
    def __init__(self, note_screen: NoteScreen):
        self.note_screen = note_screen
        self.notes = self.note_screen.notes
        self.note_index = self.note_screen.sel
        self.note = self.notes[self.note_index]

        self.widgets: list[ui.Widget] = [
            ui.Button("Duplicate", lambda app: self.duplicate(app)),
            ui.Button("Delete", lambda app: self.delete(app)),
        ]
        super().__init__(f"Note {self.note_index + 1}", self.widgets)

    def duplicate(self, app: App):
        new_note = self.note.clone()
        self.notes.append(new_note)
        loaded_preset = get_loaded_preset()
        synth.add_note(new_note, loaded_preset)
        trigger_bindings.add(new_note, loaded_preset)
        control_bindings.add_all(new_note, loaded_preset)

        self.note_screen.build_rows()
        app.pop()

    def delete(self, app: App):
        def on_yes(_):
            self.notes.remove(self.note)
            synth.delete_note(self.note)
            trigger_bindings.remove(self.note)
            control_bindings.remove_all(self.note)

            self.note_screen.build_rows()
            app.pop()

        app.push(
            Dialog(
                "Delete Note",
                f"Delete Note {self.note_index + 1}?",
                on_yes,
                False,
            )
        )
