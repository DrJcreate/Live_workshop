import streamlit as st
import pandas as pd
import psycopg2 
import os
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
ADMIN_PASSWORD = "workshop_2025" 
# Note: Ensure the environment variable on Render matches 'Database_URL' exactly
DATABASE_URL = os.environ.get('Database_URL')

# --- DATABASE FETCHING ---
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
    except Exception as e:
        st.error(f"Error saving data: {e}")

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

# --- UI HEADER WITH LIVE COUNTER ---
df_count = get_data()
# Counting unique names for total participant count
total_participants = df_count['name'].nunique() if not df_count.empty else 0

col_title, col_counter = st.columns([4, 1])
with col_title:
    st.title("🌲 Wildlife-Livestock Workshop")
with col_counter:
    st.metric("Live Participants", total_participants)

# --- ADMIN SIDEBAR ---
st.sidebar.title("🛠️ Admin Control")
admin_pwd = st.sidebar.text_input("Admin Password", type="password")

# Default values
view_mode = "Participant Form"
current_session = "Registration"

if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Logged In")
    view_mode = st.sidebar.selectbox("Window", ["📝 Participant Form", "📊 Visualisations", "⚙️ Data Management"])
    current_session = st.sidebar.radio("Active Workshop Section", 
        ["Registration", "Section B: Spatial", "Section C: Disease", "Section D: Contact", "Section E: Risk", "Section F: Mitigation", "Section G: Surveillance"])
    
    if st.sidebar.button("Download CSV"):
        df = get_data()
        st.sidebar.download_button("Export Data", df.to_csv(index=False), "workshop_export.csv")

# --- WINDOW 1: VISUALISATIONS ---
if view_mode == "📊 Visualisations" and admin_pwd == ADMIN_PASSWORD:
    st.header(f"Results: {current_session}")
    df = get_data()
    
    if df.empty:
        st.warning("No data submitted yet.")
    else:
        # --- B1 VISUALS (PERCENTAGE BARS) ---
        if current_session == "Section B: Spatial":
            b_df = df[df['session_name'] == 'Section B']
            for q in ["Grazing Freq", "Sighting Freq"]:
                if not b_df[b_df['question'] == q].empty:
                    q_df = b_df[b_df['question'] == q]['answer'].value_counts(normalize=True).reset_index()
                    q_df.columns = ['Response', 'Percentage']
                    q_df['Percentage'] *= 100
                    fig = px.bar(q_df, x='Response', y='Percentage', title=f"{q} (%)", text_auto='.1f')
                    st.plotly_chart(fig)

        # --- SECTION C VISUALS (INDIVIDUAL BARS) ---
        elif current_session == "Section C: Disease":
            c_df = df[df['session_name'] == 'Section C']
            diseases = ["FMD", "Brucellosis", "Bovine TB", "Anthrax", "Rabies", "PPR", "HS", "Parasitic"]
            for d in diseases:
                d_counts = c_df[c_df['question'] == d]['answer'].value_counts().reset_index()
                if not d_counts.empty:
                    fig = px.bar(d_counts, x='answer', y='count', title=f"Reports: {d}", color='answer', color_discrete_map={'Yes':'red', 'No':'green'})
                    st.plotly_chart(fig)

        # --- SECTION D VISUALS (RADAR) ---
        elif current_session == "Section D: Contact":
            d_df = df[df['session_name'] == 'Section D']
            # Only visualize numerical 1-5 scales
            numeric_qs = ["Phys Contact: Water", "Phys Contact: Grazing", "Phys Contact: Attack", "Env: Shared Water", "Env: Pasture", "Env: Feeding Areas", "Tick Density", "Herder Fodder Risk"]
            vis_df = d_df[d_df['question'].isin(numeric_qs)].copy()
            vis_df['answer'] = pd.to_numeric(vis_df['answer'], errors='coerce')
            avg_risk = vis_df.groupby('question')['answer'].mean().reset_index()
            if not avg_risk.empty:
                fig = px.line_polar(avg_risk, r='answer', theta='question', line_close=True, title="Average Risk Profile (1-5 Scale)")
                fig.update_traces(fill='toself')
                st.plotly_chart(fig)

        # --- SECTION E VISUALS (GROUPED VACCINATION) ---
        elif current_session == "Section E: Risk":
            e_df = df[df['session_name'] == 'Section E']
            vac_df = e_df[e_df['question'] == "Vaccination"].copy()
            if not vac_df.empty:
                fig = px.histogram(vac_df, x="answer", title="Vaccination Coverage Distribution", color_discrete_sequence=['blue'])
                st.plotly_chart(fig)

        # --- SECTION F VISUALS (MITIGATION) ---
        elif current_session == "Section F: Mitigation":
            f_df = df[df['session_name'] == 'Section F']
            feas_df = f_df[f_df['question'] == 'Buffer Feasibility']['answer'].value_counts().reset_index()
            if not feas_df.empty:
                st.plotly_chart(px.pie(feas_df, values='count', names='answer', hole=0.5, title="Feasibility of Buffer Zones"))
            
            urg_df = f_df[f_df['question'] == 'Program Urgency']['answer'].value_counts().reset_index()
            if not urg_df.empty:
                st.plotly_chart(px.pie(urg_df, values='count', names='answer', hole=0.5, title="Urgency of Collaborative Program"))

        # --- SECTION G VISUALS (SURVEILLANCE) ---
        elif current_session == "Section G: Surveillance":
            g_df = df[df['session_name'] == 'Section G']
            mech_df = g_df[g_df['question'] == 'Mechanism']['answer'].value_counts(normalize=True).reset_index()
            if not mech_df.empty:
                mech_df.columns = ['Mechanism', 'Percentage']
                mech_df['Percentage'] *= 100
                st.plotly_chart(px.bar(mech_df, x='Mechanism', y='Percentage', title="Reporting Mechanisms (%)"))

