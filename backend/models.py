from enum import Enum
from dataclasses import dataclass


@dataclass
class transfer_range:
    lower_bound: int
    upper_bound: int

    def __repr__(self):
        )