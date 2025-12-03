import os
from openai import OpenAI
from dotenv import load_dotenv


class NewsArticleFormatterService:
    """
    Simple 'agent' that rewrites raw text into a clean, structured,
    neutral news-style article using an OpenAI model.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        # initialize OpenAI client using this specific key
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    @classmethod
    def from_env(cls, env_var: str = "OPENAI_API_KEY", model_name: str = "gpt-4o-mini"):
        """
        Create service using an API key from environment or .env file.
        """
        load_dotenv()
        key = os.getenv(env_var)
        return cls(key, model_name=model_name)

    def format_as_article(self, text: str) -> str:
        """
        Takes a plain text string and returns a structured news-style article.
        """
        if not text or not text.strip():
            return ""

        system_prompt = (
            "You are a professional news editor. "
            "You rewrite input text into a clear, structured news article. "
            "Keep a neutral tone and do not invent facts."
            "Keep the originally language the text was written in. Don't turn it in other languages."
        )

        user_prompt = f"""
Rewrite the following text as a news article :
Keep the originally language the text was written in. Don't turn it in other languages
Keep it concise, structured, and easy to read. Do not add information
that is not already present in the original text.

--- ORIGINAL TEXT START ---
{text}
--- ORIGINAL TEXT END ---
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()


# ---------------- small demo ----------------

if __name__ == "__main__":
    from pathlib import Path

    # read the text directly from sample_text.txt
    sample_path = Path("sample_text.txt")
    sample_text = sample_path.read_text(encoding="utf-8")

    formatter = NewsArticleFormatterService.from_env(model_name="gpt-4o-mini")
    article = formatter.format_as_article(sample_text)

    print("\n================ NEWS ARTICLE ================\n")
    print(article)
    print("\n==============================================\n")
