import datetime
from dataclasses import dataclass


@dataclass
class Item:
    """
    Generic base class
    """
    pass


@dataclass
class Tune(Item):
    """
    MIDI file
    """
    artist: str
    title: str
    data: bytes
    game: str
    system: str
    uploadtime: datetime.datetime
