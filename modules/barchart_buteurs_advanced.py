import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# DATA
# ==========================================================

@st.cache_data
def load_goals():
    df = pd.read_csv("data/afcon_goalscorers.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    return df

@st.cache_data
def load_results():
    df = pd.read_csv("data/afcon_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df = df[df["tournament"] == "African Cup of Nations"]
    return df

# ==========================================================
# STRICT MERGE FINAL PHASE ONLY
# ==========================================================

def get_buteur_dataset():
    df_goals = load_goals()
    df_results = load_results()

    merged = df_goals.merge(
        df_results[["date", "home_team", "away_team"]],
        on=["date", "home_team", "away_team"],
        how="inner"
    )

    if "team" not in merged.columns:
        merged["team"] = merged["home_team"]

    min_year = int(merged["year"].min())
    max_year = int(merged["year"].max())

    return merged, min_year, max_year


# ==========================================================
# MODEL A — BBC STYLE
# ==========================================================

def model_bbc(df_year):
    fig = px.bar(
        df_year,
        x="goals",
        y="scorer",
        color="team",
        orientation="h",
        title=f"BBC-Style — Buteurs CAN {df_year['year'].iloc[0]}",
        height=700
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=14),
    )

    return fig


# ==========================================================
# MODEL B — ELASTIC
# ==========================================================

def model_elastic(df_year):
    fig = px.bar(
        df_year,
        x="goals",
        y="scorer",
        color="team",
        orientation="h",
        title=f"Elastic Motion — CAN {df_year['year'].iloc[0]}",
        height=700
    )

    fig.update_layout(
        transition=dict(duration=600, easing="elasticOut")
    )

    return fig


# ==========================================================
# MODEL C — FLAG INSIDE BAR (static for 1 year)
# ==========================================================

def model_flag(df_year):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_year["goals"],
        y=df_year["scorer"],
        orientation="h",
        text=df_year["team"],
        hovertext=[f"{team} : {g} buts" for team, g in zip(df_year["team"], df_year["goals"])],
        marker=dict(
            color=df_year["goals"],
            colorscale="Blues"
        ),
        name=str(df_year["year"].iloc[0])
    ))

    fig.update_layout(
        title=f"Flag Bar Chart — CAN {df_year['year'].iloc[0]}",
        height=700,
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        xaxis_title="Buts",
        yaxis_title="Buteurs"
    )

    return fig


# ==========================================================
# PAGE RENDER
# ==========================================================

def render():
    st.title("🏃‍♂️ Bar Chart — Buteurs CAN (par année)")

    merged, min_year, max_year = get_buteur_dataset()


    # ----------------------------
    # 1) Sélecteur d’année CAN
    # ----------------------------
    can_years = sorted(merged["year"].unique(), reverse=True)
    #year_choice = st.sidebar.selectbox("Année CAN", can_years, index=len(can_years)-1)

    #df_year = merged[merged["year"] == year_choice]

    # ----------------------------
    # 1) Sélecteur d’année CAN (dans la page, pas sidebar)
    # ----------------------------
    st.subheader("📅 Sélection de l’édition CAN")

    col1, col2 = st.columns([1, 3])

    with col1:
        year_choice = st.selectbox(
            "Année CAN",
            can_years,
            index=len(can_years) - 1
        )

    with col2:
        st.write("")  # espace visuel

    # Filtrage année
    df_year = merged[merged["year"] == year_choice]

    # ----------------------------
    # 2) Agrégation des buteurs pour l’année choisie
    # ----------------------------
    df_score = (
        df_year.groupby(["year", "scorer", "team"])
        .agg(goals=("scorer", "count"))
        .reset_index()
    )

    # ----------------------------
    # 3) Choix du modèle
    # ----------------------------
    model = st.radio(
        "Modèle",
        ["Flag Inside Bar"]
    )

    if model == "BBC Style":
        fig = model_bbc(df_score)
    elif model == "Elastic Motion":
        fig = model_elastic(df_score)
    else:
        fig = model_flag(df_score)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Données utilisées")
    st.dataframe(df_score)
# v2