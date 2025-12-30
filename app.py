import streamlit as st
import pandas as pd
import sqlite3 

# --- CONFIGURATION ---
ADMIN_PASSWORD = "forest_admin_2025" # Change this to your secret password

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('workshop_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS responses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, designation TEXT, dept TEXT, 
                  location TEXT, dist TEXT, block TEXT, inst TEXT,
                  email TEXT, phone TEXT, experience TEXT, session_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- SIDEBAR ADMIN CONTROLS ---
st.sidebar.title("🛠️ Admin Control")
admin_pwd = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    st.sidebar.subheader("Data Management")
    
    if st.sidebar.button("Download CSV"):
        conn = sqlite3.connect('workshop_data.db')
        df = pd.read_sql_query("SELECT * FROM responses", conn)
        conn.close()
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Click to Download CSV", csv, "workshop_results.csv", "text/csv")

# --- MAIN UI ---
st.title("🌲 Workshop Questionnaire")
st.write("Please fill in your details below.")

with st.form("session_1_form"):
    # Basic Info
    name = st.text_input("Full Name")
    designation = st.text_input("Designation")
    
    # Department Logic
    dept = st.selectbox("Select Department", ["Select...", "Forest Department", "Animal Husbandry Department"])
    
    # Conditional Fields
    location = ""
    district, block, institution = "", "", ""
    
    if dept == "Forest Department":
        location = st.selectbox("Select Park/Safari", [
            "Kanha", "Pench", "Panna", "Satpura", "Ratapani", 
            "Bandhavgarh", "Sanjay", "Van Vihar National Park", "MMSJ", "White Tiger Safari"
        ])
    elif dept == "Animal Husbandry Department":
        district = st.text_input("District")
        block = st.text_input("Block")
        institution = st.text_input("Institution")

    # Contact Info
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.text_input("Years of Experience")

    submit_btn = st.form_submit_button("Submit Registration")

    if submit_btn:
        if name and dept != "Select...":
            conn = sqlite3.connect('workshop_data.db')
            c = conn.cursor()
            c.execute("INSERT INTO responses (name, designation, dept, location, dist, block, inst, email, phone, experience) VALUES (?,?,?,?,?,?,?,?,?,?)", 
                      (name, designation, dept, location, district, block, institution, email, phone, experience))
            conn.commit()
            conn.close()
            st.success(f"Thank you {name}, your registration is complete!")
        else:
            st.error("Please provide your name and department.")
