import streamlit as st
import pandas as pd
import plotly.express as px
from src.elo_engine import compute_period_elo

def render():

    st.title("🏆 Classement Elo – Analyse dynamique")

    df = st.session_state.get("df_main")
    if df is None:
        st.error("Dataset non chargé.")
        return

    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year

    min_year = int(df["year"].min())   # 1957
    max_year = int(df["year"].max())   # 2024

    st.sidebar.subheader("📌 Choix de la période")

    period = st.sidebar.radio(
        "Analyser :",
        [
            "Toute l’histoire",
            "5 dernières années",
            "10 dernières années",
            "15 dernières années",
            "Année personnalisée"
        ]
    )

    if period == "Toute l’histoire":
        start_year = min_year
    elif period == "5 dernières années":
        start_year = max_year - 5
    elif period == "10 dernières années":
        start_year = max_year - 10
    elif period == "15 dernières années":
        start_year = max_year - 15
    else:
        start_year = st.sidebar.slider("Début analyse", min_year, max_year, 2010)

    st.markdown(f"### Analyse Elo depuis **{start_year}**")

    timeline, ratings = compute_period_elo(df, start_year)

    ranking = (
        pd.DataFrame(ratings.items(), columns=["Team", "Elo"])
        .sort_values("Elo", ascending=False)
        .reset_index(drop=True)
    )

    st.subheader("🏅 TOP 10 CAF")
    fig = px.bar(
        ranking.head(10),
        x="Team",
        y="Elo",
        text="Elo",
        color="Elo",
        color_continuous_scale="haline"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Evolution Ivory Coast
    st.subheader("🐘 Évolution Elo – Ivory Coast")

    civ = timeline[
        (timeline["home_team"] == "Ivory Coast") |
        (timeline["away_team"] == "Ivory Coast")
    ]

    civ["elo"] = civ.apply(
        lambda row: row["home_elo"] if row["home_team"] == "Ivory Coast" else row["away_elo"],
        axis=1
    )

    civ = civ[["date", "elo"]]

    fig2 = px.line(civ, x="date", y="elo", markers=True)
    st.plotly_chart(fig2, use_container_width=True)
