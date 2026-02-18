"""
Module for syllable counting in Spanish.
Uses pyphen hyphenation library.
"""

import pyphen
from typing import List


class SpanishSyllableCounter:
    """Count syllables in Spanish words and texts."""

    def __init__(self):
        self.hyphenator = pyphen.Pyphen(lang="es_ES")

    def count_syllables_in_word(self, word: str) -> int:
        """
        Count syllables in a single word.

        Args:
            word: Spanish word

        Returns:
            Number of syllables
        """
        if not word:
            return 0

        # Remove accents and convert to lowercase
        word = word.lower()

        # Use pyphen to hyphenate
        hyphenated = self.hyphenator.inserted(word)

        # Count hyphens + 1
        if hyphenated:
            syllables = hyphenated.split("-")
            return len([s for s in syllables if s])

        return 1

    def count_syllables_in_text(self, text: str) -> int:
        """
        Count total syllables in a text.

        Args:
            text: Spanish text

        Returns:
            Total number of syllables
        """
        # Remove punctuation and split by spaces
        import re

        words = re.findall(r"\b[a-záéíóúñ]+\b", text.lower())
        return sum(self.count_syllables_in_word(word) for word in words)

    def get_syllables_in_word(self, word: str) -> List[str]:
        """
        Get individual syllables of a word.

        Args:
            word: Spanish word

        Returns:
            List of syllables
        """
        word = word.lower()
        hyphenated = self.hyphenator.inserted(word)
        if hyphenated:
            return [s for s in hyphenated.split("-") if s]
        return [word]
