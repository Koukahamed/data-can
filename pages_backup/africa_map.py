import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_afcon():
    df = pd.read_csv("data/afcon_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data
def load_geojson():
    # Utilise ton fichier haute résolution uploadé
    with open("./assets/custom.geo.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def compute_can_stats(df, team):
    """
    Calcule les stats CAN finale du pays sélectionné contre tous les adversaires africains.
    """
    df = df[df["tournament"] == "African Cup of Nations"].copy()

    rows = []

    for opponent in sorted(set(df["home_team"]).union(df["away_team"])):
        if opponent == team:
            continue

        matches = df[
            ((df["home_team"] == team) & (df["away_team"] == opponent)) |
            ((df["home_team"] == opponent) & (df["away_team"] == team))
        ]

        if matches.empty:
            rows.append({
                "opponent": opponent,
                "matches": 0,
                "wins": 0,
                "winrate": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_diff": 0
            })
            continue

        wins = 0
        gf = 0
        ga = 0

        for _, r in matches.iterrows():
            if r["home_team"] == team:
                gf += r["home_score"]
                ga += r["away_score"]
            else:
                gf += r["away_score"]
                ga += r["home_score"]

            if gf > ga:
                wins += 1

        winrate = wins / len(matches) * 100

        rows.append({
            "opponent": opponent,
            "matches": len(matches),
            "wins": wins,
            "winrate": winrate,
            "goals_for": gf,
            "goals_against": ga,
            "goal_diff": gf - ga
        })

    return pd.DataFrame(rows)

# ==========================================================
# MAIN PAGE
# ==========================================================

def render():
    st.title("🌍 Carte Afrique – Analyse CAN par adversaire")

    df = load_afcon()
    geojson = load_geojson()

    # liste des pays africains ayant joué la CAN
    teams = sorted(set(df["home_team"]).union(df["away_team"]))

    # -----------------------------
    # Sidebar
    # -----------------------------
    st.sidebar.header("⚙️ Options")
    team_selected = st.sidebar.selectbox("Choisir un pays", teams, index=teams.index("Ivory Coast"))

    metric = st.sidebar.selectbox(
        "Choisir la métrique à afficher sur la carte",
        [
            "Winrate",
            "Nombre de matchs",
            "Buts marqués",
            "Buts encaissés",
            "Goal difference"
        ]
    )

    st.sidebar.info("Données : Phase finale de la CAN uniquement")

    # -----------------------------
    # Compute stats
    # -----------------------------
    stats_df = compute_can_stats(df, team_selected)

    metric_key = {
        "Winrate": "winrate",
        "Nombre de matchs": "matches",
        "Buts marqués": "goals_for",
        "Buts encaissés": "goals_against",
        "Goal difference": "goal_diff"
    }[metric]

    stats_df["value"] = stats_df[metric_key]

    # -----------------------------
    # Carte Afrique
    # -----------------------------
    st.subheader(f"Carte Afrique — {team_selected} : {metric}")

    fig = px.choropleth(
        stats_df,
        geojson=geojson,
        featureidkey="properties.name",   # IMPORTANT
        locations="opponent",
        color="value",
        color_continuous_scale="YlGnBu",
        hover_data={
            "opponent": True,
            "matches": True,
            "wins": True,
            "winrate": True,
            "goals_for": True,
            "goals_against": True,
            "goal_diff": True,
            "value": False
        },
        scope="africa"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Table détail
    # -----------------------------
    st.subheader("📊 Détail par pays (CAN)")

    st.dataframe(
        stats_df.sort_values(metric_key, ascending=False),
        use_container_width=True
    )
