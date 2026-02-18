"""
Module for extracting vowels from IPA text.
"""

from typing import List, Dict


class VowelExtractor:
    """Extract and analyze vowels from IPA text."""

    # Spanish vowels in IPA
    SPANISH_VOWELS = {"a", "e", "i", "o", "u", "ɛ", "ɔ", "ɑ", "ɒ", "æ"}

    @staticmethod
    def extract_vowels_from_ipa(ipa_text: str) -> List[str]:
        """
        Extract all vowels from IPA text.

        Args:
            ipa_text: IPA representation

        Returns:
            List of vowels
        """
        return [c for c in ipa_text if c.lower() in VowelExtractor.SPANISH_VOWELS]

    @staticmethod
    def get_final_vowels(ipa_text: str, count: int = 3) -> str:
        """
        Get the last N vowels from IPA text.

        Args:
            ipa_text: IPA representation
            count: Number of final vowels to extract

        Returns:
            String of final vowels
        """
        vowels = VowelExtractor.extract_vowels_from_ipa(ipa_text)
        return "".join(vowels[-count:]) if vowels else ""

    @staticmethod
    def get_vowel_pattern(ipa_text: str) -> str:
        """
        Get vowel pattern (e.g., "aio" from "barriño").
        Useful for detecting assonant rhymes.

        Args:
            ipa_text: IPA representation

        Returns:
            Vowel pattern
        """
        return "".join(VowelExtractor.extract_vowels_from_ipa(ipa_text))
