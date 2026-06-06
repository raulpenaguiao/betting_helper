"""
Unit tests covering fixture data, database CRUD, bet engine logic, and API endpoints.
"""

import pytest
import database as db
from bet_engine import _compute_points, compute_best_bets
from wc2026_data import ALL_FIXTURES, generate_group_fixtures, generate_knockout_fixtures


# ── fixture data ─────────────────────────────────────────────────────────────

class TestFixtureData:
    def test_total_fixture_count(self):
        assert len(ALL_FIXTURES) == 104  # 72 group + 32 knockout

    def test_group_fixture_count(self):
        assert len(generate_group_fixtures()) == 72

    def test_knockout_fixture_count(self):
        assert len(generate_knockout_fixtures()) == 32

    def test_match_numbers_are_unique(self):
        nums = [f["match_number"] for f in ALL_FIXTURES]
        assert len(nums) == len(set(nums))

    def test_group_a_teams(self):
        group_a = [f for f in ALL_FIXTURES if f.get("group") == "A"]
        teams = {t for f in group_a for t in (f["home"], f["away"])}
        assert teams == {"Mexico", "South Africa", "South Korea", "Czech Republic"}

    def test_group_a_dates(self):
        group_a = [f for f in ALL_FIXTURES if f.get("group") == "A"]
        dates = {f["date_utc"] for f in group_a}
        assert dates == {"2026-06-11", "2026-06-18", "2026-06-24"}

    def test_all_groups_have_six_fixtures(self):
        for letter in "ABCDEFGHIJKL":
            fixtures = [f for f in ALL_FIXTURES if f.get("group") == letter]
            assert len(fixtures) == 6, f"Group {letter} has {len(fixtures)} fixtures"

    def test_dates_are_iso_format(self):
        from datetime import date
        for f in ALL_FIXTURES:
            if f["date_utc"]:
                date.fromisoformat(f["date_utc"])  # raises if invalid

    def test_group_stage_dates_within_range(self):
        group_dates = [f["date_utc"] for f in ALL_FIXTURES if f["stage"] == "Group"]
        assert min(group_dates) >= "2026-06-11"
        assert max(group_dates) <= "2026-06-27"


# ── database ──────────────────────────────────────────────────────────────────

class TestDatabase:
    def test_init_creates_all_games(self, tmp_db):
        games = db.get_games()
        assert len(games) == 104

    def test_group_filter(self, tmp_db):
        games = db.get_games(stage="Group", group="A")
        assert len(games) == 6
        assert all(g["grp"] == "A" for g in games)

    def test_stage_filter(self, tmp_db):
        games = db.get_games(stage="Final")
        assert len(games) == 1

    def test_update_game_result(self, tmp_db):
        game = db.get_games(stage="Final")[0]
        db.update_game_result(game["id"], 2, 1)
        updated = db.get_game(game["id"])
        assert updated["home_score"] == 2
        assert updated["away_score"] == 1
        assert updated["played"] == 1

    def test_get_game_not_found(self, tmp_db):
        assert db.get_game(99999) is None

    def test_upsert_and_get_odds(self, tmp_db):
        game = db.get_games(stage="Group", group="A")[0]
        db.upsert_odd(game["id"], 1, 0, 2.5, "bet365")
        db.upsert_odd(game["id"], 0, 0, 3.2)
        odds = db.get_odds_for_game(game["id"])
        assert len(odds) == 2
        values = {(o["home_goals"], o["away_goals"]): o["odd_value"] for o in odds}
        assert values[(1, 0)] == 2.5
        assert values[(0, 0)] == 3.2

    def test_upsert_odd_overwrites(self, tmp_db):
        game = db.get_games(stage="Group", group="A")[0]
        db.upsert_odd(game["id"], 1, 0, 2.5)
        db.upsert_odd(game["id"], 1, 0, 3.0)
        odds = db.get_odds_for_game(game["id"])
        assert len(odds) == 1
        assert odds[0]["odd_value"] == 3.0

    def test_delete_odd(self, tmp_db):
        game = db.get_games(stage="Group", group="A")[0]
        db.upsert_odd(game["id"], 2, 1, 4.0)
        odd_id = db.get_odds_for_game(game["id"])[0]["id"]
        db.delete_odd(odd_id)
        assert db.get_odds_for_game(game["id"]) == []

    def test_settings_defaults(self, tmp_db):
        settings = db.get_settings()
        assert "exact_score_points" in settings
        assert settings["budget"] == 100.0

    def test_update_settings(self, tmp_db):
        db.update_settings({"budget": 200.0})
        assert db.get_settings()["budget"] == 200.0


