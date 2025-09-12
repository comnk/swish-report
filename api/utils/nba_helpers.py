import random, json, math

from typing import List
from rapidfuzz import fuzz

from core.config import set_youtube_key
from core.db import get_db_connection
from utils.helpers import calculate_advanced_stats

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats


def fetch_nba_player_stats(full_name: str, is_active: bool = True):
    """Fetch season-by-season stats for a player by full_name, prioritizing active status."""
    try:
        all_players = players.get_players()
        matches = [p for p in all_players if p['full_name'] == full_name]

        if not matches:
            return None

        # Prioritize active players
        if is_active:
            active_matches = [p for p in matches if p.get('is_active')]
            player = active_matches[0] if active_matches else matches[0]
        else:
            player = matches[0]

        nba_id = player['id']

        career = playercareerstats.PlayerCareerStats(player_id=nba_id)
        df = career.get_data_frames()[0]
        if df.empty:
            return None

        season_stats = []
        for _, row in df.iterrows():
            if row["TEAM_ABBREVIATION"] == "TOT" or row["GP"] == 0:
                continue

            def safe_div(numerator, denominator):
                if denominator == 0 or numerator is None or (isinstance(numerator, float) and math.isnan(numerator)):
                    return 0
                return round(numerator / denominator, 1)

            GP = int(row["GP"])
            PPG = safe_div(row["PTS"], GP)
            RPG = safe_div(row["REB"], GP)
            APG = safe_div(row["AST"], GP)
            SPG = safe_div(row["STL"], GP)
            BPG = safe_div(row["BLK"], GP)
            TOPG = safe_div(row["TOV"], GP)
            FPG = safe_div(row["PF"], GP)

            raw_stats = {
                "PTS": row.get("PTS", 0),
                "FGA": row.get("FGA", 0),
                "FGM": row.get("FGM", 0),
                "3PA": row.get("FG3A", 0),
                "3PM": row.get("FG3M", 0),
                "FTA": row.get("FTA", 0),
                "FTM": row.get("FTM", 0),
            }

            advanced = calculate_advanced_stats(GP, raw_stats)
            for k, v in advanced.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    advanced[k] = 0

            season_stats.append({
                "Season": row["SEASON_ID"],
                "Team": row["TEAM_ABBREVIATION"],
                "GP": GP,
                "PPG": PPG,
                "RPG": RPG,
                "APG": APG,
                "SPG": SPG,
                "BPG": BPG,
                "TOPG": TOPG,
                "FPG": FPG,
                **advanced
            })

        return season_stats if season_stats else None

    except Exception as e:
        print(f"Error fetching NBA stats for {full_name}: {e}")
        return None
    

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

# HELPERS

def handle_name(full_name: str):
    if (full_name == "Ron Holland"):
        full_name = "Ronald Holland"
    elif (full_name == "Brandon Boston Jr."):
        full_name = full_name.replace(" Jr.", "")
    
    return full_name