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
if current_session == "Session 2: Section B":
    st.header("Section B: Spatial Interface")
    
    # B2: Water Sources with "Other"
    st.subheader("B2. Water Source Sharing")
    b2_types = st.multiselect("Type of shared water sources:", 
                              ["Natural ponds/lakes", "Streams/rivers", "Man-made water holes", "Agricultural wells", "Other"])
    
    b2_other_val = ""
    if "Other" in b2_types:
        b2_other_val = st.text_input("Please specify the 'Other' water source:")

    # B3: Wildlife Species with "Other"
    st.subheader("B3. Wildlife Movement")
    b3_species = st.multiselect("Wildlife species commonly observed near livestock:", 
                                ["Wild boar", "Deer", "Gaur", "Nilgai", "Carnivores", "Other"])
    
    b3_other_val = ""
    if "Other" in b3_species:
        b3_other_val = st.text_input("Please specify the 'Other' species:")

    if st.button("Submit Section B"):
        # We combine the "Other" text with the selection list
        final_b2 = b2_types + ([f"Other: {b2_other_val}"] if b2_other_val else [])
        final_b3 = b3_species + ([f"Other: {b3_other_val}"] if b3_other_val else [])
        
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Water Types", final_b2)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Species Observed", final_b3)
        st.success("Section B data recorded!")

# --- SECTION 3: SECTION C (Placeholder) ---
if current_session == "Session 3: Section C":
    st.header("Section C: Placeholder")
    st.write("Waiting for your Section C questions...")
