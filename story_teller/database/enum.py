from enum import Enum


class StatusEnum(Enum):
    raw = 0
    text_edited = 1
    audio_generated = 2
    image_generated = 3
    done = 4
