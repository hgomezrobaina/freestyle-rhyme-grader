"""
Module for phonetic transcription of Spanish text to IPA.
Uses phonemizer library with espeak-ng backend.
"""

from phonemizer import phonemize
from typing import List


class SpanishPhoneticTranscriptor:
    """Transcribe Spanish text to IPA format."""

    def __init__(self):
        self.backend = "espeak"
        self.language = "es"

    def transcribe_word(self, word: str) -> str:
        """
        Convert a single word to IPA.

        Args:
            word: Spanish word to transcribe

        Returns:
            IPA representation
        """
        try:
            ipa = phonemize(
                word,
                language=self.language,
                backend=self.backend,
                strip=True,
                preserve_punctuation=False,
            )
            return ipa
        except Exception as e:
            print(f"Error transcribing word '{word}': {e}")
            return word

    def transcribe_text(self, text: str) -> str:
        """
        Convert text to IPA.

        Args:
            text: Spanish text to transcribe

        Returns:
            IPA representation
        """
        try:
            ipa = phonemize(
                text,
                language=self.language,
                backend=self.backend,
                strip=True,
                preserve_punctuation=True,
            )
            return ipa
        except Exception as e:
            print(f"Error transcribing text: {e}")
            return text

    def extract_vowels(self, word_ipa: str) -> List[str]:
        """
        Extract vowels from IPA representation.

        Args:
            word_ipa: IPA representation of a word

        Returns:
            List of vowels in the word
        """
        vowels = "aeiouɛɔɑɒæ"
        return [c for c in word_ipa if c.lower() in vowels]

    def get_final_vowels(self, word_ipa: str, count: int = 3) -> str:
        """
        Get the last N vowels from IPA representation.

        Args:
            word_ipa: IPA representation
            count: Number of final vowels to extract

        Returns:
            String of final vowels
        """
        vowels = self.extract_vowels(word_ipa)
        return "".join(vowels[-count:]) if vowels else ""
