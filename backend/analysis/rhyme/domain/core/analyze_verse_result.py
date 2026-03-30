class AnalyzeVerseResult:
    def __init__(
        self,
        words: int,
        total_words: int,
        total_rhyming_words: int,
        rhyme_pairs: list,
        rhyme_type_counts: int
    ):
        self.words = words
        self.total_words = total_words
        self.rhyming_words = total_rhyming_words
        self.rhyme_pairs = rhyme_pairs
        self.rhyme_type_counts = rhyme_type_counts