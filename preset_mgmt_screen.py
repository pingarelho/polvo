from picogui_dialog import Dialog
from picogui_picogame import App

import custom_row_kb as kb
import picogui as ui
import preset_manager
from preset_screen import PresetScreen


class PresetMgmtScreen(ui.Screen):
    def __init__(self, preset_screen: PresetScreen):
        self.preset_screen = preset_screen
        self.preset = preset_manager.presets[self.preset_screen.sel]

        self.widgets: list[ui.Widget] = [
            ui.Button("Rename", lambda app: self.rename(app)),
            ui.Button("Duplicate", lambda app: self.duplicate(app)),
            ui.Button("Delete", lambda app: self.delete(app)),
        ]
        super().__init__(self.preset.name, self.widgets)

    def rename(self, app: App):
        def on_name_submit(new_name: str):
            if preset_manager.rename(self.preset, new_name):
                self.title = new_name
                self.preset_screen.build_rows()

        keyboard = kb.RowKeyboard(
            "Rename Preset", self.preset.name, lambda v: on_name_submit(v)
        )
        app.push(keyboard)

    def duplicate(self, app: App):
        def on_name_submit(name: str):
            if preset_manager.duplicate(self.preset, name):
                self.preset_screen.build_rows()
                app.pop()

        keyboard = kb.RowKeyboard(
            "Duplicate Preset", self.preset.name, lambda v: on_name_submit(v)
        )
        app.push(keyboard)

    def delete(self, app: App):
        def on_yes(_):
            preset_manager.delete(self.preset)
            self.preset_screen.build_rows()
            app.pop()

        app.push(
            Dialog(
                "Delete Preset",
                f"Delete {self.preset.name}?",
                on_yes,
                False,
            )
        )
