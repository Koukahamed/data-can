import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# LOAD DATASETS
# ==========================================================

@st.cache_data
def load_afcon_results():
    df = pd.read_csv("data/afcon_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    return df

@st.cache_data
def load_afcon_goals():
    df = pd.read_csv("data/afcon_goalscorers.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def render():
    st.title("🐘 Analyse CAN par Pays")

    afcon = load_afcon_results()
    goals = load_afcon_goals()

    countries = sorted(
        set(afcon["home_team"]).union(afcon["away_team"])
    )

    # ==========================================================
    # COUNTRY SELECTION
    # ==========================================================
    team = st.selectbox("Sélectionne un pays", countries, index=countries.index("Ivory Coast"))

    # Subsets
    df_can = afcon[afcon["tournament"] == "African Cup of Nations"].copy()
    df_qualif = afcon[afcon["tournament"] == "African Cup of Nations qualification"].copy()

    # ==========================================================
    # 1️⃣ GLOBAL SUMMARY
    # ==========================================================

    st.header(f"1️⃣ Résumé général de {team} à la CAN")

    # CAN finale
    can_matches = df_can[
        (df_can["home_team"] == team) | (df_can["away_team"] == team)
    ]

    # Qualifs
    qualif_matches = df_qualif[
        (df_qualif["home_team"] == team) | (df_qualif["away_team"] == team)
    ]

    def stats(df, team):
        if df.empty:
            return 0,0,0,0,0

        wins = 0
        gf = 0
        ga = 0
        cs = 0

        for _, r in df.iterrows():
            if r["home_team"] == team:
                gA, gB = r["home_score"], r["away_score"]
            else:
                gA, gB = r["away_score"], r["home_score"]

            gf += gA
            ga += gB
            if gA > gB: wins += 1
            if gB == 0: cs += 1

        total = len(df)

        return (
            wins / total * 100,
            gf / total,
            ga / total,
            cs / total * 100,
            total
        )

    Wc, GFc, GAc, CSc, Mc = stats(can_matches, team)
    Wq, GFq, GAq, CSq, Mq = stats(qualif_matches, team)

    colA, colB = st.columns(2)

    with colA:
        st.subheader("📌 CAN (Phase finale)")
        st.metric("Matchs joués", Mc)
        st.metric("Winrate", f"{Wc:.1f}%")
        st.metric("Buts marqués / match", f"{GFc:.2f}")
        st.metric("Buts encaissés / match", f"{GAc:.2f}")
        st.metric("Clean Sheets", f"{CSc:.1f}%")

    with colB:
        st.subheader("📌 Qualifications CAN")
        st.metric("Matchs joués", Mq)
        st.metric("Winrate", f"{Wq:.1f}%")
        st.metric("Buts marqués / match", f"{GFq:.2f}")
        st.metric("Buts encaissés / match", f"{GAq:.2f}")
        st.metric("Clean Sheets", f"{CSq:.1f}%")

    # ==========================================================
    # 2️⃣ BUTEURS DU PAYS EN CAN
    # ==========================================================
    st.header("2️⃣ Buteurs du pays en CAN")

    team_goals = goals[goals["team"] == team]

    if team_goals.empty:
        st.info("Aucun buteur enregistré pour ce pays dans le dataset.")
    else:
        top_scorers = (
            team_goals.groupby("scorer")["scorer"]
            .count()
            .sort_values(ascending=False)
            .rename("goals")
        ).to_frame()

        st.subheader("🥅 Top buteurs (toutes CAN confondues)")
        st.dataframe(top_scorers)

        fig = px.bar(
            top_scorers.head(12),
            x=top_scorers.head(12).index,
            y="goals",
            color="goals",
            title="Top 12 buteurs du pays en CAN"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 3️⃣ PERFORMANCES PAR ANNÉE / COMPÉTITION
    # ==========================================================
    st.header("3️⃣ Performance historique à la CAN")

    # Buts par année
    def goals_per_year(df, team):
        rows = []
        for year, group in df.groupby("year"):
            gf = 0
            for _, r in group.iterrows():
                if r["home_team"] == team:
                    gf += r["home_score"]
                elif r["away_team"] == team:
                    gf += r["away_score"]
            rows.append({"year": year, "goals": gf})
        return pd.DataFrame(rows)

    df_gf = goals_per_year(can_matches, team)

    if not df_gf.empty:
        fig_g = px.line(df_gf, x="year", y="goals", title="Buts par année en CAN")
        st.plotly_chart(fig_g, use_container_width=True)

    # ==========================================================
    # 4️⃣ ADVERSAIRES LES PLUS FRÉQUENTS
    # ==========================================================
    st.header("4️⃣ Adversaires les plus affrontés en CAN")

    adversaires = []

    for _, r in can_matches.iterrows():
        if r["home_team"] == team:
            adversaires.append(r["away_team"])
        else:
            adversaires.append(r["home_team"])

    if len(adversaires) > 0:
        adv_df = pd.Series(adversaires).value_counts()
        st.bar_chart(adv_df.head(12))
    else:
        st.info("Aucun match CAN pour ce pays.")

    # ==========================================================
    # 5️⃣ HEAD-TO-HEAD EN CAN
    # ==========================================================
    st.header("5️⃣ Head-to-head CAN (vs autres équipes)")

    h2h_stats = {}

    for opp in adv_df.index:
        subset = can_matches[
            ((can_matches["home_team"] == team) & (can_matches["away_team"] == opp)) |
            ((can_matches["home_team"] == opp) & (can_matches["away_team"] == team))
        ]

        wins = 0
        for _, r in subset.iterrows():
            if r["home_team"] == team:
                gA, gB = r["home_score"], r["away_score"]
            else:
                gA, gB = r["away_score"], r["home_score"]

            if gA > gB:
                wins += 1

        h2h_stats[opp] = {
            "matchs": len(subset),
            "wins": wins,
            "winrate": wins / len(subset) * 100 if len(subset) else 0
        }

    h2h_df = (
        pd.DataFrame(h2h_stats).T.sort_values("winrate", ascending=False)
    )

    st.dataframe(h2h_df, use_container_width=True)

    # ==========================================================
    # 6️⃣ HEATMAP DES SCORES EN CAN
    # ==========================================================
    st.header("6️⃣ Heatmap des scores CAN")

    heat_df = can_matches.copy()
    heat_df["score"] = heat_df["home_score"].astype(str) + "-" + heat_df["away_score"].astype(str)

    heat_count = heat_df["score"].value_counts().reset_index()
    heat_count.columns = ["score", "count"]

    fig_heat = px.treemap(
        heat_count,
        path=["score"],
        values="count",
        title="Distribution des scores en CAN"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ==========================================================
    # 7️⃣ ANALYSE AUTOMATIQUE
    # ==========================================================
    st.header("7️⃣ Analyse automatique")

    analysis = f"""
### 🔍 Analyse synthétique de **{team}** à la CAN

- Le pays a disputé **{Mc} matchs** en phase finale et **{Mq} matchs** en qualifications.
- En CAN finale, le winrate est de **{Wc:.1f}%**, avec en moyenne **{GFc:.2f} buts/match**.
- En qualifications, la performance est plus stable avec un winrate de **{Wq:.1f}%**.
- Le pays a affronté **{len(adv_df)} adversaires différents** en CAN.
- Les scores les plus fréquents montrent une tendance à des matchs { 'ouverts offensivement' if GFc > GAc else 'fermés et serrés' }.
- Les buteurs clés incluent : **{', '.join(top_scorers.head(5).index)}**.
"""

    st.markdown(analysis)
