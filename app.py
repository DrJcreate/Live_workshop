import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURATION ---
ADMIN_PASSWORD = "forest_admin_2025" 

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('workshop_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS responses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, designation TEXT, dept TEXT, 
                  location TEXT, dist TEXT, block TEXT, inst TEXT,
                  email TEXT, phone TEXT, experience TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- SIDEBAR ADMIN ---
st.sidebar.title("🛠️ Admin Control")
admin_pwd = st.sidebar.text_input("Enter Admin Password", type="password")
if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    if st.sidebar.button("Download CSV"):
        conn = sqlite3.connect('workshop_data.db')
        df = pd.read_sql_query("SELECT * FROM responses", conn)
        conn.close()
        st.sidebar.download_button("Click to Download", df.to_csv(index=False).encode('utf-8'), "results.csv", "text/csv")

# --- MAIN UI ---
st.title("🌲 MP Forest & Animal Husbandry Workshop")

# We move these ABOVE the form so they update instantly
name = st.text_input("Full Name")
designation = st.text_input("Designation")
dept = st.selectbox("Select Department", ["Select...", "Forest Department", "Animal Husbandry Department"])

# Logical variables
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

email = st.text_input("Email Address")
phone = st.text_input("Phone Number")
experience = st.text_input("Years of Experience")

# Use a regular button instead of a form for real-time logic
if st.button("Submit Registration"):
    if name and dept != "Select...":
        conn = sqlite3.connect('workshop_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO responses (name, designation, dept, location, dist, block, inst, email, phone, experience) VALUES (?,?,?,?,?,?,?,?,?,?)", 
                  (name, designation, dept, location, district, block, institution, email, phone, experience))
        conn.commit()
        conn.close()
        st.success(f"Successfully registered: {name}")
    else:
        st.error("Please fill in Name and Department.")
