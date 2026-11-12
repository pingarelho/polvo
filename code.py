import sys

import picogame_clock as clock
import supervisor
from picogui_picogame import App
from picogui_themes import LcdTheme

from control_screen import ControlScreen
from input import handle_inputs
from modules import handle_modules
from preset_screen import PresetScreen
from trigger_screen import TriggerScreen
from wavetable_manager import WAVETABLES

supervisor.runtime.autoreload = False

if not WAVETABLES:
    print("No wavetables available.")
    sys.exit()

app = App(theme=LcdTheme(), zoom=2, exit_on_root_back=False)
clock = clock.Clock(100)

preset_screen = PresetScreen()
session = app.session
session.start(preset_screen)

ui_counter = 0
rw_counter = 0

while session.running:
    dt = clock.tick()

    # run UI stuff every 4 cycles (25 Hz)
    if ui_counter == 0:
        handle_inputs(app)
        app.tick()

    # update reading widget every 50 cycles (2 Hz)
    current_screen = session.screen
    if rw_counter == 0 and isinstance(current_screen, (TriggerScreen, ControlScreen)):
        current_screen.update_reading(app)

    # read modules every cycle (100 Hz)
    handle_modules()

    ui_counter = (ui_counter + 1) % 4
    rw_counter = (rw_counter + 1) % 50
