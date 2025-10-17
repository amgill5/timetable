import streamlit as st
import os
import json
import pandas as pd

# ======================================================
# CONFIG
# ======================================================

# Local directory for saved projects
PROJECTS_DIR = "/Users/andrewgill/Documents/agTimetable"
os.makedirs(PROJECTS_DIR, exist_ok=True)

# ======================================================
# SAVE / LOAD FUNCTIONS
# ======================================================

def save_project(data, name):
    """Save session data as JSON in the local folder."""
    file_path = os.path.join(PROJECTS_DIR, f"{name}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    st.success(f"✅ Project '{name}' saved at {file_path}")

def load_projects():
    """Load all project JSONs from the local folder."""
    projects = []
    for file in os.listdir(PROJECTS_DIR):
        if file.endswith(".json"):
            with open(os.path.join(PROJECTS_DIR, file)) as f:
                data = json.load(f)
            projects.append({"name": file.replace(".json", ""), "data": data})
    return projects

# ======================================================
# PROJECT CONTROLS
# ======================================================

def project_controls():
    st.subheader("🗂️ Project Controls")

    projects = load_projects()
    project_names = [p["name"] for p in projects]

    col1, col2 = st.columns([2, 1])

    with col1:
        project_name = st.text_input(
            "New or Current Project Name",
            value=st.session_state.get("current_project", "Untitled Project"),
            key="proj_name_input"
        )

    with col2:
        save_now = st.button("💾 Save")

    if save_now:
        if project_name.strip():
            save_project(st.session_state, project_name)
            st.session_state["current_project"] = project_name
        else:
            st.warning("Please enter a project name before saving.")

    st.divider()

    if project_names:
        st.write("📂 Load an Existing Project")
        selected_project = st.selectbox("Select Project", project_names, key="load_select")
        load_now = st.button("📥 Load")

        if load_now:
            project_data = next((p["data"] for p in projects if p["name"] == selected_project), None)
            if project_data:
                st.session_state.clear()
                st.session_state.update(project_data)
                st.session_state["current_project"] = selected_project
                st.success(f"Project '{selected_project}' loaded!")
                st.experimental_rerun()

    if "current_project" in st.session_state:
        st.info(f"✅ Current project: {st.session_state['current_project']}")

# ======================================================
# DAY STRUCTURE
# ======================================================

def day_structure():
    st.subheader("📅 Day Structure")

    if "day_structure" not in st.session_state:
        st.session_state["day_structure"] = {"same": True, "periods": 6, "period_names": [f"Period {i+1}" for i in range(6)]}

    same_structure = st.radio(
        "Use the same structure each day?",
        ["Yes", "No"],
        index=0 if st.session_state["day_structure"].get("same", True) else 1,
        horizontal=True
    )

    if same_structure == "Yes":
        num_periods = st.number_input(
            "Number of periods per day",
            1, 12,
            st.session_state["day_structure"].get("periods", 6),
            key="num_periods_same"
        )

        # Ensure list length matches
        period_names = st.session_state["day_structure"].get("period_names", [])
        if len(period_names) < num_periods:
            period_names += [f"Period {i+1}" for i in range(len(period_names), num_periods)]
        elif len(period_names) > num_periods:
            period_names = period_names[:num_periods]

        updated_names = []
        for i in range(int(num_periods)):
            updated_name = st.text_input(
                f"Name for Period {i+1}",
                value=period_names[i],
                key=f"same_period_name_{i}"
            )
            updated_names.append(updated_name)

        st.session_state["day_structure"] = {
            "same": True,
            "periods": int(num_periods),
            "period_names": updated_names
        }

    else:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if "structure" not in st.session_state["day_structure"]:
            st.session_state["day_structure"]["structure"] = {}

        for d in days:
            with st.expander(f"{d}"):
                current_day = st.session_state["day_structure"]["structure"].get(d, {})
                num_periods = st.number_input(
                    f"Number of periods on {d}",
                    1, 12,
                    current_day.get("num_periods", 6),
                    key=f"{d}_num_periods"
                )

                period_names = current_day.get("period_names", [])
                if len(period_names) < num_periods:
                    period_names += [f"Period {i+1}" for i in range(len(period_names), num_periods)]
                elif len(period_names) > num_periods:
                    period_names = period_names[:num_periods]

                updated_periods = []
                for i in range(int(num_periods)):
                    p_name = st.text_input(
                        f"{d} - Period {i+1} name",
                        value=period_names[i],
                        key=f"{d}_period_name_{i}"
                    )
                    updated_periods.append(p_name)

                st.session_state["day_structure"]["structure"][d] = {
                    "num_periods": int(num_periods),
                    "period_names": updated_periods
                }

        st.session_state["day_structure"]["same"] = False

# ======================================================
# SCHOOL DATA (Teachers / Subjects)
# ======================================================

def school_data():
    st.subheader("🏫 School Data")

    # Teachers
    st.write("### 👩‍🏫 Teachers")
    teacher_template = pd.DataFrame({
        "UID": [], "Email": [], "Title": [], "FirstName": [],
        "MiddleName": [], "LastName": [], "PreferredName": [],
        "Department1": [], "Department2": []
    })

    st.download_button(
        "⬇️ Download Teacher CSV Template",
        teacher_template.to_csv(index=False),
        file_name="teacher_template.csv",
        mime="text/csv"
    )

    teacher_file = st.file_uploader("📤 Upload Teacher CSV", type=["csv"])
    if teacher_file:
        teachers_df = pd.read_csv(teacher_file)
        st.dataframe(teachers_df)
        st.session_state["teachers"] = teachers_df.to_dict(orient="records")

    st.divider()

    # Subjects
    st.write("### 📘 Subjects")
    subject_template = pd.DataFrame({
        "Subject": [], "PreferredRoom": [], "AlternativeRoom": [],
        "Building": [], "Level": [], "Capacity": [], "Specialty": []
    })

    st.download_button(
        "⬇️ Download Subject CSV Template",
        subject_template.to_csv(index=False),
        file_name="subject_template.csv",
        mime="text/csv"
    )

    subject_file = st.file_uploader("📤 Upload Subject CSV", type=["csv"])
    if subject_file:
        subjects_df = pd.read_csv(subject_file)
        st.dataframe(subjects_df)
        st.session_state["subjects"] = subjects_df.to_dict(orient="records")

# ======================================================
# APP
# ======================================================

def main():
    st.title("🧭 Timetable Builder")

    tab1, tab2, tab3 = st.tabs(["Project", "Day Structure", "School Data"])

    with tab1:
        project_controls()
    with tab2:
        day_structure()
    with tab3:
        school_data()

if __name__ == "__main__":
    main()
