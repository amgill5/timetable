import streamlit as st
import pandas as pd
import json, os, uuid

# -----------------------------------------------------------
#  SETUP & PROJECT SAVE / LOAD
# -----------------------------------------------------------

PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def save_project(data, name):
    with open(f"{PROJECTS_DIR}/{name}.json", "w") as f:
        json.dump(data, f)

def load_projects():
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
        save_now = st.button("💾 Save", key=f"save_button_{key_prefix}")

    if save_now:
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
        load_now = st.button("📥 Load", key=f"load_button_{key_prefix}")

        if load_now:
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
#  DAY STRUCTURE
# -----------------------------------------------------------

def day_structure():
    st.subheader("📅 Day Structure")
    same_structure = st.radio(
        "Use same structure each day?",
        ["Yes", "No"],
        key=f"same_struct_{uuid.uuid4()}",
        horizontal=True,
    )

    if same_structure == "Yes":
        num_periods = st.number_input("Number of periods per day", 1, 12, 6)
        st.session_state["day_structure"] = {"same": True, "periods": num_periods}
    else:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        structure = {}
        for d in days:
            structure[d] = st.number_input(f"Periods on {d}", 1, 12, 6, key=f"{d}_{uuid.uuid4()}")
        st.session_state["day_structure"] = {"same": False, "structure": structure}

# -----------------------------------------------------------
#  SCHOOL DATA (TEACHERS)
# -----------------------------------------------------------

def school_data():
    st.subheader("🏫 School Data — Teachers")

    # Downloadable CSV template
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
        df_template.to_csv("teacher_template.csv", index=False)
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
        st.markdown("**Subjects**")
        subjects = st.text_area(
            "Enter subjects (one per line):",
            value="\n".join(st.session_state.get("subjects", [])),
            height=150,
            key=f"subjects_{uuid.uuid4()}",
        )
        st.session_state["subjects"] = [s.strip() for s in subjects.split("\n") if s.strip()]

    with col2:
        st.markdown("**Rooms**")
        room_data = st.text_area(
            "Enter rooms (Format: Room,Building/Level,Capacity,Specialty):",
            value="\n".join(st.session_state.get("rooms", [])),
            height=150,
            key=f"rooms_{uuid.uuid4()}",
        )
        st.session_state["rooms"] = [r.strip() for r in room_data.split("\n") if r.strip()]

# -----------------------------------------------------------
#  CLASS ASSIGNMENTS
# -----------------------------------------------------------

def class_assignments():
    st.subheader("👩‍🏫 Class Assignments")

    st.write("Enter classes and constraints:")

    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.selectbox(
            "Subject",
            st.session_state.get("subjects", []),
            key=f"subject_{uuid.uuid4()}",
        )
    with col2:
        teacher = st.text_input("Teacher UID", key=f"teacher_{uuid.uuid4()}")
    with col3:
        periods = st.number_input("Number of Periods", 1, 10, 4, key=f"periods_{uuid.uuid4()}")

    fit = st.radio(
        "Scheduling Type",
        ["Relaxed (best fit)", "Strict (fixed day/period)"],
        horizontal=True,
        key=f"fit_type_{uuid.uuid4()}",
    )

    if fit == "Strict (fixed day/period)":
        day = st.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri"], key=f"day_{uuid.uuid4()}")
        period = st.number_input("Period", 1, 12, 1, key=f"period_{uuid.uuid4()}")
    else:
        day, period = None, None

    if st.button("➕ Add Class", key=f"add_class_{uuid.uuid4()}"):
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

    st.write("This section will eventually auto-generate a timetable grid and detect conflicts.")

    df = pd.DataFrame(st.session_state["classes"])
    st.dataframe(df)

    # Example conflict check
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
