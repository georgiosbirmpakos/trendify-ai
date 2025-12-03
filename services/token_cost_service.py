import tiktoken

class TokenCostService:
    """
    Token counter + cost calculator for GPT-4o-mini.
    Uses tiktoken encoding and OpenAI pricing.
    """

    # OpenAI pricing (Feb 2025)
    COST_PER_1K_INPUT = 0.00015
    COST_PER_1K_OUTPUT = 0.00060

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.encoding = self._load_encoding()

    def _load_encoding(self):
        """Get correct encoding, fallback to cl100k_base."""
        try:
            return tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Return total tokens for the given text."""
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def estimate_input_cost(self, token_count: int) -> float:
        """Cost for input tokens."""
        return (token_count / 1000) * self.COST_PER_1K_INPUT

    def estimate_output_cost(self, token_count: int) -> float:
        """Cost for output tokens."""
        return (token_count / 1000) * self.COST_PER_1K_OUTPUT

    def estimate_total_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Total cost (input + output)."""
        return (
            self.estimate_input_cost(input_tokens)
            + self.estimate_output_cost(output_tokens)
        )


# ------------------ small demo ------------------

if __name__ == "__main__":
    from pathlib import Path

    # read the text directly from sample_text.txt
    sample_path = Path("sample_text.txt")
    sample_text = sample_path.read_text(encoding="utf-8")

    svc = TokenCostService()
    input_tokens = svc.count_tokens(sample_text)

    print("Tokens:", input_tokens)
    print("Input cost:", svc.estimate_input_cost(input_tokens))
    print("Output cost (assume 200 tokens):", svc.estimate_output_cost(200))
    print("Total cost:", svc.estimate_total_cost(input_tokens, 200))
