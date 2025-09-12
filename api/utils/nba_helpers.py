import random, json

from typing import List
from rapidfuzz import fuzz

from core.config import set_youtube_key
from core.db import get_db_connection

import time
from fastapi import HTTPException
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

def fetch_nba_player_stats(full_name: str):
    """
    Given a player's full name, fetch their NBA career stats using nba_api.
    Returns: list of dicts (per-season stats).
    """
    player_info = players.find_players_by_full_name(full_name)
    if not player_info:
        raise HTTPException(status_code=404, detail=f"NBA API could not find player: {full_name}")
    
    nba_player_id = player_info[0]["id"]

    time.sleep(0.6)
    career = playercareerstats.PlayerCareerStats(player_id=nba_player_id)
    stats_df = career.get_data_frames()[0]

    return stats_df.to_dict(orient="records")

def refresh_player_videos(player_id: int, full_name: str, draft_year: int):
    """Background task to refresh YouTube videos cache."""
    upsert_cache_sql = """
        INSERT INTO player_videos_cache (player_uid, videos_json)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE videos_json = VALUES(videos_json)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Fetch the latest YouTube videos
        youtube_videos = get_nba_youtube_videos(full_name=full_name, start_year=draft_year)

        # Step 2: Save to cache safely
        cursor.execute(upsert_cache_sql, (player_id, json.dumps(youtube_videos)))
        conn.commit()

    except Exception as e:
        # Optional: log error instead of silently failing
        print(f"Error refreshing player {player_id} videos: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def get_nba_youtube_videos(
    full_name: str,
    threshold: int = 85,
    max_videos: int = 3,
    start_year: int = None,
    trusted_channels: List[str] = None
) -> List[str]:
    """
    Fetch NBA YouTube videos for a given player.
    Filters by fuzzy match on player name, upload date, and optionally channel.
    Returns at most max_videos with randomness.
    If YouTube API fails, returns [] gracefully.
    """
    youtube = set_youtube_key()

    params = dict(
        part="snippet",
        maxResults=25,
        q=f"{full_name} NBA highlights",
        type="video",
        videoDuration="medium",
        videoEmbeddable="true",
    )

    if start_year:
        params["publishedAfter"] = f"{start_year}-01-01T00:00:00Z"

    try:
        request = youtube.search().list(**params)
        response = request.execute()
    except Exception as e:
        # Gracefully handle API errors
        print(f"YouTube API error for {full_name}: {e}")
        return []

    videos_with_score = []
    trusted_channels = [c.lower() for c in trusted_channels] if trusted_channels else []

    for item in response.get("items", []):
        video_title = item["snippet"]["title"].lower()
        channel_title = item["snippet"]["channelTitle"].lower()
        published_at = item["snippet"]["publishedAt"]

        # Channel whitelist filter
        if trusted_channels and channel_title not in trusted_channels:
            continue

        # Upload date cutoff
        if start_year:
            video_year = int(published_at[:4])
            if video_year < start_year:
                continue

        # Fuzzy match
        score = fuzz.partial_ratio(full_name.lower(), video_title)
        if score >= threshold:
            video_id = item["id"]["videoId"]
            videos_with_score.append((score, f"https://www.youtube.com/watch?v={video_id}"))

    # Shuffle within score groups
    score_groups = {}
    for score, url in videos_with_score:
        score_groups.setdefault(score, []).append(url)

    selected_videos = []
    for score in sorted(score_groups.keys(), reverse=True):
        urls = score_groups[score]
        random.shuffle(urls)
        for url in urls:
            if len(selected_videos) < max_videos:
                selected_videos.append(url)
            else:
                break
        if len(selected_videos) >= max_videos:
            break

    return selected_videos