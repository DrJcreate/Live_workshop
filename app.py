import streamlit as st
import pandas as pd
import psycopg2 # This is for the permanent Postgres database
import os

# --- CONFIGURATION ---
ADMIN_PASSWORD = "forest_admin_2025" 
# This pulls the database link from Render's settings automatically
Database_URL = os.environ.get('postgresql://workshop_db_bgad_user:zD5HloYoxWmx6SOB2axxlM4LnTQmC9bE@dpg-d59pfk0gjchc73asifj0-a/workshop_db_bgad')

# --- DATABASE SETUP (Postgres) ---
def init_db():
    try:
        conn = psycopg2.connect(Database_URL)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS workshop_data 
             (id SERIAL PRIMARY KEY, 
              name TEXT, dept TEXT, location TEXT,
              session_name TEXT, question TEXT, answer TEXT)''')
        conn.commit()
        cur.close()
        conn.close()
    except:
        st.error("Database connection failed. Check Render Environment Variables.")

init_db()

def save_answer(name, dept, loc, session, q, ans):
    conn = psycopg2.connect(Database_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO workshop_data (name, dept, location, session_name, question, answer) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, dept, loc, session, q, str(ans)))
    conn.commit()
    cur.close()
    conn.close()

# --- ADMIN SIDEBAR ---
st.sidebar.title("🛠️ Admin Control")
admin_pwd = st.sidebar.text_input("Admin Password", type="password")

current_session = "Registration"
if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    current_session = st.sidebar.radio("Active Session", ["Registration", "Session 2: Section B"])
    
    if st.sidebar.button("Download CSV"):
        conn = psycopg2.connect(Database_URL)
        df = pd.read_sql_query("SELECT * FROM workshop_data", conn)
        conn.close()
        st.sidebar.download_button("Download Results", df.to_csv(index=False), "workshop_data.csv")

# --- PARTICIPANT UI ---
st.title("🌲 Wildlife-Livestock Interface Workshop")

# SESSION 1: REGISTRATION (Always Visible)
st.header("Step 1: Registration")
p_name = st.text_input("Full Name", key="reg_name")
p_dept = st.selectbox("Department", ["Select...", "Forest Department", "Animal Husbandry Department"])
p_loc = st.text_input("Park or District Name")

if st.button("Save Registration"):
    save_answer(p_name, p_dept, p_loc, "Registration", "User Check-in", "Active")
    st.success("Registration Saved!")

st.divider()

# SESSION 2: SECTION B (Hidden until Admin unlocks)
if current_session == "Session 2: Section B":
    st.header("Section B: Spatial Interface & Contact Patterns")
    
    with st.container():
        st.subheader("B1. Grazing Patterns")
        b1_freq = st.radio("How frequently do livestock graze in/near forest areas?", 
                           ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
        
        b1_dist = st.radio("Distance livestock typically graze from forest edge:", 
                           ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
        
        b1_count = st.number_input("Approximate number of livestock entering forest daily:", min_value=0)

        st.subheader("B2. Water Source Sharing")
        b2_share = st.radio("Do livestock and wildlife share water sources?", 
                            ["Yes, regularly", "Yes, seasonally", "Occasionally", "Rarely", "No"])
        
        b2_types = st.multiselect("Type of shared water sources (Check all that apply):", 
                                  ["Natural ponds/lakes", "Streams/rivers", "Man-made water holes", "Agricultural wells", "Other"])

        st.subheader("B3. Wildlife Movement")
        b3_freq = st.radio("Frequency of wildlife sightings in grazing areas:", 
                           ["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"])
        
        b3_species = st.multiselect("Wildlife species commonly observed near livestock:", 
                                    ["Wild boar", "Deer (Chital/Sambar)", "Gaur/Wild buffalo", "Nilgai", "Carnivores", "Other"])

        if st.button("Submit Section B"):
            # Saving multiple answers
            save_answer(p_name, p_dept, p_loc, "Section B", "Grazing Frequency", b1_freq)
            save_answer(p_name, p_dept, p_loc, "Section B", "Grazing Distance", b1_dist)
            save_answer(p_name, p_dept, p_loc, "Section B", "Livestock Count", b1_count)
            save_answer(p_name, p_dept, p_loc, "Section B", "Water Sharing", b2_share)
            save_answer(p_name, p_dept, p_loc, "Section B", "Water Types", b2_types)
            save_answer(p_name, p_dept, p_loc, "Section B", "Wildlife Frequency", b3_freq)
            save_answer(p_name, p_dept, p_loc, "Section B", "Species Observed", b3_species)
            st.success("Section B responses recorded!")
