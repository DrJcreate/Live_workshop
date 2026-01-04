import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import Error as PsycopgError
import os
import json
import random
from contextlib import contextmanager
import plotly.express as px
from datetime import datetime

# ── CONFIGURATION ───────────────────────────────────────────────────────────────

# 1. Try to read from Streamlit secrets (recommended for Render/Fly.io/etc)
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    DATABASE_URL = st.secrets["DATABASE_URL"]
except Exception:
    # Development fallback - NEVER commit this to git in production!
    ADMIN_PASSWORD = "workshop_2025"           # ← change this for real use
    DATABASE_URL = os.environ.get("Database_URL")  # ← correct spelling

# Optional: Add this line if you want to warn yourself during development
if "localhost" in DATABASE_URL or DATABASE_URL is None:
    st.sidebar.warning("⚠️ Using local/development database config")
