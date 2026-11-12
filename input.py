import board
from microcontroller import Pin
from picogame_input import SELECT, A, B, Buttons
from picogui_picogame import App
from rotaryio import IncrementalEncoder

import picogui as ui
from custom_row_kb import RowKeyboard
from custom_widgets import SteppedChoice
from note_mgmt_screen import NoteMgmtScreen
from note_screen import NoteScreen
from preset_mgmt_screen import PresetMgmtScreen
from preset_screen import PresetScreen
from property_screen import PropertyScreen

MAX_ENCODER_STEPS = 2
ENCODER_DIVISOR = 2
ENC_RANGE_STEPS = 30

PROFILE = ((board.GP7, A), (board.GP22, B), (board.GP26, SELECT))

buttons = Buttons(profile=PROFILE)


class Encoder:
    def __init__(self, pin_a: Pin, pin_b: Pin):
        self.encoder = IncrementalEncoder(pin_a, pin_b, ENCODER_DIVISOR)
        self.last_pos = self.encoder.position

    @property
    def pos(self) -> int:
        return self.encoder.position

    def poll(self) -> int:
        pos = self.pos
        delta = pos - self.last_pos
        self.last_pos = pos
        return delta


encoder_a = Encoder(board.GP8, board.GP9)
encoder_b = Encoder(board.GP20, board.GP21)


def apply_encoder_delta(delta: int, positive, negative):
    steps = min(
        abs(delta), MAX_ENCODER_STEPS
    )  # allow "acceleration" but only up to n steps
    for _ in range(steps):
        if delta > 0:
            positive()
        else:
            negative()


def handle_inputs(app: App):
    buttons.poll()

    # get the current screen because shift has different behaviours
    # depending on screen type
    current_screen = app.session.screen

    # shift + encoder b skips steps in IntField, allowing the user to
    # reach the desired number more quickly
    if isinstance(current_screen, ui.Screen):
        sel = current_screen.sel
        widget = current_screen.widgets[sel]
        if isinstance(widget, (ui.IntField, SteppedChoice)):
            if buttons.just_pressed(SELECT):
                hi = (
                    widget.hi
                    if isinstance(widget, ui.IntField)
                    else len(widget.options)
                )
                widget.step = max(round(hi / ENC_RANGE_STEPS), 1)
            elif buttons.just_released(SELECT):
                widget.step = 1

    apply_encoder_delta(encoder_a.poll(), app.down, app.up)
    apply_encoder_delta(encoder_b.poll(), app.right, app.left)

    shift_held = buttons.is_pressed(SELECT)

    # input logic should be moved to the screens themselves and just
    # call "current_screen.handle_a"
    if buttons.just_pressed(A):
        if shift_held:
            if isinstance(current_screen, PresetScreen):
                current_screen.load_sel_preset(app)
            elif isinstance(current_screen, PropertyScreen):
                current_screen.toggle_sel_control(app)
        else:
            app.ok()

    elif buttons.just_pressed(B):
        if shift_held:
            if (
                isinstance(current_screen, PresetScreen)
                and not current_screen.is_add_selected()
            ):
                app.push(PresetMgmtScreen(current_screen))
            elif (
                isinstance(current_screen, NoteScreen)
                and not current_screen.is_add_selected()
            ):
                app.push(NoteMgmtScreen(current_screen))
        else:
            if isinstance(current_screen, PresetScreen):
                current_screen.save_presets(app)
            else:
                app.back()

    elif buttons.just_pressed(SELECT) and isinstance(current_screen, RowKeyboard):
        current_screen.toggle_shift(app)
