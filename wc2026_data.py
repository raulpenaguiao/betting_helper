"""
FIFA World Cup 2026 fixture data — official group stage schedule.
Source: Wikipedia / FIFA (June 2026).
Groups A–L, 4 teams each (48 teams total).
"""


GROUP_FIXTURES = [
    # Group A: Mexico, South Africa, South Korea, Czech Republic
    {"group": "A", "home": "Mexico",        "away": "South Africa",           "date_utc": "2026-06-11"},
    {"group": "A", "home": "South Korea",   "away": "Czech Republic",         "date_utc": "2026-06-11"},
    {"group": "A", "home": "Czech Republic","away": "South Africa",           "date_utc": "2026-06-18"},
    {"group": "A", "home": "Mexico",        "away": "South Korea",            "date_utc": "2026-06-18"},
    {"group": "A", "home": "Czech Republic","away": "Mexico",                 "date_utc": "2026-06-24"},
    {"group": "A", "home": "South Africa",  "away": "South Korea",            "date_utc": "2026-06-24"},
    # Group B: Canada, Bosnia and Herzegovina, Qatar, Switzerland
    {"group": "B", "home": "Canada",        "away": "Bosnia and Herzegovina", "date_utc": "2026-06-12"},
    {"group": "B", "home": "Qatar",         "away": "Switzerland",            "date_utc": "2026-06-13"},
    {"group": "B", "home": "Switzerland",   "away": "Bosnia and Herzegovina", "date_utc": "2026-06-18"},
    {"group": "B", "home": "Canada",        "away": "Qatar",                  "date_utc": "2026-06-18"},
    {"group": "B", "home": "Switzerland",   "away": "Canada",                 "date_utc": "2026-06-24"},
    {"group": "B", "home": "Bosnia and Herzegovina", "away": "Qatar",         "date_utc": "2026-06-24"},
    # Group C: Brazil, Morocco, Haiti, Scotland
    {"group": "C", "home": "Brazil",        "away": "Morocco",                "date_utc": "2026-06-13"},
    {"group": "C", "home": "Haiti",         "away": "Scotland",               "date_utc": "2026-06-13"},
    {"group": "C", "home": "Scotland",      "away": "Morocco",                "date_utc": "2026-06-19"},
    {"group": "C", "home": "Brazil",        "away": "Haiti",                  "date_utc": "2026-06-19"},
    {"group": "C", "home": "Scotland",      "away": "Brazil",                 "date_utc": "2026-06-24"},
    {"group": "C", "home": "Morocco",       "away": "Haiti",                  "date_utc": "2026-06-24"},
    # Group D: United States, Paraguay, Australia, Turkey
    {"group": "D", "home": "United States", "away": "Paraguay",               "date_utc": "2026-06-12"},
    {"group": "D", "home": "Australia",     "away": "Turkey",                 "date_utc": "2026-06-13"},
    {"group": "D", "home": "United States", "away": "Australia",              "date_utc": "2026-06-19"},
    {"group": "D", "home": "Turkey",        "away": "Paraguay",               "date_utc": "2026-06-19"},
    {"group": "D", "home": "Turkey",        "away": "United States",          "date_utc": "2026-06-25"},
    {"group": "D", "home": "Paraguay",      "away": "Australia",              "date_utc": "2026-06-25"},
    # Group E: Germany, Curaçao, Ivory Coast, Ecuador
    {"group": "E", "home": "Germany",       "away": "Curaçao",                "date_utc": "2026-06-14"},
    {"group": "E", "home": "Ivory Coast",   "away": "Ecuador",                "date_utc": "2026-06-14"},
    {"group": "E", "home": "Germany",       "away": "Ivory Coast",            "date_utc": "2026-06-20"},
    {"group": "E", "home": "Ecuador",       "away": "Curaçao",                "date_utc": "2026-06-20"},
    {"group": "E", "home": "Curaçao",       "away": "Ivory Coast",            "date_utc": "2026-06-25"},
    {"group": "E", "home": "Ecuador",       "away": "Germany",                "date_utc": "2026-06-25"},
    # Group F: Netherlands, Japan, Sweden, Tunisia
    {"group": "F", "home": "Netherlands",   "away": "Japan",                  "date_utc": "2026-06-14"},
    {"group": "F", "home": "Sweden",        "away": "Tunisia",                "date_utc": "2026-06-14"},
    {"group": "F", "home": "Netherlands",   "away": "Sweden",                 "date_utc": "2026-06-20"},
    {"group": "F", "home": "Tunisia",       "away": "Japan",                  "date_utc": "2026-06-20"},
    {"group": "F", "home": "Japan",         "away": "Sweden",                 "date_utc": "2026-06-25"},
    {"group": "F", "home": "Tunisia",       "away": "Netherlands",            "date_utc": "2026-06-25"},
    # Group G: Iran, New Zealand, Belgium, Egypt
    {"group": "G", "home": "Iran",          "away": "New Zealand",            "date_utc": "2026-06-15"},
    {"group": "G", "home": "Belgium",       "away": "Egypt",                  "date_utc": "2026-06-15"},
    {"group": "G", "home": "Belgium",       "away": "Iran",                   "date_utc": "2026-06-21"},
    {"group": "G", "home": "New Zealand",   "away": "Egypt",                  "date_utc": "2026-06-21"},
    {"group": "G", "home": "Egypt",         "away": "Iran",                   "date_utc": "2026-06-26"},
    {"group": "G", "home": "New Zealand",   "away": "Belgium",                "date_utc": "2026-06-26"},
    # Group H: Spain, Cape Verde, Saudi Arabia, Uruguay
    {"group": "H", "home": "Spain",         "away": "Cape Verde",             "date_utc": "2026-06-15"},
    {"group": "H", "home": "Saudi Arabia",  "away": "Uruguay",                "date_utc": "2026-06-15"},
    {"group": "H", "home": "Spain",         "away": "Saudi Arabia",           "date_utc": "2026-06-21"},
    {"group": "H", "home": "Uruguay",       "away": "Cape Verde",             "date_utc": "2026-06-21"},
    {"group": "H", "home": "Cape Verde",    "away": "Saudi Arabia",           "date_utc": "2026-06-26"},
    {"group": "H", "home": "Uruguay",       "away": "Spain",                  "date_utc": "2026-06-26"},
    # Group I: France, Senegal, Iraq, Norway
    {"group": "I", "home": "France",        "away": "Senegal",                "date_utc": "2026-06-16"},
    {"group": "I", "home": "Iraq",          "away": "Norway",                 "date_utc": "2026-06-16"},
    {"group": "I", "home": "France",        "away": "Iraq",                   "date_utc": "2026-06-22"},
    {"group": "I", "home": "Norway",        "away": "Senegal",                "date_utc": "2026-06-22"},
    {"group": "I", "home": "Norway",        "away": "France",                 "date_utc": "2026-06-26"},
    {"group": "I", "home": "Senegal",       "away": "Iraq",                   "date_utc": "2026-06-26"},
    # Group J: Argentina, Algeria, Austria, Jordan
    {"group": "J", "home": "Argentina",     "away": "Algeria",                "date_utc": "2026-06-16"},
    {"group": "J", "home": "Austria",       "away": "Jordan",                 "date_utc": "2026-06-16"},
    {"group": "J", "home": "Argentina",     "away": "Austria",                "date_utc": "2026-06-22"},
    {"group": "J", "home": "Jordan",        "away": "Algeria",                "date_utc": "2026-06-22"},
    {"group": "J", "home": "Algeria",       "away": "Austria",                "date_utc": "2026-06-27"},
    {"group": "J", "home": "Jordan",        "away": "Argentina",              "date_utc": "2026-06-27"},
    # Group K: Portugal, DR Congo, Uzbekistan, Colombia
    {"group": "K", "home": "Portugal",      "away": "DR Congo",               "date_utc": "2026-06-17"},
    {"group": "K", "home": "Uzbekistan",    "away": "Colombia",               "date_utc": "2026-06-17"},
    {"group": "K", "home": "Portugal",      "away": "Uzbekistan",             "date_utc": "2026-06-23"},
    {"group": "K", "home": "Colombia",      "away": "DR Congo",               "date_utc": "2026-06-23"},
    {"group": "K", "home": "Colombia",      "away": "Portugal",               "date_utc": "2026-06-27"},
    {"group": "K", "home": "DR Congo",      "away": "Uzbekistan",             "date_utc": "2026-06-27"},
    # Group L: England, Croatia, Ghana, Panama
    {"group": "L", "home": "England",       "away": "Croatia",                "date_utc": "2026-06-17"},
    {"group": "L", "home": "Ghana",         "away": "Panama",                 "date_utc": "2026-06-17"},
    {"group": "L", "home": "England",       "away": "Ghana",                  "date_utc": "2026-06-23"},
    {"group": "L", "home": "Panama",        "away": "Croatia",                "date_utc": "2026-06-23"},
    {"group": "L", "home": "Panama",        "away": "England",                "date_utc": "2026-06-27"},
    {"group": "L", "home": "Croatia",       "away": "Ghana",                  "date_utc": "2026-06-27"},
]


def _knockout_date(stage, slot):
    from datetime import date, timedelta
    if stage == "Round of 32":
        return (date(2026, 6, 28) + timedelta(days=(slot - 1) // 4)).isoformat()
    if stage == "Round of 16":
        return (date(2026, 7, 4) + timedelta(days=(slot - 1) // 2)).isoformat()
    if stage == "Quarterfinal":
        return (date(2026, 7, 10) + timedelta(days=(slot - 1) // 2)).isoformat()
    if stage == "Semifinal":
        return date(2026, 7, 14 + (slot - 1)).isoformat()
    if stage == "Third Place":
        return "2026-07-18"
    if stage == "Final":
        return "2026-07-19"


def generate_group_fixtures():
    fixtures = []
    for i, f in enumerate(GROUP_FIXTURES, start=1):
        fixtures.append({
            "stage": "Group",
            "group": f["group"],
            "home": f["home"],
            "away": f["away"],
            "match_number": i,
            "date_utc": f["date_utc"],
        })
    return fixtures


def generate_knockout_fixtures():
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
                "date_utc": _knockout_date(stage_name, i + 1),
            })
            slot += 2
            match_num += 1
    return fixtures


ALL_FIXTURES = generate_group_fixtures() + generate_knockout_fixtures()
