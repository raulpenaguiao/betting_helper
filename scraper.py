"""
Scrape live World Cup 2026 results and schedule from Wikipedia.
"""

import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
WIKIPEDIA_GROUP_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_{}"
WIKIPEDIA_KNOCKOUT_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage"

GROUP_LETTERS = list("ABCDEFGHIJKL")

# Venue name fragment → UTC offset (hours). Used when Wikipedia omits the offset.
# All offsets are for the tournament period (June–July 2026, summer DST in effect).
VENUE_OFFSET = {
    # Mexico (no DST since 2023)
    "Estadio Azteca": -6, "Estadio Akron": -6, "Estadio BBVA": -6,
    # US Eastern (EDT = UTC-4)
    "MetLife": -4, "Gillette": -4, "Lincoln Financial": -4,
    "Hard Rock": -4, "Mercedes-Benz": -4,
    # US Central (CDT = UTC-5)
    "AT&T": -5, "Arrowhead": -5, "NRG": -5,
    # US Pacific (PDT = UTC-7)
    "Levi": -7, "SoFi": -7, "Lumen": -7,
    # Canada
    "BMO Field": -4,   # Toronto (EDT)
    "BC Place": -7,    # Vancouver (PDT)
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BettingHelper/1.0; +https://github.com/user/betting_helper)"
    )
}


def _parse_datetime_utc(date_iso: str, time_raw: str, fallback_offset: int = None):
    """
    Convert local date + '1:00\xa0p.m. UTC−6' into (utc_date, utc_time).
    Handles midnight rollover (e.g. 8pm UTC-6 = 02:00 UTC next day).
    If the UTC offset is absent from time_raw, uses fallback_offset when provided.
    Returns (date_iso, None) if time is unparseable.
    """
    text = time_raw.replace("\xa0", " ").replace("−", "-")
    m = re.match(r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)\s*UTC([+-]?\d+)", text, re.I)
    if not m:
        # Try without UTC offset — requires fallback
        m2 = re.match(r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)", text, re.I)
        if not m2 or fallback_offset is None:
            return date_iso, None
        hour, minute = int(m2.group(1)), int(m2.group(2))
        ampm = m2.group(3).lower()
        offset = fallback_offset
    else:
        hour, minute = int(m.group(1)), int(m.group(2))
        ampm = m.group(3).lower()
        offset = int(m.group(4))
    if ampm == "p.m." and hour != 12:
        hour += 12
    elif ampm == "a.m." and hour == 12:
        hour = 0
    local_dt = datetime.strptime(date_iso, "%Y-%m-%d").replace(hour=hour, minute=minute)
    utc_dt = local_dt - timedelta(hours=offset)
    return utc_dt.strftime("%Y-%m-%d"), utc_dt.strftime("%H:%M")


def _extract_team_name(th):
    """Extract plain team name from a fhome/faway <th> element."""
    if not th:
        return None
    span = th.find("span", itemprop="name")
    if span:
        a = span.find("a")
        if a:
            return a.get_text(strip=True)
        # strip flag icons and return remaining text
        for icon in span.find_all("span", class_=lambda c: c and "flagicon" in c):
            icon.decompose()
        return span.get_text(strip=True) or None
    a = th.find("a")
    return a.get_text(strip=True) if a else th.get_text(strip=True) or None


def _parse_footballboxes(soup):
    """Return list of fixture dicts from all footballbox divs in a parsed page."""
    fixtures = []
    for box in soup.find_all("div", class_="footballbox"):
        iso_span = box.find("span", class_="bday")
        local_date = iso_span.get_text(strip=True) if iso_span else None

        fright_div = box.find("div", class_="fright")
        venue_text = fright_div.get_text(strip=True) if fright_div else ""
        fallback_offset = next(
            (off for fragment, off in VENUE_OFFSET.items() if fragment in venue_text),
            None,
        )

        ftime_div = box.find("div", class_="ftime")
        if ftime_div and local_date:
            date_utc, time_utc = _parse_datetime_utc(
                local_date, ftime_div.get_text(separator=" ", strip=True), fallback_offset
            )
        else:
            date_utc, time_utc = local_date, None

        home = _extract_team_name(box.find("th", class_="fhome"))
        away = _extract_team_name(box.find("th", class_="faway"))

        fhgoal = box.find("td", class_="fhgoal")
        fagoal = box.find("td", class_="fagoal")
        home_score_txt = fhgoal.get_text(strip=True) if fhgoal else ""
        away_score_txt = fagoal.get_text(strip=True) if fagoal else ""
        home_score = int(home_score_txt) if home_score_txt.isdigit() else None
        away_score = int(away_score_txt) if away_score_txt.isdigit() else None

        if home and away and date_utc:
            fixtures.append({
                "home": home,
                "away": away,
                "date_utc": date_utc,
                "time_utc": time_utc,
                "home_score": home_score,
                "away_score": away_score,
                "played": home_score is not None and away_score is not None,
            })
    return fixtures


def fetch_group_fixtures(group_letter: str):
    """Fetch and parse fixtures for one group. Returns list of fixture dicts."""
    url = WIKIPEDIA_GROUP_URL.format(group_letter)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e), "fixtures": []}
    soup = BeautifulSoup(resp.text, "html.parser")
    return {"error": None, "fixtures": _parse_footballboxes(soup)}


def fetch_all_group_fixtures():
    """Fetch all 12 group pages. Returns {group_letter: [fixture, ...], errors: [...]}."""
    result = {}
    errors = []
    for letter in GROUP_LETTERS:
        data = fetch_group_fixtures(letter)
        if data["error"]:
            errors.append(f"Group {letter}: {data['error']}")
        else:
            result[letter] = data["fixtures"]
    return {"groups": result, "errors": errors}


def fetch_knockout_fixtures():
    """Fetch and parse knockout stage fixtures."""
    try:
        resp = requests.get(WIKIPEDIA_KNOCKOUT_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e), "fixtures": []}
    soup = BeautifulSoup(resp.text, "html.parser")
    return {"error": None, "fixtures": _parse_footballboxes(soup)}


def _parse_score(text: str):
    """Return (home, away) int goals or (None, None)."""
    m = re.search(r"(\d+)\s*[–\-]\s*(\d+)", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def fetch_results():
    """
    Fetch current results from Wikipedia.
    Returns list of dicts with keys: home, away, home_score, away_score, stage, group.
    Only returns games that have been played (score present).
    """
    try:
        resp = requests.get(WIKIPEDIA_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e), "results": []}

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Wikipedia match tables use class "wikitable" inside section headings.
    # Each played match row typically has team names and a score cell.
    tables = soup.find_all("table", class_=lambda c: c and "wikitable" in c)

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            texts = [c.get_text(strip=True) for c in cells]
            # Look for rows that contain a score pattern between two team names
            row_text = " ".join(texts)
            h, a = _parse_score(row_text)
            if h is None:
                continue
            # Try to extract team names — heuristic: first and last non-empty text cells
            non_empty = [t for t in texts if t and not re.match(r"^\d+[–\-]\d+$", t)]
            if len(non_empty) >= 2:
                results.append({
                    "home": non_empty[0],
                    "away": non_empty[-1],
                    "home_score": h,
                    "away_score": a,
                })

    return {"error": None, "results": results}


def fetch_results_mock():
    """Return a small mock result set for testing without network."""
    return {
        "error": None,
        "results": [
            {"home": "USA", "away": "Mexico", "home_score": 2, "away_score": 1},
            {"home": "Canada", "away": "New Zealand", "home_score": 3, "away_score": 0},
        ],
    }
