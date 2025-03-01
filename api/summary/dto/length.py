from enum import Enum


class Length(str, Enum):
    SHORT = 'short',
    LONG = 'long',
    BULLET_POINTS = 'bullet_points'