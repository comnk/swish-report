import re
import random
import isodate

from datetime import date, datetime
from typing import Tuple, Optional, List
from rapidfuzz import fuzz

from core.config import set_youtube_key

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
    name = name.lower().strip()
    name = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', name)
    name = re.sub(r'\b([a-z])\.([a-z])\b', r'\1 \2', name)
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def initials_from_name(name: str) -> str:
    tokens = name.split()
    return "".join(t[0] for t in tokens) if tokens else ""

def find_matching_player(existing_players_by_year, class_year, candidate_name, threshold=83):
    # HARD-CODED SPECIAL CASE
    if candidate_name.strip().lower() in ["cornelius ingram jr.", "cj ingram"] or candidate_name.strip().lower() in ["johnuel fland", "boogie fland"]:
        for player_uid, full_name in existing_players_by_year.get(class_year, []):
            if full_name.strip().lower() in ["cornelius ingram jr.", "cj ingram"]:
                return player_uid
            if full_name.strip().lower() in ["johnuel fland", "boogie fland"]:
                return player_uid
        return None

    # normalize candidate
    norm_candidate = normalize_name(candidate_name)
    c_tokens = norm_candidate.split()
    if not c_tokens:
        return None

    candidate_first = c_tokens[0]
    candidate_last = c_tokens[-1] if len(c_tokens) > 1 else ""
    candidate_initials = initials_from_name(norm_candidate)

    best_match = None
    best_score = 0

    for player_uid, full_name in existing_players_by_year.get(class_year, []):
        norm_full = normalize_name(full_name)
        f_tokens = norm_full.split()
        if not f_tokens:
            continue

        full_first = f_tokens[0]
        full_last = f_tokens[-1] if len(f_tokens) > 1 else ""
        full_initials = initials_from_name(norm_full)

        # Compute separate fuzzy ratios
        first_score = fuzz.partial_ratio(candidate_first, full_first)    # 0-100
        last_score = fuzz.ratio(candidate_last, full_last)               # 0-100

        # Combine scores: first name = 0.6, last name = 0.35, initials = 5
        initials_score = 5 if candidate_initials == full_initials else 0
        total_score = int(first_score * 0.6 + last_score * 0.35) + initials_score

        if total_score > best_score and total_score >= threshold:
            best_score = total_score
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