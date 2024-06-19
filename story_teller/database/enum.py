from enum import Enum


class StatusEnum(Enum):
    raw = 0
    translated = 1
    edited = 2
    generated = 3
    done = 4
