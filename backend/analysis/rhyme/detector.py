"""
Rhyme detection algorithm for Spanish rap lyrics.
"""

import re
import time
import logging
from typing import List, Dict, Tuple, Set
from analysis.phonetic.transcriptor import SpanishPhoneticTranscriptor
from analysis.phonetic.vowel_extractor import VowelExtractor
from analysis.rhyme.types import RhymeType, RhymePattern
from analysis.rhyme.domain.core.analyze_verse_result import AnalyzeVerseResult

logger = logging.getLogger(__name__)


class SpanishRhymeDetector:
    """Detect and analyze rhymes in Spanish text."""

    def __init__(self):
        self.transcriptor = SpanishPhoneticTranscriptor()
        self.vowel_extractor = VowelExtractor()

        # Minimum similarity score for a consonant rhyme (0.0 to 1.0)
        self.consonant_threshold = 0.8
        
        # Minimum similarity for assonant rhyme
        self.assonant_threshold = 0.6

    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text, removing punctuation."""
        # Match Spanish words (including accented characters)
        words = re.findall(r"\b[a-záéíóúñ]+\b", text.lower())

        return words

    def _get_final_syllable_ipa(self, word: str) -> str:
        """Get IPA representation of the final syllable(s) of a word."""
        # Transcribe the word to IPA
        ipa = self.transcriptor.transcribe_word(word)
        return ipa

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (simplified).
        Uses longest common suffix approach.
        """
        if not str1 or not str2:
            return 0.0

        # Compare from the end
        matches = 0
        max_len = min(len(str1), len(str2))

        for i in range(1, max_len + 1):
            if str1[-i] == str2[-i]:
                matches += 1
            else:
                break

        return matches / max_len if max_len > 0 else 0.0

    def detect_consonant_rhyme(self, word1: str, word2: str) -> Tuple[bool, float]:
        """
        Detect consonant rhyme (full rhyme).
        Last 2+ sounds must match including consonants.

        Returns:
            (is_rhyme, strength)
        """
        if word1 == word2:
            return False, 0.0  # Same word doesn't count

        ipa1 = self._get_final_syllable_ipa(word1)
        ipa2 = self._get_final_syllable_ipa(word2)

        # Get last 2+ characters from IPA (syllable ending)
        ending1 = ipa1[-4:] if len(ipa1) >= 4 else ipa1
        ending2 = ipa2[-4:] if len(ipa2) >= 4 else ipa2

        similarity = self._calculate_similarity(ending1, ending2)

        is_rhyme = similarity >= self.consonant_threshold
        return is_rhyme, similarity

    def detect_assonant_rhyme(self, word1: str, word2: str) -> Tuple[bool, float]:
        """
        Detect assonant rhyme (vowel-only rhyme).

        Returns:
            (is_rhyme, strength)
        """
        if word1 == word2:
            return False, 0.0

        ipa1 = self._get_final_syllable_ipa(word1)
        ipa2 = self._get_final_syllable_ipa(word2)

        vowels1 = self.vowel_extractor.extract_vowels_from_ipa(ipa1)
        vowels2 = self.vowel_extractor.extract_vowels_from_ipa(ipa2)

        if not vowels1 or not vowels2:
            return False, 0.0

        # Get last 2+ vowels
        key1 = "".join(vowels1[-3:])
        key2 = "".join(vowels2[-3:])

        similarity = self._calculate_similarity(key1, key2)
        is_rhyme = similarity >= self.assonant_threshold
        return is_rhyme, similarity

    def find_rhyming_pairs(
        self, 
        words: List[str]
    ) -> Dict[str, List[RhymePattern]]:
        """
        Find all rhyming pairs in a word list.

        Returns:
            Dictionary mapping each word to its rhyming partners
        """
        rhyme_pairs = {}
        total_comparisons = len(words) * (len(words) - 1) // 2
        logger.info(f"[RhymeDetector] find_rhyming_pairs: {len(words)} words, {total_comparisons} comparisons to make")
        t_start = time.time()
        comparisons_done = 0
        rhymes_found = 0

        for i, word in enumerate(words):
            rhyme_pairs[word] = []

            for j in range(i + 1, len(words)):
                partner = words[j]
                comparisons_done += 1

                # Try consonant rhyme first
                is_cons, cons_strength = self.detect_consonant_rhyme(word, partner)

                if is_cons:
                    pattern = RhymePattern(
                        word1=word,
                        word2=partner,
                        rhyme_type=RhymeType.CONSONANT,
                        strength=cons_strength,
                        syllable_count=2,  # Simplified
                    )
                    rhyme_pairs[word].append(pattern)
                    rhymes_found += 1
                else:
                    # Try assonant rhyme
                    is_asso, asso_strength = self.detect_assonant_rhyme(
                        word, partner
                    )
                    if is_asso:
                        pattern = RhymePattern(
                            word1=word,
                            word2=partner,
                            rhyme_type=RhymeType.ASSONANT,
                            strength=asso_strength,
                            syllable_count=2,
                        )
                        rhyme_pairs[word].append(pattern)
                        rhymes_found += 1

            # Log progress every 50 words
            if (i + 1) % 50 == 0 or i == len(words) - 1:
                elapsed = time.time() - t_start
                logger.info(
                    f"[RhymeDetector] Progress: word {i+1}/{len(words)}, "
                    f"{comparisons_done}/{total_comparisons} comparisons, "
                    f"{rhymes_found} rhymes found, {elapsed:.1f}s elapsed"
                )

        elapsed = time.time() - t_start
        logger.info(f"[RhymeDetector] find_rhyming_pairs completed: {rhymes_found} rhymes in {elapsed:.1f}s")
        return rhyme_pairs

    def analyze_verse(self, text: str) -> AnalyzeVerseResult:
        """
        Analyze a verse for rhyme patterns.

        Returns:
            Dictionary with rhyme metrics
        """
        t_start = time.time()
        words = self._extract_words(text)
        logger.info(f"[RhymeDetector] analyze_verse: extracted {len(words)} words from text ({len(text)} chars)")
        rhyme_pairs = self.find_rhyming_pairs(words)

        # Count total rhyming syllables (simplified)
        total_rhyming_words = sum(
            1 for patterns in rhyme_pairs.values() if patterns
        )
        total_words = len(words)

        # Count by type
        rhyme_type_counts = {}
        for patterns in rhyme_pairs.values():
            for pattern in patterns:
                rhyme_type = pattern.rhyme_type.value
                rhyme_type_counts[rhyme_type] = (
                    rhyme_type_counts.get(rhyme_type, 0) + 1
                )

        elapsed = time.time() - t_start
        logger.info(
            f"[RhymeDetector] analyze_verse completed: {total_words} words, "
            f"{total_rhyming_words} rhyming, types={rhyme_type_counts}, {elapsed:.1f}s"
        )

        return AnalyzeVerseResult(
            words=words,
            total_words=total_words,
            rhyme_pairs=rhyme_pairs,
            rhyme_type_counts=rhyme_type_counts,
            total_rhyming_words=total_rhyming_words
        )
