from picogui_picogame import App

import picogui as ui
import trigger_bindings
from consts import MODULE_MAX, NUMBER_OF_MODULES
from custom_widgets import CoolLabel
from models import Trigger
from modules import read_adc


class TriggerScreen(ui.Screen):
    def __init__(self, trigger: Trigger):
        self.trigger = trigger

        self.reading_widget = CoolLabel(
            label="Reading", value=str(read_adc(self.trigger.module))
        )

        self.attack_widget = ui.IntField(
            label="Attack Threshold",
            value=self.trigger.attack_threshold,
            hi=self.trigger.release_threshold,
            on_change=lambda v: self.on_attack_change(v),
        )

        self.release_widget = ui.IntField(
            label="Release Threshold",
            value=self.trigger.release_threshold,
            lo=self.trigger.attack_threshold,
            hi=MODULE_MAX,
            on_change=lambda v: self.on_release_change(v),
        )

        self.widgets: list[ui.Widget] = [
            ui.IntField(
                label="Module",
                value=self.trigger.module + 1,  # 1 based indexing
                lo=1,
                hi=NUMBER_OF_MODULES,
                on_change=lambda v: self.on_module_change(v),
            ),
            self.reading_widget,
            self.attack_widget,
            self.release_widget,
        ]

        super().__init__("Trigger", self.widgets)

    def on_module_change(self, value):
        value = value - 1  # 0 based indexing
        trigger_bindings.move(value, self.trigger)
        self.trigger.module = value

    def on_attack_change(self, value):
        self.release_widget.lo = value
        self.trigger.attack_threshold = value

    def on_release_change(self, value):
        self.attack_widget.hi = value
        self.trigger.release_threshold = value

    def update_reading(self, app: App):
        reading = read_adc(self.trigger.module)
        if self.reading_widget.value != reading:
            self.reading_widget.value = str(reading)
            app.invalidate()
