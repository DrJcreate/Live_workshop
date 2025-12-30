import streamlit as st
import pandas as pd
import psycopg2 
import os

# --- CONFIGURATION ---
ADMIN_PASSWORD = "workshop_2025" 
DATABASE_URL = os.environ.get('Database_URL')

# --- DATABASE SETUP ---
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # NOTE: If you get a 'column' error, uncomment the line below for ONE deploy to reset
        # cur.execute("DROP TABLE IF EXISTS workshop_data") 
        cur.execute('''CREATE TABLE IF NOT EXISTS workshop_data 
             (id SERIAL PRIMARY KEY, name TEXT, designation TEXT, dept TEXT, location_info TEXT,
              email TEXT, phone TEXT, experience TEXT,
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
st.sidebar.title("🛠️ Workshop Controller")
admin_pwd = st.sidebar.text_input("Admin Password", type="password")
current_session = "Registration"

if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    current_session = st.sidebar.radio("Active Session", 
        ["Registration", "Section B: Spatial", "Section C: Disease", "Section D: Contact", "Section E: Risk", "Section F: Mitigation", "Section G: Surveillance"])
    if st.sidebar.button("Download CSV"):
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql_query("SELECT * FROM workshop_data", conn)
        conn.close()
        st.sidebar.download_button("Download Results", df.to_csv(index=False), "workshop_results.csv")

# --- MAIN UI ---
st.title("🌲 Wildlife-Livestock Interface Workshop")
p_name = st.text_input("Full Name")
p_dept = st.selectbox("Select Department", ["Select...", "Forest Department", "Animal Husbandry Department"])

p_loc_detail = ""
if p_dept == "Forest Department":
    p_loc_detail = st.selectbox("Select Tiger Reserve/Safari", ["Kanha", "Pench", "Panna", "Satpura", "Ratapani", "Bandhavgarh", "Sanjay", "Van Vihar", "MMSJ", "White Tiger Safari"])
elif p_dept == "Animal Husbandry Department":
    dist, blk = st.columns(2)
    with dist: d_val = st.text_input("District")
    with blk: b_val = st.text_input("Block")
    i_val = st.text_input("Institution")
    p_loc_detail = f"{d_val} | {b_val} | {i_val}"

st.divider()

# --- REGISTRATION ---
if current_session == "Registration":
    st.header("Step 1: Registration")
    p_desig = st.text_input("Designation")
    p_email = st.text_input("Email")
    p_phone = st.text_input("Phone")
    p_exp = st.text_input("Years of Experience")
    if st.button("Save Registration"):
        save_answer(p_name, p_dept, p_loc_detail, "Registration", "Profile", f"{p_desig}, {p_email}, {p_phone}, {p_exp}")
        st.success("Registration Saved!")

# --- SECTION B: SPATIAL ---
elif current_session == "Section B: Spatial":
    st.header("Section B: Spatial Interface")
    b1_freq = st.radio("Livestock grazing frequency near forest?", ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
    b1_dist = st.radio("Distance from forest edge?", ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
    b2_share = st.radio("Do livestock and wildlife share water sources?", ["Yes, regularly", "Yes, seasonally", "Occasionally", "Rarely", "No"])
    b2_types = st.multiselect("Types of shared water sources:", ["Natural ponds", "Streams/Rivers", "Man-made holes", "Agricultural wells", "Other"])
    if "Other" in b2_types:
        b2_other = st.text_input("Specify other water source:")
    
    if st.button("Save Section B"):
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Grazing Freq", b1_freq)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Water Sharing", b2_share)
        save_answer(p_name, p_dept, p_loc_detail, "Section B", "Water Types", b2_types)
        st.success("Section B Recorded!")

# --- SECTION C: DISEASE ---
elif current_session == "Section C: Disease":
    st.header("Section C: Disease Occurrence (Past 3 Years)")
    diseases = ["FMD", "Brucellosis", "Bovine TB", "Anthrax", "Rabies", "PPR", "HS", "Parasitic"]
    for d in diseases:
        with st.expander(f"📋 {d} Details"):
            occ = st.radio(f"Occurred?", ["No", "Yes"], key=d)
            if occ == "Yes":
                sp = st.text_input("Species affected", key=f"s_{d}")
                cs = st.text_input("Approx. cases", key=f"c_{d}")
                if st.button(f"Save {d} Data"):
                    save_answer(p_name, p_dept, p_loc_detail, "Section C", d, f"Spec:{sp}, Cases:{cs}")
                    st.toast(f"{d} data saved!")

# --- SECTION D: CONTACT ---
elif current_session == "Section D: Contact":
    st.header("Section D: Contact Pathways (Score 1-5)")
    f1_water = st.slider("Contact at water sources", 1, 5, 3)
    f1_grazing = st.slider("Contact at grazing areas", 1, 5, 3)
    f2_vector = st.slider("Tick/Mosquito density", 1, 5, 3)
    if st.button("Submit Scores"):
        save_answer(p_name, p_dept, p_loc_detail, "Section D", "Water Risk", f1_water)
        save_answer(p_name, p_dept, p_loc_detail, "Section D", "Vector Risk", f2_vector)
        st.success("Risk Scores Saved!")

# --- SECTION E: RISK ---
elif current_session == "Section E: Risk":
    st.header("Section E: Risk Factor Assessment")
    fmd_v = st.select_slider("FMD Vaccination Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
    bru_v = st.select_slider("Brucella Vaccination Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
    hs_v = st.select_slider("HS Vaccination Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
    bq_v = st.select_slider("BQ Vaccination Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
    lsd_v = st.select_slider("LSD Vaccination Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
    quarantine = st.radio("Quarantine practices for new livestock:", ["Always", "Usually", "Sometimes", "Rarely", "Never"])
    carcass = st.radio("Carcass Disposal:", ["Proper burial/burning", "Burial without lime", "Left in fields", "Dumped near forest"])
    if st.button("Save Section E"):
        save_answer(p_name, p_dept, p_loc_detail, "Section E", "Vaccination", fmd_v)
        save_answer(p_name, p_dept, p_loc_detail, "Section E", "Carcass Disposal", carcass)
        st.success("Risk Factors Saved!")

# --- SECTION F: MITIGATION ---
elif current_session == "Section F: Mitigation":
    st.header("Section F: Mitigation & Recommendations")
    interv = st.multiselect("Existing disease control measures:", ["Vaccination", "Movement restrictions", "Awareness programs", "Forest dept coordination", "Wildlife monitoring"])
    eff = st.radio("Effectiveness of current measures:", ["Highly", "Moderately", "Minimally", "Not"])
    rank1 = st.text_input("Priority Intervention 1")
    rank2 = st.text_input("Priority Intervention 2")
    if st.button("Save Recommendations"):
        save_answer(p_name, p_dept, p_loc_detail, "Section F", "Measures", interv)
        save_answer(p_name, p_dept, p_loc_detail, "Section F", "Priority 1", rank1)
        st.success("Recommendations Saved!")

# --- SECTION G: SURVEILLANCE ---
elif current_session == "Section G: Surveillance":
    st.header("Section G: Surveillance & Diagnostics")
    diag = st.radio("Availability of diagnostic facilities:", ["Within district", "Neighboring district", "Regional lab", "None"])
    time_diag = st.number_input("Average time for confirmation (days):", min_value=0)
    mechanism = st.radio("Disease reporting mechanism:", ["Active surveillance", "Passive surveillance", "No formal system"])
    frequency = st.radio("Frequency of surveillance activities:", ["Weekly", "Monthly", "Quarterly", "Only during outbreaks", "None"])
    if st.button("Finish Workshop"):
        save_answer(p_name, p_dept, p_loc_detail, "Section G", "Diagnostics", diag)
        save_answer(p_name, p_dept, p_loc_detail, "Section G", "Mechanism", mechanism)
        st.balloons()
        st.success("All data submitted. Thank you!")
