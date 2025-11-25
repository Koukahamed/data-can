import streamlit as st
import pandas as pd
from datetime import datetime

# ===========================================
# CONFIG PAGE
# ===========================================
def render():
    st.set_page_config(layout="wide")

    # Logo CAN 2025 (toi tu mettras ton png)
    LOGO_PATH = "assets/logo_can2025.png"

    # Hero Section
    st.markdown("""
        <style>
            .hero {
                background: linear-gradient(90deg, #c1272d, #007a3d);
                padding: 30px;
                border-radius: 12px;
                color: white;
                margin-bottom: 20px;
            }
            .hero h1 {
                font-size: 42px;
                margin-bottom: 0;
            }
            .hero h3 {
                font-weight: 300;
                margin-top: 8px;
                font-size: 22px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="hero">
            <h1>🇲🇦 Coupe d'Afrique des Nations 2025</h1>
            <h3>Le grand rendez-vous du football africain – Maroc • Décembre 2025 → Janvier 2026</h3>
        </div>
    """, unsafe_allow_html=True)

    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.image(LOGO_PATH, width=180)

    with col_title:
        st.subheader("📌 Informations générales")
        st.markdown("""
        - **Pays hôte** : Maroc 🇲🇦  
        - **Dates** : 21 décembre 2025 → 18 janvier 2026  
        - **Équipes** : 24 nations  
        - **Format** : 6 groupes de 4  
        - **Phase finale** : 16 équipes (12+4 meilleurs 3e)  
        """)

    st.markdown("---")

    # ===========================================
    # GROUPES (STATIC CARDS)
    # ===========================================
    st.subheader("🅶 Groupes officiels de la CAN 2025")

    # 👉 Je vais mettre les groupes vides. Tu pourras me donner les vrais groupes après le tirage final si tu veux.

    groups = {
        "Groupe A": ["Maroc", "Mali", "Zambie", "Comores"],
        "Groupe B": ["Égypte", "Angola", "Afrique du Sud", "Zimbabwe"],
        "Groupe C": ["Tunisie", "Nigeria", "Ouganda", "Tanzanie"],
        "Groupe D": ["Sénégal", "RD Congo", "Botswana", "Bénin"],
        "Groupe E": ["Algérie", "Burkina Faso", "Guinée équatoriale", "Soudan"],
        "Groupe F": ["Côte d'Ivoire", "Cameroun", "Gabon", "Mozambique"]
    }

    cols = st.columns(3)
    g_idx = 0

    for group_name, teams in groups.items():
        with cols[g_idx % 3]:
            st.markdown(f"### 🟩 {group_name}")
            st.markdown("".join([f"- **{t}**\n" for t in teams]))
            st.markdown("---")
        g_idx += 1

    st.markdown("---")

    # ===========================================
    # CALENDRIER (Dynamique)
    # ===========================================
    st.subheader("📅 Calendrier complet de la CAN 2025")

    # Je transforme ton calendrier en DataFrame structuré
    # (je te mets seulement les colonnes nécessaires, toi tu rempliras le CSV si tu veux)
    st.markdown("""
    ⬇️ **Voici l’ensemble des rencontres, avec les dates, groupes, villes et stades.  
    Tu peux filtrer par groupe ou par date :**
    """)

    # ==============================
    # Construction du calendrier depuis ton texte
    # ==============================

    data = [
        # 21 décembre
        ("2025-12-21", "19:00", "Maroc", "Comores", "A", "Prince Moulay Abdellah", "Rabat"),

        # 22 décembre
        ("2025-12-22", "15:30", "Mali", "Zambie", "A", "Mohammed V", "Casablanca"),
        ("2025-12-22", "17:00", "Égypte", "Zimbabwe", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-22", "19:30", "Afrique du Sud", "Angola", "B", "Grand stade de Marrakech", "Marrakech"),

        # 23 décembre
        ("2025-12-23", "12:00", "Nigeria", "Tanzanie", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-23", "14:30", "Tunisie", "Ouganda", "C", "Annexe Moulay Abdellah", "Rabat"),
        ("2025-12-23", "17:00", "Sénégal", "Botswana", "D", "Grand stade de Tanger", "Tanger"),
        ("2025-12-23", "19:30", "RD Congo", "Bénin", "D", "Stade El Barid", "Rabat"),

        # 24 décembre
        ("2025-12-24", "12:00", "Algérie", "Soudan", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-24", "14:30", "Burkina Faso", "Guinée équatoriale", "E", "Mohammed V", "Casablanca"),
        ("2025-12-24", "17:00", "Côte d'Ivoire", "Mozambique", "F", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-24", "19:30", "Cameroun", "Gabon", "F", "Grand stade d’Agadir", "Agadir"),

        # 26 décembre
        ("2025-12-26", "12:00", "Maroc", "Mali", "A", "Prince Moulay Abdellah", "Rabat"),
        ("2025-12-26", "14:30", "Zambie", "Comores", "A", "Mohammed V", "Casablanca"),
        ("2025-12-26", "17:00", "Égypte", "Afrique du Sud", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-26", "19:30", "Angola", "Zimbabwe", "B", "Grand stade de Marrakech", "Marrakech"),

        # 27 décembre
        ("2025-12-27", "12:00", "Nigeria", "Tunisie", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-27", "14:30", "Ouganda", "Tanzanie", "C", "Stade El Barid", "Rabat"),
        ("2025-12-27", "17:00", "RD Congo", "Sénégal", "D", "Grand stade de Tanger", "Tanger"),
        ("2025-12-27", "19:30", "Bénin", "Botswana", "D", "Annexe Moulay Abdellah", "Rabat"),

        # 28 décembre
        ("2025-12-28", "12:00", "Algérie", "Burkina Faso", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-28", "14:30", "Guinée équatoriale", "Soudan", "E", "Mohammed V", "Casablanca"),
        ("2025-12-28", "17:00", "Cameroun", "Côte d'Ivoire", "F", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-28", "19:30", "Gabon", "Mozambique", "F", "Grand stade d’Agadir", "Agadir"),

        # 29 décembre
        ("2025-12-29", "17:30", "Maroc", "Zambie", "A", "Prince Moulay Abdellah", "Rabat"),
        ("2025-12-29", "17:30", "Comores", "Mali", "A", "Mohammed V", "Casablanca"),
        ("2025-12-29", "19:30", "Égypte", "Angola", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-29", "19:30", "Zimbabwe", "Afrique du Sud", "B", "Grand stade de Marrakech", "Marrakech"),

        # 30 décembre
        ("2025-12-30", "17:00", "Nigeria", "Ouganda", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-30", "17:00", "Tanzanie", "Tunisie", "C", "Annexe Moulay Abdellah", "Rabat"),
        ("2025-12-30", "19:30", "Botswana", "RD Congo", "D", "Stade El Barid", "Rabat"),
        ("2025-12-30", "19:30", "Bénin", "Sénégal", "D", "Grand stade de Tanger", "Tanger"),

        # 31 décembre
        ("2025-12-31", "17:00", "Guinée équatoriale", "Algérie", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-31", "17:00", "Burkina Faso", "Soudan", "E", "Mohammed V", "Casablanca"),
        ("2025-12-31", "19:30", "Cameroun", "Mozambique", "F", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-31", "19:30", "Côte d'Ivoire", "Gabon", "F", "Grand stade de Marrakech", "Marrakech"),
    ]

    df = pd.DataFrame(data, columns=["date", "heure", "équipe_a", "équipe_b", "groupe", "stade", "ville"])
    df["date"] = pd.to_datetime(df["date"])

    # Filtres
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        groupe_filter = st.selectbox("Filtrer par groupe :", ["Tous", "A", "B", "C", "D", "E", "F"])

    with col_f2:
        date_filter = st.date_input("Filtrer par date :", value=None)

    df_vis = df.copy()

    if groupe_filter != "Tous":
        df_vis = df_vis[df_vis["groupe"] == groupe_filter]

    if date_filter:
        df_vis = df_vis[df_vis["date"] == pd.to_datetime(date_filter)]

    st.dataframe(df_vis, use_container_width=True)

    st.markdown("---")

    # ===========================================
    # RÈGLES OFFICIELLES
    # ===========================================
    st.subheader("📖 Règlement de la CAN 2025")

    st.markdown("""
    ### 🟦 Phase de groupes
    - 3 points victoire  
    - 1 point nul  
    - 0 point défaite  
    - **Départage** : confrontation directe → diff. buts → buts marqués → fair play → tirage  

    ### 🟩 Meilleurs troisièmes
    Les **4 meilleurs 3e** sont déterminés selon :
    1. Points  
    2. Diff. de buts  
    3. Buts marqués  
    4. Tirage au sort  

    ### 🟥 Phase finale
    - Match unique  
    - Prolongations si égalité  
    - Tirs au but si besoin  
    - Bracket prédéfini selon le classement des 3e  
    """)

    st.markdown("---")

    # ===========================================
    # FAVORIS (placeholder)
    # ===========================================
    st.subheader("🔥 Favoris CAN 2025 (modèle Elo pondéré)")

    # Ici tu appelleras ton futur modèle prédictions
    st.info("Les probabilités seront affichées ici lorsqu'on intégrera le modèle Monte Carlo.")

    st.progress(0.5)

    st.markdown("---")

    st.success("Page CAN 2025 générée ✔️")
