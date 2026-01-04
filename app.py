import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import json
from contextlib import contextmanager
import plotly.express as px
from datetime import datetime

# ── CONFIGURATION ───────────────────────────────────────────────────────────────

# Try to read from secure Streamlit secrets (recommended for Render)
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    DATABASE_URL = st.secrets["Database_URL"]
except Exception:
    # Only for local testing! Remove or change this when you deploy
    ADMIN_PASSWORD = "workshop_2025"
    DATABASE_URL = os.environ.get('DATABASE_URL')  # you can set this manually locally
@contextmanager
def get_db_connection():
    """Safe way to connect and disconnect from database"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        conn.autocommit = False           # We control when to save changes
        yield conn
        conn.commit()                     # Save changes only if everything was ok
    except Exception as e:
        if conn:
            conn.rollback()               # Undo changes if error happened
        st.error(f"Database connection problem: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
def get_data():
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT id, name, dept, location_info, session_name, question, answer, created_at "
                "FROM workshop_data ORDER BY created_at DESC NULLS LAST",
                conn
            )
        return df
    except Exception as e:
        st.error(f"Cannot load data: {str(e)}")
        return pd.DataFrame()

def save_answer(name, dept, location, session_name, question, answer):
    if not name or not question:
        st.warning("Name and question are required")
        return False
    
    # Convert list/multiselect answers to JSON string
    answer_value = json.dumps(answer) if isinstance(answer, (list, dict)) else str(answer)
    
    query = sql.SQL("""
        INSERT INTO workshop_data 
            (name, dept, location_info, session_name, question, answer, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (name, session_name, question)
        DO UPDATE SET 
            answer = EXCLUDED.answer,
            created_at = NOW()
    """)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, dept, location, session_name, question, answer_value))
        return True
    except Exception as e:
        st.error(f"Cannot save answer: {str(e)}")
        return False

def delete_row(row_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM workshop_data WHERE id = %s", (row_id,))
        return True
    except Exception as e:
        st.error(f"Cannot delete row: {str(e)}")
        return False

def clear_all_data():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE workshop_data RESTART IDENTITY CASCADE")
        return True
    except Exception as e:
        st.error(f"Cannot clear database: {str(e)}")
        return False
# Page settings - wide layout looks better for workshops
st.set_page_config(
    layout="wide",
    page_title="Wildlife-Livestock Workshop",
    page_icon="🌲"
)

# Live counter of unique participants
df_live = get_data()
total_participants = df_live['name'].nunique() if not df_live.empty else 0

col_title, col_counter = st.columns([5, 1])
with col_title:
    st.title("🌲 Wildlife–Livestock Interface Workshop")
with col_counter:
    st.metric("Live Participants", total_participants)
# ── SIDEBAR – ADMIN CONTROLS ──────────────────────────────────────────────────

st.sidebar.title("🛠️ Control Panel")

# Password input
admin_pwd = st.sidebar.text_input("Admin Password", type="password", key="admin_password_input")

# Check password and remember status
if admin_pwd == ADMIN_PASSWORD:
    st.session_state.admin_authenticated = True
    st.sidebar.success("Admin access granted ✓")

# If admin is logged in → show all options
if st.session_state.get("admin_authenticated", False):
    
    view_mode = st.sidebar.selectbox(
        "Select view mode",
        ["📝 Participant Form", "📊 Visualisations", "⚙️ Data Management"]
    )
    
    current_session = st.sidebar.radio(
        "Active Session",
        list(QUESTIONS.keys())  # Uses the question dictionary keys from Section 1
    )
    
    # Download button
    if st.sidebar.button("Download Full Data (CSV)"):
        df = get_data()
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            filename = f"workshop_data_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
            st.sidebar.download_button(
                label="Click to Download",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
        else:
            st.sidebar.warning("No data to download yet")
    
    # ── DANGER ZONE ──
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Danger Zone** (only for workshop host)")
    
    if st.sidebar.button("WIPE ALL DATA"):
        st.session_state.confirm_wipe = True
    
    if st.session_state.get("confirm_wipe", False):
        st.sidebar.error("**ARE YOU ABSOLUTELY SURE?**")
        st.sidebar.warning("This will delete **EVERYTHING** and cannot be undone!")
        
        col_yes, col_no = st.sidebar.columns(2)
        
        with col_yes:
            if st.button("YES – DELETE EVERYTHING"):
                if clear_all_data():
                    st.success("All data has been wiped!")
                    st.session_state.confirm_wipe = False
                    st.rerun()
        
        with col_no:
            if st.button("No, cancel"):
                st.session_state.confirm_wipe = False
                st.rerun()

else:
    # Non-admin users always see participant form
    view_mode = "📝 Participant Form"
    current_session = "Registration"
