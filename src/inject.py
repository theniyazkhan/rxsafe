"""Controlled error injection pipeline.

Simulates optical character recognition (OCR) errors, typos, and visual confusion
to systematically evaluate safety detector degradation and error propagation.
"""

import random
from typing import List, Dict, Tuple


# Common OCR character confusion mappings
OCR_CONFUSION_MAP = {
    'l': ['1', 'I', 'i', '|'],
    'O': ['0', 'Q', 'D'],
    '0': ['O', 'o'],
    'S': ['5', '$'],
    'B': ['8'],
    'rn': ['m'],
    'cl': ['d'],
    'vv': ['w'],
}


class ErrorInjector:
    """Injects controlled character or word-level noise into drug name strings."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def set_seed(self, seed: int) -> None:
        self.random.seed(seed)

    def substitute_char(self, text: str) -> str:
        """Randomly substitute a character with a keyboard or visual neighbor."""
        if not text:
            return text
        idx = self.random.randint(0, len(text) - 1)
        char = text[idx]
        
        # Check confusion map
        if char in OCR_CONFUSION_MAP:
            replacement = self.random.choice(OCR_CONFUSION_MAP[char])
        else:
            # Random lower char
            replacement = chr(self.random.randint(97, 122))

        return text[:idx] + replacement + text[idx + 1:]

    def delete_char(self, text: str) -> str:
        """Randomly delete a character from text."""
        if len(text) <= 1:
            return text
        idx = self.random.randint(0, len(text) - 1)
        return text[:idx] + text[idx + 1:]

    def insert_char(self, text: str) -> str:
        """Randomly insert a character into text."""
        idx = self.random.randint(0, len(text))
        char = chr(self.random.randint(97, 122))
        return text[:idx] + char + text[idx:]

    def inject_noise(self, text: str, error_rate: float = 0.1) -> str:
        """Apply noise operations with probability proportional to error rate."""
        if not text or error_rate <= 0:
            return text

        chars = list(text)
        num_errors = max(1, int(len(text) * error_rate))

        corrupted = text
        for _ in range(num_errors):
            op = self.random.choice(["sub", "del", "ins"])
            if op == "sub":
                corrupted = self.substitute_char(corrupted)
            elif op == "del":
                corrupted = self.delete_char(corrupted)
            else:
                corrupted = self.insert_char(corrupted)

        return corrupted

    def corrupt_prescription(
        self, brand_list: List[str], error_rate: float = 0.1
    ) -> List[str]:
        """Corrupt a list of prescribed brand names."""
        return [self.inject_noise(brand, error_rate) for brand in brand_list]
