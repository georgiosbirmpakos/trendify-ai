import os
from datetime import datetime, timedelta, timezone

import pyyoutube
from dotenv import load_dotenv


class YouTubeTrendingService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("YouTube API key is required")
        self.api = pyyoutube.Api(api_key=api_key)

    @classmethod
    def from_env(cls, env_var: str = "YT_DATA_API_KEY") -> "YouTubeTrendingService":
        """Create service using an API key stored in a .env / environment variable"""
        load_dotenv()
        key = os.getenv(env_var)
        return cls(key)

    def get_trending_videos(
        self,
        topic: str,
        days_back: int = 1,
        top_n: int = 10,
        country_code: str | None = None,
    ):
        """
        Videos for `topic`:
        - published in the last `days_back` days
        - ordered by viewCount
        """
        # Time filter: now - days_back
        start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
        start_time = start_time.replace(microsecond=0)
        published_after = start_time.isoformat().replace("+00:00", "Z")

        search_params = {
            "q": topic,
            "search_type": "video",
            "order": "viewCount",
            "count": top_n,
            "parts": ["snippet"],
            "published_after": published_after,
        }
        if country_code:
            search_params["region_code"] = country_code

        search_resp = self.api.search(**search_params)
        items = search_resp.items or []
        video_ids = [item.id.videoId for item in items if getattr(item, "id", None)]

        if not video_ids:
            return []

        details = self.api.get_video_by_id(video_id=",".join(video_ids))
        videos = []

        for v in details.items or []:
            vid = v.id
            title = v.snippet.title
            published_at = v.snippet.publishedAt
            stats = getattr(v, "statistics", None)
            views = int(stats.viewCount) if stats and stats.viewCount else 0

            videos.append(
                {
                    "id": vid,
                    "title": title,
                    "views": views,
                    "publishedAt": published_at,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                }
            )

        videos.sort(key=lambda x: x["views"], reverse=True)
        return videos

    def get_viral_all_time(
        self,
        topic: str,
        top_n: int = 5,
        country_code: str | None = None,
    ):
        """
        Most viewed videos for `topic` (no time limit).
        """
        params = {
            "q": topic,
            "search_type": "video",
            "order": "viewCount",
            "count": top_n,
            "parts": ["snippet"],
        }
        if country_code:
            params["region_code"] = country_code

        search_resp = self.api.search(**params)
        items = search_resp.items or []
        video_ids = [it.id.videoId for it in items]

        if not video_ids:
            return []

        details = self.api.get_video_by_id(video_id=",".join(video_ids))
        results = []

        for v in details.items or []:
            stats = getattr(v, "statistics", None)
            views = int(stats.viewCount) if stats and stats.viewCount else 0

            results.append(
                {
                    "id": v.id,
                    "title": v.snippet.title,
                    "views": views,
                    "publishedAt": v.snippet.publishedAt,
                    "url": f"https://www.youtube.com/watch?v={v.id}",
                }
            )

        results.sort(key=lambda x: x["views"], reverse=True)
        return results


if __name__ == "__main__":
    topic = "Ritchie Blackmore"
    # Create service from .env
    svc = YouTubeTrendingService.from_env()

    print("---------TODAY (last 1 day)-----------------------")
    today_videos = svc.get_trending_videos(
        topic=topic,
        days_back=1,
        top_n=5
    )
    for v in today_videos:
        print(v["views"], v["publishedAt"], v["title"], v["url"], v["id"])

    print("---------ALL TIME-----------------------")
    viral_videos = svc.get_viral_all_time(
        topic=topic,
        top_n=5,
        country_code=None
    )
    for v in viral_videos:
        print(v["views"], v["publishedAt"], v["title"], v["url"], v["id"])
