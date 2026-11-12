PRESET_DIR = "presets"

MAX_PRESET_NAME_LENGTH = 18

NUMBER_OF_MODULES = 6

MODULE_MAX = 1023

PROPERTY_MAX = 127  # 7 bit resolution for most properties

# A 10-bit resolution for special properties that require
# greater resolution (e.g. wavetable position, where each wave
# gets 16 different start positions instead of two).
SP_PROPERTY_MAX = 1023
