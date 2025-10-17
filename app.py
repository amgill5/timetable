import streamlit as st
import pandas as pd

st.title("📅 Timetable Builder")

# --- Project Parameters ---
project_name = st.text_input("Project Name")

if project_name:
    st.success(f"Project: {project_name}")

    # --- Day Structure ---
    st.header("📆 Day Structure")
    structure = st.radio("Structure", ["Same Each Day", "Different Each Day"])

    if structure == "Same Each Day":
        num_periods = st.number_input("Number of periods per day", min_value=1, max_value=12, value=6)
        st.write("Enter lesson sequence for the day:")
        sequence = []
        for i in range(1, num_periods + 1):
            seq = st.text_input(f"Period {i}", key=f"same_{i}")
            sequence.append(seq)
        st.session_state["day_structure"] = {"type": "same", "sequence": sequence}

    else:  # Different Each Day
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_struct = {}
        for day in days:
            st.subheader(day)
            num_periods = st.number_input(f"Number of periods on {day}", min_value=1, max_value=12, value=6, key=f"num_{day}")
            seq = []
            for i in range(1, num_periods + 1):
                val = st.text_input(f"{day} - Period {i}", key=f"{day}_{i}")
                seq.append(val)
            day_struct[day] = seq
        st.session_state["day_structure"] = {"type": "different", "days": day_struct}

    # --- School Data ---
    st.header("🏫 School Data")

    # Initialize session storage
    if "teachers" not in st.session_state:
        st.session_state["teachers"] = []

    # --- CSV Template Download ---
    st.subheader("👩‍🏫 Teacher List")
    template_df = pd.DataFrame(columns=[
        "UID", "Email", "Title", "FirstName", "MiddleName", 
        "LastName", "PreferredName", "Department1", "Department2"
    ])
    st.download_button(
        label="📥 Download Teacher CSV Template",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="teacher_template.csv",
        mime="text/csv"
    )

    # --- Upload from CSV ---
    uploaded_file = st.file_uploader("Upload Teacher CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["teachers"].extend(df.to_dict("records"))
        st.info(f"✅ Imported {len(df)} teachers from CSV")

    # --- Manual Entry Form ---
    with st.expander("➕ Add Teacher Manually"):
        with st.form("teacher_form", clear_on_submit=True):
            uid = st.text_input("UID")
            email = st.text_input("Email")
            title = st.selectbox("Title/Honorific", ["", "Mr", "Mrs", "Ms", "Dr", "Prof"])
            first = st.text_input("First Name")
            middle = st.text_input("Middle Name")
            last = st.text_input("Last Name")
            preferred = st.text_input("Preferred Name")
            dept1 = st.text_input("Department 1")
            dept2 = st.text_input("Department 2")

            submitted = st.form_submit_button("Add Teacher")
            if submitted:
                st.session_state["teachers"].append({
                    "UID": uid, "Email": email, "Title": title,
                    "FirstName": first, "MiddleName": middle, "LastName": last,
                    "PreferredName": preferred, "Department1": dept1, "Department2": dept2
                })
                st.success(f"Added teacher: {first} {last}")

    # --- Display Teacher List ---
    if st.session_state["teachers"]:
        teacher_df = pd.DataFrame(st.session_state["teachers"])
        st.dataframe(teacher_df)
    else:
        st.warning("No teachers added yet. Upload a CSV or add manually.")
