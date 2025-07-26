import re
from typing import Tuple, Optional

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