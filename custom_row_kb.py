from picogui_picogame import App

from consts import MAX_PRESET_NAME_LENGTH
from picogui import View, _font_cw

KB_KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789 -_@/#")


class RowKeyboard(View):
    ACTIONS = ("done", "back")

    def __init__(self, title: str, buf: str, on_name_submit):
        self.title = title
        self.buf = buf
        self.on_name_submit = on_name_submit

        # Cursor for the keyboard row
        self.cursor = 0

        # Cursor for the action row: 0 = done, 1 = back
        self.action_cursor = 0

        # 0 = keyboard, 1 = actions
        self.focus = 0

        self._shift = False

    # -- helpers --------------------------------------------------------------------------------

    def _cased(self, ch):
        return ch.upper() if self._shift and "a" <= ch <= "z" else ch

    def toggle_shift(self, app: App):
        self._shift = not self._shift
        app.invalidate()

    # -- input ----------------------------------------------------------------------------------

    def key(self, app, k):
        # RIGHT switches from the keyboard row to the action row
        # Always enter the action row on "done"
        if k == "R" and self.focus == 0:
            self.focus = 1
            self.action_cursor = 0
            return True

        # LEFT switches from the action row back to the keyboard row
        if k == "L" and self.focus == 1:
            self.focus = 0
            return True

        # UP / DOWN move within the currently focused row
        if self.focus == 0:
            n = len(KB_KEYS)

            if k == "U":
                self.cursor = (self.cursor - 1) % n
                return True

            if k == "D":
                self.cursor = (self.cursor + 1) % n
                return True

        else:
            n = len(self.ACTIONS)

            if k == "U":
                self.action_cursor = (self.action_cursor - 1) % n
                return True

            if k == "D":
                self.action_cursor = (self.action_cursor + 1) % n
                return True

        # B deletes the last typed character
        if k == "B" and self.focus == 0:
            if not self.buf:
                return False  # backspace on empty buffer: no change

            self.buf = self.buf[:-1]
            return True

        if k == "A":
            # Action row is focused
            if self.focus == 1:
                if self.action_cursor == 0:  # done
                    if not self.buf:
                        return False

                    self.on_name_submit(self.buf)
                    app.pop()
                    return True

                if self.action_cursor == 1:  # back
                    return app.pop()

            # Keyboard row is focused.
            cur = KB_KEYS[self.cursor]

            # Typed character.
            if (
                len(self.buf) >= MAX_PRESET_NAME_LENGTH
            ):  # a typed character at max length: no change
                return False

            self.buf += self._cased(cur)
            return True

        return False

    # -- geometry / draw -------------------------------------------------------------------------

    def _geom(self, th, cw, W, H):
        """Layout:

        label
        value
        keyboard strip
        action row
        """
        fh = th.font.get_bounding_box()[1]
        row = fh + 3
        sbox = fh + 6

        top = max(0, (H - (row * 3 + sbox)) // 2)

        cy = top + row * 2 + sbox // 2

        slot = cw + 6
        half = max(1, (W - 4) // slot) // 2

        return W // 2, cy, slot, sbox, half, top, fh, row

    def _draw_actions(self, p, cx, y, sbox, fh):
        """Draw the bottom done/delete action selector."""
        th = p.th
        cw = _font_cw(th.font)

        # Space between the two action buttons
        spacing = cw * 2

        # Monospace font: size each button from its character count
        widths = [(len(action) + 2) * cw for action in self.ACTIONS]

        total = sum(widths) + spacing
        x = cx - total // 2

        for i, action in enumerate(self.ACTIONS):
            w = widths[i]
            action_cx = x + w // 2

            if self.focus == 1 and i == self.action_cursor:
                # Selected action uses the same selected colors
                # as the selected keyboard key
                p.fill(
                    x,
                    y - sbox // 2,
                    w,
                    sbox,
                    th.sel_bg,
                )
                p.ctext(
                    action_cx,
                    y - fh // 2,
                    action,
                    th.sel_fg,
                )
            else:
                # The entire inactive row is dim. When the action row
                # is focused, its unselected action is normal fg
                p.ctext(
                    action_cx,
                    y - fh // 2,
                    action,
                    th.fg if self.focus == 1 else th.dim,
                )

            x += w + spacing

    def draw(self, p, W, H):
        th = p.th
        cw = p.cw

        cx, cy, slot, sbox, half, top, fh, row = self._geom(
            th,
            cw,
            W,
            H,
        )

        p.fill(0, 0, W, H, th.bg)

        # -- edit buffer -------------------------------------------------------------------------

        shown = self.buf
        maxc = max(1, (W - 2 * th.pad) // cw)

        if len(shown) > maxc:
            shown = shown[-maxc:]

        p.ctext(
            cx,
            top,
            self.title,
            th.dim,
        )

        p.ctext(
            cx,
            top + row,
            shown,
            th.fg,
        )

        # -- keyboard strip ----------------------------------------------------------------------

        # The horizontal key strip is a window centred on self.cursor
        # It wraps around the keyboard contents
        n = len(KB_KEYS)
        gtop = cy - fh // 2

        for off in range(-half, half + 1):
            idx = (self.cursor + off) % n
            sx = cx + off * slot
            g = self._cased(KB_KEYS[idx])

            if self.focus == 0 and off == 0:
                # Selected keyboard key.
                p.fill(
                    sx - slot // 2,
                    cy - sbox // 2,
                    slot,
                    sbox,
                    th.sel_bg,
                )
                p.ctext(
                    sx,
                    gtop,
                    g,
                    th.sel_fg,
                )
            else:
                # Entire keyboard row is dim when the action row
                # has focus; otherwise nearby keys use the original
                # fade behavior.
                if self.focus == 0:
                    color = th.fg if abs(off) <= 3 else th.dim
                else:
                    color = th.dim

                p.ctext(
                    sx,
                    gtop,
                    g,
                    color,
                )

        # -- action row --------------------------------------------------------------------------

        action_y = top + row * 3 + sbox + row

        self._draw_actions(
            p,
            cx,
            action_y,
            sbox,
            fh,
        )
