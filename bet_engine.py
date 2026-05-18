"""
Best-bet computation engine.

For each game with odds, compute the expected score-points per unit staked
for every entered scoreline, then rank them.

Points awarded for a prediction (home_pred, away_pred) vs actual (home_act, away_act):
  - exact_score           if both match exactly
  - correct_goals_home    if home_pred == home_act  (and not exact)
  - correct_goals_away    if away_pred == away_act  (and not exact)
  - correct_goal_diff     if (home_pred - away_pred) == (home_act - away_act)  (and not exact)
  - correct_result        if sign(home_pred - away_pred) == sign(home_act - away_act)

All non-exclusive — points stack (except exact_score replaces the others).

Expected value of betting 1 unit at decimal odd O on scoreline S:
  EV = (1/O) * points(S) - (1 - 1/O) * 0
     = points(S) / O

We rank by EV descending and return the top candidates.
"""

from database import get_games, get_odds_for_game, get_settings


def _implied_prob(odd: float) -> float:
    return 1.0 / odd if odd > 0 else 0.0


def _compute_points(pred_h, pred_a, act_h, act_a, cfg):
    if pred_h == act_h and pred_a == act_a:
        return cfg["exact_score_points"]

    pts = 0
    if pred_h == act_h:
        pts += cfg["correct_goals_home_points"]
    if pred_a == act_a:
        pts += cfg["correct_goals_away_points"]
    # goal difference
    if (pred_h - pred_a) == (act_h - act_a):
        pts += cfg["correct_goal_diff_points"]
    # result (win/draw/loss)
    def sign(x): return (x > 0) - (x < 0)
    if sign(pred_h - pred_a) == sign(act_h - act_a):
        pts += cfg["correct_result_points"]
    return pts


def compute_best_bets(top_n: int = 20):
    """
    Returns a ranked list of betting opportunities across all unplayed games.
    Each entry: {game_id, match_number, home, away, stage, group,
                 home_goals, away_goals, odd_value, implied_prob, ev, expected_points}
    EV here = expected_points / odd_value  (higher = better per unit staked)
    """
    cfg = get_settings()
    games = get_games()
    results = []

    for game in games:
        if game["played"]:
            continue
        odds = get_odds_for_game(game["id"])
        if not odds:
            continue

        # Normalise implied probabilities (strip bookmaker margin)
        total_implied = sum(_implied_prob(o["odd_value"]) for o in odds)

        for o in odds:
            raw_prob = _implied_prob(o["odd_value"])
            # fair probability after removing overround
            fair_prob = raw_prob / total_implied if total_implied > 0 else raw_prob

            # Expected points: sum over all other possible outcomes weighted by their fair_prob
            # We treat each entered scoreline as a possible outcome.
            # EV = sum_outcomes( fair_prob(outcome) * points_if_we_bet_on_this_scoreline )
            # i.e., we're betting on (o.home_goals, o.away_goals), outcome is drawn from the
            # distribution implied by all entered odds.
            expected_pts = 0.0
            for possible in odds:
                p_outcome = _implied_prob(possible["odd_value"]) / total_implied if total_implied > 0 else 0
                pts = _compute_points(
                    o["home_goals"], o["away_goals"],
                    possible["home_goals"], possible["away_goals"],
                    cfg,
                )
                expected_pts += p_outcome * pts

            # Return per unit staked: expected_points / odd_value
            ev = expected_pts / o["odd_value"]

            results.append({
                "game_id": game["id"],
                "match_number": game["match_number"],
                "home": game["home"],
                "away": game["away"],
                "stage": game["stage"],
                "group": game["grp"],
                "home_goals": o["home_goals"],
                "away_goals": o["away_goals"],
                "odd_value": o["odd_value"],
                "bookmaker": o.get("bookmaker"),
                "implied_prob_pct": round(raw_prob * 100, 2),
                "fair_prob_pct": round(fair_prob * 100, 2),
                "expected_points": round(expected_pts, 3),
                "ev": round(ev, 4),
            })

    results.sort(key=lambda x: x["ev"], reverse=True)
    return results[:top_n]
