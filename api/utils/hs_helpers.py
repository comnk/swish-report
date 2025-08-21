import re
from datetime import date, datetime
from typing import Tuple, Optional, List
from rapidfuzz import fuzz

from ..core.config import set_youtube_key

def get_youtube_videos(full_name: str, class_year: str, threshold: int = 85, max_videos: int = 3) -> List[str]:
    """
    Fetch YouTube videos for a given high school basketball player,
    filtering by fuzzy match on the player's full name, returning at most max_videos,
    prioritizing the most recent high school videos.

    Args:
        full_name (str): Player's full name.
        class_year (str): Player's graduating class year.
        threshold (int): Minimum fuzzy match score to include a video.
        max_videos (int): Maximum number of videos to return.

    Returns:
        List[str]: List of YouTube video URLs matching the player.
    """
    youtube = set_youtube_key()
    request = youtube.search().list(
        part="snippet",
        maxResults=10,  # Fetch more to filter down
        q=f"{full_name} high school basketball {class_year}",
        type="video",
        videoEmbeddable="true",
        order="date"  # Sorts by newest first
    )
    response = request.execute()
    videos_with_score = []

    for item in response.get("items", []):
        video_title = item["snippet"]["title"]
        score = fuzz.partial_ratio(full_name.lower(), video_title.lower())
        if score >= threshold:
            video_id = item["id"]["videoId"]
            published_at = item["snippet"]["publishedAt"]
            # Convert publishedAt to datetime for sorting if needed
            published_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            videos_with_score.append((score, published_dt, f"https://www.youtube.com/watch?v={video_id}"))

    # Sort primarily by fuzzy match score, secondarily by most recent date
    videos_with_score.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [url for _, _, url in videos_with_score[:max_videos]]

def parse_school(source: str,
                high_school_raw: str = "",
                hometown_raw: str = "") -> Tuple[str, Optional[str], Optional[str]]:
    """
    Normalize school info into (school_name, city, state).

    Parameters:
        source: 'espn', '247sports', or 'rivals'
        high_school_raw:
            - ESPN: the whole raw text (contains city/state and school separated by newline)
            - 247Sports: the whole raw text (School (City, ST))
            - Rivals: the text inside <a> for High School
        hometown_raw:
            - Only used for Rivals: the text inside the Hometown <dd>

    Returns:
        (school_name, city, state)
    """

    if source == "espn":
        parts = high_school_raw.strip().split("\n")
        if len(parts) == 2:
            city_state = parts[0].strip()
            school_name = parts[1].strip()
            if "," in city_state:
                city, state = [p.strip() for p in city_state.split(",", 1)]
            else:
                city, state = city_state, None
            return (school_name, city, state)
        else:
            return (high_school_raw.strip(), None, None)

    elif source == "247sports":
        match = re.match(r"^(.*?)\s*\((.*?),\s*(.*?)\)$", high_school_raw.strip())
        if match:
            school_name = match.group(1).strip()
            city = match.group(2).strip()
            state = match.group(3).strip()
            return (school_name, city, state)
        else:
            return (high_school_raw.strip(), None, None)

    elif source == "rivals":
        school_name = high_school_raw.strip()

        hometown_raw = hometown_raw.strip()
        hometown_raw = hometown_raw.replace("(", "").replace(")", "").replace('"', '').strip()
        if "," in hometown_raw:
            city, state = [p.strip() for p in hometown_raw.split(",", 1)]
        else:
            city, state = hometown_raw, None

        return (school_name, city, state)

    else:
        return (high_school_raw.strip(), None, None)

def parse_247_metrics(metrics: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a 247Sports metrics string like '6-10 / 220' into (height, weight).
    Matches ESPN structure where height and weight are separate.
    """
    if not metrics:
        return (None, None)

    metrics = metrics.strip()
    # Expected format: HEIGHT / WEIGHT
    if "/" in metrics:
        parts = metrics.split("/")
        height = parts[0].strip()        # '6-10'
        weight = parts[1].strip()        # '220'
        return (height, weight)
    else:
        # If format is unexpected, treat entire string as height
        return (metrics, None)

def normalize_espn_height(raw_height: str) -> str:
    if not raw_height:
        return ""
    h = raw_height.strip()
    # normalize curly quotes/backticks
    h = h.replace("’", "'").replace("‘", "'").replace("`", "'")
    # replace all single quotes with dash
    h = h.replace("'", "-")
    # remove any double quotes
    h = h.replace('"', "")
    # collapse multiple consecutive dashes
    while "--" in h:
        h = h.replace("--", "-")
    # strip trailing dashes just in case
    h = h.rstrip("-")
    return h

def get_espn_star_count(class_str: str) -> int:
    WORD_TO_NUM = {
        "one":   1,
        "two":   2,
        "three": 3,
        "four":  4,
        "five":  5,
    }
    """
    Given a class attribute like "star five-star", returns 5.
    """
    # find any token ending with "-star"
    m = re.search(r"\b([a-z]+)-star\b", class_str)
    if not m:
        return 0   # or None, if you prefer
    word = m.group(1).lower()
    return WORD_TO_NUM.get(word, 0)

FINALIZATION_MONTH = 5
FINALIZATION_DAY = 7

def is_rankings_finalized(class_year: int) -> bool:
    today = datetime.today().date()

    if class_year < today.year:
        return True

    if class_year == today.year:
        cutoff = date(today.year, FINALIZATION_MONTH, FINALIZATION_DAY)
        return today >= cutoff

    return False

def get_rivals_star_count():
    pass

def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    # remove jr, sr, ii, iii
    name = re.sub(r'\b(jr|sr|ii|iii)\b', '', name)
    # remove punctuation
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def find_matching_player(existing_players_by_year, class_year, candidate_name, threshold=83):
    """
    existing_players_by_year: dict[class_year] = list of (player_uid, full_name)
    Returns player_uid if a sufficiently similar player exists, else None.
    """
    norm_candidate = normalize_name(candidate_name)
    best_match = None
    best_score = 0

    for player_uid, full_name in existing_players_by_year.get(class_year, []):
        score = fuzz.token_set_ratio(norm_candidate, normalize_name(full_name))
        if score > best_score and score >= threshold:
            best_score = score
            best_match = player_uid

    return best_match

def clean_player_rank(rank):
    try:
        if rank is None:
            return None
        if isinstance(rank, int):
            return rank

        rank_int = int(str(rank).strip())
        return rank_int
    except (ValueError, TypeError):
        return None