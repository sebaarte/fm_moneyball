from enum import Enum
from dataclasses import dataclass


@dataclass
class TransferRange:
    lower_bound: int
    upper_bound: int

    def format_monetary_value(self,value: int) -> str:
        if value == 0:
            return "€0"
        
        # Déterminer le meilleur multiplicateur
        if value >= 1_000_000_000:  # Milliards
            num = value // 1_000_000_000
            suffix = 'B'
        elif value >= 1_000_000:  # Millions
            num = value // 1_000_000
            suffix = 'M'
        elif value >= 1_000:  # Milliers
            num = value // 1_000
            suffix = 'K'

        return f"€{num}{suffix}"

    def __repr__(self):
        if self.lower_bound == float('inf') and self.upper_bound == float('inf'):
            return "Not for Sale"
        elif self.lower_bound == -1 and self.upper_bound == -1:
            return "Unknown"
        return self.format_monetary_value(self.lower_bound) if self.lower_bound == self.upper_bound else f"{self.format_monetary_value(self.lower_bound)} - {self.format_monetary_value(self.upper_bound)}"
