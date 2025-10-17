import streamlit as st
import pandas as pd
import os, json

# ==============================
# 🔧 Basic setup
# ==============================
st.set_page_config(page_title="Timetable Builder", layout="wide")
SAVE_DIR = "saved_projects"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# ==============================
# 💾 Save/Load Helpers
# ==============================
def save_project(name):
    data = {}
    for key, value in st.session_state.items():
        if isinstance(value, (dict, list, str, int, float, bool)):
            data[key] = value
        elif isinstance(value, pd.DataFrame):
            data[key] = value.to_dict()
    with open(os.path.join(SAVE_DIR, f"{name}.json"), "w") as f:
        json.dump(data, f, indent=2)
    st.success(f"💾 Project '{name}' saved!")


def load_project(name):
    file_path = os.path.join(SAVE_DIR, f"{name}.json")
    if not os.path.exists(file_path):
        st.error("Project not found.")
        return
    with open(file_path, "r") as f:
        data = json.load(f)
    for key, value in data.items():
        if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
            st.session_state[key] = pd.DataFrame.from_dict(value)
        else:
            st.session_state[key] = value
    st.success(f"📂 Project '{name}' loaded successfully!")


def project_controls():
    """Reusable Save/Load UI"""
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        project_name = st.text_input(
            "Project name",
            value=st.session_state.get("current_project", "Untitled Project"),
            key="proj_name_input",
        )
    with col2:
        if st.button("💾 Save Project"):
            st.session_state["current_project"] = project_name
            save_project(project_name)

    saved_files = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    col3, col4 = st.columns([1, 1])
    with col3:
        selected_load = st.selectbox("📂 Load existing project", ["-- Select --"] + saved_files)
    with col4:
        if st.button("Load Selected Project") and selected_load != "-- Select --":
            st.session_state["current_project"] = selected_load
            load_project(selected_load)


# ==============================
# 🧱 App Tabs
# ==============================
tabs = st.tabs([
    "1️⃣ Project Setup",
    "2️⃣ Day Structure",
    "3️⃣ School Data",
    "4️⃣ Subjects & Rooms",
    "5️⃣ Class Assignments",
    "6️⃣ Timetable Generator",
])

# -------------------------------------
# 1️⃣ PROJECT SETUP
# -------------------------------------
with tabs[0]:
    st.header("🗂️ Project Setup")
    project_controls()
    st.write("Set basic parameters for your timetable project.")

    st.session_state["num_days"] = st.number_input("Number of days per cycle", 1, 14, 5)
    st.session_state["num_periods"] = st.number_input("Number of periods per day", 1, 12, 6)

    st.session_state["days"] = [f"Day {i+1}" for i in range(st.session_state["num_days"])]
    st.session_state["periods"] = [str(i+1) for i in range(st.session_state["num_periods"])]

    st.success("✅ Parameters set successfully!")

# -------------------------------------
# 2️⃣ DAY STRUCTURE
# -------------------------------------
with tabs[1]:
    st.header("🗓️ Day Structure")
    project_controls()

    same_structure = st.radio("Use the same structure each day?", ["Yes", "No"], index=0)
    if same_structure == "Yes":
        st.session_state["day_structure"] = {
            "Periods": st.session_state["periods"]
        }
        st.info("Using the same structure each day.")
    else:
        st.session_state["day_structure"] = {}
        for day in st.session_state["days"]:
            with st.expander(day):
                periods = st.text_area(
                    f"Enter periods for {day} (comma-separated)",
                    value=",".join(st.session_state["periods"]),
                ).split(",")
                st.session_state["day_structure"][day] = [p.strip() for p in periods]

    st.success("✅ Day structure saved.")

# -------------------------------------
# 3️⃣ SCHOOL DATA
# -------------------------------------
with tabs[2]:
    st.header("🏫 School Data – Teacher List")
    project_controls()

    st.download_button(
        "📄 Download Teacher CSV Template",
        data="UID,Email,Title,FirstName,MiddleName,LastName,PreferredName,Department1,Department2\n",
        file_name="teacher_template.csv",
    )

    uploaded = st.file_uploader("Upload Teacher List CSV", type="csv")
    if uploaded:
        teachers = pd.read_csv(uploaded)
        st.session_state["teachers"] = teachers
        st.success("✅ Teacher list uploaded!")
        st.dataframe(teachers)
    else:
        st.info("Or enter manually below:")
        if "teachers" not in st.session_state:
            st.session_state["teachers"] = pd.DataFrame(
                columns=[
                    "UID", "Email", "Title", "FirstName", "MiddleName",
                    "LastName", "PreferredName", "Department1", "Department2"
                ]
            )
        st.data_editor(st.session_state["teachers"], num_rows="dynamic")

