from picogui import Link, _Field


def dim_val_draw(self, p, x, y, w, focused):
    th = p.th
    active = focused and p.active  # the focused row is in encoder edit mode
    screen = active and th.active_screen  # 1bpp: screen the row + halo the text
    if focused:
        p.fill(x, y, w, th.row_h, th.active_bg if active else th.sel_bg)
        if screen:
            p.checker(x, y, w, th.row_h, th.active_hatch)
    fg = (th.active_fg if active else th.sel_fg) if focused else th.fg
    halo = th.active_bg if screen else None
    p.text(x + th.pad, y + th.text_dy, self.label, fg, halo)
    vt = self.value_text()
    if vt:
        p.rtext(
            x + w - th.pad, y + th.text_dy, vt, th.sel_fg if focused else th.dim, halo
        )


class CoolLabel(_Field):
    def __init__(self, label, value):
        super().__init__(label)
        self.value = value

    def hint(self):
        return ""

    def value_text(self):
        return self.value

    def draw(self, p, x, y, w, focused):
        dim_val_draw(self, p, x, y, w, focused)


class EllipsisLink(Link):
    def value_text(self):
        return "..."

    def draw(self, p, x, y, w, focused):
        dim_val_draw(self, p, x, y, w, focused)


class SteppedChoice(_Field):
    adjustable = True

    def __init__(self, label, options, index=0, step=1, on_change=None):
        super().__init__(label, on_change)
        if step <= 0:
            raise ValueError("SteppedChoice step must be positive")
        options = list(options)
        if not options:
            raise ValueError("Choice needs at least one option")
        self.options = options
        self.step = step
        self.index = min(max(index, 0), len(options) - 1)  # clamp initial index

    def hint(self):
        return "<>: change"

    def get_value(self):
        return self.options[self.index]

    def set_value(self, v):
        if v in self.options:
            self.index = self.options.index(v)

    def value_text(self):
        return f"< {self.options[self.index]} >"

    def key(self, app, k):
        old = self.index
        if len(self.options) < 2:  # nothing to cycle to: no change, no emit
            return False
        if k == "R":
            self.index = min(len(self.options) - 1, self.index + self.step)
        elif k == "L":
            self.index = max(0, self.index - self.step)
        else:
            return False
        if self.index == old:  # already at the limit: no change, no redraw/emit
            return False
        self._emit(self.options[self.index])
        return True
