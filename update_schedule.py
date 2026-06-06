"""
Fetch live WC 2026 fixtures and results from Wikipedia and sync to the local DB.

Run manually:  python update_schedule.py
Run via timer: see deploy/betting-helper-update.timer

What it updates per game row:
  - home / away team names  (fills TBD slots in knockout stage as teams qualify)
  - date_utc / time_utc     (exact kick-off time once confirmed)
  - home_score / away_score / played  (once the match is finished)

Matching strategy:
  Group stage:   team-pair match {home,away} == {wiki_home,wiki_away},
                 with positional fallback for unmatched rows.
  Knockout stage: positional within each stage (Wikipedia lists them in order).
"""

import sys
import database as db
from scraper import fetch_all_group_fixtures, fetch_knockout_fixtures

KNOCKOUT_STAGE_ORDER = [
    "Round of 32",
    "Round of 16",
    "Quarterfinal",
    "Semifinal",
    "Third Place",
    "Final",
]


def _match_fixtures_to_records(wiki_fixtures, db_records):
    """
    Pair Wikipedia fixtures to DB records by team-pair, with positional fallback.
    Returns list of (db_id, wiki_fixture).
    """
    wiki_sorted = sorted(
        wiki_fixtures,
        key=lambda f: (f["date_utc"] or "", f["time_utc"] or ""),
    )
    db_remaining = list(db_records)
    pairs = []

    for wf in wiki_sorted:
        wiki_pair = {wf["home"], wf["away"]}
        matched = None
        for i, rec in enumerate(db_remaining):
            if {rec["home"], rec["away"]} == wiki_pair:
                matched = db_remaining.pop(i)
                break
        if matched is None and db_remaining:
            matched = db_remaining.pop(0)
        if matched:
            pairs.append((matched["id"], wf))

    return pairs


def _apply_fixture(conn, db_id, wf):
    """Write all scraped fields for one game into the DB."""
    played = 1 if wf.get("played") else 0
    conn.execute(
        """UPDATE games
           SET home=?, away=?, date_utc=?, time_utc=?,
               home_score=COALESCE(?, home_score),
               away_score=COALESCE(?, away_score),
               played=MAX(played, ?)
           WHERE id=?""",
        (
            wf["home"], wf["away"], wf.get("date_utc"), wf.get("time_utc"),
            wf.get("home_score"), wf.get("away_score"),
            played, db_id,
        ),
    )


def update_group_stage(conn):
    print("Fetching group stage fixtures from Wikipedia…")
    data = fetch_all_group_fixtures()

    for e in data.get("errors", []):
        print(f"  WARNING: {e}")

    total = 0
    for letter, wiki_fixtures in data["groups"].items():
        if not wiki_fixtures:
            print(f"  Group {letter}: no fixtures found, skipping")
            continue

        db_records = [
            dict(r)
            for r in conn.execute(
                "SELECT id, home, away FROM games WHERE grp=? AND stage='Group' ORDER BY match_number",
                (letter,),
            ).fetchall()
        ]

        pairs = _match_fixtures_to_records(wiki_fixtures, db_records)
        for db_id, wf in pairs:
            _apply_fixture(conn, db_id, wf)
            total += 1

        print(f"  Group {letter}: {len(pairs)}/{len(db_records)} records synced")

    print(f"Group stage done — {total} games updated.\n")


def update_knockout_stage(conn):
    print("Fetching knockout stage fixtures from Wikipedia…")
    data = fetch_knockout_fixtures()
    if data["error"]:
        print(f"  ERROR: {data['error']}")
        return

    wiki_fixtures = list(data["fixtures"])

    for stage in KNOCKOUT_STAGE_ORDER:
        db_records = [
            dict(r)
            for r in conn.execute(
                "SELECT id, home, away FROM games WHERE stage=? ORDER BY match_number",
                (stage,),
            ).fetchall()
        ]
        if not db_records:
            continue

        # Wikipedia lists knockout games in stage order; consume positionally.
        stage_wiki = wiki_fixtures[: len(db_records)]
        wiki_fixtures = wiki_fixtures[len(db_records) :]

        for db_rec, wf in zip(db_records, stage_wiki):
            _apply_fixture(conn, db_rec["id"], wf)

        print(f"  {stage}: {len(stage_wiki)}/{len(db_records)} records synced")

    print("Knockout stage done.\n")


def main():
    db.init_db()
    conn = db.get_conn()
    try:
        update_group_stage(conn)
        update_knockout_stage(conn)
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()
    print("Schedule update complete.")


if __name__ == "__main__":
    main()
