"""
app.py
-------
Main Streamlit application for the "AI CV Analyser".

Features:
  - Register / Login using email + username + password (SQLite backed, see database.py)
  - CV Analyser: upload a PDF / DOCX / TXT resume (or paste text) and get:
        * predicted job category (from the trained ML model)
        * top-5 category probabilities
        * matched skills highlighted as neon badges
        * basic CV stats (word count, has email/phone, etc.)
  - About page describing the app + developer credit
  - Neon UI theme with a Dark / Light toggle that stays consistent on every page

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

import database
import theme
import model_utils

# --------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit call)
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI CV Analyser",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# INITIALISATION (runs once per session)
# --------------------------------------------------------------------------
database.init_db()  # make sure users.db + users table exist

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # default theme is Dark Neon
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Login"  # or "Register"

# Inject neon CSS for the currently selected theme on every rerun
theme.inject_css(st.session_state.theme)

# Cache the trained model artifacts so they load only once per server process
@st.cache_resource(show_spinner="Loading trained CV analyser model...")
def get_model_artifacts():
    return model_utils.load_artifacts()

vectorizer, model, labels, skills_master, metrics = get_model_artifacts()


# --------------------------------------------------------------------------
# AUTH SCREENS
# --------------------------------------------------------------------------
def render_login():
    st.markdown("## 🔐 Login")
    theme.neon_card_start()
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            success, result = database.verify_user(email, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.username = result
                st.success(f"Welcome back, {result}! Redirecting...")
                st.rerun()
            else:
                st.error(result)
    theme.neon_card_end()

    st.markdown("Don't have an account?")
    if st.button("Go to Register"):
        st.session_state.auth_page = "Register"
        st.rerun()


def render_register():
    st.markdown("## 🆕 Register")
    theme.neon_card_start()
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create Account")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = database.create_user(username, email, password)
                if success:
                    st.success(message)
                    st.session_state.auth_page = "Login"
                    st.rerun()
                else:
                    st.error(message)
    theme.neon_card_end()

    st.markdown("Already have an account?")
    if st.button("Go to Login"):
        st.session_state.auth_page = "Login"
        st.rerun()


def render_auth_gate():
    """Shown when the user is not logged in: toggles between Login / Register."""
    st.markdown(
        "<h1 style='text-align:center;'>🧬 AI CV ANALYSER</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;' class='neon-sub'>AI-powered resume insight.</p>",
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 1.3, 1])
    with mid:
        if st.session_state.auth_page == "Login":
            render_login()
        else:
            render_register()


# --------------------------------------------------------------------------
# MAIN APP PAGES (only reachable once authenticated)
# --------------------------------------------------------------------------
def render_home():
    st.markdown("## 📄 CV Analyser")
    st.markdown(
        f"<p class='neon-sub'>Logged in as <b>{st.session_state.username}</b> — "
        f"model trained on <b>{metrics['num_resumes_trained']}</b> resumes across "
        f"<b>{metrics['num_categories']}</b> job categories "
        f"(test accuracy: <b>{metrics['test_accuracy']*100:.1f}%</b>).</p>",
        unsafe_allow_html=True,
    )

    theme.neon_card_start()
    input_mode = st.radio("How would you like to provide the CV?", ["Upload File", "Paste Text"], horizontal=True)

    raw_text = ""
    if input_mode == "Upload File":
        uploaded_file = st.file_uploader("Upload your CV (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                raw_text = model_utils.extract_text(uploaded_file)
            except ValueError as e:
                st.error(str(e))
    else:
        raw_text = st.text_area("Paste your CV text here", height=250)

    analyse_clicked = st.button("⚡ Analyse CV")
    theme.neon_card_end()

    if analyse_clicked:
        if not raw_text or not raw_text.strip():
            st.warning("Please upload a file or paste some CV text first.")
            return

        with st.spinner("Analysing CV..."):
            top_predictions = model_utils.predict_category(raw_text, vectorizer, model, top_n=5)
            matched_skills = model_utils.match_skills(raw_text, skills_master, limit=30)
            stats = model_utils.basic_cv_stats(raw_text)

        # ---- Predicted category ----
        best_label, best_prob = top_predictions[0]
        theme.neon_card_start()
        st.markdown(f"### 🎯 Predicted Category: **{best_label}**")
        st.progress(min(int(best_prob * 100), 100), text=f"Confidence: {best_prob*100:.1f}%")

        st.markdown("#### Top matching categories")
        chart_df = pd.DataFrame(top_predictions, columns=["Category", "Probability"]).set_index("Category")
        st.bar_chart(chart_df)
        theme.neon_card_end()

        # ---- Skills ----
        theme.neon_card_start()
        st.markdown(f"#### 🛠️ Matched Skills ({len(matched_skills)} found)")
        theme.skill_badges(matched_skills)
        theme.neon_card_end()

        # ---- CV stats ----
        theme.neon_card_start()
        st.markdown("#### 📊 CV Stats")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Word Count", stats["word_count"])
        c2.metric("Character Count", stats["char_count"])
        c3.metric("Email Found", "Yes" if stats["has_email"] else "No")
        c4.metric("Phone Found", "Yes" if stats["has_phone"] else "No")
        theme.neon_card_end()


def render_about():
    st.markdown("## ℹ️ About This App")
    theme.neon_card_start()
    st.markdown(
        """
**AI CV Analyser** is an AI-powered resume screening tool built with a
custom-trained machine learning model (TF-IDF + Logistic Regression) on
thousands of real resumes spanning 45+ job categories.

**What it does:**
- 🔐 Secure registration & login (SQLite-backed, salted & hashed passwords)
- 📄 Accepts CVs as PDF, DOCX, TXT, or pasted text
- 🎯 Predicts the most likely job category for a given CV
- 🛠️ Extracts and highlights known technical & professional skills
- 📊 Surfaces quick CV stats (word count, contact info detection, etc.)
- 🎨 Neon-themed interface with switchable Dark / Light modes

**Tech stack:** Python, Streamlit, scikit-learn, pandas, SQLite, PyPDF2, python-docx.

---
### 👨‍💻 Developer
**Ali Haider Butt**
Built as an end-to-end ML + web app project — from data cleaning and model
training to a fully styled, authenticated Streamlit product.
        """
    )
    theme.neon_card_end()


def render_settings():
    st.markdown("## ⚙️ Settings")
    theme.neon_card_start()
    st.markdown("#### 🎨 Theme")
    choice = st.radio(
        "Choose your theme",
        options=["Dark Neon", "Light Neon"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True,
    )
    new_theme = "dark" if choice == "Dark Neon" else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    theme.neon_card_end()

    theme.neon_card_start()
    st.markdown("#### 👤 Account")
    st.write(f"Logged in as: **{st.session_state.username}**")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    theme.neon_card_end()


# --------------------------------------------------------------------------
# APP ROUTER
# --------------------------------------------------------------------------
def render_app():
    st.sidebar.markdown("## 🧬 AI CV Analyser")
    st.sidebar.markdown(f"Welcome, **{st.session_state.username}** 👋")
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Navigate", ["CV Analyser", "About App", "Settings"])
    st.sidebar.markdown("---")
    st.sidebar.caption("Developed by Ali Haider Butt")

    if page == "CV Analyser":
        render_home()
    elif page == "About App":
        render_about()
    elif page == "Settings":
        render_settings()


# --------------------------------------------------------------------------
# ENTRY POINT
# --------------------------------------------------------------------------
if st.session_state.authenticated:
    render_app()
else:
    render_auth_gate()
