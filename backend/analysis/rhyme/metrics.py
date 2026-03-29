"""
Metrics calculation for rhyme analysis.
"""

from typing import Dict
from analysis.rhyme.detector import SpanishRhymeDetector
from analysis.phonetic.syllable_counter import SpanishSyllableCounter
from analysis.rhyme.domain.core.metric_calculator_result import MetricCalculatorResult 

class RhymeMetricsCalculator:
    """Calculate comprehensive rhyme metrics for a verse."""

    def __init__(self):
        self.detector = SpanishRhymeDetector()
        self.syllable_counter = SpanishSyllableCounter()

    def calculate_metrics(self, text: str) -> Dict:
        """
        Calculate all rhyme metrics for a verse.

        Args:
            text: Spanish text (verse)

        Returns:
            Dictionary with all metrics
        """
        # Analyze verse
        analysis = self.detector.analyze_verse(text)

        # Calculate syllables
        total_syllables = self.syllable_counter.count_syllables_in_text(text)

        # Basic metrics
        total_words = analysis.total_words
        rhyming_words = analysis.rhyming_words

        # Rhyme density: approximate based on rhyming words
        # More accurate calculation would track syllable-level rhymes
        rhyme_density = (
            rhyming_words / total_words if total_words > 0 else 0.0
        )

        # Count rhyme types
        rhyme_types = analysis.rhyme_type_counts

        # Multisyllabic ratio (simplified: count pairs with 2+ syllables)
        total_rhymes = sum(
            len(patterns) for patterns in analysis["rhyme_pairs"].values()
        )
        multisyllabic_count = rhyme_types.get("multisyllabic", 0)
        multisyllabic_ratio = (
            multisyllabic_count / total_rhymes if total_rhymes > 0 else 0.0
        )

        # Internal rhymes (rhymes within the same line - simplified)
        internal_rhymes_count = rhyme_types.get("internal", 0)

        # Rhyme diversity: how many different rhyme types used
        rhyme_diversity = len([v for v in rhyme_types.values() if v > 0]) / 5.0

        return MetricCalculatorResult(
            rhyme_density=rhyme_density,
            multisyllabic_ratio=multisyllabic_ratio,
            internal_rhymes_count=internal_rhymes_count,
            rhyme_diversity=rhyme_diversity,
            total_syllables=total_syllables,
            rhyme_types=rhyme_types,
        )

    def get_descriptive_analysis(self, metrics: Dict) -> str:
        """
        Get a human-readable description of the metrics.

        Args:
            metrics: Dictionary from calculate_metrics()

        Returns:
            String description
        """
        density = metrics["rhyme_density"]
        diversity = metrics["rhyme_diversity"]

        if density < 0.05:
            density_desc = "muy baja"
        elif density < 0.10:
            density_desc = "baja"
        elif density < 0.20:
            density_desc = "media"
        elif density < 0.35:
            density_desc = "alta"
        else:
            density_desc = "muy alta"

        if diversity < 0.2:
            diversity_desc = "baja"
        elif diversity < 0.4:
            diversity_desc = "media"
        else:
            diversity_desc = "alta"

        return (
            f"Densidad de rimas {density_desc} ({density*100:.1f}%), "
            f"diversidad {diversity_desc}"
        )
