# todo create chunks and produce article chunk by chunk in a lazy model

from pathlib import Path

from services.youtube_transcriptor_service import YouTubeTranscriptorService
from services.token_cost_service import TokenCostService
from services.text_summarizer_service import TextSummarizerService
from services.news_article_formatter_service import NewsArticleFormatterService


MAX_TOKENS = 2000


def main():
    # 1) Get input from user
    video_id = input("Enter YouTube video ID: ").strip()
    if not video_id:
        print("No video ID provided, exiting")
        return

    base_dir = Path(__file__).resolve().parent

    # 2) Get transcript and save it as .txt
    transcript_service = YouTubeTranscriptorService()  # adjust if your class uses from_env()
    transcript_text = transcript_service.transcribe(video_id)

    transcript_path = base_dir / f"{video_id}_transcript.txt"
    transcript_path.write_text(transcript_text, encoding="utf-8")
    print(f"Transcript saved to: {transcript_path}")

    # 3) Count tokens
    token_service = TokenCostService()
    original_tokens = token_service.count_tokens(transcript_text)
    print(f"Original transcript tokens: {original_tokens}")

    # 4) If more than MAX_TOKENS, summarize down to <= MAX_TOKENS
    text_for_article = transcript_text

    if original_tokens > MAX_TOKENS:
        print("Transcript is too long, summarizing...")

        # Choose an initial ratio based on length (simple heuristic)
        # Example: if 8000 tokens, ratio ~ 2000/8000 = 0.25
        initial_ratio = min(0.3, MAX_TOKENS / original_tokens)

        summarizer = TextSummarizerService(ratio=initial_ratio, fallback_words=600)
        summary = summarizer.summarize_text(transcript_text)

        summary_tokens = token_service.count_tokens(summary)
        print(f"First summary tokens: {summary_tokens}")

        # If still too long, shrink further in a loop
        current_ratio = initial_ratio
        while summary_tokens > MAX_TOKENS and current_ratio > 0.05:
            current_ratio *= 0.5  # make it smaller
            print(f"Summary still > {MAX_TOKENS} tokens, trying smaller ratio: {current_ratio}")

            summarizer = TextSummarizerService(ratio=current_ratio, fallback_words=400)
            summary = summarizer.summarize_text(summary)
            summary_tokens = token_service.count_tokens(summary)
            print(f"New summary tokens: {summary_tokens}")

        text_for_article = summary
        print(f"Final summary tokens: {summary_tokens}")
    else:
        print("No summarization needed, tokens within limit")
        summary_tokens = original_tokens

    # 5) Format as a news-style article using the LLM
    formatter = NewsArticleFormatterService.from_env()  # uses OPENAI_API_KEY
    article_text = formatter.format_as_article(text_for_article)

    article_path = base_dir / f"{video_id}_article.txt"
    article_path.write_text(article_text, encoding="utf-8")
    print(f"News-style article saved to: {article_path}")

    # (Optional) show cost estimate
    total_input_tokens = summary_tokens  # what you sent to the LLM
    est_input_cost = token_service.estimate_input_cost(total_input_tokens)
    print(f"Estimated LLM input cost (gpt-4o-mini): ${est_input_cost:.6f}")


if __name__ == "__main__":
    main()
