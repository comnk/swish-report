import re
from typing import Tuple, Optional
from rapidfuzz import fuzz

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