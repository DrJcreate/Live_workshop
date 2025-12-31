import streamlit as st
import pandas as pd
import psycopg2 
import os
import plotly.express as px

# --- CONFIGURATION ---
ADMIN_PASSWORD = "workshop_2025" 
DATABASE_URL = os.environ.get('Database_URL')

# --- DATABASE LOGIC ---
def get_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql_query("SELECT * FROM workshop_data", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def save_answer(name, dept, loc, session, q, ans):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO workshop_data (name, dept, location_info, session_name, question, answer) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, dept, loc, session, q, str(ans)))
        conn.commit()
        cur.close()
        conn.close()
    except:
        st.error("Error saving to database.")

def delete_row(row_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM workshop_data WHERE id = %s", (row_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

# --- UI HEADER & LIVE COUNTER ---
st.set_page_config(layout="wide", page_title="Wildlife-Livestock Workshop")
df_count = get_data()
total_participants = df_count['name'].nunique() if not df_count.empty else 0

col_t, col_c = st.columns([4, 1])
with col_t:
    st.title("🌲 Wildlife-Livestock Interface Workshop")
with col_c:
    st.metric("Live Participants", total_participants)

# --- ADMIN SIDEBAR ---
st.sidebar.title("🛠️ Controller")
admin_pwd = st.sidebar.text_input("Password", type="password")

view_mode = "Participant Form"
current_session = "Registration"

if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Admin Access")
    view_mode = st.sidebar.selectbox("Select Window", ["📝 Participant Form", "📊 Visualisations", "⚙️ Data Management"])
    current_session = st.sidebar.radio("Active Session", 
        ["Registration", "Section B: Spatial", "Section C: Disease", "Section D: Contact", "Section E: Risk", "Section F: Mitigation", "Section G: Surveillance"])
    
    if st.sidebar.button("Download Data"):
        df = get_data()
        st.sidebar.download_button("CSV Export", df.to_csv(index=False), "workshop_data.csv")

# --- WINDOW 1: VISUALISATIONS ---
if view_mode == "📊 Visualisations" and admin_pwd == ADMIN_PASSWORD:
    st.header(f"Projector View: {current_session}")
    df = get_data()
    
    if df.empty:
        st.info("Waiting for data...")
    else:
        if current_session == "Section B: Spatial":
            b_qs = ["Grazing Freq", "Grazing Distance", "Water Sharing", "Sighting Freq"]
            for q in b_qs:
                q_df = df[(df['session_name'] == 'Section B') & (df['question'] == q)]
                if not q_df.empty:
                    counts = q_df['answer'].value_counts(normalize=True).reset_index()
                    counts.columns = ['Option', 'Percentage']
                    counts['Percentage'] *= 100
                    st.plotly_chart(px.bar(counts, x='Option', y='Percentage', title=f"{q} (%)", text_auto='.1f'))

        elif current_session == "Section C: Disease":
            c_df = df[df['session_name'] == 'Section C']
            if not c_df.empty:
                yes_df = c_df[c_df['answer'].str.contains("Yes", na=False)]
                disease_counts = yes_df['question'].value_counts().reset_index()
                disease_counts.columns = ['Disease', 'Reports']
                st.plotly_chart(px.bar(disease_counts, x='Disease', y='Reports', title="Disease Presence (Yes Counts Only)"))

        elif current_session == "Section D: Contact":
            d_df = df[df['session_name'] == 'Section D'].copy()
            d_df['num_ans'] = pd.to_numeric(d_df['answer'], errors='coerce')
            d_avg = d_df.groupby('question')['num_ans'].mean().reset_index().dropna()
            st.plotly_chart(px.bar(d_avg, x='question', y='num_ans', title="Mean Risk Scores (1-5 Scale)"))

        elif current_session == "Section E: Risk":
            e_df = df[df['session_name'] == 'Section E']
            vac_df = e_df[e_df['question'].str.contains("Vac")].copy()
            if not vac_df.empty:
                fig = px.histogram(vac_df, x="question", color="answer", barmode="relative", barnorm='percent', 
                                   title="Vaccination Profile (%)", category_orders={"answer": ["<20%", "20-40%", "40-60%", "60-80%", ">80%"]})
                st.plotly_chart(fig)

        elif current_session in ["Section F: Mitigation", "Section G: Surveillance"]:
            curr_df = df[df['session_name'] == current_session]
            for q in curr_df['question'].unique():
                q_counts = curr_df[curr_df['question'] == q]['answer'].value_counts(normalize=True).reset_index()
                q_counts.columns = ['Option', 'Percentage']
                q_counts['Percentage'] *= 100
                st.plotly_chart(px.bar(q_counts, x='Option', y='Percentage', title=f"{q} (%)", text_auto='.1f'))

# --- WINDOW 2: DATA MANAGEMENT ---
elif view_mode == "⚙️ Data Management" and admin_pwd == ADMIN_PASSWORD:
    st.header("⚙️ Data Management")
    df = get_data()
    st.dataframe(df, use_container_width=True)
    del_id = st.number_input("ID to Delete", min_value=1, step=1)
    if st.button("Delete Row"):
        if delete_row(del_id): st.rerun()

# --- WINDOW 3: PARTICIPANT FORM ---
else:
    p_name = st.text_input("Full Name")
    p_dept = st.selectbox("Department", ["Select...", "Forest Department", "Animal Husbandry Department"])
    
    p_loc = ""
    if p_dept == "Forest Department":
        p_loc = st.selectbox("Select Tiger Reserve/Safari", ["Kanha", "Pench", "Panna", "Satpura", "Ratapani", "Bandhavgarh", "Sanjay", "Van Vihar", "MMSJ", "White Tiger Safari"])
    elif p_dept == "Animal Husbandry Department":
        p_loc = st.text_input("District and Block")

    st.divider()
    
    if current_session == "Registration":
        st.header("Registration")
        p_desig = st.text_input("Designation")
        p_exp = st.text_input("Years of Experience")
        if st.button("Register"):
            save_answer(p_name, p_dept, p_loc, "Registration", "Profile", f"{p_desig} | {p_exp}")
            st.success("Registered!")

    elif current_session == "Section B: Spatial":
        st.header("Section B: Spatial")
        b1 = st.radio("Grazing Frequency", ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
        b2 = st.radio("Grazing Distance", ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
        b3 = st.radio("Water Sharing", ["Regularly", "Seasonally", "Occasionally", "Rarely", "No"])
        b4 = st.multiselect("Shared Water Types", ["Natural ponds", "Streams/Rivers", "Man-made holes", "Agricultural wells", "Other"])
        b5 = st.multiselect("Wildlife Observed Near Livestock", ["Wild boar", "Deer", "Gaur", "Nilgai", "Carnivores", "Other"])
        b6 = st.radio("Sighting Frequency", ["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"])
        if st.button("Save Section B"):
            save_answer(p_name, p_dept, p_loc, "Section B", "Grazing Freq", b1)
            save_answer(p_name, p_dept, p_loc, "Section B", "Grazing Distance", b2)
            save_answer(p_name, p_dept, p_loc, "Section B", "Water Sharing", b3)
            save_answer(p_name, p_dept, p_loc, "Section B", "Sighting Freq", b6)
            st.success("Section B Saved")

    elif current_session == "Section C: Disease":
        st.header("Section C: Disease (Last 3 Years)")
        diseases = ["FMD", "Anthrax", "Rabies", "HS", "PPR", "Brucellosis", "Bovine TB", "Parasitic"]
        for d in diseases:
            occ = st.radio(f"{d} Outbreak?", ["No", "Yes"], key=d)
            if st.button(f"Save {d}", key=f"btn_{d}"):
                save_answer(p_name, p_dept, p_loc, "Section C", d, occ)
                st.toast(f"{d} Saved")

    elif current_session == "Section D: Contact":
        st.header("Section D: Contact & Risk (Score 1-5)")
        st.subheader("Direct Physical Contact")
        d1 = st.slider("At water sources", 1, 5, 3)
        d2 = st.slider("At grazing areas", 1, 5, 3)
        d3 = st.slider("During wildlife attacks", 1, 5, 3)
        
        st.subheader("Wildlife Predation")
        d4 = st.radio("Number of incidents per month:", ["1-2", "3-5", "More than 10"])
        d5 = st.multiselect("Most affected species:", ["Cattle", "Buffalo", "Goat", "Other"])
        
        st.subheader("Indirect/Environmental Contact")
        d6 = st.slider("Shared water sources", 1, 5, 3)
        d7 = st.slider("Pasture contamination", 1, 5, 3)
        d8 = st.slider("Shared feeding areas", 1, 5, 3)
        
        st.subheader("Vectors & Fomites")
        d9 = st.slider("Tick density in shared areas", 1, 5, 3)
        # CORRECTED QUESTIONS BELOW
        d10 = st.slider("Herders entering forest for fodder", 1, 5, 3)
        d11 = st.slider("Collection of forest products", 1, 5, 3)
        
        if st.button("Submit Section D"):
            save_answer(p_name, p_dept, p_loc, "Section D", "Phys: Water", d1)
            save_answer(p_name, p_dept, p_loc, "Section D", "Phys: Grazing", d2)
            save_answer(p_name, p_dept, p_loc, "Section D", "Phys: Attack", d3)
            save_answer(p_name, p_dept, p_loc, "Section D", "Predation Count", d4)
            save_answer(p_name, p_dept, p_loc, "Section D", "Env: Shared Water", d6)
            save_answer(p_name, p_dept, p_loc, "Section D", "Env: Pasture", d7)
            save_answer(p_name, p_dept, p_loc, "Section D", "Tick Density", d9)
            save_answer(p_name, p_dept, p_loc, "Section D", "Herders in Forest", d10)
            save_answer(p_name, p_dept, p_loc, "Section D", "Forest Product Collection", d11)
            st.success("Section D Saved")

    elif current_session == "Section E: Risk":
        st.header("Section E: Risk & Vaccination")
        v_diseases = ["FMD Vac", "Brucella Vac", "HS Vac", "BQ Vac", "LSD Vac"]
        for v in v_diseases:
            cov = st.select_slider(f"{v} Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"], key=v)
            if st.button(f"Save {v}", key=f"v_{v}"):
                save_answer(p_name, p_dept, p_loc, "Section E", v, cov)
        
        st.divider()
        quarantine = st.radio("Quarantine practices for new livestock:", ["Always", "Usually", "Sometimes", "Rarely", "Never"])
        carcass = st.radio("Carcass Disposal", ["Proper burial/burning", "Burial without lime", "Left in fields", "Dumped near forest"])
        
        if st.button("Save Biosecurity Settings"):
            save_answer(p_name, p_dept, p_loc, "Section E", "Quarantine", quarantine)
            save_answer(p_name, p_dept, p_loc, "Section E", "Carcass Disposal", carcass)
            st.success("E Saved")

    elif current_session == "Section F: Mitigation":
        st.header("Section F: Recommendations")
        f1 = st.radio("Feasibility of buffer zones:", ["Highly feasible", "Moderately feasible", "Difficult", "Not feasible"])
        f2 = st.radio("Urgency of collaborative program:", ["Urgent", "Important", "Desirable", "Not necessary"])
        f3 = st.multiselect("Existing control measures:", ["Vaccination", "Movement restrictions", "Awareness", "Wildlife monitoring"])
        if st.button("Save Section F"):
            save_answer(p_name, p_dept, p_loc, "Section F", "Buffer Feasibility", f1)
            save_answer(p_name, p_dept, p_loc, "Section F", "Program Urgency", f2)
            st.success("Section F Saved")

    elif current_session == "Section G: Surveillance":
        st.header("Section G: Surveillance & Diagnostics")
        # ADDED DIAGNOSTIC TEST QUESTIONS
        st.subheader("G1. Diagnostics")
        g1 = st.radio("Diagnostic facility availability:", ["Within district", "Neighboring district", "Regional lab", "None"])
        g2 = st.multiselect("Available diagnostic tests:", ["ELISA", "PCR", "Culture & Sensitivity", "Rapid Tests/Kits", "Microscopy"])
        
        st.subheader("G2. Reporting")
        g3 = st.radio("Disease reporting mechanism:", ["Active surveillance", "Passive surveillance", "No formal system"])
        g4 = st.radio("Surveillance activity frequency:", ["Weekly", "Monthly", "Quarterly", "Outbreaks only", "None"])
        
        if st.button("Finish Workshop"):
            save_answer(p_name, p_dept, p_loc, "Section G", "Facility", g1)
            save_answer(p_name, p_dept, p_loc, "Section G", "Tests", g2)
            save_answer(p_name, p_dept, p_loc, "Section G", "Mechanism", g3)
            save_answer(p_name, p_dept, p_loc, "Section G", "Frequency", g4)
            st.balloons()
            st.success("All data submitted. Thank you!")
