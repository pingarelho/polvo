import audiobusio
import audiomixer
import board
import synthio

from models import Note, Preset

BUFFER_SIZE = 8192
SAMPLE_RATE = 28000

audio = audiobusio.I2SOut(bit_clock=board.GP2, word_select=board.GP3, data=board.GP4)
mixer = audiomixer.Mixer(
    sample_rate=SAMPLE_RATE, channel_count=2, buffer_size=BUFFER_SIZE
)

synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, channel_count=2)
mixer.voice[0].play(synth)
audio.play(mixer)


def add_note(note: Note, loaded_preset: Preset | None):
    if (loaded_preset and note in loaded_preset.notes) and not note.trigger.use_control:
        synth.press(note.synth_note)


def delete_note(note: Note):
    synth.release(note.synth_note)


def unload_preset():
    synth.release_all()


def load_preset(preset: Preset):
    for note in preset.notes:
        if not note.trigger.use_control:
            synth.press(note.synth_note)
