"""
Scrape live World Cup 2026 results from Wikipedia.
Returns a list of result dicts: {match_number, home, away, home_score, away_score}
"""

import re
import requests
from bs4 import BeautifulSoup

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BettingHelper/1.0; +https://github.com/user/betting_helper)"
    )
}


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
