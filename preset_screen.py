from picogui_dialog import Dialog
from picogui_picogame import App
from picogui_records import RecordList

import custom_row_kb as kb
import preset_manager
from note_screen import NoteScreen
from preset_saver import save_all_presets


class PresetScreen(RecordList):
    ADD_PRESET = ("+ Add preset", "")

    def __init__(self):
        self.rows: list[tuple[str, str]] = []
        self.build_rows()

        super().__init__("Presets", self.rows, on_select=self.new_or_edit_preset)

    def build_rows(self):
        self.rows.clear()
        self.rows.extend(
            (
                f"[{preset.name}]" if preset_manager.is_loaded(preset) else preset.name,
                "...",
            )
            for preset in preset_manager.presets
        )
        self.rows.append(self.ADD_PRESET)

    def add_preset(self, name: str):
        if preset_manager.add(name):
            self.build_rows()

    def new_or_edit_preset(self, app: App, i: int):
        if self.is_add_selected():
            keyboard = kb.RowKeyboard("New Preset", "", self.add_preset)
            app.push(keyboard)
            return

        note_screen = NoteScreen(preset_manager.presets[i])
        app.push(note_screen)

    def load_sel_preset(self, app: App):
        if not self.is_add_selected():
            preset_manager.load_preset(preset_manager.presets[self.sel])
            self.build_rows()
            app.invalidate()

    def is_add_selected(self):
        return self.rows[self.sel] == self.ADD_PRESET

    def save_presets(self, app: App):
        app.push(
            Dialog(
                "Save Presets",
                "Save presets?",
                lambda _: save_all_presets(),
                False,
            )
        )

    # "b: save" instead of "b: back"
    def draw(self, p, W, H):
        th = p.th
        p.fill(0, 0, W, H, th.bg)
        self._titlebar(p, W, self.title)
        n = len(self.items)
        if self.sel >= n:
            self.sel = n - 1 if n else 0
        y0 = self._top_h(th) + 2
        rows = self._visible_rows(H, th)
        cw = self._content_w(th, W, n, rows)  # room for a thumb, if the theme wants one
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + rows:
            self.top = self.sel - rows + 1
        if n == 0:
            p.ctext(W // 2, H // 2 - 8, self.empty, th.dim)
        y = y0
        for i in range(self.top, min(n, self.top + rows)):
            if p.visible(y, th.row_h):  # skip rows outside the current band
                it = self.items[i]
                if isinstance(it, tuple):
                    left, right = it
                else:
                    left, right = it, ""
                focused = i == self.sel
                if focused:
                    p.fill(0, y, cw, th.row_h, th.sel_bg)
                fg = th.sel_fg if focused else th.fg
                p.text(th.pad, y + th.text_dy, left, fg)
                if right:
                    p.rtext(
                        cw - th.pad,
                        y + th.text_dy,
                        right,
                        th.sel_fg if focused else th.dim,
                    )
            y += th.row_h
        self._scrollmark(p, W, H, y0, self.top, rows, n)
        self._softbar(p, W, H, self._hint if n else "", "B: save")
