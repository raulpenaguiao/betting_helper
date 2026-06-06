import sqlite3
import json
from pathlib import Path
from wc2026_data import ALL_FIXTURES

DB_PATH = Path(__file__).parent / "betting.db"

DEFAULT_SETTINGS = {
    "exact_score_points": 10,
    "correct_goals_home_points": 3,
    "correct_goals_away_points": 3,
    "correct_goal_diff_points": 4,
    "correct_result_points": 2,
    "budget": 100.0,
    "currency": "EUR",
    "timezone": "Europe/Berlin",
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_number INTEGER UNIQUE NOT NULL,
            stage       TEXT NOT NULL,
            grp         TEXT,
            home        TEXT NOT NULL,
            away        TEXT NOT NULL,
            home_score  INTEGER,
            away_score  INTEGER,
            played      INTEGER NOT NULL DEFAULT 0,
            date_utc    TEXT,
            time_utc    TEXT
        );

        CREATE TABLE IF NOT EXISTS odds (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            home_goals  INTEGER NOT NULL,
            away_goals  INTEGER NOT NULL,
            odd_value   REAL NOT NULL,
            bookmaker   TEXT,
            updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(game_id, home_goals, away_goals)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL
        );
    """)

    for col in ("date_utc TEXT", "time_utc TEXT"):
        try:
            conn.execute(f"ALTER TABLE games ADD COLUMN {col}")
            conn.commit()
        except Exception:
            pass

    # Seed games if empty
    count = c.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    if count == 0:
        for f in ALL_FIXTURES:
            c.execute(
                "INSERT INTO games (match_number, stage, grp, home, away, date_utc) VALUES (?,?,?,?,?,?)",
                (f["match_number"], f["stage"], f.get("group"), f["home"], f["away"], f.get("date_utc")),
            )
    else:
        # Sync teams and dates from fixture data (keeps results/scores intact)
        for f in ALL_FIXTURES:
            conn.execute(
                "UPDATE games SET home=?, away=?, date_utc=? WHERE match_number=?",
                (f["home"], f["away"], f.get("date_utc"), f["match_number"]),
            )

    # Seed settings if empty
    for key, val in DEFAULT_SETTINGS.items():
        c.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, json.dumps(val)),
        )

    conn.commit()
    conn.close()


def get_settings():
    conn = get_conn()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: json.loads(r["value"]) for r in rows}


def update_settings(updates: dict):
    conn = get_conn()
    for key, val in updates.items():
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, json.dumps(val)),
        )
    conn.commit()
    conn.close()


def get_games(stage: str = None, group: str = None):
    conn = get_conn()
    sql = "SELECT * FROM games"
    params = []
    conditions = []
    if stage:
        conditions.append("stage = ?")
        params.append(stage)
    if group:
        conditions.append("grp = ?")
        params.append(group)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY match_number"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_game(game_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_game_result(game_id: int, home_score: int, away_score: int, home: str = None, away: str = None):
    conn = get_conn()
    if home and away:
        conn.execute(
            "UPDATE games SET home_score=?, away_score=?, played=1, home=?, away=? WHERE id=?",
            (home_score, away_score, home, away, game_id),
        )
    else:
        conn.execute(
            "UPDATE games SET home_score=?, away_score=?, played=1 WHERE id=?",
            (home_score, away_score, game_id),
        )
    conn.commit()
    conn.close()


def update_game_schedule(game_id: int, home: str, away: str, date_utc: str, time_utc: str):
    conn = get_conn()
    conn.execute(
        "UPDATE games SET home=?, away=?, date_utc=?, time_utc=? WHERE id=?",
        (home, away, date_utc, time_utc, game_id),
    )
    conn.commit()
    conn.close()


def update_game_teams(game_id: int, home: str, away: str):
    conn = get_conn()
    conn.execute("UPDATE games SET home=?, away=? WHERE id=?", (home, away, game_id))
    conn.commit()
    conn.close()


def upsert_odd(game_id: int, home_goals: int, away_goals: int, odd_value: float, bookmaker: str = None):
    conn = get_conn()
    conn.execute(
        """INSERT INTO odds (game_id, home_goals, away_goals, odd_value, bookmaker, updated_at)
           VALUES (?, ?, ?, ?, ?, datetime('now'))
           ON CONFLICT(game_id, home_goals, away_goals)
           DO UPDATE SET odd_value=excluded.odd_value,
                         bookmaker=excluded.bookmaker,
                         updated_at=excluded.updated_at""",
        (game_id, home_goals, away_goals, odd_value, bookmaker),
    )
    conn.commit()
    conn.close()


def delete_odd(odd_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM odds WHERE id=?", (odd_id,))
    conn.commit()
    conn.close()


def get_odds_for_game(game_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM odds WHERE game_id=? ORDER BY home_goals, away_goals",
        (game_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_odds():
    conn = get_conn()
    rows = conn.execute(
        """SELECT o.*, g.home, g.away, g.stage, g.grp, g.match_number
           FROM odds o JOIN games g ON o.game_id = g.id
           ORDER BY g.match_number, o.home_goals, o.away_goals"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
