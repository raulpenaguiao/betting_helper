"""
Fetch the real WC 2026 fixture schedule from Wikipedia and update the local DB.

Idempotency:
  - Group stage: for each group, match Wikipedia fixtures to DB records by team-pair
    (either order). On first run with placeholder teams, falls back to positional
    mapping (Wikipedia chronological order → DB match_number order). Subsequent
    runs find exact team-pair matches and overwrite with the same data.
  - Knockout stage: matched purely by positional order within each stage, since
    teams are TBD on Wikipedia too.

Run:
    python update_schedule.py
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
    Return list of (db_id, wiki_fixture) pairs.

    Strategy: for each Wikipedia fixture (sorted chrono), try to find a DB record
    whose {home, away} set matches the Wikipedia {home, away} set.  If no exact
    match is found, take the next unmatched DB record in match_number order
    (positional fallback for the first run when DB has placeholder teams).
    """
    wiki_sorted = sorted(
        wiki_fixtures,
        key=lambda f: (f["date_utc"] or "", f["time_utc"] or ""),
    )
    db_remaining = list(db_records)  # already ordered by match_number
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


def update_group_stage():
    conn = db.get_conn()
    print("Fetching group stage fixtures from Wikipedia…")
    data = fetch_all_group_fixtures()

    if data["errors"]:
        for e in data["errors"]:
            print(f"  WARNING: {e}")

    total_updated = 0
    for letter, wiki_fixtures in data["groups"].items():
        if not wiki_fixtures:
            print(f"  Group {letter}: no fixtures found, skipping")
            continue

        db_records = conn.execute(
            "SELECT id, home, away FROM games WHERE grp=? AND stage='Group' ORDER BY match_number",
            (letter,),
        ).fetchall()
        db_records = [dict(r) for r in db_records]

        pairs = _match_fixtures_to_records(wiki_fixtures, db_records)

        for db_id, wf in pairs:
            conn.execute(
                "UPDATE games SET home=?, away=?, date_utc=?, time_utc=? WHERE id=?",
                (wf["home"], wf["away"], wf["date_utc"], wf["time_utc"], db_id),
            )
            total_updated += 1

        print(f"  Group {letter}: {len(pairs)}/{len(db_records)} records updated")

    conn.commit()
    conn.close()
    print(f"Group stage done — {total_updated} games updated.\n")


def update_knockout_stage():
    print("Fetching knockout stage fixtures from Wikipedia…")
    data = fetch_knockout_fixtures()
    if data["error"]:
        print(f"  ERROR: {data['error']}")
        return

    wiki_fixtures = data["fixtures"]
    conn = db.get_conn()

    # Group wiki fixtures by stage (in Wikipedia order)
    wiki_by_stage = {}
    for wf in wiki_fixtures:
        # We don't scrape stage from the knockout page directly; infer from count
        pass

    # Simpler: just match positionally within each stage using DB order
    for stage in KNOCKOUT_STAGE_ORDER:
        db_records = conn.execute(
            "SELECT id, home, away FROM games WHERE stage=? ORDER BY match_number",
            (stage,),
        ).fetchall()
        db_records = [dict(r) for r in db_records]
        if not db_records:
            continue

        # Pull next len(db_records) fixtures from wiki_fixtures
        stage_wiki = wiki_fixtures[: len(db_records)]
        wiki_fixtures = wiki_fixtures[len(db_records) :]

        for db_rec, wf in zip(db_records, stage_wiki):
            conn.execute(
                "UPDATE games SET home=?, away=?, date_utc=?, time_utc=? WHERE id=?",
                (wf["home"], wf["away"], wf["date_utc"], wf["time_utc"], db_rec["id"]),
            )
        print(f"  {stage}: {len(stage_wiki)}/{len(db_records)} records updated")

    conn.commit()
    conn.close()
    print("Knockout stage done.\n")


def main():
    db.init_db()
    update_group_stage()
    update_knockout_stage()
    print("Schedule update complete.")


if __name__ == "__main__":
    main()
