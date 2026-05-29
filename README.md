# WC 2026 Betting Helper

A local web app for tracking scoreline odds and finding the best bets for the 2026 FIFA World Cup.

## What it does

- Stores odds you find across bookmakers for any game and scoreline
- Ranks all entered odds by expected score-points per unit staked (EV)
- Tracks actual results and shows which bets paid off
- Links directly to Oddschecker for each game

## Stack

- **Backend**: FastAPI + SQLite
- **Frontend**: Single-page HTML/JS (no build step)

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
bash run.sh
# or
uvicorn app:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Usage

1. Pick a game from the table (click or use **↑/↓ + Enter**)
2. Press **A** to add an odd for a scoreline
3. Switch to **Best Bets** and click **Compute** to rank all entered odds
4. Use **Update Results** to pull in scores from Wikipedia automatically

## Scoring model

Points awarded per correct prediction (configurable in Settings):

| Match | Points |
|---|---|
| Exact scoreline | 10 |
| Correct home goals | 3 |
| Correct away goals | 3 |
| Correct goal difference | 4 |
| Correct result (W/D/L) | 2 |

EV is computed as `expected_points / odd_value` using the implied probability distribution across all odds entered for that game.
