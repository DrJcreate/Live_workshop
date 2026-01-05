import streamlit as st
import pandas as pd
import psycopg2 
import os
import plotly.express as px
import random  # for dummy data generation

# --- CONFIGURATION ---
ADMIN_PASSWORD = "admin_2027" 
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
        cur.execute(
            "INSERT INTO workshop_data (name, dept, location_info, session_name, question, answer) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, dept, loc, session, q, str(ans))
        )
        conn.commit()
        cur.close()
        conn.close()
    except:
        st.error("Error saving to database.")

# --- DUMMY DATA GENERATOR FOR TESTING VISUALS ---
def run_test_simulation(n_participants: int = 40):
    """
    Populate the database with dummy data for visual testing.
    Generates at least `n_participants` test participants.
    Uses the same question labels and categories as the current form.
    """

    # Create a list of synthetic participant names
    test_participants = [
        f"Test_Participant_{i+1:02d}" for i in range(n_participants)
    ]

    for p_name in test_participants:
        p_dept = random.choice(["Forest Department", "Animal Husbandry Department"])
        p_loc = "Test Sanctuary" if p_dept == "Forest Department" else "Test District"

        # ---------- Section B: Spatial ----------
        save_answer(
            p_name, p_dept, p_loc, "Section B", "Grazing Freq",
            random.choice(["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section B", "Grazing Distance",
            random.choice(["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section B", "Water Sharing",
            random.choice(["Regularly", "Seasonally", "Occasionally", "Rarely", "No"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section B", "Sighting Freq",
            random.choice(["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"])
        )

        # ---------- Section C: Disease ----------
        diseases = ["FMD", "Anthrax", "Rabies", "HS", "PPR", "Brucellosis", "Bovine TB", "Parasitic"]
        for d in diseases:
            save_answer(
                p_name, p_dept, p_loc, "Section C", d,
                random.choice(["Yes", "No"])
            )

        # ---------- Section D: Contact ----------
        for q in [
            "Phys: Water",
            "Phys: Grazing",
            "Phys: Attack",
            "Env: Shared Water",
            "Env: Pasture",
            "Tick Density",
            "Herders in Forest",
            "Forest Product Collection",
        ]:
            save_answer(
                p_name, p_dept, p_loc, "Section D", q,
                random.randint(1, 5)
            )

        save_answer(
            p_name, p_dept, p_loc, "Section D", "Predation Count",
            random.choice(["1-2", "3-5", "More than 10"])
        )

        # ---------- Section E: Vaccination + biosecurity ----------
        for v in ["FMD Vac", "Brucella Vac", "HS Vac", "BQ Vac", "LSD Vac"]:
            save_answer(
                p_name, p_dept, p_loc, "Section E", v,
                random.choice(["<20%", "20-40%", "40-60%", "60-80%", ">80%"])
            )

        save_answer(
            p_name, p_dept, p_loc, "Section E", "Quarantine",
            random.choice(["Always", "Usually", "Sometimes", "Rarely", "Never"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section E", "Carcass Disposal",
            random.choice([
                "Proper burial/burning",
                "Burial without lime",
                "Left in fields",
                "Dumped near forest"
            ])
        )

        # ---------- Section F: Mitigation ----------
        save_answer(
            p_name, p_dept, p_loc, "Section F", "Buffer Feasibility",
            random.choice(["Highly feasible", "Moderately feasible", "Difficult", "Not feasible"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section F", "Program Urgency",
            random.choice(["Urgent", "Important", "Desirable", "Not necessary"])
        )

        # ---------- Section G: Surveillance & diagnostics ----------
        save_answer(
            p_name, p_dept, p_loc, "Section G", "Facility",
            random.choice(["Within district", "Neighboring district", "Regional lab", "None"])
        )

        all_tests = ["ELISA", "PCR", "Culture & Sensitivity", "Rapid Tests/Kits", "Microscopy"]
        tests_subset = random.sample(all_tests, k=random.randint(1, len(all_tests)))
        save_answer(
            p_name, p_dept, p_loc, "Section G", "Tests",
            tests_subset
        )

        save_answer(
            p_name, p_dept, p_loc, "Section G", "Mechanism",
            random.choice(["Active surveillance", "Passive surveillance", "No formal system"])
        )
        save_answer(
            p_name, p_dept, p_loc, "Section G", "Frequency",
            random.choice(["Weekly", "Monthly", "Quarterly", "Outbreaks only", "None"])
        )


# --- RESET DATABASE FUNCTION ---
def clear_all_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE workshop_data RESTART IDENTITY")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

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

# defaults for non-admin
view_mode = "Participant Form"
current_session = "Registration"

if admin_pwd == ADMIN_PASSWORD:
    st.sidebar.success("Admin Access")

    # --- BASIC CONTROLS ---
    view_mode = st.sidebar.selectbox(
        "Select Window",
        ["📝 Participant Form", "📊 Visualisations", "⚙️ Data Management"]
    )
    current_session = st.sidebar.radio(
        "Active Session",
        [
            "Registration",
            "Section B: Spatial",
            "Section C: Disease",
            "Section D: Contact",
            "Section E: Risk",
            "Section F: Mitigation",
            "Section G: Surveillance"
        ]
    )

    # --- DATA EXPORT ---
    st.sidebar.markdown("### Data export")
    if st.sidebar.button("Download Data"):
        df = get_data()
        st.sidebar.download_button(
            "CSV Export",
            df.to_csv(index=False),
            "workshop_data.csv"
        )

    # --- TEST MODE: RESET + DUMMY DATA ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Testing tools")

    test_mode = st.sidebar.checkbox(
        "Enable test mode (load dummy data)",
        key="test_mode_checkbox"
    )

    if test_mode:
        if st.sidebar.button("Reset DB with dummy test data"):
            if clear_all_data():
                run_test_simulation()
                st.sidebar.success("Database cleared and dummy data loaded.")
                st.rerun()
            else:
                st.sidebar.error("Failed to clear database. Check DB connection.")

    # --- DANGER ZONE: HARD WIPE ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Danger zone")

    confirm_wipe = st.sidebar.checkbox(
        "I confirm I want to delete ALL records",
        key="confirm_wipe_checkbox"
    )

    if st.sidebar.button("⚠️ Wipe ALL data", key="wipe_all_button"):
        if confirm_wipe:
            ok = clear_all_data()
            if ok:
                st.sidebar.success("All data deleted. Database is now empty.")
                st.rerun()
            else:
                st.sidebar.error("Could not clear database. Check DB connection.")
        else:
            st.sidebar.warning("Tick the confirmation box first.")


# --- WINDOW 1: VISUALISATIONS ---
if view_mode == "📊 Visualisations" and admin_pwd == ADMIN_PASSWORD:
    st.header(f"Projector View: {current_session}")
    df = get_data()
    
    if df.empty:
        st.info("Waiting for participant data...")
    else:
                # --- SECTION B: SPATIAL VISUALS ---
        if current_session == "Section B: Spatial":
            b_df = df[df['session_name'] == 'Section B'].copy()

            if b_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.subheader("Section B: Spatial – Group Results")

                st.markdown("### Snapshot: What are people reporting?")

                question_order = {
                    "Grazing Freq": ["Daily", "4-6 times/week", "2-3 times/week", "Occasionally", "Rarely/Never"],
                    "Grazing Distance": ["Inside forest", "0-500m", "500m-1km", "1-2km", ">2km"],
                    "Water Sharing": ["Regularly", "Seasonally", "Occasionally", "Rarely", "No"],
                    "Sighting Freq": ["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"]
                }

                snapshot_questions = list(question_order.keys())

                for q in snapshot_questions:
                    q_df = b_df[b_df["question"] == q]

                    if not q_df.empty:
                        n = len(q_df)

                        counts = (
                            q_df["answer"]
                            .value_counts(normalize=True)
                            .mul(100)
                            .reindex(question_order[q])
                            .reset_index()
                        )
                        counts.columns = ["Response", "Percentage"]

                        fig = px.bar(
                            counts,
                            x="Response",
                            y="Percentage",
                            title=f"{q} (n = {n})",
                            text=counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                        )

                        fig.update_traces(textposition="outside")
                        fig.update_layout(
                            yaxis_title="Percentage of respondents",
                            xaxis_title="",
                            uniformtext_minsize=8,
                            uniformtext_mode='show',
                            showlegend=False
                        )

                        st.plotly_chart(fig, use_container_width=True)

        # --- SECTION C: DISEASE VISUALS ---
        elif current_session == "Section C: Disease":
            c_df = df[df["session_name"] == "Section C"].copy()

            if c_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.header("Section C: Disease (Last 3 Years)")

                if "id" in c_df.columns:
                    c_df = (
                        c_df.sort_values("id")
                        .drop_duplicates(subset=["name", "question"], keep="last")
                    )

                c_df = c_df[c_df["answer"].notna()]

                st.subheader("Outbreak reporting by disease")

                counts = (
                    c_df.groupby(["question", "answer"])["name"]
                    .nunique()
                    .reset_index(name="Participants")
                )

                if counts.empty:
                    st.info("No valid disease responses yet.")
                else:
                    counts["Total"] = counts.groupby("question")["Participants"].transform("sum")
                    counts["Percentage"] = counts["Participants"] / counts["Total"] * 100

                    yes_pct = counts[counts["answer"] == "Yes"].copy()

                    all_diseases = c_df["question"].unique()
                    yes_pct = yes_pct.set_index("question").reindex(all_diseases).reset_index()
                    yes_pct["answer"] = yes_pct["answer"].fillna("Yes")
                    yes_pct["Participants"] = yes_pct["Participants"].fillna(0)
                    yes_pct["Total"] = yes_pct["Total"].fillna(0)
                    yes_pct["Percentage"] = yes_pct["Percentage"].fillna(0)

                    fig_yes = px.bar(
                        yes_pct,
                        x="question",
                        y="Percentage",
                        title="Percentage of participants reporting outbreaks (Yes)",
                        text=yes_pct["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_yes.update_traces(textposition="outside")
                    fig_yes.update_layout(
                        xaxis_title="Disease",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_yes, use_container_width=True)

                    with st.expander("Show counts for Yes and No by disease"):
                        st.dataframe(counts.sort_values(["question", "answer"]), use_container_width=True)

                st.subheader("Where are outbreaks reported?")

                yes_df = c_df[c_df["answer"] == "Yes"].copy()

                if yes_df.empty:
                    st.info("No 'Yes' outbreak reports yet.")
                else:
                    heat = (
                        yes_df.groupby(["location_info", "question"])["name"]
                        .nunique()
                        .reset_index(name="Participants reporting outbreak")
                    )

                    loc_order = (
                        heat.groupby("location_info")["Participants reporting outbreak"]
                        .sum()
                        .sort_values(ascending=False)
                        .index
                        .tolist()
                    )

                    heat["location_info"] = pd.Categorical(
                        heat["location_info"],
                        categories=loc_order,
                        ordered=True
                    )

                    heat = heat.sort_values(["location_info", "question"])

                    fig_heat = px.density_heatmap(
                        heat,
                        x="question",
                        y="location_info",
                        z="Participants reporting outbreak",
                        color_continuous_scale="Reds",
                        title="Reported outbreaks by location and disease",
                    )
                    fig_heat.update_layout(
                        xaxis_title="Disease",
                        yaxis_title="Location"
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)

                st.subheader("How many different diseases are reported per location?")

                if yes_df.empty:
                    st.info("No disease breadth to show yet, as there are no 'Yes' reports.")
                else:
                    breadth = (
                        yes_df.groupby("location_info")["question"]
                        .nunique()
                        .reset_index(name="Diseases_reported")
                    )

                    breadth = breadth.sort_values("Diseases_reported", ascending=False)

                    fig_breadth = px.bar(
                        breadth,
                        x="location_info",
                        y="Diseases_reported",
                        title="Number of distinct diseases with reported outbreaks per location"
                    )
                    fig_breadth.update_layout(
                        xaxis_title="Location",
                        yaxis_title="Number of diseases with at least one outbreak reported"
                    )
                    st.plotly_chart(fig_breadth, use_container_width=True)

        # --- SECTION D: CONTACT & RISK VISUALS ---
        elif current_session == "Section D: Contact":
            d_df = df[df["session_name"] == "Section D"].copy()

            if d_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.header("Section D: Contact and Risk (1–5 scores)")

                if "id" in d_df.columns:
                    d_df = (
                        d_df.sort_values("id")
                        .drop_duplicates(subset=["name", "question"], keep="last")
                    )

                d_df["num_ans"] = pd.to_numeric(d_df["answer"], errors="coerce")

                risk_questions = [
                    "Phys: Water",
                    "Phys: Grazing",
                    "Phys: Attack",
                    "Env: Shared Water",
                    "Env: Pasture",
                    "Tick Density",
                    "Herders in Forest",
                    "Forest Product Collection",
                ]

                numeric_df = d_df[d_df["question"].isin(risk_questions)].copy()
                numeric_df = numeric_df.dropna(subset=["num_ans"])

                if numeric_df.empty:
                    st.info("No numeric contact scores recorded yet.")
                else:
                    question_cat = pd.CategoricalDtype(categories=risk_questions, ordered=True)
                    numeric_df["question"] = numeric_df["question"].astype(question_cat)

                    st.subheader("Average risk scores by contact pathway")

                    d_avg = (
                        numeric_df.groupby("question")["num_ans"]
                        .mean()
                        .reset_index()
                        .dropna()
                    )
                    d_avg = d_avg.sort_values("question")

                    fig_bar = px.bar(
                        d_avg,
                        x="question",
                        y="num_ans",
                        title="Mean risk score (1–5 scale)",
                        text=d_avg["num_ans"].apply(lambda x: f"{x:.2f}")
                    )
                    fig_bar.update_traces(textposition="outside")
                    fig_bar.update_layout(
                        xaxis_title="Contact pathway",
                        yaxis_title="Mean score (1–5)",
                        yaxis=dict(range=[1, 5]),
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.subheader("Overall contact profile (radar plot)")

                    fig_radar = px.line_polar(
                        d_avg,
                        r="num_ans",
                        theta="question",
                        line_close=True,
                        range_r=[1, 5],
                        title="Mean contact risk profile across all participants"
                    )
                    fig_radar.update_traces(fill="toself")
                    st.plotly_chart(fig_radar, use_container_width=True)

                    st.subheader("Average contact score by location")

                    per_person = (
                        numeric_df.groupby(["name", "location_info"])["num_ans"]
                        .mean()
                        .reset_index(name="MeanScore")
                    )

                    loc_scores = (
                        per_person.groupby("location_info")["MeanScore"]
                        .mean()
                        .reset_index(name="MeanContactScore")
                    )

                    if not loc_scores.empty:
                        loc_scores = loc_scores.sort_values("MeanContactScore", ascending=False)

                        fig_loc = px.bar(
                            loc_scores,
                            x="location_info",
                            y="MeanContactScore",
                            title="Mean contact risk score by location",
                            text=loc_scores["MeanContactScore"].apply(lambda x: f"{x:.2f}")
                        )
                        fig_loc.update_traces(textposition="outside")
                        fig_loc.update_layout(
                            xaxis_title="Location",
                            yaxis_title="Mean contact score (1–5)",
                            yaxis=dict(range=[1, 5])
                        )
                        st.plotly_chart(fig_loc, use_container_width=True)
                    else:
                        st.info("No location information available for contact scores.")

                st.subheader("Wildlife predation incidents per month")

                pred_df = d_df[d_df["question"] == "Predation Count"].copy()

                if pred_df.empty:
                    st.info("No predation incident data recorded yet.")
                else:
                    pred_counts = (
                        pred_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    pred_counts.columns = ["Incidents_per_month", "Percentage"]

                    order = ["1-2", "3-5", "More than 10"]
                    pred_counts["Incidents_per_month"] = pd.Categorical(
                        pred_counts["Incidents_per_month"],
                        categories=order,
                        ordered=True
                    )
                    pred_counts = pred_counts.sort_values("Incidents_per_month")

                    fig_pred = px.bar(
                        pred_counts,
                        x="Incidents_per_month",
                        y="Percentage",
                        title="Distribution of reported predation incidents per month",
                        text=pred_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_pred.update_traces(textposition="outside")
                    fig_pred.update_layout(
                        xaxis_title="Number of incidents per month",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_pred, use_container_width=True)

        # --- SECTION E: RISK & VACCINATION VISUALS (FOUR DISEASES ONLY) ---
# --- SECTION E: RISK & VACCINATION VISUALS (FOUR DISEASES ONLY) ---
        elif current_session == "Section E: Risk":
            e_df = df[df["session_name"] == "Section E"].copy()

            if e_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.header("Section E: Vaccination, Biosecurity and Risk")

                if "id" in e_df.columns:
                    e_df = (
                        e_df.sort_values("id")
                        .drop_duplicates(subset=["name", "question"], keep="last")
                    )

                e_df = e_df[e_df["answer"].notna()]

                vac_questions = ["FMD Vac", "HS Vac", "BQ Vac", "LSD Vac"]

                vac_df = e_df[e_df["question"].isin(vac_questions)].copy()

                coverage_order = ["<20%", "20-40%", "40-60%", "60-80%", ">80%"]

                coverage_score_map = {
                    "<20%": 1,
                    "20-40%": 2,
                    "40-60%": 3,
                    "60-80%": 4,
                    ">80%": 5
                }

                st.subheader("Average vaccination coverage score (1 low, 5 high)")

                if vac_df.empty:
                    st.info("No vaccination coverage data recorded yet for FMD, HS, BQ and LSD.")
                else:
                    vac_df["CoverageScore"] = vac_df["answer"].map(coverage_score_map)

                    avg_cov = (
                        vac_df.groupby("question")["CoverageScore"]
                        .mean()
                        .reset_index()
                        .dropna()
                    )

                    avg_cov["question"] = pd.Categorical(
                        avg_cov["question"],
                        categories=vac_questions,
                        ordered=True
                    )
                    avg_cov = avg_cov.sort_values("question")

                    fig_avg = px.bar(
                        avg_cov,
                        x="question",
                        y="CoverageScore",
                        title="Average coverage score by vaccine (FMD, HS, BQ, LSD)",
                        text=avg_cov["CoverageScore"].apply(lambda x: f"{x:.2f}")
                    )
                    fig_avg.update_traces(textposition="outside")
                    fig_avg.update_layout(
                        xaxis_title="Vaccination type",
                        yaxis_title="Mean coverage score (1–5)",
                        yaxis=dict(range=[1, 5]),
                        showlegend=False
                    )
                    st.plotly_chart(fig_avg, use_container_width=True)

                st.subheader("Quarantine practices for new livestock")

                q_df = e_df[e_df["question"] == "Quarantine"].copy()

                if q_df.empty:
                    st.info("No quarantine responses recorded yet.")
                else:
                    q_counts = (
                        q_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    q_counts.columns = ["Response", "Percentage"]

                    q_order = ["Always", "Usually", "Sometimes", "Rarely", "Never"]
                    q_counts["Response"] = pd.Categorical(
                        q_counts["Response"],
                        categories=q_order,
                        ordered=True
                    )
                    q_counts = q_counts.sort_values("Response")

                    fig_q = px.bar(
                        q_counts,
                        x="Response",
                        y="Percentage",
                        title="Quarantine practice frequency",
                        text=q_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_q.update_traces(textposition="outside")
                    fig_q.update_layout(
                        xaxis_title="Self reported practice",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_q, use_container_width=True)

                st.subheader("Carcass disposal practices")

                c_df = e_df[e_df["question"] == "Carcass Disposal"].copy()

                if c_df.empty:
                    st.info("No carcass disposal responses recorded yet.")
                else:
                    c_counts = (
                        c_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    c_counts.columns = ["Practice", "Percentage"]

                    c_order = [
                        "Proper burial/burning",
                        "Burial without lime",
                        "Left in fields",
                        "Dumped near forest"
                    ]
                    c_counts["Practice"] = pd.Categorical(
                        c_counts["Practice"],
                        categories=c_order,
                        ordered=True
                    )
                    c_counts = c_counts.sort_values("Practice")

                    fig_carcass = px.bar(
                        c_counts,
                        x="Practice",
                        y="Percentage",
                        title="Carcass disposal practices reported",
                        text=c_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_carcass.update_traces(textposition="outside")
                    fig_carcass.update_layout(
                        xaxis_title="Practice",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_carcass, use_container_width=True)

        # --- SECTION F: MITIGATION / RECOMMENDATIONS VISUALS ---
        elif current_session == "Section F: Mitigation":
            f_df = df[df["session_name"] == "Section F"].copy()

            if f_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.header("Section F: Recommendations and Feasibility")

                if "id" in f_df.columns:
                    f_df = (
                        f_df.sort_values("id")
                        .drop_duplicates(subset=["name", "question"], keep="last")
                    )

                f_df = f_df[f_df["answer"].notna()]

                feasibility_order = [
                    "Highly feasible",
                    "Moderately feasible",
                    "Difficult",
                    "Not feasible"
                ]

                urgency_order = [
                    "Urgent",
                    "Important",
                    "Desirable",
                    "Not necessary"
                ]

                st.subheader("Feasibility of buffer zones")

                feas_df = f_df[f_df["question"] == "Buffer Feasibility"].copy()

                if feas_df.empty:
                    st.info("No responses recorded yet for feasibility.")
                else:
                    feas_counts = (
                        feas_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    feas_counts.columns = ["Response", "Percentage"]

                    feas_counts["Response"] = pd.Categorical(
                        feas_counts["Response"],
                        categories=feasibility_order,
                        ordered=True
                    )
                    feas_counts = feas_counts.sort_values("Response")

                    fig_feas = px.bar(
                        feas_counts,
                        x="Response",
                        y="Percentage",
                        title="Feasibility of buffer zones",
                        text=feas_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_feas.update_traces(textposition="outside")
                    fig_feas.update_layout(
                        xaxis_title="Response",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_feas, use_container_width=True)

                st.subheader("Urgency of collaborative programme")

                urg_df = f_df[f_df["question"] == "Program Urgency"].copy()

                if urg_df.empty:
                    st.info("No responses recorded yet for programme urgency.")
                else:
                    urg_counts = (
                        urg_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    urg_counts.columns = ["Response", "Percentage"]

                    urg_counts["Response"] = pd.Categorical(
                        urg_counts["Response"],
                        categories=urgency_order,
                        ordered=True
                    )
                    urg_counts = urg_counts.sort_values("Response")

                    fig_urg = px.bar(
                        urg_counts,
                        x="Response",
                        y="Percentage",
                        title="Perceived urgency of a collaborative programme",
                        text=urg_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_urg.update_traces(textposition="outside")
                    fig_urg.update_layout(
                        xaxis_title="Response",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_urg, use_container_width=True)
                               
        # --- SECTION G: SURVEILLANCE & DIAGNOSTICS VISUALS ---
        elif current_session == "Section G: Surveillance":
            g_df = df[df["session_name"] == "Section G"].copy()

            if g_df.empty:
                st.info("Waiting for participant data...")
            else:
                st.header("Section G: Surveillance and diagnostics")

                if "id" in g_df.columns:
                    g_df = (
                        g_df.sort_values("id")
                        .drop_duplicates(subset=["name", "question"], keep="last")
                    )

                g_df = g_df[g_df["answer"].notna()]

                facility_order = [
                    "Within district",
                    "Neighboring district",
                    "Regional lab",
                    "None"
                ]

                mechanism_order = [
                    "Active surveillance",
                    "Passive surveillance",
                    "No formal system"
                ]

                frequency_order = [
                    "Weekly",
                    "Monthly",
                    "Quarterly",
                    "Outbreaks only",
                    "None"
                ]

                st.subheader("Diagnostic facility availability")

                fac_df = g_df[g_df["question"] == "Facility"].copy()

                if fac_df.empty:
                    st.info("No responses recorded yet for diagnostic facility availability.")
                else:
                    fac_counts = (
                        fac_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    fac_counts.columns = ["Availability", "Percentage"]

                    fac_counts["Availability"] = pd.Categorical(
                        fac_counts["Availability"],
                        categories=facility_order,
                        ordered=True
                    )
                    fac_counts = fac_counts.sort_values("Availability")

                    fig_fac = px.bar(
                        fac_counts,
                        x="Availability",
                        y="Percentage",
                        title="Where are diagnostic facilities located",
                        text=fac_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_fac.update_traces(textposition="outside")
                    fig_fac.update_layout(
                        xaxis_title="Reported availability",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_fac, use_container_width=True)

                st.subheader("Surveillance mechanism")

                mech_df = g_df[g_df["question"] == "Mechanism"].copy()

                if mech_df.empty:
                    st.info("No responses recorded yet for surveillance mechanism.")
                else:
                    mech_counts = (
                        mech_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    mech_counts.columns = ["Mechanism", "Percentage"]

                    mech_counts["Mechanism"] = pd.Categorical(
                        mech_counts["Mechanism"],
                        categories=mechanism_order,
                        ordered=True
                    )
                    mech_counts = mech_counts.sort_values("Mechanism")

                    fig_mech = px.bar(
                        mech_counts,
                        x="Mechanism",
                        y="Percentage",
                        title="How diseases are reported",
                        text=mech_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_mech.update_traces(textposition="outside")
                    fig_mech.update_layout(
                        xaxis_title="Reporting mechanism",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_mech, use_container_width=True)

                st.subheader("Surveillance activity frequency")

                freq_df = g_df[g_df["question"] == "Frequency"].copy()

                if freq_df.empty:
                    st.info("No responses recorded yet for surveillance frequency.")
                else:
                    freq_counts = (
                        freq_df["answer"]
                        .value_counts(normalize=True)
                        .mul(100)
                        .reset_index()
                    )
                    freq_counts.columns = ["Frequency", "Percentage"]

                    freq_counts["Frequency"] = pd.Categorical(
                        freq_counts["Frequency"],
                        categories=frequency_order,
                        ordered=True
                    )
                    freq_counts = freq_counts.sort_values("Frequency")

                    fig_freq = px.bar(
                        freq_counts,
                        x="Frequency",
                        y="Percentage",
                        title="How often surveillance activities are carried out",
                        text=freq_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                    )
                    fig_freq.update_traces(textposition="outside")
                    fig_freq.update_layout(
                        xaxis_title="Reported frequency",
                        yaxis_title="Percentage of respondents",
                        showlegend=False
                    )
                    st.plotly_chart(fig_freq, use_container_width=True)

                st.subheader("Diagnostic tests reportedly available")

                tests_df = g_df[g_df["question"] == "Tests"].copy()

                if tests_df.empty:
                    st.info("No responses recorded yet for diagnostic tests.")
                else:
                    import ast

                    records = []

                    for _, row in tests_df.iterrows():
                        name = row["name"]
                        raw = row["answer"]

                        try:
                            parsed = ast.literal_eval(raw)
                            if isinstance(parsed, list):
                                tests_list = parsed
                            else:
                                tests_list = [parsed]
                        except Exception:
                            tests_list = [raw]

                        for t in tests_list:
                            t_str = str(t).strip()
                            if t_str:
                                records.append({"name": name, "Test": t_str})

                    if not records:
                        st.info("No valid test names parsed from responses.")
                    else:
                        tests_expanded = pd.DataFrame(records)

                        tests_counts = (
                            tests_expanded.groupby("Test")["name"]
                            .nunique()
                            .reset_index(name="Participants")
                        )

                        total_participants = tests_df["name"].nunique()
                        tests_counts["Percentage"] = (
                            tests_counts["Participants"] / total_participants * 100.0
                        )

                        test_order = ["ELISA", "PCR", "Culture & Sensitivity", "Rapid Tests/Kits", "Microscopy"]
                        tests_counts["Test"] = pd.Categorical(
                            tests_counts["Test"],
                            categories=test_order,
                            ordered=True
                        )
                        tests_counts = tests_counts.sort_values("Test")

                        fig_tests = px.bar(
                            tests_counts,
                            x="Test",
                            y="Percentage",
                            title="Participants reporting availability of each diagnostic test",
                            text=tests_counts["Percentage"].apply(lambda x: f"{x:.1f}%")
                        )
                        fig_tests.update_traces(textposition="outside")
                        fig_tests.update_layout(
                            xaxis_title="Diagnostic test",
                            yaxis_title="Percentage of respondents",
                            showlegend=False
                        )
                        st.plotly_chart(fig_tests, use_container_width=True)

                        with st.expander("Show participant counts per test type"):
                            st.dataframe(tests_counts, use_container_width=True)

# --- WINDOW 2: DATA MANAGEMENT ---
elif view_mode == "⚙️ Data Management" and admin_pwd == ADMIN_PASSWORD:
    st.header("⚙️ Data Management")
    df = get_data()

    if df.empty:
        st.info("No data available.")
    else:
        st.dataframe(df, use_container_width=True)

        # Make sure the table has an 'id' column
        if "id" not in df.columns:
            st.error("No 'id' column found in workshop_data table.")
        else:
            id_list = df["id"].tolist()
            selected_ids = st.multiselect(
                "Select IDs to delete",
                options=id_list
            )

            if st.button("Delete selected rows"):
                if not selected_ids:
                    st.warning("No rows selected.")
                else:
                    for row_id in selected_ids:
                        delete_row(row_id)
                    st.success(f"Deleted {len(selected_ids)} rows.")
                    st.rerun()

# --- WINDOW 3: PARTICIPANT FORM ---
else:
    p_name = st.text_input("Full Name")
    p_dept = st.selectbox("Department", ["Select...", "Forest Department", "Animal Husbandry Department"])
    
    p_loc = ""
    if p_dept == "Forest Department":
        p_loc = st.selectbox(
            "Select Tiger Reserve/Safari",
            ["Kanha", "Pench", "Panna", "Satpura", "Ratapani", "Bandhavgarh", "Sanjay", "Van Vihar", "MMSJ", "White Tiger Safari"]
        )
    elif p_dept == "Animal Husbandry Department":
        p_loc = st.text_input("District and Block")

    st.divider()
    # --- Registration (always visible) ---
    with st.expander("Registration", expanded=True):
        st.header("Registration")
        p_desig = st.text_input("Designation")
        p_exp = st.text_input("Years of Experience")
        if st.button("Register"):
            save_answer(p_name, p_dept, p_loc, "Registration", "Profile", f"{p_desig} | {p_exp}")
            st.success("Registered!")

    # --- Section B: Spatial ---
    with st.expander("Section B: Spatial"):
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

    # --- Section C: Disease ---
    with st.expander("Section C: Disease (Last 3 Years)"):
        st.header("Section C: Disease (Last 3 Years)")
        diseases = ["FMD", "Anthrax", "Rabies", "HS", "PPR", "Brucellosis", "Bovine TB", "Parasitic"]
        for d in diseases:
            occ = st.radio(f"{d} Outbreak?", ["No", "Yes"], key=f"C_{d}")
            if st.button(f"Save {d}", key=f"btn_{d}"):
                save_answer(p_name, p_dept, p_loc, "Section C", d, occ)
                st.toast(f"{d} Saved")

    # --- Section D: Contact ---
    with st.expander("Section D: Contact & Risk (Score 1–5)"):
        st.header("Section D: Contact & Risk (Score 1–5)")
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

    # --- Section E: Risk & Vaccination ---
    with st.expander("Section E: Risk & Vaccination"):
        st.header("Section E: Risk & Vaccination")
        v_diseases = ["FMD Vac", "Brucella Vac", "HS Vac", "BQ Vac", "LSD Vac"]
        for v in v_diseases:
            cov = st.select_slider(f"{v} Coverage", ["<20%", "20-40%", "40-60%", "60-80%", ">80%"], key=f"E_{v}")
            if st.button(f"Save {v}", key=f"v_{v}"):
                save_answer(p_name, p_dept, p_loc, "Section E", v, cov)
        
        st.divider()
        quarantine = st.radio(
            "Quarantine practices for new livestock:",
            ["Always", "Usually", "Sometimes", "Rarely", "Never"]
        )
        carcass = st.radio(
            "Carcass Disposal",
            ["Proper burial/burning", "Burial without lime", "Left in fields", "Dumped near forest"]
        )
        
        if st.button("Save Biosecurity Settings"):
            save_answer(p_name, p_dept, p_loc, "Section E", "Quarantine", quarantine)
            save_answer(p_name, p_dept, p_loc, "Section E", "Carcass Disposal", carcass)
            st.success("Section E Saved")

    # --- Section F: Mitigation ---
    with st.expander("Section F: Recommendations"):
        st.header("Section F: Recommendations")
        f1 = st.radio(
            "Feasibility of buffer zones:",
            ["Highly feasible", "Moderately feasible", "Difficult", "Not feasible"]
        )
        f2 = st.radio(
            "Urgency of collaborative program:",
            ["Urgent", "Important", "Desirable", "Not necessary"]
        )
        f3 = st.multiselect(
            "Existing control measures:",
            ["Vaccination", "Movement restrictions", "Awareness", "Wildlife monitoring"]
        )
        if st.button("Save Section F"):
            save_answer(p_name, p_dept, p_loc, "Section F", "Buffer Feasibility", f1)
            save_answer(p_name, p_dept, p_loc, "Section F", "Program Urgency", f2)
            st.success("Section F Saved")

    # --- Section G: Surveillance ---
    with st.expander("Section G: Surveillance & Diagnostics"):
        st.header("Section G: Surveillance & Diagnostics")

        st.subheader("G1. Diagnostics")
        g1 = st.radio(
            "Diagnostic facility availability:",
            ["Within district", "Neighboring district", "Regional lab", "None"]
        )
        g2 = st.multiselect(
            "Available diagnostic tests:",
            ["ELISA", "PCR", "Culture & Sensitivity", "Rapid Tests/Kits", "Microscopy"]
        )
        
        st.subheader("G2. Reporting")
        g3 = st.radio(
            "Disease reporting mechanism:",
            ["Active surveillance", "Passive surveillance", "No formal system"]
        )
        g4 = st.radio(
            "Surveillance activity frequency:",
            ["Weekly", "Monthly", "Quarterly", "Outbreaks only", "None"]
        )
        
        if st.button("Finish Workshop"):
            save_answer(p_name, p_dept, p_loc, "Section G", "Facility", g1)
            save_answer(p_name, p_dept, p_loc, "Section G", "Tests", g2)
            save_answer(p_name, p_dept, p_loc, "Section G", "Mechanism", g3)
            save_answer(p_name, p_dept, p_loc, "Section G", "Frequency", g4)
            st.balloons()
            st.success("All data submitted. Thank you!")

