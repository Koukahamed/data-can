import streamlit as st
import pandas as pd

# ============================================================
# IMPORTS DIRECTS DES MODULES
# ============================================================
from modules.home import render as home_render
from modules.compare import render as compare_render
from modules.analyse_pays_can import render as focus_render
from modules.barchart_buteurs_advanced import render as barchart_render
from modules.can2025_info import render as can2025_render

# ============================================================
# INITIALISATION DES DONNÉES
# ============================================================
if "df_main" not in st.session_state:
    try:
        st.session_state["df_main"] = pd.read_csv("data/afcon_results.csv")
    except:
        st.session_state["df_main"] = pd.DataFrame()

if "df_goals" not in st.session_state:
    try:
        st.session_state["df_goals"] = pd.read_csv("data/afcon_goalscorers.csv")
    except:
        st.session_state["df_goals"] = pd.DataFrame()

if "page" not in st.session_state:
    st.session_state["page"] = "Home"


# ============================================================
# ROUTER AVEC IMPORTS DIRECTS
# ============================================================
def render_page(page):
    if page == "Home":
        home_render()
    elif page == "Comparateur pays":
        compare_render()
    elif page == "Focus pays":
        focus_render()
    elif page == "Barchart buteurs CAN":
        barchart_render()
    elif page == "CAN 2025":
        can2025_render()

    else:
        st.error(f"❌ Page '{page}' non configurée dans app.py")


# ============================================================
# MENU
# ============================================================
st.sidebar.title("📌 Navigation")

pages = [
    "Home",
    "Comparateur pays",
    "Focus pays",
    "Barchart buteurs CAN",
    "CAN 2025",
]

choice = st.sidebar.radio("Aller à :", pages, index=pages.index(st.session_state["page"]))

if choice != st.session_state["page"]:
    st.session_state["page"] = choice
    st.rerun()


# ============================================================
# RENDU DE LA PAGE
# ============================================================
render_page(st.session_state["page"])
