"""
Types and classifications of rhymes in Spanish.
"""

from enum import Enum
from typing import NamedTuple


class RhymeType(str, Enum):
    """Types of rhymes that can be detected."""

    CONSONANT = "consonant"  # Full rhyme (same vowels + consonants)
    ASSONANT = "assonant"  # Only vowels match
    INTERNAL = "internal"  # Rhyme within same verse
    MULTISYLLABIC = "multisyllabic"  # Multi-syllable rhyme
    MOSAIC = "mosaic"  # Composed rhyme (e.g., "para ti" / "compartí")


class RhymePattern(NamedTuple):
    """Represents a detected rhyme pattern."""

    word1: str
    word2: str
    rhyme_type: RhymeType
    strength: float  # 0.0 to 1.0
    syllable_count: int  # Number of syllables involved in the rhyme
