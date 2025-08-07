import re
from datetime import date, datetime
from typing import Tuple, Optional
from rapidfuzz import fuzz

from playwright.async_api import async_playwright

async def launch_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    return playwright, browser

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

def find_matching_player(cursor, class_year, candidate_name, threshold=83):
    """
    Returns player_uid if a sufficiently similar player exists, else None.
    """
    cursor.execute("SELECT player_uid, full_name FROM players WHERE class_year=%s", (class_year,))
    existing = cursor.fetchall()

    norm_candidate = normalize_name(candidate_name)
    best_match = None
    best_score = 0

    for player_uid, full_name in existing:
        score = fuzz.ratio(norm_candidate, normalize_name(full_name))
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