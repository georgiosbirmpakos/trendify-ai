from typing import List, Optional
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

class YouTubeTranscriptorService:
    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()

    def list_caption_languages(self, video_id: str) -> Optional[List[str]]:
        """
        Returns a list of language codes for available captions,
        or None if no captions exist.
        """
        try:
            transcript_list = self.ytt_api.list(video_id)
            return [t.language_code for t in transcript_list]
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
            print(f"[WARN] No transcripts available for {video_id}: {e}")
            return None

    def transcribe(self, video_id: str) -> str:
        """
        Returns merged captions text if available, otherwise a message
        indicating that no captions exist.
        """
        langs = self.list_caption_languages(video_id)

        if langs is None or len(langs) == 0:
            return "No captions available for this video."

        # use the languages we already retrieved
        fetched_transcript = self.ytt_api.fetch(video_id, languages=langs)
        languages_found = ", ".join(langs)
        captions_merged = " ".join(txt.text for txt in fetched_transcript.snippets)

        return f"{languages_found} languages found for {video_id} :\n{captions_merged}"


if __name__ == "__main__":
    yt = YouTubeTranscriptorService()

    # Test video ID (replace with anything you want)
    video_id = "OJmVoOTUhng"

    print("\n=== Checking available caption languages ===")
    langs = yt.list_caption_languages(video_id)
    print("Languages:", langs)

    print("\n=== Fetching transcript ===")
    transcript_text = yt.transcribe(video_id)
    print(transcript_text)