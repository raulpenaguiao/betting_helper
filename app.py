from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import pathlib
import anthropic

import database as db
from bet_engine import compute_best_bets
from scraper import fetch_results, fetch_results_mock

app = FastAPI(title="WC 2026 Betting Helper")

BASE = pathlib.Path(__file__).parent
STATIC = BASE / "static"


# ── startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    db.init_db()


# ── static files ──────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
def root():
    return FileResponse(str(STATIC / "index.html"))


# ── games ─────────────────────────────────────────────────────────────────────

@app.get("/api/games")
def list_games(stage: Optional[str] = None, group: Optional[str] = None):
    games = db.get_games(stage=stage, group=group)
    for g in games:
        g["odds"] = db.get_odds_for_game(g["id"])
    return games


@app.get("/api/games/{game_id}")
def get_game(game_id: int):
    g = db.get_game(game_id)
    if not g:
        raise HTTPException(404, "Game not found")
    g["odds"] = db.get_odds_for_game(game_id)
    return g


class ResultBody(BaseModel):
    home_score: int
    away_score: int
    home: Optional[str] = None
    away: Optional[str] = None


@app.patch("/api/games/{game_id}/result")
def set_result(game_id: int, body: ResultBody):
    g = db.get_game(game_id)
    if not g:
        raise HTTPException(404, "Game not found")
    db.update_game_result(game_id, body.home_score, body.away_score, body.home, body.away)
    return {"ok": True}


class TeamsBody(BaseModel):
    home: str
    away: str


@app.patch("/api/games/{game_id}/teams")
def set_teams(game_id: int, body: TeamsBody):
    g = db.get_game(game_id)
    if not g:
        raise HTTPException(404, "Game not found")
    db.update_game_teams(game_id, body.home, body.away)
    return {"ok": True}


# ── odds ──────────────────────────────────────────────────────────────────────

class OddBody(BaseModel):
    home_goals: int
    away_goals: int
    odd_value: float
    bookmaker: Optional[str] = None


@app.put("/api/games/{game_id}/odds")
def upsert_odd(game_id: int, body: OddBody):
    if not db.get_game(game_id):
        raise HTTPException(404, "Game not found")
    if body.odd_value < 1.0:
        raise HTTPException(400, "Odd must be >= 1.0")
    db.upsert_odd(game_id, body.home_goals, body.away_goals, body.odd_value, body.bookmaker)
    return {"ok": True}


@app.delete("/api/odds/{odd_id}")
def remove_odd(odd_id: int):
    db.delete_odd(odd_id)
    return {"ok": True}


# ── best bets ─────────────────────────────────────────────────────────────────

@app.get("/api/best-bets")
def best_bets(top_n: int = 20):
    return compute_best_bets(top_n=top_n)


# ── settings ──────────────────────────────────────────────────────────────────

@app.get("/api/settings")
def get_settings():
    return db.get_settings()


@app.patch("/api/settings")
def patch_settings(updates: dict):
    db.update_settings(updates)
    return db.get_settings()


# ── image parse ───────────────────────────────────────────────────────────────

class ImageBody(BaseModel):
    image_data: str  # base64-encoded
    media_type: str  # e.g. "image/jpeg"

@app.post("/api/parse-image")
def parse_image_endpoint(body: ImageBody):
    settings = db.get_settings()
    api_key = settings.get("anthropic_api_key") or None
    try:
        client = anthropic.Anthropic(**({ "api_key": api_key } if api_key else {}))
    except Exception as e:
        raise HTTPException(500, f"Anthropic client error: {e}")
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": body.media_type,
                            "data": body.image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "This image contains a table of betting odds for football final scores. "
                            "Each entry pairs a fractional odd (format X/Y, where X and Y are integers) "
                            "with a scoreline (format X-Y, where X and Y are integers). "
                            "Extract every such pair faithfully. "
                            "Output one pair per line in the format: X/Y X-Y (odds first, then score). "
                            "Output only the pairs, no other text."
                        ),
                    },
                ],
            }],
        )
        return {"text": message.content[0].text}
    except Exception as e:
        raise HTTPException(502, f"Claude API error: {e}")


# ── scraper / update ──────────────────────────────────────────────────────────

@app.post("/api/update-results")
def update_results(mock: bool = False):
    """Fetch results from Wikipedia and apply matches where team names match."""
    data = fetch_results_mock() if mock else fetch_results()
    if data["error"]:
        raise HTTPException(502, f"Scrape error: {data['error']}")

    applied = []
    skipped = []
    games = db.get_games()

    for result in data["results"]:
        r_home = result["home"].strip().lower()
        r_away = result["away"].strip().lower()
        matched = None
        for g in games:
            if g["home"].strip().lower() == r_home and g["away"].strip().lower() == r_away:
                matched = g
                break
        if matched:
            db.update_game_result(
                matched["id"],
                result["home_score"],
                result["away_score"],
            )
            applied.append(f"{result['home']} {result['home_score']}-{result['away_score']} {result['away']}")
        else:
            skipped.append(f"{result['home']} vs {result['away']}")

    return {"applied": applied, "skipped": skipped, "raw_count": len(data["results"])}