# -------------------------------------
# 4️⃣ SUBJECTS & ROOMS
# -------------------------------------
with tabs[3]:
    st.header("📚 Subjects & Rooms")
    project_controls()

    # Subject list
    st.subheader("Subjects")
    if "subjects" not in st.session_state:
        st.session_state["subjects"] = pd.DataFrame(columns=["Code", "Name", "Department"])
    st.session_state["subjects"] = st.data_editor(st.session_state["subjects"], num_rows="dynamic")

    # Rooms
    st.subheader("Rooms")
    if "rooms" not in st.session_state:
        st.session_state["rooms"] = pd.DataFrame(
            columns=["Code", "Building", "Level", "Capacity", "Specialty"]
        )
    st.session_state["rooms"] = st.data_editor(st.session_state["rooms"], num_rows="dynamic")

# -------------------------------------
# 5️⃣ CLASS ASSIGNMENTS
# -------------------------------------
with tabs[4]:
    st.header("👩‍🏫 Class Assignments")
    project_controls()

    if "classes" not in st.session_state:
        st.session_state["classes"] = []

    with st.form("add_class"):
        st.subheader("Add a New Class")
        class_name = st.text_input("Class Name")
        teacher_uid = st.text_input("Teacher UID")
        subject_code = st.text_input("Subject Code")
        room_code = st.text_input("Preferred Room")
        num_periods = st.number_input("Number of Periods", 1, 20, 3)
        schedule_type = st.selectbox("Schedule Type", ["Relaxed", "Strict"])
        day = st.selectbox("Fixed Day (for Strict only)", [""] + st.session_state["days"])
        period = st.selectbox("Fixed Period (for Strict only)", [""] + st.session_state["periods"])
        submitted = st.form_submit_button("Add Class")

        if submitted:
            st.session_state["classes"].append({
                "ClassName": class_name,
                "TeacherUID": teacher_uid,
                "SubjectCode": subject_code,
                "RoomCode": room_code,
                "NumPeriods": num_periods,
                "ScheduleType": schedule_type,
                "Day": day,
                "Period": period
            })
            st.success(f"✅ Added class '{class_name}'")

    if st.session_state["classes"]:
        st.dataframe(pd.DataFrame(st.session_state["classes"]))

# -------------------------------------
# 6️⃣ TIMETABLE GENERATOR
# -------------------------------------
with tabs[5]:
    st.header("📅 Timetable Generator")
    project_controls()

    if not st.session_state.get("classes"):
        st.warning("Please add class assignments first.")
    else:
        num_days = len(st.session_state["days"])
        num_periods = len(st.session_state["periods"])

        if "timetable" not in st.session_state:
            st.session_state["timetable"] = pd.DataFrame(
                [["" for _ in range(num_periods)] for _ in range(num_days)],
                index=st.session_state["days"],
                columns=st.session_state["periods"]
            )

        if st.button("🧮 Generate Timetable Automatically"):
            df = st.session_state["timetable"].copy()
            used_slots = set()

            for c in st.session_state["classes"]:
                periods_needed = int(c.get("NumPeriods", 1))
                schedule_type = c.get("ScheduleType", "Relaxed")
                teacher = c["TeacherUID"]
                class_name = c["ClassName"]

                placed = 0

                if schedule_type == "Strict" and c.get("Day") and c.get("Period"):
                    day, period = c["Day"], c["Period"]
                    if (day, period) not in used_slots:
                        df.at[day, period] = f"{class_name}\n({teacher})"
                        used_slots.add((day, period))
                        placed += 1

                if schedule_type == "Relaxed":
                    for d in st.session_state["days"]:
                        for p in st.session_state["periods"]:
                            if placed >= periods_needed:
                                break
                            if (d, p) not in used_slots and df.at[d, p] == "":
                                df.at[d, p] = f"{class_name}\n({teacher})"
                                used_slots.add((d, p))
                                placed += 1
                        if placed >= periods_needed:
                            break

            st.session_state["timetable"] = df
            st.success("✅ Timetable generated successfully!")

        st.dataframe(st.session_state["timetable"], use_container_width=True)

        if st.button("🔍 Check for Conflicts"):
            df = st.session_state["timetable"]
            conflicts = []
            cell_teachers = {}

            for d in st.session_state["days"]:
                for p in st.session_state["periods"]:
                    val = df.at[d, p]
                    if val and "(" in val and ")" in val:
                        teacher = val.split("(")[-1].split(")")[0]
                        key = (d, p)
                        cell_teachers.setdefault(key, []).append(teacher)

            for key, teachers in cell_teachers.items():
                if len(teachers) > 1:
                    conflicts.append(f"Teacher conflict on {key[0]} Period {key[1]}: {', '.join(teachers)}")

            if conflicts:
                st.error("⚠️ Conflicts detected:")
                for c in conflicts:
                    st.write(f"- {c}")
            else:
                st.success("✅ No teacher conflicts detected!")
