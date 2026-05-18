"""
FIFA World Cup 2026 fixture data.
Groups A–L, 4 teams each (48 teams total).
Group stage: C(4,2)=6 games per group → 72 games.
Knockout: R32(16) + R16(8) + QF(4) + SF(2) + 3rd(1) + F(1) = 32 games.
"""

GROUPS = {
    "A": ["Mexico", "USA", "Canada", "New Zealand"],
    "B": ["Argentina", "Chile", "Peru", "Australia"],
    "C": ["Brazil", "Colombia", "Paraguay", "Japan"],
    "D": ["France", "Belgium", "Morocco", "Algeria"],
    "E": ["England", "Netherlands", "Portugal", "Senegal"],
    "F": ["Spain", "Germany", "Switzerland", "Cameroon"],
    "G": ["Italy", "Croatia", "Ukraine", "Nigeria"],
    "H": ["Uruguay", "Ecuador", "Bolivia", "South Korea"],
    "I": ["Denmark", "Serbia", "Czech Republic", "Saudi Arabia"],
    "J": ["Poland", "Austria", "Slovakia", "Iran"],
    "K": ["Egypt", "Tunisia", "DR Congo", "Turkey"],
    "L": ["Qatar", "Costa Rica", "Honduras", "Ivory Coast"],
}

# Hosts: USA, Canada, Mexico — all pre-qualified
# Actual draw hasn't happened yet (as of May 2026 data isn't fully official);
# these are placeholder teams for the structure.

def generate_group_fixtures():
    """Return list of group-stage fixture dicts."""
    fixtures = []
    game_num = 1
    for group, teams in GROUPS.items():
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                fixtures.append({
                    "stage": "Group",
                    "group": group,
                    "home": teams[i],
                    "away": teams[j],
                    "match_number": game_num,
                })
                game_num += 1
    return fixtures


def generate_knockout_fixtures():
    """Return placeholder knockout fixtures (TBD teams)."""
    fixtures = []
    stages = [
        ("Round of 32", 16),
        ("Round of 16", 8),
        ("Quarterfinal", 4),
        ("Semifinal", 2),
        ("Third Place", 1),
        ("Final", 1),
    ]
    match_num = 73
    slot = 1
    for stage_name, count in stages:
        for i in range(count):
            fixtures.append({
                "stage": stage_name,
                "group": None,
                "home": f"TBD {slot}",
                "away": f"TBD {slot + 1}",
                "match_number": match_num,
            })
            slot += 2
            match_num += 1
    return fixtures


ALL_FIXTURES = generate_group_fixtures() + generate_knockout_fixtures()
