import streamlit as st
import pandas as pd
import json, os, uuid

# -----------------------------------------------------------
#  SETUP & PROJECT SAVE / LOAD
# -----------------------------------------------------------

PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def save_project(data, name):
    """Save session state data to a JSON file."""
    state_to_save = {k: v for k, v in data.items() if not k.startswith("_")}
    with open(f"{PROJECTS_DIR}/{name}.json", "w") as f:
        json.dump(state_to_save, f)

def load_projects():
    """Load all existing project files."""
    projects = []
    for f in os.listdir(PROJECTS_DIR):
        if f.endswith(".json"):
            with open(f"{PROJECTS_DIR}/{f}") as j:
                data = json.load(j)
                projects.append({"name": f[:-5], "data": data})
    return projects

# -----------------------------------------------------------
#  PROJECT CONTROLS
# -----------------------------------------------------------

def project_controls():
    st.subheader("🗂️ Project Controls")

    key_prefix = str(uuid.uuid4())[:8]
    projects = load_projects()
    project_names = [p["name"] for p in projects]

    col1, col2 = st.columns([2, 1])
    with col1:
        project_name = st.text_input(
            "New or Current Project Name",
            value=st.session_state.get("current_project", "Untitled Project"),
            key=f"proj_name_input_{key_prefix}",
        )
    with col2:
        if st.button("💾 Save Project", key=f"save_button_{key_prefix}"):
            if project_name.strip():
                save_project(st.session_state, project_name)
                st.session_state["current_project"] = project_name
                st.success(f"Project '{project_name}' saved!")
            else:
                st.warning("Please enter a project name before saving.")

    st.divider()

    if project_names:
        st.write("📂 Load an Existing Project")
        selected_project = st.selectbox(
            "Select Project to Load", project_names, key=f"load_select_{key_prefix}"
        )
        if st.button("📥 Load Project", key=f"load_button_{key_prefix}"):
            project_data = next(
                (p["data"] for p in projects if p["name"] == selected_project), None
            )
            if project_data:
                st.session_state.clear()
                st.session_state.update(project_data)
                st.session_state["current_project"] = selected_project
                st.success(f"Project '{selected_project}' loaded successfully!")
                st.experimental_rerun()

    if "current_project" in st.session_state:
        st.info(f"✅ Current project: {st.session_state['current_project']}")

# -----------------------------------------------------------
#  DAY STRUCTURE (now includes period naming)
# -----------------------------------------------------------

def day_structure():
    st.subheader("📅 Day Structure")

    if "day_structure" not in st.session_state:
        st.session_state["day_structure"] = {"same": True, "periods": 6, "period_names": [f"Period {i+1}" for i in range(6)]}

    same_structure = st.radio(
        "Use the same structure each day?",
        ["Yes", "No"],
        index=0 if st.session_state["day_structure"].get("same", True) else 1,
        horizontal=True,
        key="same_structure_toggle",
    )

    if same_structure == "Yes":
        num_periods = st.number_input(
            "Number of periods per day",
            1, 12,
            st.session_state["day_structure"].get("periods", 6),
            key="num_periods_same",
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
                key=f"same_period_name_{i}",
            )
            updated_names.append(updated_name)

        st.session_state["day_structure"] = {
            "same": True,
            "periods": int(num_periods),
            "period_names": updated_names,
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
                    key=f"{d}_num_periods",
                )

                # Ensure period list length is consistent
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
                        key=f"{d}_period_name_{i}",
                    )
                    updated_periods.append(p_name)

                st.session_state["day_structure"]["structure"][d] = {
                    "num_periods": int(num_periods),
                    "period_names": updated_periods,
                }

        st.session_state["day_structure"]["same"] = False


# -----------------------------------------------------------
#  SCHOOL DATA (Teachers)
# -----------------------------------------------------------

