import streamlit as st
import pandas as pd
import psycopg2 
import os

# --- CONFIGURATION ---
ADMIN_PASSWORD = "workshop_admin_2025" 
DATABASE_URL = os.environ.get('Database_URL')

# --- DATABASE SETUP ---
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS workshop_data 
             (id SERIAL PRIMARY KEY, 
              name TEXT, dept TEXT, location_info TEXT,
              session_name TEXT, question TEXT, answer TEXT)''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database connection failed: {e}")

init_db()

def save_answer(name, dept, loc, session, q, ans):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO workshop_data (name, dept, location_info, session_name, question, answer) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, dept, loc, session, q, str(ans)))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error saving data: {e}")

# --- ADMIN SIDEBAR ---
st.sidebar.title("🛠️ Admin Control")
admin_pwd = st.sidebar.text_input("Admin Password", type="password")
current_session = "Registration"
if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    current_session = st.sidebar.radio("Active Session", ["Registration", "Session 2: Section B", "Session 3: Section C"])
    if st.sidebar.button("Download CSV"):
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql_query("SELECT * FROM workshop_data", conn)
        conn.close()
        st.sidebar.download_button("Download Results", df.to_csv(index=False), "workshop_data.csv")

# --- PARTICIPANT UI ---
st.title("🌲 Wildlife-Livestock Interface Workshop")

# --- SECTION 1: REGISTRATION ---
st.header("Step 1: Registration")
p_name = st.text_input("Full Name")
p_dept = st.selectbox("Select Department", ["Select...", "Forest Department", "Animal Husbandry Department"])

p_loc_detail = ""
if p_dept == "Forest Department":
    p_loc_detail = st.selectbox("Select Tiger Reserve/Safari", ["Kanha", "Pench", "Panna", "Satpura", "Ratapani", "Bandhavgarh", "Sanjay", "Van Vihar", "MMSJ", "White Tiger Safari"])
elif p_dept == "Animal Husbandry Department":
    dist = st.text_input("District")
    blk = st.text_input("Block")
    inst = st.text_input("Institution")
    p_loc_detail = f"{dist} | {blk} | {inst}"

if st.button("Save Registration"):
    save_answer(p_name, p_dept, p_loc_detail, "Registration", "Check-in", "Active")
    st.success("Registration saved!")

st.divider()

# --- SECTION 2: SECTION B ---
# --- SECTION 2: SECTION B ---
if current_session == "Session 2: Section B":
    st.header("Section B: Spatial Interface & Contact Patterns")
    
    st.subheader("B1. Grazing Patterns")
    b1_freq = st.radio("How frequently do livestock graze in/near forest areas?", 
                       ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
    b1_dist = st.radio("Distance livestock typically graze from forest edge:", 
                       ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
    b1_count = st.number_input("Approximate number of livestock entering forest daily:", min_value=0)

    st.subheader("B2. Water Source Sharing")
    b2_share = st.radio("Do livestock and wildlife share water sources?", 
                        ["Yes, regularly", "Yes, seasonally", "Occasionally", "Rarely", "No"])
    b2_types = st.multiselect("Type of shared water sources:", 
                              ["Natural ponds/lakes", "Streams/rivers", "Man-made water holes", "Agricultural wells", "Other"])

    st.subheader("B3. Wildlife Movement")
    b3_freq = st.radio("Frequency of wildlife sightings in grazing areas:", 
                       ["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"])
    b3_species = st.multiselect("Wildlife species commonly observed near livestock:", 
                                ["Wild boar", "Deer", "Gaur", "Nilgai", "Carnivores", "Other"])

    if st.button("Submit Section B"):
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Grazing Frequency", b1_freq)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Grazing Distance", b1_dist)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Livestock Count", b1_count)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Water Sharing", b2_share)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Water Types", b2_types)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Wildlife Frequency", b3_freq)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Species Observed", b3_species)
        st.success("Section B data recorded!")

# --- SECTION 3: SECTION C (Placeholder) ---
if current_session == "Session 3: Section C":
    st.header("Section C: Placeholder")
    st.write("Waiting for your Section C questions...")
