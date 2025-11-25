import pandas as pd
import os

# ======================================================
# Paths
# ======================================================
DATA_PATH = "./data/"

RESULTS_FILE = DATA_PATH + "results.csv"
GOALSCORERS_FILE = DATA_PATH + "goalscorers.csv"
SHOOTOUTS_FILE = DATA_PATH + "shootouts.csv"
FORMER_NAMES_FILE = DATA_PATH + "former_names.csv"

# Output files
AFCON_RESULTS_OUT = DATA_PATH + "afcon_results.csv"
AFCON_GOALS_OUT = DATA_PATH + "afcon_goalscorers.csv"
OFFICIAL_LAST_YEAR_OUT = DATA_PATH + "official_A_last_year.csv"


# ======================================================
# Load datasets safely
# ======================================================
def load_data():
    results = pd.read_csv(RESULTS_FILE)
    goals = pd.read_csv(GOALSCORERS_FILE)
    shootouts = pd.read_csv(SHOOTOUTS_FILE)
    former_names = pd.read_csv(FORMER_NAMES_FILE)

    # Convert date columns
    results["date"] = pd.to_datetime(results["date"], errors="coerce")
    goals["date"] = pd.to_datetime(goals["date"], errors="coerce")
    shootouts["date"] = pd.to_datetime(shootouts["date"], errors="coerce")

    print("✔️ Datasets loaded successfully.")

    return results, goals, shootouts, former_names


# ======================================================
# Generate AFCON datasets (matches + goals)
# ======================================================
def build_afcon(results, goals):
    # Filter AFCON matches
    afcon = results[
        results["tournament"].str.contains("African Cup of Nations", case=False, na=False)
    ].copy()
    afcon = afcon.sort_values("date")

    # Filter AFCON goalscorers
    afcon_goals = goals.merge(
        afcon[["date", "home_team", "away_team"]],
        on=["date", "home_team", "away_team"],
        how="inner"
    )

    # Export
    afcon.to_csv(AFCON_RESULTS_OUT, index=False)
    afcon_goals.to_csv(AFCON_GOALS_OUT, index=False)

    print(f"🏆 AFCON matches exported → {AFCON_RESULTS_OUT} ({len(afcon)} matches)")
    print(f"🥅 AFCON goalscorers exported → {AFCON_GOALS_OUT} ({len(afcon_goals)} goals)")

    return afcon, afcon_goals


# ======================================================
# Build Official A-team dataset (exclude CHAN, Youth, etc.)
# ======================================================
def filter_official_A(df):
    df = df.copy()
    df["tourn_lower"] = df["tournament"].str.lower()

    # Competitions to exclude
    exclude = [
        "chan", "u-17", "u17", "u-18", "u-19", "u-20", "u20",
        "u-21", "u-22", "u-23", "u23",
        "youth", "olympic", "games",
        "wafu", "cecafa", "cosafa", "unaf",
        "local"
    ]

    for bad in exclude:
        df = df[~df["tourn_lower"].str.contains(bad)]

    return df


# ======================================================
# Only matches from last 365 days
# ======================================================
def filter_last_12_months(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    cutoff = df["date"].max() - pd.Timedelta(days=365)
    return df[df["date"] >= cutoff]


# ======================================================
# Build dataset for radar chart
# ======================================================
def build_official_last_year(results):
    official_A = filter_official_A(results)
    recent_A = filter_last_12_months(official_A)

    recent_A.to_csv(OFFICIAL_LAST_YEAR_OUT, index=False)
    print(f"📊 Official A-team last 12 months exported → {OFFICIAL_LAST_YEAR_OUT} ({len(recent_A)} matches)")

    return recent_A


# ======================================================
# MAIN
# ======================================================
def main():
    results, goals, shootouts, former_names = load_data()

    # 1) Build AFCON datasets
    build_afcon(results, goals)

    # 2) Build Official A for radar chart
    build_official_last_year(results)

    print("\n🎉 All datasets successfully generated!")


if __name__ == "__main__":
    main()
