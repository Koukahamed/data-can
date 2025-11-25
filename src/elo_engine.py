import pandas as pd

def expected_score(rA, rB):
    return 1 / (1 + 10 ** ((rB - rA) / 400))

def update_elo(rA, rB, scoreA, k=30):
    expA = expected_score(rA, rB)
    expB = expected_score(rB, rA)
    rA_new = rA + k * (scoreA - expA)
    rB_new = rB + k * (1 - scoreA - expB)
    return rA_new, rB_new

def compute_elo_incremental(df, initial_rating=1500, k=30):
    """
    Calcule Elo sur TOUT l'historique (1957 → 2024).
    :param df: pd.DataFrame
    :param initial_rating:
    :param k:
    :return: full_timeline : Elo match par match ; final_ratings : Elo final par équipe
    """

    df = df.sort_values("date").copy()

    ratings = {}
    timeline = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        h = row["home_score"]
        a = row["away_score"]

        ratings.setdefault(home, initial_rating)
        ratings.setdefault(away, initial_rating)

        if h > a:
            SA = 1
        elif h == a:
            SA = 0.5
        else:
            SA = 0

        newA, newB = update_elo(ratings[home], ratings[away], SA, k)

        ratings[home] = newA
        ratings[away] = newB

        timeline.append({
            "date": row["date"],
            "home_team": home,
            "away_team": away,
            "home_elo": newA,
            "away_elo": newB
        })

    return pd.DataFrame(timeline), ratings


def compute_period_elo(df, start_year, initial_rating=1500, k=30):
    """
    Option C :
    1) On calcule Elo complet depuis 1957 → start_year - 1
    2) On récupère les ratings *hérités*
    3) On continue le calcul à partir de start_year
    """

    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year

    # part 1: pre-period history (1957 → start_year-1)
    history = df[df["year"] < start_year]
    timeline_hist, ratings_hist = compute_elo_incremental(history, initial_rating, k)

    # part 2: period (start_year → 2024)
    period = df[df["year"] >= start_year].sort_values("date")

    ratings = ratings_hist.copy()
    timeline_period = []

    for _, row in period.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        h = row["home_score"]
        a = row["away_score"]

        ratings.setdefault(home, initial_rating)
        ratings.setdefault(away, initial_rating)

        if h > a:
            SA = 1
        elif h == a:
            SA = 0.5
        else:
            SA = 0

        newA, newB = update_elo(ratings[home], ratings[away], SA, k)

        ratings[home] = newA
        ratings[away] = newB

        timeline_period.append({
            "date": row["date"],
            "home_team": home,
            "away_team": away,
            "home_elo": newA,
            "away_elo": newB
        })

    return pd.DataFrame(timeline_period), ratings
