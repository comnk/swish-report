import random
from typing import List
from rapidfuzz import fuzz

from ..core.config import set_youtube_key

def get_nba_youtube_videos(full_name: str, threshold: int = 85, max_videos: int = 3) -> List[str]:
    """
    Fetch YouTube videos for a given high school basketball player,
    filtering by fuzzy match on the player's full name, returning at most max_videos.
    Adds randomness to avoid always selecting the same top videos.
    """
    youtube = set_youtube_key()
    request = youtube.search().list(
        part="snippet",
        maxResults=15,  # fetch a few more to increase variety
        q=f"{full_name} NBA highlights",
        type="video",
        videoEmbeddable="true",
    )
    response = request.execute()
    videos_with_score = []

    for item in response.get("items", []):
        video_title = item["snippet"]["title"]
        score = fuzz.partial_ratio(full_name.lower(), video_title.lower())
        if score >= threshold:
            video_id = item["id"]["videoId"]
            videos_with_score.append((score, f"https://www.youtube.com/watch?v={video_id}"))

    # Group videos by score to allow shuffling within same-score group
    score_groups = {}
    for score, url in videos_with_score:
        score_groups.setdefault(score, []).append(url)

    selected_videos = []
    for score in sorted(score_groups.keys(), reverse=True):
        urls = score_groups[score]
        random.shuffle(urls)  # shuffle videos with same score
        for url in urls:
            if len(selected_videos) < max_videos:
                selected_videos.append(url)
            else:
                break
        if len(selected_videos) >= max_videos:
            break

    return selected_videos