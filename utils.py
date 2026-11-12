from consts import PROPERTY_MAX, SP_PROPERTY_MAX
from models import PropertyType


def sanitize(s: str):
    words = s.replace("_", " ").split()
    return " ".join(word[0].upper() + word[1:].lower() for word in words)


def slugify(s: str):
    return s.lower().replace(" ", "_")


# 7 bit or 10 bit resolution
def get_property_max(property_type: PropertyType):
    return SP_PROPERTY_MAX if property_type == PropertyType.POSITION else PROPERTY_MAX
