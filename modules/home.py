import streamlit as st
import pandas as pd

def render():

    # ================================
    # HERO BANNER PREMIUM
    # ================================
    st.markdown("""
    <style>
        .hero2 {
            padding: 50px;
            border-radius: 16px;
            background: linear-gradient(135deg, #ff8a00, #fc4a1a);
            color: white;
            animation: fadeIn 1.2s ease-out;
            text-align: center;
        }
        .hero2 h1 {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 15px;
        }
        .hero2 h3 {
            font-size: 22px;
            font-weight: 300;
            opacity: 0.95;
        }
    </style>

    <div class="hero2">
        <h1>🏆 AFCON Analytics Dashboard</h1>
        <h3>Visualisez + Analysez + Explorez l’histoire de la CAN</h3>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ================================
    # CARDS FONCTIONNALITÉS
    # ================================
    st.subheader("🚀 Fonctionnalités principales")
    st.write("")

    st.markdown("""
    <style>
        .card-container {
            display: flex;
            gap: 25px;
            justify-content: center;
        }
        .card {
            background: #111827;
            padding: 28px;
            width: 26%;
            border-radius: 12px;
            color: white;
            transition: 0.25s;
            border: 1px solid #222;
        }
        .card:hover {
            transform: translateY(-6px);
            background: #1b253d;
            border-color: #ff8a00;
        }
        .card h3 {
            margin-bottom: 12px;
        }
    </style>

    <div class="card-container">
        <div class="card">
            <h3>⚔️ Comparateur</h3>
            <p>Comparer 2 nations africaines : historique, stats, forme.</p>
        </div>
        <div class="card">
            <h3>🐘 Focus pays</h3>
            <p>Analyse détaillée d’un pays dans toutes les CAN.</p>
        </div>
        <div class="card">
            <h3>📊 Buteurs CAN</h3>
            <p>Animation Bar Chart Race avec les meilleurs buteurs.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # ================================
    # STATS AVANCÉES
    # ================================
    st.subheader("🧠 Statistiques globales CAN")

    df = pd.read_csv("data/afcon_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df_final = df[df["tournament"] == "African Cup of Nations"]

    best_attack = df_final.groupby("home_team")["home_score"].sum().sort_values(ascending=False)
    best_team = best_attack.index[0]
    goals = int(best_attack.iloc[0])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🔥 Meilleure attaque totale", f"{best_team}", f"{goals} buts")
    with col2:
        st.metric("📅 Éditions analysées", df_final["year"].nunique())

    st.write("---")

    # ================================
    # MINI PALMARÈS CIV
    # ================================
    st.subheader("🐘 Focus Côte d’Ivoire (Palmarès)")

    colA, colB, colC = st.columns(3)

    with colA:
        st.metric("Titres", "3 🏆")
    with colB:
        st.metric("Finales", "5")
    with colC:
        st.metric("Participations", "25")

    st.info("⭐ Gagnant des CAN : 1992 – 2015 – 2023")