# --- WINDOW 2: DATA MANAGEMENT ---
elif view_mode == "⚙️ Data Management" and admin_pwd == ADMIN_PASSWORD:
    st.header("⚙️ Data Review & Deletion")
    df = get_data()
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    del_id = st.number_input("Enter Row ID to Delete", min_value=1, step=1)
    if st.button("Confirm Deletion"):
        if delete_row(del_id):
            st.success(f"Row {del_id} deleted.")
            st.rerun()
        else:
            st.error("Failed to delete.")

# --- WINDOW 3: PARTICIPANT FORM ---
else:
    # Capturing Identity first so it is available for all sections
    p_name = st.text_input("Full Name")
    p_dept = st.selectbox("Select Department", ["Select...", "Forest Department", "Animal Husbandry Department"])

    p_loc_detail = ""
    if p_dept == "Forest Department":
        p_loc_detail = st.selectbox("Select Tiger Reserve/Safari", ["Kanha", "Pench", "Panna", "Satpura", "Ratapani", "Bandhavgarh", "Sanjay", "Van Vihar", "MMSJ", "White Tiger Safari"])
    elif p_dept == "Animal Husbandry Department":
        dist_col, blk_col = st.columns(2)
        with dist_col: dist = st.text_input("District")
        with blk_col: blk = st.text_input("Block")
        inst = st.text_input("Institution")
        p_loc_detail = f"{dist} | {blk} | {inst}"

    st.divider()
    st.write(f"Active Session: **{current_session}**")

    # --- REGISTRATION ---
    if current_session == "Registration":
        st.header("Step 1: Registration")
        p_desig = st.text_input("Designation")
        p_email = st.text_input("Email")
        p_phone = st.text_input("Phone")
        p_exp = st.text_input("Years of Experience")
        
        if st.button("Save Registration"):
            if p_name and p_dept != "Select...":
                save_answer(p_name, p_dept, p_loc_detail, "Registration", "Profile", f"{p_desig}, {p_email}, {p_phone}, {p_exp}")
                st.success("Registration Saved!")
            else:
                st.warning("Please enter your name and department.")

    # --- SECTION B: SPATIAL ---
    elif current_session == "Section B: Spatial":
        st.header("Section B: Spatial Interface & Contact Patterns")
        st.subheader("B1. Grazing Patterns")
        b1_freq = st.radio("Livestock grazing frequency near forest?", ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
        b1_dist = st.radio("Distance from forest edge?", ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
        b1_count = st.number_input("Approximate number of livestock entering forest daily:", min_value=0)

        st.subheader("B2. Water Source Sharing")
        b2_share = st.radio("Do livestock and wildlife share water sources?", ["Yes, regularly", "Yes, seasonally", "Occasionally", "Rarely", "No"])
        b2_types = st.multiselect("Type of shared water sources:", ["Natural ponds/lakes", "Streams/rivers", "Man-made water holes", "Agricultural wells", "Other"])

        st.subheader("B3. Wildlife Movement")
        b3_freq = st.radio("Frequency of wildlife sightings in grazing areas:", ["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"])
        b3_species = st.multiselect("Wildlife species commonly observed near livestock:", ["Wild boar", "Deer (Chital/Sambar)", "Gaur/Wild buffalo", "Nilgai", "Carnivores (Tiger/Leopard/Wild dogs)", "Other"])

        if st.button("Save Section B"):
            save_answer(p_name, p_dept, p_loc_detail, "Section B", "Grazing Freq", b1_freq)
            save_answer(p_name, p_dept, p_loc_detail, "Section B", "Sighting Freq", b3_freq)
            save_answer(p_name, p_dept, p_loc_detail, "Section B", "Species Observed", b3_species)
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

    # --- SECTION D: CONTACT PATHWAYS ---
    elif current_session == "Section D: Contact":
        st.header("Section D: Contact Pathways & Predation")
        st.subheader("D1. Physical Contact Pathways (Score 1-5)")
        d1_phys_water = st.slider("At water sources", 1, 5, 3, key="d1_w")
        d1_phys_grazing = st.slider("At grazing areas", 1, 5, 3, key="d1_g")
        d1_phys_attack = st.slider("During wildlife attacks on livestock", 1, 5, 3, key="d1_a")

        st.subheader("D2. Wildlife Predation")
        pred_incidents = st.radio("Number of wildlife predation incidents per month:", ["1-2", "3-5", "More than 10"])
        pred_species = st.multiselect("Most affected species:", ["Cattle", "Buffalo", "Goat", "Other"])
        
        st.subheader("D3. Indirect Contact (Score 1-5)")
        d3_env_water = st.slider("Shared water sources", 1, 5, 3, key="d3_w")
        d3_env_pasture = st.slider("Pasture contamination", 1, 5, 3, key="d3_p")
        d3_env_feeding = st.slider("Shared feeding areas", 1, 5, 3, key="d3_f")

        st.subheader("D4. Vectors & Fomites (Score 1-5)")
        tick_density = st.slider("Tick density in shared areas", 1, 5, 3)
        mosq_density = st.slider("Mosquito/fly abundance", 1, 5, 3)
        herder_fodder = st.slider("Risk: Herders entering forest for fodder", 1, 5, 3)
        forest_products = st.slider("Risk: Collection of forest products", 1, 5, 3)

        if st.button("Submit Section D"):
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Phys Contact: Water", d1_phys_water)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Phys Contact: Grazing", d1_phys_grazing)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Phys Contact: Attack", d1_phys_attack)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Predation Incidents", pred_incidents)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Env: Shared Water", d3_env_water)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Env: Pasture", d3_env_pasture)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Env: Feeding Areas", d3_env_feeding)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Tick Density", tick_density)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Herder Fodder Risk", herder_fodder)
            save_answer(p_name, p_dept, p_loc_detail, "Section D", "Forest Product Risk", forest_products)
            st.success("Section D responses recorded!")

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
        interv = st.multiselect("Existing disease control measures:", ["Regular vaccination campaigns", "Movement restrictions", "Awareness programs", "Forest department coordination", "Wildlife health monitoring", "Other"])
        eff = st.radio("Effectiveness of current measures:", ["Highly effective", "Moderately effective", "Minimally effective", "Not effective"])
        rank1 = st.text_input("Priority Intervention 1")
        buffer_feasibility = st.radio("Feasibility of implementing buffer zones:", ["Highly feasible", "Moderately feasible", "Difficult", "Not feasible"])
        program_need = st.radio("Need for collaborative health program:", ["Urgent", "Important", "Desirable", "Not necessary"])

        if st.button("Save Recommendations"):
            save_answer(p_name, p_dept, p_loc_detail, "Section F", "Buffer Feasibility", buffer_feasibility)
            save_answer(p_name, p_dept, p_loc_detail, "Section F", "Program Urgency", program_need)
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
