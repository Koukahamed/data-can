import streamlit as st
import pandas as pd
import os
import datetime
import random
import altair as alt

# --- CONFIGURATION ---
st.set_page_config(page_title="AFCON Pro Analytics", page_icon="⚽", layout="wide")

# --- CSS MODERNE ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .metric-card {
        background-color: #262730; border-radius: 10px; padding: 20px;
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #3d3d3d;
    }
    .metric-card h1 { font-size: 28px; color: #4ecca3; margin:0; }
    .metric-card h3 { font-size: 14px; color: #a0a0a0; text-transform: uppercase; margin-bottom:5px; }
    .highlight-card {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;
        border: 2px solid #ffd700;
    }
    .match-result {
        background-color: #1f2937;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 4px solid #4ecca3;
        font-size: 14px;
    }
    .form-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        margin-right: 5px;
        font-size: 12px;
    }
    .form-W { background-color: #28a745; } /* Vert */
    .form-D { background-color: #ffc107; color: black; } /* Jaune */
    .form-L { background-color: #dc3545; } /* Rouge */
</style>
""", unsafe_allow_html=True)


# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    path_all_results = os.path.join("data", "results.csv")
    path_can_goals = os.path.join("data", "afcon_goalscorers.csv")
    path_can_results = os.path.join("data", "afcon_results.csv")
    path_shootouts = os.path.join("data", "shootouts.csv")

    try:
        # 1. Données globales (Entraînement Elo + Forme récente)
        df_all = pd.read_csv(path_all_results)
        df_all['date'] = pd.to_datetime(df_all['date'], errors='coerce')
        df_all = df_all.dropna(subset=['date'])

        df_training = df_all[
            (df_all['date'].dt.year >= 2010) &
            (df_all['tournament'] != 'African Nations Championship')
            ].sort_values('date').copy()

        # 2. Données spécifiques CAN (Résultats)
        df_can = pd.read_csv(path_can_results)
        df_can['date'] = pd.to_datetime(df_can['date'], errors='coerce')
        df_can = df_can.dropna(subset=['date'])
        df_can = df_can[df_can['tournament'] == 'African Cup of Nations']

        # 3. Données spécifiques CAN (Buteurs)
        df_goals = pd.read_csv(path_can_goals)
        df_goals['date'] = pd.to_datetime(df_goals['date'], errors='coerce')
        df_goals = df_goals.dropna(subset=['date'])
        df_goals['Year'] = df_goals['date'].dt.year

        # 4. Tirs au but
        df_shootouts = pd.read_csv(path_shootouts)
        df_shootouts['date'] = pd.to_datetime(df_shootouts['date'], errors='coerce')
        df_shootouts = df_shootouts.dropna(subset=['date'])

        return df_training, df_can, df_goals, df_shootouts
    except Exception as e:
        print(f"Erreur de chargement: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


df_training, df_can_history, df_goals, df_shootouts = load_data()

if df_training.empty:
    st.error("Erreur critique : Impossible de charger les données.")
    st.stop()


# --- MOTEUR ELO ---
class AdvancedElo:
    def __init__(self, base_rating=1500):
        self.ratings = {}
        self.base_rating = base_rating

    def get_rating(self, team):
        return self.ratings.get(team, self.base_rating)

    def get_match_weight(self, tournament):
        t = str(tournament).lower()
        if "world cup" in t and "qualification" not in t: return 60
        if "african cup" in t and "qualification" not in t: return 50
        if "qualification" in t: return 40
        if "friendly" in t: return 20
        return 30

    def expected_result(self, rating_a, rating_b, home_advantage=0):
        return 1 / (1 + 10 ** ((rating_b - (rating_a + home_advantage)) / 400))

    def update(self, team_a, team_b, score_a, score_b, tournament, neutral_ground=False):
        k = self.get_match_weight(tournament)
        rat_a = self.get_rating(team_a)
        rat_b = self.get_rating(team_b)
        home_adv = 100 if not neutral_ground else 0
        expected_a = self.expected_result(rat_a, rat_b, home_adv)

        if score_a > score_b:
            actual = 1
        elif score_a == score_b:
            actual = 0.5
        else:
            actual = 0

        change = k * (actual - expected_a)
        self.ratings[team_a] = rat_a + change
        self.ratings[team_b] = rat_b - change

    def train_model(self, df):
        progress_text = "Entraînement de l'IA..."
        my_bar = st.progress(0, text=progress_text)
        total = len(df)
        chunks = max(1, total // 100)
        for i, row in enumerate(df.itertuples()):
            self.update(row.home_team, row.away_team, row.home_score, row.away_score, row.tournament, row.neutral)
            if i % chunks == 0:
                my_bar.progress(min(i / total, 1.0), text=progress_text)
        my_bar.empty()


@st.cache_resource
def build_model(df):
    model = AdvancedElo()
    model.train_model(df)
    return model


elo_model = build_model(df_training)

# --- MAPPING NOMS ---
name_map = {
    "Maroc": "Morocco", "Égypte": "Egypt", "Sénégal": "Senegal", "Côte d'Ivoire": "Ivory Coast",
    "Cameroun": "Cameroon", "Algérie": "Algeria", "Tunisie": "Tunisia", "Afrique du Sud": "South Africa",
    "RD Congo": "DR Congo", "Guinée": "Guinea", "Guinée équatoriale": "Equatorial Guinea",
    "Comores": "Comoros", "Zambie": "Zambia", "Ouganda": "Uganda", "Tanzanie": "Tanzania",
    "Bénin": "Benin", "Soudan": "Sudan", "Mozambique": "Mozambique", "Mali": "Mali",
    "Nigeria": "Nigeria", "Burkina Faso": "Burkina Faso", "Angola": "Angola", "Gabon": "Gabon",
    "Zimbabwe": "Zimbabwe", "Botswana": "Botswana"
}
inv_map = {v: k for k, v in name_map.items()}


def get_english_name(french_name):
    return name_mapping.get(french_name, french_name)


def get_elo(team_fr):
    en_name = name_map.get(team_fr, team_fr)
    return int(elo_model.get_rating(en_name))


# --- APP ---
st.title("🧠 AFCON Pro Analytics")

tab_hist, tab_focus, tab_can25, tab_simu, tab_shootouts = st.tabs([
    "🏛️ Historique & Stats", "🌍 Focus Pays", "🔮 CAN 2025", "🤖 Prédictions IA", "🥅 Tirs au But"
])

# ==========================================
# ONGLET 1 : HISTORIQUE & STATS
# ==========================================
with tab_hist:
    col1, col2, col3, col4 = st.columns(4)
    total_goals = len(df_goals[~df_goals['own_goal']])
    total_matches = len(df_can_history)
    col1.metric("Buts Marqués (Total)", total_goals)
    col2.metric("Matchs Joués", total_matches)
    col3.metric("Moyenne Buts/Match", f"{total_goals / total_matches:.2f}" if total_matches else "0")
    col4.metric("Pays Hôte 2025", "Maroc 🇲🇦")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Évolution des buts par édition")
        goals_by_year = df_goals[~df_goals['own_goal']].groupby('Year').size()
        st.area_chart(goals_by_year, color="#4ecca3")

    with c2:
        st.subheader("🏆 Top 10 Buteurs Légendaires")
        top_n = 10
        scorers = df_goals[~df_goals['own_goal']]['scorer'].value_counts().head(top_n)
        st.bar_chart(scorers, color="#ffd700")

# ==========================================
# ONGLET 2 : FOCUS PAYS
# ==========================================
with tab_focus:
    st.header("🌍 Analyse détaillée par Pays")
    all_teams = sorted(pd.concat([df_can_history['home_team'], df_can_history['away_team']]).unique())
    country_focus = st.selectbox("Sélectionnez un pays", all_teams)

    if country_focus:
        st.subheader(f"État de forme (5 derniers matchs TCC)")
        recent_matches = df_training[
            (df_training['home_team'] == country_focus) |
            (df_training['away_team'] == country_focus)
            ].sort_values('date', ascending=False).head(5)

        if not recent_matches.empty:
            cols_form = st.columns(5)
            for i, (_, row) in enumerate(recent_matches.iterrows()):
                if i >= 5: break
                is_home = row['home_team'] == country_focus
                opp = row['away_team'] if is_home else row['home_team']
                s_my = int(row['home_score']) if is_home else int(row['away_score'])
                s_opp = int(row['away_score']) if is_home else int(row['home_score'])
                res_code = "W" if s_my > s_opp else ("D" if s_my == s_opp else "L")
                res_color = "form-W" if s_my > s_opp else ("form-D" if s_my == s_opp else "form-L")
                with cols_form[i]:
                    st.markdown(f"""
                    <div style="text-align:center; background-color:#262730; padding:10px; border-radius:5px;">
                        <div class="form-badge {res_color}">{res_code}</div>
                        <div style="font-size:12px; margin-top:5px;">vs {opp}</div>
                        <div style="font-weight:bold;">{s_my}-{s_opp}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Pas de matchs récents.")

        st.divider()

        country_matches = df_can_history[
            (df_can_history['home_team'] == country_focus) | (df_can_history['away_team'] == country_focus)].copy()

        if not country_matches.empty:
            games_played = len(country_matches)
            wins = 0
            for _, row in country_matches.iterrows():
                is_home = row['home_team'] == country_focus
                my_score = row['home_score'] if is_home else row['away_score']
                opp_score = row['away_score'] if is_home else row['home_score']
                if my_score > opp_score: wins += 1

            current_elo = int(elo_model.get_rating(country_focus))

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.markdown(f"<div class='metric-card'><h3>Matchs CAN</h3><h1>{games_played}</h1></div>",
                            unsafe_allow_html=True)
            col_s2.markdown(f"<div class='metric-card'><h3>Victoires</h3><h1>{wins}</h1></div>", unsafe_allow_html=True)
            col_s3.markdown(f"<div class='metric-card'><h3>Score Elo</h3><h1>{current_elo}</h1></div>",
                            unsafe_allow_html=True)
            perc_win = (wins / games_played * 100) if games_played > 0 else 0
            col_s4.markdown(f"<div class='metric-card'><h3>% Victoire</h3><h1>{perc_win:.1f}%</h1></div>",
                            unsafe_allow_html=True)

            st.subheader(f"⚽ Meilleurs Buteurs : {country_focus}")
            country_scorers = df_goals[(df_goals['team'] == country_focus) & (~df_goals['own_goal'])]
            if not country_scorers.empty:
                top_scorers_country = country_scorers['scorer'].value_counts().head(10)
                st.bar_chart(top_scorers_country, color="#ffd700")
        else:
            st.warning("Aucun match de phase finale de CAN trouvé.")

# ==========================================
# ONGLET 3 : CAN 2025
# ==========================================
with tab_can25:
    st.header("🔮 Cap sur le Maroc 2025")
    target_date = datetime.datetime(2025, 12, 21)
    delta = target_date - datetime.datetime.now()
    st.success(f"⏳ **Compte à rebours :** J-{delta.days} avant la CAN 2025 !")

    # Données des Groupes 2025 (REMIS EN PLACE)
    groups_2025 = {
        "Groupe A": ["Maroc", "Mali", "Zambie", "Comores"],
        "Groupe B": ["Égypte", "Angola", "Afrique du Sud", "Zimbabwe"],
        "Groupe C": ["Tunisie", "Nigeria", "Ouganda", "Tanzanie"],
        "Groupe D": ["Sénégal", "RD Congo", "Botswana", "Bénin"],
        "Groupe E": ["Algérie", "Burkina Faso", "Guinée équatoriale", "Soudan"],
        "Groupe F": ["Côte d'Ivoire", "Cameroun", "Gabon", "Mozambique"]
    }

    st.markdown("### 🏆 Les Groupes Officiels")

    cols = st.columns(3)
    for i, (group_name, teams) in enumerate(groups_2025.items()):
        with cols[i % 3]:
            teams_html = "".join([f"<li style='text-align:left'>{t}</li>" for t in teams])
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:20px;'>
                <h4 style='color:#4CAF50'>{group_name}</h4>
                <ul style='list-style-type:none; padding:0; margin:0;'>
                    {teams_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    matches_data = [
        ("2025-12-21", "19:00", "Maroc", "Comores", "A", "Prince Moulay Abdellah", "Rabat"),
        ("2025-12-22", "15:30", "Mali", "Zambie", "A", "Mohammed V", "Casablanca"),
        ("2025-12-22", "17:00", "Égypte", "Zimbabwe", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-22", "19:30", "Afrique du Sud", "Angola", "B", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-23", "12:00", "Nigeria", "Tanzanie", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-23", "14:30", "Tunisie", "Ouganda", "C", "Annexe Moulay Abdellah", "Rabat"),
        ("2025-12-23", "17:00", "Sénégal", "Botswana", "D", "Grand stade de Tanger", "Tanger"),
        ("2025-12-23", "19:30", "RD Congo", "Bénin", "D", "Stade El Barid", "Rabat"),
        ("2025-12-24", "12:00", "Algérie", "Soudan", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-24", "14:30", "Burkina Faso", "Guinée équatoriale", "E", "Mohammed V", "Casablanca"),
        ("2025-12-24", "17:00", "Côte d'Ivoire", "Mozambique", "F", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-24", "19:30", "Cameroun", "Gabon", "F", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-26", "12:00", "Maroc", "Mali", "A", "Prince Moulay Abdellah", "Rabat"),
        ("2025-12-26", "14:30", "Zambie", "Comores", "A", "Mohammed V", "Casablanca"),
        ("2025-12-26", "17:00", "Égypte", "Afrique du Sud", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-26", "19:30", "Angola", "Zimbabwe", "B", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-27", "12:00", "Nigeria", "Tunisie", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-27", "14:30", "Ouganda", "Tanzanie", "C", "Stade El Barid", "Rabat"),
        ("2025-12-27", "17:00", "RD Congo", "Sénégal", "D", "Grand stade de Tanger", "Tanger"),
        ("2025-12-27", "19:30", "Bénin", "Botswana", "D", "Annexe Moulay Abdellah", "Rabat"),
        ("2025-12-28", "12:00", "Algérie", "Burkina Faso", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-28", "14:30", "Guinée équatoriale", "Soudan", "E", "Mohammed V", "Casablanca"),
        ("2025-12-28", "17:00", "Cameroun", "Côte d'Ivoire", "F", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-28", "19:30", "Gabon", "Mozambique", "F", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-29", "17:30", "Maroc", "Zambie", "A", "Prince Moulay Abdellah", "Rabat"),
        ("2025-12-29", "17:30", "Comores", "Mali", "A", "Mohammed V", "Casablanca"),
        ("2025-12-29", "19:30", "Égypte", "Angola", "B", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-29", "19:30", "Zimbabwe", "Afrique du Sud", "B", "Grand stade de Marrakech", "Marrakech"),
        ("2025-12-30", "17:00", "Nigeria", "Ouganda", "C", "Complexe sportif de Fès", "Fès"),
        ("2025-12-30", "17:00", "Tanzanie", "Tunisie", "C", "Annexe Moulay Abdellah", "Rabat"),
        ("2025-12-30", "19:30", "Botswana", "RD Congo", "D", "Stade El Barid", "Rabat"),
        ("2025-12-30", "19:30", "Bénin", "Sénégal", "D", "Grand stade de Tanger", "Tanger"),
        ("2025-12-31", "17:00", "Guinée équatoriale", "Algérie", "E", "Prince Moulay El Hassan", "Rabat"),
        ("2025-12-31", "17:00", "Burkina Faso", "Soudan", "E", "Mohammed V", "Casablanca"),
        ("2025-12-31", "19:30", "Cameroun", "Mozambique", "F", "Grand stade d’Agadir", "Agadir"),
        ("2025-12-31", "19:30", "Côte d'Ivoire", "Gabon", "F", "Grand stade de Marrakech", "Marrakech"),
    ]

    st.markdown("### 📅 Calendrier des Matchs")
    df_matches = pd.DataFrame(matches_data,
                              columns=["Date", "Heure", "Équipe A", "Équipe B", "Groupe", "Stade", "Ville"])

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_group = st.selectbox("Filtrer par Groupe", ["Tous"] + sorted(list(set(df_matches['Groupe']))))
    with col_f2:
        all_teams_cal = sorted(list(set(df_matches['Équipe A']).union(set(df_matches['Équipe B']))))
        filter_team = st.selectbox("Filtrer par Équipe", ["Tous"] + all_teams_cal)

    filtered_df = df_matches.copy()
    if filter_group != "Tous":
        filtered_df = filtered_df[filtered_df['Groupe'] == filter_group]
    if filter_team != "Tous":
        filtered_df = filtered_df[(filtered_df['Équipe A'] == filter_team) | (filtered_df['Équipe B'] == filter_team)]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ==========================================
# ONGLET 4 : PRÉDICTIONS IA
# ==========================================
with tab_simu:
    st.header("🤖 Simulateur IA de la CAN 2025")

    with st.expander("📊 Voir le Classement de Puissance (Elo Actuel)", expanded=True):
        can_teams_fr = list(name_map.keys())
        elo_data = [{"Pays": t, "Score Elo": get_elo(t)} for t in can_teams_fr]
        df_elo_rank = pd.DataFrame(elo_data).sort_values("Score Elo", ascending=False).reset_index(drop=True)
        df_elo_rank.index += 1
        st.dataframe(df_elo_rank, use_container_width=True)

    with st.expander("🌡️ Matrice des Probabilités (Qui bat qui ?)", expanded=False):
        teams_2025_fr = list(name_map.keys())
        matrix_data = []
        for t1 in teams_2025_fr:
            for t2 in teams_2025_fr:
                if t1 == t2:
                    prob = 0.5
                else:
                    t1_en, t2_en = name_map[t1], name_map[t2]
                    r1, r2 = elo_model.get_rating(t1_en), elo_model.get_rating(t2_en)
                    home_adv = 100 if t1 == "Maroc" else (-100 if t2 == "Maroc" else 0)
                    prob = 1 / (1 + 10 ** ((r2 - (r1 + home_adv)) / 400))
                matrix_data.append({"Équipe A": t1, "Équipe B": t2, "Probabilité": round(prob, 2)})

        heatmap = alt.Chart(pd.DataFrame(matrix_data)).mark_rect().encode(
            x='Équipe B:O', y='Équipe A:O',
            color=alt.Color('Probabilité:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
            tooltip=['Équipe A', 'Équipe B', 'Probabilité']
        ).properties(width=800, height=800)
        st.altair_chart(heatmap, use_container_width=True)

    st.divider()

    # SIMULATION
    groups_sim = {
        "A": ["Maroc", "Mali", "Zambie", "Comores"],
        "B": ["Égypte", "Angola", "Afrique du Sud", "Zimbabwe"],
        "C": ["Tunisie", "Nigeria", "Ouganda", "Tanzanie"],
        "D": ["Sénégal", "RD Congo", "Botswana", "Bénin"],
        "E": ["Algérie", "Burkina Faso", "Guinée équatoriale", "Soudan"],
        "F": ["Côte d'Ivoire", "Cameroun", "Gabon", "Mozambique"]
    }

    if st.button("🚀 Lancer la Simulation", type="primary"):
        with st.spinner("L'IA joue les matchs..."):

            def sim_match(t1_fr, t2_fr, knockout=False):
                t1_en, t2_en = name_map.get(t1_fr, t1_fr), name_map.get(t2_fr, t2_fr)
                elo_a, elo_b = elo_model.get_rating(t1_en), elo_model.get_rating(t2_en)
                home_bonus = 100 if t1_fr == "Maroc" else (-100 if t2_fr == "Maroc" else 0)
                prob_a = 1 / (1 + 10 ** ((elo_b - (elo_a + home_bonus)) / 400))

                diff = (elo_a + home_bonus) - elo_b
                base = 1.3
                ga = max(0, int(random.gauss(base + (diff / 400), 1.1)))
                gb = max(0, int(random.gauss(base - (diff / 400), 1.1)))

                if knockout and ga == gb:
                    if random.random() < prob_a:
                        ga += 1
                    else:
                        gb += 1
                return ga, gb


            # Groupes
            qualified, thirds = [], []
            group_res_display = {}

            for grp, teams in groups_sim.items():
                stats = {t: {'Pts': 0, 'BP': 0, 'Diff': 0} for t in teams}
                matchups = [(teams[i], teams[j]) for i in range(4) for j in range(i + 1, 4)]

                for t1, t2 in matchups:
                    s1, s2 = sim_match(t1, t2)
                    stats[t1]['BP'] += s1;
                    stats[t2]['BP'] += s2
                    stats[t1]['Diff'] += (s1 - s2);
                    stats[t2]['Diff'] += (s2 - s1)
                    if s1 > s2:
                        stats[t1]['Pts'] += 3
                    elif s2 > s1:
                        stats[t2]['Pts'] += 3
                    else:
                        stats[t1]['Pts'] += 1; stats[t2]['Pts'] += 1

                sorted_teams = sorted(stats.keys(), key=lambda x: (stats[x]['Pts'], stats[x]['Diff'], stats[x]['BP']),
                                      reverse=True)
                qualified.append((sorted_teams[0], 1));
                qualified.append((sorted_teams[1], 2))
                thirds.append((sorted_teams[2], stats[sorted_teams[2]]))
                group_res_display[grp] = [(t, stats[t]['Pts'], stats[t]['Diff']) for t in sorted_teams]

            thirds.sort(key=lambda x: (x[1]['Pts'], x[1]['Diff']), reverse=True)
            qualified.extend([(t[0], 3) for t in thirds[:4]])

            # Affichage Groupes
            cols = st.columns(3)
            for i, (grp, res) in enumerate(group_res_display.items()):
                with cols[i % 3]:
                    with st.expander(f"Groupe {grp}"):
                        st.table(pd.DataFrame(res, columns=["Pays", "Pts", "Diff"]))

            # Phase Finale
            st.subheader("🏆 Phase Finale")

            # Création des paires aléatoires pour le premier tour (8èmes)
            random.shuffle(qualified)
            # On s'assure d'avoir un nombre pair d'équipes pour les paires
            if len(qualified) % 2 != 0:
                # Gestion de secours si jamais la logique de qualification échoue (peu probable ici)
                qualified = qualified[:-1]

            current_round = []
            for i in range(0, len(qualified), 2):
                current_round.append((qualified[i][0], qualified[i + 1][0]))  # On garde juste les noms

            rounds = ["8èmes de Finale", "Quarts de Finale", "Demi-Finales", "Finale"]

            winner_tournament = None

            for r_name in rounds:
                next_round = []
                st.markdown(f"#### {r_name}")
                match_cols = st.columns(2)

                # S'assurer qu'il y a des matchs à jouer
                if not current_round:
                    break

                for i, (t1, t2) in enumerate(current_round):
                    s1, s2 = sim_match(t1, t2, knockout=True)
                    winner = t1 if s1 > s2 else t2
                    next_round.append(winner)

                    with match_cols[i % 2]:
                        win_color = "#4ecca3"
                        t1_fmt = f"**{t1}**" if t1 == winner else t1
                        t2_fmt = f"**{t2}**" if t2 == winner else t2
                        st.markdown(
                            f"""<div class="match-result">{t1_fmt} <span style="float:right; font-weight:bold; color:{win_color}">{s1} - {s2}</span> <br>{t2_fmt}</div>""",
                            unsafe_allow_html=True)

                # Préparation du tour suivant : recréer des paires
                if len(next_round) > 1:
                    new_pairs = []
                    for i in range(0, len(next_round), 2):
                        if i + 1 < len(next_round):
                            new_pairs.append((next_round[i], next_round[i + 1]))
                        else:
                            # Cas impair théoriquement impossible ici avec 16 équipes au départ
                            new_pairs.append((next_round[i], "Bye"))
                    current_round = new_pairs
                else:
                    winner_tournament = next_round[0]
                    current_round = []  # Fin du tournoi

            if winner_tournament:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div class='highlight-card'><h3 style="color:white; margin-bottom:10px;">🌟 VAINQUEUR CAN 2025 🌟</h3><h1 style='font-size: 60px; color: #FFD700; text-shadow: 2px 2px 4px #000000;'>{winner_tournament}</h1></div>""",
                    unsafe_allow_html=True)

# ==========================================
# ONGLET 5 : TIRS AU BUT (FILTRÉ CAN)
# ==========================================
with tab_shootouts:
    st.header("🥅 Analyse des Tirs au But (Focus CAN)")

    if not df_shootouts.empty and not df_can_history.empty:
        # Filtre intelligent par date
        can_dates = set(df_can_history['date'].dt.date)
        df_shootouts_can = df_shootouts[df_shootouts['date'].dt.date.isin(can_dates)]

        if not df_shootouts_can.empty:
            home_part = df_shootouts_can[['home_team', 'winner']].rename(columns={'home_team': 'team'})
            away_part = df_shootouts_can[['away_team', 'winner']].rename(columns={'away_team': 'team'})
            all_part = pd.concat([home_part, away_part])

            stats_pk = all_part.groupby('team').agg(Participations=('winner', 'count')).reset_index()
            wins_count = df_shootouts_can['winner'].value_counts().reset_index()
            wins_count.columns = ['team', 'Victoires']

            stats_pk = pd.merge(stats_pk, wins_count, on='team', how='left').fillna(0)
            stats_pk['% Réussite'] = (stats_pk['Victoires'] / stats_pk['Participations'] * 100).round(1)
            stats_pk_filtered = stats_pk.sort_values(['Participations', '% Réussite'], ascending=False)

            col_pk1, col_pk2 = st.columns([2, 1])
            with col_pk1:
                st.subheader("Les Rois du Sang-Froid à la CAN")
                st.dataframe(stats_pk_filtered[['team', 'Participations', 'Victoires', '% Réussite']],
                             use_container_width=True, hide_index=True)
            with col_pk2:
                st.subheader("Statistique Globale")
                st.metric("Total Séances CAN", len(df_shootouts_can))
                st.info("⚠️ Filtrage basé sur les dates de matchs de la CAN.")
        else:
            st.warning("Aucune séance trouvée aux dates de la CAN.")
    else:
        st.warning("Données manquantes.")

st.markdown("---")
st.caption("Développé avec Streamlit | Modèle Elo Simplifié")
