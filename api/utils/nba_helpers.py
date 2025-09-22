import random, json, math

from typing import List
from rapidfuzz import fuzz

from core.config import set_youtube_key
from core.db import get_db_connection
from utils.helpers import calculate_advanced_stats

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats


def fetch_nba_player_stats(full_name: str, is_active: bool = True, player_uid: int = None):
    """Fetch season stats from NBA API and return with frontend-friendly keys."""
    try:
        all_players = players.get_players()
        matches = [p for p in all_players if p['full_name'] == full_name]
        if not matches:
            return None

        player = None
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

            GP = int(row["GP"])
            safe_div = lambda num: round(num / GP, 2) if GP > 0 else 0.0

            raw_stats = {
                "PTS": row.get("PTS", 0),
                "FGA": row.get("FGA", 0),
                "FGM": row.get("FGM", 0),
                "3PA": row.get("FG3A", 0),
                "3PM": row.get("FG3M", 0),
                "FTA": row.get("FTA", 0),
                "FTM": row.get("FTM", 0),
            }

            advanced = calculate_advanced_stats(raw_stats)

            season_entry = {
                "Season": row["SEASON_ID"],
                "Team": row["TEAM_ABBREVIATION"],
                "GP": GP,
                "PPG": safe_div(row.get("PTS", 0)),
                "RPG": safe_div(row.get("REB", 0)),
                "APG": safe_div(row.get("AST", 0)),
                "SPG": safe_div(row.get("STL", 0)),
                "BPG": safe_div(row.get("BLK", 0)),
                "TOPG": safe_div(row.get("TOV", 0)),
                "FPG": safe_div(row.get("PF", 0)),
                "PTS": raw_stats["PTS"],
                "FGA": raw_stats["FGA"],
                "FGM": raw_stats["FGM"],
                "3PA": raw_stats["3PA"],
                "3PM": raw_stats["3PM"],
                "FTA": raw_stats["FTA"],
                "FTM": raw_stats["FTM"],
                "TS": advanced["ts_pct"],
                "FG": advanced["fg"],
                "eFG": advanced["efg"],
                "3P": advanced["three_p"],
                "FT": advanced["ft"],
            }

            # Replace NaN/Inf with 0
            for k, v in season_entry.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    season_entry[k] = 0.0

            season_stats.append(season_entry)

        return season_stats if season_stats else None

    except Exception as e:
        print(f"Error fetching NBA stats for {full_name}: {e}")
        return None


def normalize_season(season: dict) -> dict:
    """Ensure consistent lowercase keys across DB and API rows."""
    return {
        "season": season.get("Season") or season.get("season") or "",
        "team": season.get("Team") or season.get("team") or "",
        "gp": season.get("GP") or season.get("gp") or 0,
        "ppg": season.get("PPG") or season.get("ppg") or 0,
        "apg": season.get("APG") or season.get("apg") or 0,
        "rpg": season.get("RPG") or season.get("rpg") or 0,
        "spg": season.get("SPG") or season.get("spg") or 0,
        "bpg": season.get("BPG") or season.get("bpg") or 0,
        "topg": season.get("TOPG") or season.get("topg") or 0,
        "fpg": season.get("FPG") or season.get("fpg") or 0,
        "pts": season.get("PTS") or season.get("pts") or 0,
        "fga": season.get("FGA") or season.get("fga") or 0,
        "fgm": season.get("FGM") or season.get("fgm") or 0,
        "three_pa": season.get("3PA") or season.get("three_pa") or 0,
        "three_pm": season.get("3PM") or season.get("three_pm") or 0,
        "fta": season.get("FTA") or season.get("fta") or 0,
        "ftm": season.get("FTM") or season.get("ftm") or 0,
        "ts_pct": season.get("TS") or season.get("ts_pct") or 0,
        "fg": season.get("FG") or season.get("fg") or 0,
        "efg": season.get("eFG") or season.get("efg") or 0,
        "three_p": season.get("3P") or season.get("three_p") or 0,
        "ft": season.get("FT") or season.get("ft") or 0,
    }
    

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
        full_name = "Ronald Holland II"
    elif (full_name == "Brandon Boston Jr."):
        full_name = full_name.replace(" Jr.", "")
    elif (full_name == "Nikola Jokic"):
        full_name = full_name.replace("Jokic", "Jokić")
    return full_name