import streamlit as st
import pandas as pd

def render():
    # ================================
    # TITRE PRINCIPAL
    # ================================
    st.title("🏆 AFCON Analytics Dashboard")
    st.markdown("### Plateforme d'analyse avancée de la Coupe d’Afrique des Nations")

    st.write("---")

    # ================================
    # HERO ANIMATION
    # ================================
    st.markdown("""
        <style>
            @keyframes fadeIn {
                from {opacity: 0; transform: translateY(20px);}
                to {opacity: 1; transform: translateY(0);}
            }
            .hero {
                animation: fadeIn 1.2s ease-out;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
                background: linear-gradient(90deg, #ff7b00, #ffb347);
                color: white;
            }
            .hero h1 {
                font-size: 36px;
                margin: 0;
            }
            .hero h3 {
                margin-top: 8px;
                font-weight: 300;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>🏆 AFCON Analytics Dashboard</h1>
        <h3>L’histoire complète de la CAN, en données.</h3>
    </div>
    """, unsafe_allow_html=True)


    # ================================
    # PRESENTATION
    # ================================
    st.subheader("📌 À propos de ce projet")
    st.markdown("""
    Bienvenue dans le **AFCON Analytics Dashboard**, une application interactive qui permet d’explorer  
    l’histoire complète de la **Coupe d’Afrique des Nations (CAN)** à travers des visualisations modernes :

    - ⚔️ Comparateur de nations africaines  
    - 🐘 Focus ultras détaillé par pays  
    - 📊 Bar Chart Race des buteurs CAN par édition  
    - ⚽ Classement des buteurs  
    - 🔎 Analyses statistiques complètes  
    """)

    st.write("---")

    # ================================
    # NAVIGATION RAPIDE (alignée avec ton menu)
    # ================================
    st.subheader("🚀 Accès rapide")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚔️ Comparateur pays")
        st.markdown("Comparer 2 nations africaines : victoires, buts, forme récente.")
        if st.button("Ouvrir", key="go_compare"):
            st.session_state["page"] = "Comparateur pays"
            st.rerun()

    with col2:
        st.markdown("### 🐘 Focus pays")
        st.markdown("Analyse détaillée d’une sélection dans l’histoire de la CAN.")
        if st.button("Voir focus", key="go_focus"):
            st.session_state["page"] = "Focus pays"
            st.rerun()

    with col3:
        st.markdown("### 📊 ⚽ Barchart buteurs CAN")
        st.markdown("Animation des buteurs par édition.")
        if st.button("Voir buteurs", key="go_buteurs"):
            st.session_state["page"] = "Barchart buteurs CAN"
            st.rerun()

    col4, col5 = st.columns(2)


    with col5:
        st.markdown("### 🏠 Home")
        st.markdown("Revenir à l’accueil.")
        st.button("Accueil", key="go_home")

    with col4:
        st.markdown("### 🇲🇦 CAN 2025 — Infos")
        st.markdown("Calendrier, groupes, stades et règlement.")
        if st.button("Ouvrir CAN 2025", key="go_can2025"):
            st.session_state["page"] = "CAN 2025"
            st.rerun()

    st.write("---")

    # ============================================
    # STATS AVANCÉES - GLOBAL CAN
    # ============================================

    st.subheader("🧠 Statistiques avancées CAN")

    df = pd.read_csv("data/afcon_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df_final = df[df["tournament"] == "African Cup of Nations"]

    # 1 – ÉQUIPE LA PLUS RÉGULIÈRE
    team_consistency = (
        df_final.groupby("home_team")
        .size()
        .sort_values(ascending=False)
    )
    most_consistent = team_consistency.index[0]

    # 2 – MEILLEURE ATTAQUE 2024
    df_2024 = df_final[df_final["year"] == 2024]
    best_attack = df_2024.groupby("home_team")["home_score"].sum().sort_values(ascending=False)
    best_attack_team = best_attack.index[0]
    best_attack_goals = int(best_attack.iloc[0])

    # 3 – MEILLEURE DÉFENSE 2024
    best_defense = df_2024.groupby("home_team")["away_score"].sum().sort_values()
    best_defense_team = best_defense.index[0]
    best_defense_goals = int(best_defense.iloc[0])

    # 4 – MATCH LE PLUS PROLIFIQUE
    df_final["total_goals"] = df_final["home_score"] + df_final["away_score"]
    max_goals_row = df_final.loc[df_final["total_goals"].idxmax()]
    prolific_match = f"{max_goals_row['home_team']} {int(max_goals_row['home_score'])}–{int(max_goals_row['away_score'])} {max_goals_row['away_team']}"

    # 5 – SCORE LE PLUS FRÉQUENT
    score_freq = df_final.groupby(["home_score", "away_score"]).size()
    most_common_score = score_freq.idxmax()
    score_display = f"{most_common_score[0]} – {most_common_score[1]}"

    colA, colB = st.columns(2)

    with colA:
        st.metric("🏅 Équipe la plus régulière", most_consistent)
        st.metric("⚽ Meilleure attaque 2024", f"{best_attack_team} ({best_attack_goals} buts)")

    with colB:
        st.metric("🧤 Meilleure défense 2024", f"{best_defense_team} ({best_defense_goals} encaissés)")
        st.metric("🔥 Match le plus prolifique de l'histoire de la CAN", prolific_match)

    st.info(f"📊 Score le plus fréquent dans l’histoire : **{score_display}**")

    # ================================
    # FOCUS CÔTE D’IVOIRE (corrigé : 3 TITRES)
    # ================================
    st.subheader("🐘 Focus : Côte d’Ivoire – Palmarès CAN")

    colA, colB, colC = st.columns(3)

    with colA:
        st.metric("Titres CAN", "3 🏆", "1992, 2015, 2023")

    with colB:
        st.metric("Finales jouées", "5", "+2 finales perdues")

    with colC:
        st.metric("Participations", "25", "Depuis 1965")

    st.markdown("""
    La Côte d’Ivoire fait partie des **grandes nations du football africain** :

    - 🏆 **3 titres de champion d’Afrique**  
    - ⭐ Une génération dorée dans les années 2010 (Yaya, Gervinho, Drogba)  
    - 🔥 Un renouveau spectaculaire lors de la CAN 2023  
    """)

    st.write("---")

    # ================================
    # APERÇU DU DATASET
    # ================================
    st.subheader("📂 Aperçu du dataset")

    try:
        df = pd.read_csv("data/afcon_results.csv")
        st.dataframe(df.head(), height=180)
    except:
        st.warning("Impossible de charger `data/afcon_results.csv`. Vérifie le dossier /data.")







