import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==========================================================
# LOAD DATASETS
# ==========================================================

def load_main_data():
    return st.session_state["df_main"]  # results.csv

@st.cache_data
def load_official_recent():
    return pd.read_csv("data/official_A_last_year.csv")

@st.cache_data
def load_afcon():
    return pd.read_csv("data/afcon_results.csv")  # CAN + qualifiers (we will filter)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def compute_stats(df, team):
    """Compute winrate, GF/match, GA/match, clean sheets."""
    matches = df[
        (df["home_team"] == team) | (df["away_team"] == team)
    ]

    if matches.empty:
        return 0, 0, 0, 0

    wins = 0
    gf_total, ga_total = 0, 0
    clean_sheets = 0

    for _, r in matches.iterrows():
        if r["home_team"] == team:
            gf, ga = r["home_score"], r["away_score"]
        else:
            gf, ga = r["away_score"], r["home_score"]

        if gf > ga:
            wins += 1
        if ga == 0:
            clean_sheets += 1

        gf_total += gf
        ga_total += ga

    total = len(matches)
    return (
        wins / total * 100,
        gf_total / total,
        ga_total / total,
        clean_sheets / total * 100
    )


def compute_h2h(df, team1, team2):
    """H2H CAN-only (df already filtered)."""
    return df[
        ((df["home_team"] == team1) & (df["away_team"] == team2)) |
        ((df["home_team"] == team2) & (df["away_team"] == team1))
    ].copy()


def rolling_goals(df, team):
    matches = df[
        (df["home_team"] == team) | (df["away_team"] == team)
    ].sort_values("date")

    if matches.empty:
        return pd.DataFrame({"date": [], "goals_rm": []})

    matches["goals"] = matches.apply(
        lambda r: r["home_score"] if r["home_team"] == team else r["away_score"],
        axis=1
    )
    matches["goals_rm"] = matches["goals"].rolling(3).mean()

    return matches[["date", "goals_rm"]]