# ── bet engine ────────────────────────────────────────────────────────────────

class TestComputePoints:
    CFG = {
        "exact_score_points": 10,
        "correct_goal_diff_points": 4,
        "correct_result_points": 2,
    }

    def test_exact_score(self):
        assert _compute_points(2, 1, 2, 1, self.CFG) == 10

    def test_correct_goal_diff(self):
        assert _compute_points(3, 1, 2, 0, self.CFG) == 4

    def test_correct_result_win(self):
        assert _compute_points(2, 1, 3, 1, self.CFG) == 2

    def test_correct_result_draw(self):
        assert _compute_points(1, 1, 0, 0, self.CFG) == 4  # correct diff (0)

    def test_wrong_prediction(self):
        assert _compute_points(2, 0, 0, 1, self.CFG) == 0

    def test_exact_draw(self):
        assert _compute_points(1, 1, 1, 1, self.CFG) == 10


class TestBestBets:
    def test_no_odds_returns_empty(self, tmp_db):
        bets = compute_best_bets()
        assert bets == []

    def test_returns_ranked_by_ev(self, tmp_db):
        game = db.get_games(stage="Group", group="A")[0]
        db.upsert_odd(game["id"], 1, 0, 2.0)
        db.upsert_odd(game["id"], 0, 1, 3.0)
        db.upsert_odd(game["id"], 0, 0, 5.0)
        bets = compute_best_bets()
        assert len(bets) > 0
        evs = [b["ev"] for b in bets]
        assert evs == sorted(evs, reverse=True)

    def test_played_games_excluded(self, tmp_db):
        game = db.get_games(stage="Group", group="A")[0]
        db.upsert_odd(game["id"], 1, 0, 2.0)
        db.update_game_result(game["id"], 1, 0)
        assert compute_best_bets() == []

    def test_top_n_limit(self, tmp_db):
        for game in db.get_games(stage="Group"):
            db.upsert_odd(game["id"], 1, 0, 2.0)
            db.upsert_odd(game["id"], 0, 1, 3.0)
        bets = compute_best_bets(top_n=5)
        assert len(bets) <= 5


# ── API endpoints ─────────────────────────────────────────────────────────────

class TestAPI:
    def test_root_returns_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_list_games(self, client):
        r = client.get("/api/games")
        assert r.status_code == 200
        assert len(r.json()) == 104

    def test_list_games_filter_group(self, client):
        r = client.get("/api/games?stage=Group&group=A")
        assert r.status_code == 200
        assert len(r.json()) == 6

    def test_get_game(self, client):
        games = client.get("/api/games").json()
        gid = games[0]["id"]
        r = client.get(f"/api/games/{gid}")
        assert r.status_code == 200
        assert r.json()["id"] == gid

    def test_get_game_not_found(self, client):
        r = client.get("/api/games/99999")
        assert r.status_code == 404

    def test_set_result(self, client):
        gid = client.get("/api/games").json()[0]["id"]
        r = client.patch(f"/api/games/{gid}/result", json={"home_score": 2, "away_score": 0})
        assert r.status_code == 200
        game = client.get(f"/api/games/{gid}").json()
        assert game["home_score"] == 2
        assert game["played"] == 1

    def test_upsert_odd_valid(self, client):
        gid = client.get("/api/games").json()[0]["id"]
        r = client.put(f"/api/games/{gid}/odds", json={"home_goals": 1, "away_goals": 0, "odd_value": 2.5})
        assert r.status_code == 200
        odds = client.get(f"/api/games/{gid}").json()["odds"]
        assert len(odds) == 1

    def test_upsert_odd_rejects_below_one(self, client):
        gid = client.get("/api/games").json()[0]["id"]
        r = client.put(f"/api/games/{gid}/odds", json={"home_goals": 1, "away_goals": 0, "odd_value": 0.5})
        assert r.status_code == 400

    def test_best_bets_empty(self, client):
        r = client.get("/api/best-bets")
        assert r.status_code == 200
        assert r.json() == []

    def test_settings_get(self, client):
        r = client.get("/api/settings")
        assert r.status_code == 200
        assert "budget" in r.json()

    def test_settings_patch(self, client):
        r = client.patch("/api/settings", json={"budget": 500.0})
        assert r.status_code == 200
        assert r.json()["budget"] == 500.0
