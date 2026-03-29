class MetricCalculatorResult:
    def __init__(
        self, 
        rhyme_density: float, 
        multisyllabic_ratio: float,
        internal_rhymes_count: float,
        rhyme_diversity: float,
        total_syllables: float,
        rhyme_types: float
    ):
        self.rhyme_density = round(rhyme_density, 3)
        self.multisyllabic_ratio = round(multisyllabic_ratio, 3),
        self.internal_rhymes_count = internal_rhymes_count,
        self.rhyme_diversity = round(rhyme_diversity, 3),
        self.total_syllables = total_syllables,
        self.rhymed_syllables = int(total_syllables * rhyme_density),
        self.rhyme_types = rhyme_types,