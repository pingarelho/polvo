from picogui_picogame import App

import control_bindings
import picogui as ui
from consts import MODULE_MAX, NUMBER_OF_MODULES
from custom_widgets import CoolLabel, SteppedChoice
from models import Control, Curve, PropertyType
from modules import read_adc
from utils import get_property_max


class ControlScreen(ui.Screen):
    def __init__(self, control: Control, property_type: PropertyType):
        self.control = control
        self.property_type = property_type

        self.reading_widget = CoolLabel(
            label="Reading", value=str(read_adc(self.control.module))
        )

        self.module_min_widget = ui.IntField(
            label="Module Min",
            value=self.control.module_min,
            hi=self.control.module_max,
            on_change=lambda v: self.on_module_min_change(v),
        )

        self.module_max_widget = ui.IntField(
            label="Module Max",
            value=self.control.module_max,
            lo=self.control.module_min,
            hi=MODULE_MAX,
            on_change=lambda v: self.on_module_max_change(v),
        )

        self.widgets: list[ui.Widget] = [
            ui.IntField(
                label="Module",
                value=self.control.module + 1,  # 1 based indexing
                lo=1,
                hi=NUMBER_OF_MODULES,
                on_change=lambda v: self.on_module_change(v),
            ),
            self.reading_widget,
            self.module_min_widget,
            self.module_max_widget,
            ui.IntField(
                label="Property Min",
                value=self.control.property_min,
                hi=get_property_max(self.property_type),
                on_change=lambda v: setattr(self.control, "property_min", v),
            ),
            ui.IntField(
                label="Property Max",
                value=self.control.property_max,
                hi=get_property_max(self.property_type),
                on_change=lambda v: setattr(self.control, "property_max", v),
            ),
            SteppedChoice(
                label="Curve",
                options=Curve.ALL,
                index=Curve.ALL.index(self.control.curve),
                on_change=lambda v: setattr(self.control, "curve", v),
            ),
        ]

        super().__init__("Control", self.widgets)

    def on_module_change(self, value):
        value = value - 1  # 0 based indexing
        control_bindings.move(value, self.control, self.property_type)
        self.control.module = value

    def on_module_min_change(self, value):
        self.module_max_widget.lo = value
        self.control.module_min = value

    def on_module_max_change(self, value):
        self.module_min_widget.hi = value
        self.control.module_max = value

    def update_reading(self, app: App):
        reading = read_adc(self.control.module)
        if self.reading_widget.value != reading:
            self.reading_widget.value = str(reading)
            app.invalidate()
