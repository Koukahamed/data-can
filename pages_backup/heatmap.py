import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.title("🔥 Heatmap des scores – Analyse filtrée")

    df = st.session_state.get("df_main").copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

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

    df = df[df["year"] >= start_year]

    df["Score"] = df["home_score"].astype(int).astype(str) + "-" + df["away_score"].astype(int).astype(str)

    st.subheader("🏅 Scores les plus fréquents")
    st.dataframe(df["Score"].value_counts().reset_index())

    max_home = int(df["home_score"].max())
    max_away = int(df["away_score"].max())

    matrix = pd.crosstab(df["home_score"], df["away_score"])

    fig = px.imshow(
        matrix,
        labels=dict(x="Buts encaissés", y="Buts marqués", color="Fréquence"),
        color_continuous_scale="OrRd"
    )
    fig.update_layout(height=700)

    st.plotly_chart(fig, use_container_width=True)