def decade_win(df, team):
    df = df.copy()
    df["decade"] = (df["date"].dt.year // 10) * 10

    rows = []
    for dec, group in df.groupby("decade"):
        wins = 0
        matches = 0
        for _, r in group.iterrows():
            if r["home_team"] == team:
                gf, ga = r["home_score"], r["away_score"]
            elif r["away_team"] == team:
                gf, ga = r["away_score"], r["home_score"]
            else:
                continue

            matches += 1
            if gf > ga:
                wins += 1

        winrate = wins / matches * 100 if matches else 0
        rows.append({"decade": dec, "winrate": winrate})

    return pd.DataFrame(rows)


# ==========================================================
# MAIN STREAMLIT RENDER
# ==========================================================

def render():

    st.title("⚔️ Comparateur CAF – Phase finale de la CAN")

    # ===== Load base datasets =====
    main_df = load_main_data()               # ONLY used for radar (12 months all comps)
    official_recent = load_official_recent() # 12 months official games
    afcon = load_afcon()                     # CAN + qualifiers

    # Convert dates
    main_df["date"] = pd.to_datetime(main_df["date"])
    official_recent["date"] = pd.to_datetime(official_recent["date"])
    afcon["date"] = pd.to_datetime(afcon["date"])

    # ==========================================================
    # 1) RESTRICT TO CAN FINAL ONLY
    # ==========================================================
    df_can = afcon[afcon["tournament"] == "African Cup of Nations"].copy()

    # List of African countries (those that have played CAN final)
    teams = sorted(
        set(df_can["home_team"]).union(df_can["away_team"])
    )

    # ==========================================================
    # TEAM SELECTION
    # ==========================================================
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Équipe A (référence)", teams, index=teams.index("Ivory Coast"))
    with col2:
        team2 = st.selectbox("Équipe B (comparée)", teams)

    if team1 == team2:
        st.warning("Choisis deux équipes différentes.")
        return

    # ==========================================================
    # PERIOD SELECTION (affects only CAN data)
    # ==========================================================
    st.sidebar.subheader("📌 Choix de la période (CAN finale uniquement)")

    min_year = int(df_can["date"].dt.year.min())
    max_year = int(df_can["date"].dt.year.max())

    period = st.sidebar.radio(
        "Analyser :",
        [
            "Toute l’histoire",
            "5 dernières éditions",
            "10 dernières années",
            "15 dernières années",
            "Année personnalisée"
        ]
    )

    if period == "Toute l’histoire":
        start_year = min_year
    elif period == "5 dernières éditions":
        start_year = max_year - 12
    elif period == "10 dernières années":
        start_year = max_year - 10
    elif period == "15 dernières années":
        start_year = max_year - 15
    else:
        start_year = st.sidebar.slider("Année de départ", min_year, max_year, 2010)

    df_period = df_can[df_can["date"].dt.year >= start_year]

    # ==========================================================
    # 2) HEAD-TO-HEAD CAN ONLY
    # ==========================================================
    st.header("1️⃣ Face-à-face en CAN (phase finale)")

    h2h = compute_h2h(df_period, team1, team2)

    wins1 = 0
    wins2 = 0
    draws = 0

    for _, r in h2h.iterrows():
        if r["home_team"] == team1:
            gA, gB = r["home_score"], r["away_score"]
        else:
            gA, gB = r["away_score"], r["home_score"]

        if gA > gB: wins1 += 1
        elif gA < gB: wins2 += 1
        else: draws += 1

    colA, colB, colC, colD = st.columns(4)
    colA.metric("Matchs CAN", len(h2h))
    colB.metric(f"Victoire {team1}", wins1)
    colC.metric("Nuls", draws)
    colD.metric(f"Victoire {team2}", wins2)

    if len(h2h) > 0:
        st.subheader("Dernier affrontement (CAN)")
        st.dataframe(
            h2h.sort_values("date", ascending=False).head(1),
            use_container_width=True
        )

    # ==========================================================
    # 3) STATS GLOBAL CAN ONLY
    # ==========================================================
    st.header("2️⃣ Statistiques globales – phase finale CAN")

    W1, GF1, GA1, CS1 = compute_stats(df_period, team1)
    W2, GF2, GA2, CS2 = compute_stats(df_period, team2)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(team1)
        st.metric("Winrate CAN", f"{W1:.1f}%")
        st.metric("Buts marqués (CAN)", f"{GF1:.2f} / match")
        st.metric("Buts encaissés (CAN)", f"{GA1:.2f} / match")
        st.metric("Clean sheets CAN", f"{CS1:.1f}%")

    with col2:
        st.subheader(team2)
        st.metric("Winrate CAN", f"{W2:.1f}%")
        st.metric("Buts marqués (CAN)", f"{GF2:.2f} / match")
        st.metric("Buts encaissés (CAN)", f"{GA2:.2f} / match")
        st.metric("Clean sheets CAN", f"{CS2:.1f}%")

    # ==========================================================
    # 4) MATCHES DETAILS CAN ONLY
    # ==========================================================
    st.header("3️⃣ Détails des confrontations CAN")

    st.dataframe(
        h2h[["date", "home_team", "home_score", "away_score", "away_team", "city", "country"]]
        .sort_values("date"),
        use_container_width=True
    )

    # ==========================================================
    # 5) ROLLING MEAN CAN ONLY
    # ==========================================================
    st.header("4️⃣ Forme offensive (CAN uniquement)")

    t1_rm = rolling_goals(df_period, team1)
    t2_rm = rolling_goals(df_period, team2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t1_rm["date"], y=t1_rm["goals_rm"], mode="lines+markers", name=team1))
    fig.add_trace(go.Scatter(x=t2_rm["date"], y=t2_rm["goals_rm"], mode="lines+markers", name=team2))
    fig.update_layout(title="Rolling mean (3 matchs) – CAN")
    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 6) RADAR — OFFICIAL A (12 MONTHS)
    # ==========================================================
    st.header("5️⃣ Forme récente (12 mois – matchs officiels A)")

    W1_r, GF1_r, GA1_r, CS1_r = compute_stats(official_recent, team1)
    W2_r, GF2_r, GA2_r, CS2_r = compute_stats(official_recent, team2)

    radar_df = pd.DataFrame({
        "Stat": ["Winrate", "Attaque", "Défense", "Clean Sheets"],
        team1: [W1_r/100, GF1_r/3, 1 - GA1_r/3, CS1_r/100],
        team2: [W2_r/100, GF2_r/3, 1 - GA2_r/3, CS2_r/100],
    })

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=radar_df[team1],
        theta=radar_df["Stat"],
        fill='toself',
        name=team1
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_df[team2],
        theta=radar_df["Stat"],
        fill='toself',
        name=team2
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ==========================================================
    # 7) WINRATE PAR DÉCENNIE CAN
    # ==========================================================
    st.header("6️⃣ Winrate par décennie (CAN)")

    dfD1 = decade_win(df_period, team1)
    dfD2 = decade_win(df_period, team2)

    fig_dec = go.Figure()
    fig_dec.add_trace(go.Bar(x=dfD1["decade"], y=dfD1["winrate"], name=team1))
    fig_dec.add_trace(go.Bar(x=dfD2["decade"], y=dfD2["winrate"], name=team2))
    fig_dec.update_layout(barmode='group')
    st.plotly_chart(fig_dec, use_container_width=True)

    # ==========================================================
    # 8) ANALYSE AUTOMATIQUE BASED ON CAN
    # ==========================================================
    st.header("7️⃣ Analyse automatique – CAN")

    analysis = f"""
### 🔍 Analyse CAN — période {start_year} → {max_year}

**📌 Performances CAN**
- {team1} : Winrate **{W1:.1f}%**, {GF1:.2f} buts marqués / match, {GA1:.2f} encaissés / match  
- {team2} : Winrate **{W2:.1f}%**, {GF2:.2f} buts marqués / match, {GA2:.2f} encaissés / match  

**📌 Face-à-face CAN**
- {team1} : **{wins1} victoires**
- {team2} : **{wins2} victoires**
- Nuls : {draws}

**📌 Tendance offensive CAN**
L'équipe la plus régulière offensivement sur la période est :
➡️ **{team1 if t1_rm['goals_rm'].mean() > t2_rm['goals_rm'].mean() else team2}**

**📌 Forme récente (matchs officiels A – 12 mois)**
- {team1} : Winrate {W1_r:.1f}%, Attaque {GF1_r}, Défense {GA1_r}, Clean Sheets {CS1_r:.1f}%
- {team2} : Winrate {W2_r:.1f}%, Attaque {GF2_r}, Défense {GA2_r}, Clean Sheets {CS2_r:.1f}%
"""

    st.markdown(analysis)
