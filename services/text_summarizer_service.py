from summa.summarizer import summarize

class TextSummarizerService:
    """
    Simple text summarization service using summa.summarizer.
    - First tries ratio-based summarization
    - Falls back to fixed word count summarization if needed
    """

    def __init__(self, ratio: float = 0.1, fallback_words: int = 300):
        self.ratio = ratio
        self.fallback_words = fallback_words

    def summarize_text(self, text: str) -> str:
        """Return a summary of the given text."""
        if not text or not text.strip():
            return ""

        # first attempt: ratio-based
        summary = summarize(
            text,
            ratio=self.ratio,
            split=False
        )

        # if summary is empty, try fallback word-count
        if not summary.strip():
            summary = summarize(
                text,
                words=self.fallback_words,
                split=False
            )

        return summary


# ------------------ small demo ------------------

if __name__ == "__main__":
    from pathlib import Path

    # read the text directly from sample_text.txt
    sample_path = Path("sample_text.txt")
    sample_text = sample_path.read_text(encoding="utf-8")

    summarizer = TextSummarizerService(ratio=0.1, fallback_words=300)
    summary = summarizer.summarize_text(sample_text)

    print("\n================ SUMMARY ================\n")
    print(summary)
    print("\n=========================================\n")
