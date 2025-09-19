import re
import random
import isodate

from datetime import date, datetime
from typing import Tuple, Optional, List
from rapidfuzz import fuzz

from core.config import set_youtube_key

def high_school_highlights(
    full_name: str, 
    class_year: str, 
    threshold: int = 85, 
    max_videos: int = 3, 
    max_duration_minutes: int = 10
) -> List[str]:
    """
    Fetch YouTube videos likely to be highlight clips for a given HS basketball player.
    Filters by fuzzy match on player name, title keywords, and duration.
    """
    youtube = set_youtube_key()
    request = youtube.search().list(
        part="snippet",
        maxResults=20,  # fetch more results to increase filtering options
        q=f"{full_name} high school basketball {class_year}",
        type="video",
        videoEmbeddable="true",
    )
    response = request.execute()
    videos_with_score = []

    # Step 1: Filter by fuzzy match on player name + title keywords
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        title_lower = title.lower()
        score = fuzz.partial_ratio(full_name.lower(), title_lower)

        # Only accept videos likely to be highlights
        keywords = ["highlight", "hs", "basketball", "top plays", "top shots", "mix"]
        if score >= threshold and any(k in title_lower for k in keywords):
            videos_with_score.append((score, video_id, title))

    if not videos_with_score:
        return []

    # Step 2: Filter by video duration
    video_ids = [v[1] for v in videos_with_score]
    video_request = youtube.videos().list(
        part="contentDetails",
        id=",".join(video_ids)
    )
    video_response = video_request.execute()

    duration_map = {}
    for v in video_response.get("items", []):
        duration_iso = v["contentDetails"]["duration"]
        duration_min = isodate.parse_duration(duration_iso).total_seconds() / 60
        duration_map[v["id"]] = duration_min

    filtered_videos = [
        (score, vid_id)
        for score, vid_id, _ in videos_with_score
        if 0 < duration_map.get(vid_id, 0) <= max_duration_minutes
    ]

    if not filtered_videos:
        return []

    # Step 3: Sort by score and shuffle same-score videos
    score_groups = {}
    for score, vid_id in filtered_videos:
        score_groups.setdefault(score, []).append(f"https://www.youtube.com/watch?v={vid_id}")

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

def get_youtube_videos(full_name: str, class_year: str, threshold: int = 85, max_videos: int = 3) -> List[str]:
    """
    Fetch YouTube videos for a given high school basketball player,
    filtering by fuzzy match on the player's full name, returning at most max_videos.
    Adds randomness to avoid always selecting the same top videos.
    """
    youtube = set_youtube_key()
    request = youtube.search().list(
        part="snippet",
        maxResults=15,  # fetch a few more to increase variety
        q=f"{full_name} high school basketball {class_year}",
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

def parse_espn_bio(bio_text: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Parse bio string like '6-0, 165 | Class of 2025' into (height, weight, class_year).
    - height as original string (e.g. '6-0')
    - weight as int (165)
    - class_year as int (2025)
    """
    bio_text = bio_text.strip()

    # match height and weight
    hw_match = re.search(r"(\d+-\d+),\s*(\d+)", bio_text)
    height = hw_match.group(1) if hw_match else None
    weight = int(hw_match.group(2)) if hw_match else None

    # match class year
    year_match = re.search(r"Class of (\d{4})", bio_text, flags=re.I)
    class_year = int(year_match.group(1)) if year_match else None

    return height, weight, class_year

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

def parse_city_state(text: str):
    """
    Convert 'Los Angeles, Calif.' -> ('Los Angeles', 'CA')
    """
    text = text.strip()
    if "," not in text:
        return text, None

    city, state_raw = [t.strip() for t in text.split(",", 1)]

    STATE_MAP = {
        "Calif.": "CA",
        "Fla.": "FL",
        "Tex.": "TX",
        "Ga.": "GA",
        "N.Y.": "NY",
        "Ill.": "IL",
        "Ohio": "OH",
        "Nev.": "NV",
        "Wash.": "WA",
        "Ore.": "OR",
        "Ariz.": "AZ",
        "Mass.": "MA",
        "Pa.": "PA",
        "Mich.": "MI",
        "N.C.": "NC",
        "S.C.": "SC",
        # add more as needed
    }

    state = STATE_MAP.get(state_raw, state_raw)  # fallback to raw if not in map
    return city, state

def parse_rivals_high_school(high_school_raw: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse a Rivals high school string into (school_name, city, state).
    
    Example:
        'William Penn Charter (Malvern, PA)' -> 
        ('William Penn Charter', 'Malvern', 'PA')
    """
    high_school_raw = high_school_raw.strip()
    
    # Match "School Name (City, State)"
    match = re.match(r"^(.*?)\s*\((.*?),\s*(.*?)\)$", high_school_raw)
    if match:
        school_name = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3).strip()
        return school_name, city, state
    else:
        # fallback if format doesn't match
        return high_school_raw, None, None

def normalize_position(pos: str) -> str:
    """
    Convert position names to standard abbreviations.
    """
    pos = pos.strip().lower()
    mapping = {
        "point guard": "PG",
        "shooting guard": "SG",
        "small forward": "SF",
        "power forward": "PF",
        "center": "C",
    }
    return mapping.get(pos, pos.upper())  # fallback to uppercase