def school_data():
    st.subheader("🏫 School Data — Teachers")

    if st.button("⬇️ Download Teacher CSV Template"):
        df_template = pd.DataFrame({
            "UID": [],
            "Email": [],
            "Title": [],
            "FirstName": [],
            "MiddleName": [],
            "LastName": [],
            "PreferredName": [],
            "Department1": [],
            "Department2": [],
        })
        st.download_button(
            label="Download Template",
            data=df_template.to_csv(index=False),
            file_name="teacher_template.csv",
            mime="text/csv",
        )

    uploaded_file = st.file_uploader("Upload Teacher CSV", type=["csv"])
    if uploaded_file:
        teachers_df = pd.read_csv(uploaded_file)
        st.session_state["teachers"] = teachers_df.to_dict()
        st.dataframe(teachers_df)

# -----------------------------------------------------------
#  SUBJECTS & ROOMS
# -----------------------------------------------------------

def subjects_data():
    st.subheader("📘 Subjects & Rooms")

    col1, col2 = st.columns(2)
    with col1:
        subjects = st.text_area(
            "Enter subjects (one per line):",
            value="\n".join(st.session_state.get("subjects", [])),
            height=150,
        )
        st.session_state["subjects"] = [s.strip() for s in subjects.split("\n") if s.strip()]

    with col2:
        room_data = st.text_area(
            "Enter rooms (Format: Room,Building/Level,Capacity,Specialty):",
            value="\n".join(st.session_state.get("rooms", [])),
            height=150,
        )
        st.session_state["rooms"] = [r.strip() for r in room_data.split("\n") if r.strip()]

# -----------------------------------------------------------
#  CLASS ASSIGNMENTS
# -----------------------------------------------------------

def class_assignments():
    st.subheader("👩‍🏫 Class Assignments")

    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.selectbox("Subject", st.session_state.get("subjects", []))
    with col2:
        teacher = st.text_input("Teacher UID")
    with col3:
        periods = st.number_input("Number of Periods", 1, 10, 4)

    fit = st.radio(
        "Scheduling Type",
        ["Relaxed (best fit)", "Strict (fixed day/period)"],
        horizontal=True,
    )

    if fit == "Strict (fixed day/period)":
        day = st.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri"])
        period = st.text_input("Period name or number")
    else:
        day, period = None, None

    if st.button("➕ Add Class"):
        new_class = {
            "Subject": subject,
            "Teacher": teacher,
            "Periods": periods,
            "Type": fit,
            "Day": day,
            "Period": period,
        }
        st.session_state.setdefault("classes", []).append(new_class)
        st.success("Class added!")

    if "classes" in st.session_state:
        st.dataframe(pd.DataFrame(st.session_state["classes"]))

# -----------------------------------------------------------
#  TIMETABLE GENERATOR
# -----------------------------------------------------------

def timetable_generator():
    st.subheader("🧮 Timetable Generator & Conflict Checker")

    if "classes" not in st.session_state:
        st.warning("No classes to generate timetable from yet.")
        return

    df = pd.DataFrame(st.session_state["classes"])
    st.dataframe(df)

    if {"Teacher", "Day", "Period"}.issubset(df.columns):
        conflicts = df[df.duplicated(subset=["Teacher", "Day", "Period"], keep=False)]
        if not conflicts.empty:
            st.error("Conflicts found:")
            st.dataframe(conflicts)
        else:
            st.success("✅ No teacher conflicts found!")

# -----------------------------------------------------------
#  MAIN APP
# -----------------------------------------------------------

st.title("📚 Smart Timetable Builder")
project_controls()

tabs = st.tabs([
    "1️⃣ Day Structure",
    "2️⃣ School Data",
    "3️⃣ Subjects & Rooms",
    "4️⃣ Class Assignments",
    "5️⃣ Timetable Generator",
])

with tabs[0]:
    day_structure()
with tabs[1]:
    school_data()
with tabs[2]:
    subjects_data()
with tabs[3]:
    class_assignments()
with tabs[4]:
    timetable_generator()
