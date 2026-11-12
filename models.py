import note_builder


class PropertyType:
    PITCH = "pitch"
    FINE_TUNE = "fine_tune"
    AMPLITUDE = "amplitude"
    WAVETABLE = "wavetable"
    POSITION = "position"
    PANNING = "panning"
    ATTACK = "attack"
    DECAY = "decay"
    SUSTAIN = "sustain"
    RELEASE = "release"

    ALL = (
        PITCH,
        FINE_TUNE,
        AMPLITUDE,
        WAVETABLE,
        POSITION,
        PANNING,
        ATTACK,
        DECAY,
        SUSTAIN,
        RELEASE,
    )


class Curve:
    LINEAR = "linear"
    LOG = "log"
    EXP = "exp"

    ALL = (LINEAR, LOG, EXP)


class Control:
    def __init__(
        self,
        module: int,
        module_min: int,
        module_max: int,
        property_min: int,
        property_max: int,
        curve: Curve,
    ):
        self.module = module
        self.module_min = module_min
        self.module_max = module_max
        self.property_min = property_min
        self.property_max = property_max
        self.curve = curve

    def clone(self):
        return Control(
            self.module,
            self.module_min,
            self.module_max,
            self.property_min,
            self.property_max,
            self.curve,
        )


class Trigger:
    def __init__(
        self,
        module: int,
        attack_threshold: int,
        release_threshold: int,
        use_control: bool,
    ):
        self.module = module
        self.attack_threshold = attack_threshold
        self.release_threshold = release_threshold
        # if use_control is False, then note is always playing
        self.use_control = use_control

    def toggle_control(self):
        self.use_control = not self.use_control

    def clone(self):
        return Trigger(
            self.module,
            self.attack_threshold,
            self.release_threshold,
            self.use_control,
        )


class Property:
    def __init__(
        self,
        type: PropertyType,
        value: int | str,
        control: Control | None,
        use_control: bool | None,
    ):
        self.type = type
        self.value = value  # fixed value
        self.control = control
        self.use_control = use_control

    def toggle_control(self):
        self.use_control = not self.use_control

    def clone(self):
        return Property(
            self.type,
            self.value,
            self.control.clone() if self.control else None,
            self.use_control,
        )


class Note:
    def __init__(
        self,
        trigger: Trigger,
        pitch: Property,
        fine_tune: Property,
        amplitude: Property,
        wavetable: Property,
        position: Property,
        panning: Property,
        attack: Property,
        decay: Property,
        sustain: Property,
        release: Property,
    ):
        self.trigger = trigger
        self.pitch = pitch
        self.fine_tune = fine_tune
        self.amplitude = amplitude
        self.wavetable = wavetable
        self.position = position
        self.panning = panning
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

        self.synth_note = note_builder.build(self)

    def clone(self):
        return Note(
            trigger=self.trigger.clone(),
            pitch=self.pitch.clone(),
            fine_tune=self.fine_tune.clone(),
            amplitude=self.amplitude.clone(),
            wavetable=self.wavetable.clone(),
            position=self.position.clone(),
            panning=self.panning.clone(),
            attack=self.attack.clone(),
            decay=self.decay.clone(),
            sustain=self.sustain.clone(),
            release=self.release.clone(),
        )


class Preset:
    def __init__(self, name: str, file_name: str, notes: list[Note]):
        self.name = name
        self.file_name = file_name
        self.notes = notes
