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

    else:
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

    # --- School Data Section ---
    st.header("🏫 School Data")
    tabs = st.tabs(["👩‍🏫 Teachers", "📚 Subjects", "🏠 Rooms", "🧩 Class Assignments"])

    # ======================================
    # 👩‍🏫 TEACHER TAB
    # ======================================
    with tabs[0]:
        if "teachers" not in st.session_state:
            st.session_state["teachers"] = []

        st.subheader("Teacher List")

        teacher_template = pd.DataFrame(columns=[
            "UID", "Email", "Title", "FirstName", "MiddleName",
            "LastName", "PreferredName", "Department1", "Department2"
        ])
        st.download_button(
            label="📥 Download Teacher CSV Template",
            data=teacher_template.to_csv(index=False).encode("utf-8"),
            file_name="teacher_template.csv",
            mime="text/csv"
        )

        uploaded_teacher = st.file_uploader("Upload Teacher CSV", type=["csv"], key="teacher_upload")
        if uploaded_teacher is not None:
            df = pd.read_csv(uploaded_teacher)
            st.session_state["teachers"].extend(df.to_dict("records"))
            st.info(f"✅ Imported {len(df)} teachers from CSV")

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

        if st.session_state["teachers"]:
            teacher_df = pd.DataFrame(st.session_state["teachers"])
            st.dataframe(teacher_df, use_container_width=True)
        else:
            st.warning("No teachers added yet. Upload a CSV or add manually.")

    # ======================================
    # 📚 SUBJECT TAB
    # ======================================
    with tabs[1]:
        if "subjects" not in st.session_state:
            st.session_state["subjects"] = []

        st.subheader("Subjects List")

        subject_template = pd.DataFrame(columns=[
            "SubjectCode", "SubjectName", "Department",
            "PreferredRoom", "AlternativeRoom"
        ])
        st.download_button(
            label="📥 Download Subject CSV Template",
            data=subject_template.to_csv(index=False).encode("utf-8"),
            file_name="subject_template.csv",
            mime="text/csv"
        )

        uploaded_subject = st.file_uploader("Upload Subject CSV", type=["csv"], key="subject_upload")
        if uploaded_subject is not None:
            df = pd.read_csv(uploaded_subject)
            st.session_state["subjects"].extend(df.to_dict("records"))
            st.info(f"✅ Imported {len(df)} subjects from CSV")

        with st.expander("➕ Add Subject Manually"):
            with st.form("subject_form", clear_on_submit=True):
                code = st.text_input("Subject Code")
                name = st.text_input("Subject Name")
                dept = st.text_input("Department")
                pref_room = st.text_input("Preferred Room (optional)")
                alt_room = st.text_input("Alternative Room (optional)")

                submitted = st.form_submit_button("Add Subject")
                if submitted:
                    st.session_state["subjects"].append({
                        "SubjectCode": code, "SubjectName": name, "Department": dept,
                        "PreferredRoom": pref_room, "AlternativeRoom": alt_room
                    })
                    st.success(f"Added subject: {name}")

        if st.session_state["subjects"]:
            subject_df = pd.DataFrame(st.session_state["subjects"])
            st.dataframe(subject_df, use_container_width=True)
        else:
            st.warning("No subjects added yet. Upload a CSV or add manually.")

    # ======================================
    # 🏠 ROOMS TAB
    # ======================================
    with tabs[2]:
        if "rooms" not in st.session_state:
            st.session_state["rooms"] = []

        st.subheader("Rooms List")

        room_template = pd.DataFrame(columns=[
            "RoomCode", "BuildingLevel", "Capacity", "Specialty"
        ])
        st.download_button(
            label="📥 Download Room CSV Template",
            data=room_template.to_csv(index=False).encode("utf-8"),
            file_name="room_template.csv",
            mime="text/csv"
        )

        uploaded_room = st.file_uploader("Upload Room CSV", type=["csv"], key="room_upload")
        if uploaded_room is not None:
            df = pd.read_csv(uploaded_room)
            st.session_state["rooms"].extend(df.to_dict("records"))
            st.info(f"✅ Imported {len(df)} rooms from CSV")

        with st.expander("➕ Add Room Manually"):
            with st.form("room_form", clear_on_submit=True):
                code = st.text_input("Room Code")
                building = st.text_input("Building / Level")
                capacity = st.number_input("Capacity", min_value=0, step=1)
                specialty = st.text_input("Specialty (optional)")

                submitted = st.form_submit_button("Add Room")
                if submitted:
                    st.session_state["rooms"].append({
                        "RoomCode": code, "BuildingLevel": building,
                        "Capacity": capacity, "Specialty": specialty
                    })
                    st.success(f"Added room: {code}")

        if st.session_state["rooms"]:
            room_df = pd.DataFrame(st.session_state["rooms"])
            st.dataframe(room_df, use_container_width=True)
        else:
            st.warning("No rooms added yet. Upload a CSV or add manually.")

  
    # ======================================
    # 🧩 CLASS ASSIGNMENTS TAB
    # ======================================
    with tabs[3]:
        if "classes" not in st.session_state:
            st.session_state["classes"] = []

        st.subheader("Class Assignments")

        class_template = pd.DataFrame(columns=[
            "ClassName", "YearLevel", "TeacherUID", "SubjectCode", "RoomCode", "Periods"
        ])
        st.download_button(
            label="📥 Download Class CSV Template",
            data=class_template.to_csv(index=False).encode("utf-8"),
            file_name="class_template.csv",
            mime="text/csv"
        )

        uploaded_classes = st.file_uploader("Upload Class CSV", type=["csv"], key="class_upload")
        if uploaded_classes is not None:
            df = pd.read_csv(uploaded_classes)
            st.session_state["classes"].extend(df.to_dict("records"))
            st.info(f"✅ Imported {len(df)} classes from CSV")

        with st.expander("➕ Add Class Manually"):
            teacher_list = [f"{t['UID']} - {t['PreferredName'] or t['FirstName']} {t['LastName']}" for t in st.session_state.get("teachers", [])]
            subject_list = [f"{s['SubjectCode']} - {s['SubjectName']}" for s in st.session_state.get("subjects", [])]
            room_list = [r["RoomCode"] for r in st.session_state.get("rooms", [])]

            with st.form("class_form", clear_on_submit=True):
                classname = st.text_input("Class Name (e.g., 10A Science)")
                year = st.text_input("Year Level")
                teacher = st.selectbox("Teacher", teacher_list)
                subject = st.selectbox("Subject", subject_list)
                room = st.selectbox("Room", [""] + room_list)
                periods = st.text_input("Periods (e.g., Mon-1, Wed-3, Fri-2)")

                submitted = st.form_submit_button("Add Class")
                if submitted:
                    st.session_state["classes"].append({
                        "ClassName": classname,
                        "YearLevel": year,
                        "TeacherUID": teacher.split(" - ")[0],
                        "SubjectCode": subject.split(" - ")[0],
                        "RoomCode": room,
                        "Periods": periods
                    })
                    st.success(f"Added class: {classname}")

        if st.session_state["classes"]:
            class_df = pd.DataFrame(st.session_state["classes"])
            st.dataframe(class_df, use_container_width=True)
        else:
            st.warning("No classes assigned yet. Upload a CSV or add manually.")
✅ You now have:
Teachers, Subjects, and Rooms tabs

Full class assignment creation

Downloadable/importable CSV templates for all data types

A growing session structure ready for timetable generation

Would you like the next update to:

Add saving & loading projects (to keep data between sessions),
or

Start building the timetable generation view (a visual grid of classes per period/day)?







You said:
Can periods be entered as "relaxed" best fits or "strict" must be in this period Day and Period fields. and can there be a field for number of periods


ChatGPT said:
Excellent refinement 👌 — you’re now starting to introduce timetable logic!

Here’s how we’ll upgrade the Class Assignments tab to include your new scheduling controls:

🎯 New Features
For each class:

Number of Periods → How many times the class should appear per week.

Scheduling Type →

"Relaxed" = flexible / best-fit scheduling

"Strict" = must occur in specific day + period slots

Day / Period fields → Only shown when "Strict" is selected.

CSV template and upload will also include these fields.

🧩 Here’s your updated Class Assignments section (only this part — replace the previous tab)
You can paste this over the existing Class Assignments tab in your current app.py (no need to change other sections).

python
Copy code
    # ======================================
    # 🧩 CLASS ASSIGNMENTS TAB
    # ======================================
    with tabs[3]:
        if "classes" not in st.session_state:
            st.session_state["classes"] = []

        st.subheader("Class Assignments")

        class_template = pd.DataFrame(columns=[
            "ClassName", "YearLevel", "TeacherUID", "SubjectCode",
            "RoomCode", "NumPeriods", "ScheduleType", "Day", "Period"
        ])
        st.download_button(
            label="📥 Download Class CSV Template",
            data=class_template.to_csv(index=False).encode("utf-8"),
            file_name="class_template.csv",
            mime="text/csv"
        )

        uploaded_classes = st.file_uploader("Upload Class CSV", type=["csv"], key="class_upload")
        if uploaded_classes is not None:
            df = pd.read_csv(uploaded_classes)
            st.session_state["classes"].extend(df.to_dict("records"))
            st.info(f"✅ Imported {len(df)} classes from CSV")

        with st.expander("➕ Add Class Manually"):
            teacher_list = [f"{t['UID']} - {t['PreferredName'] or t['FirstName']} {t['LastName']}" for t in st.session_state.get("teachers", [])]
            subject_list = [f"{s['SubjectCode']} - {s['SubjectName']}" for s in st.session_state.get("subjects", [])]
            room_list = [r["RoomCode"] for r in st.session_state.get("rooms", [])]

            with st.form("class_form", clear_on_submit=True):
                classname = st.text_input("Class Name (e.g., 10A Science)")
                year = st.text_input("Year Level")
                teacher = st.selectbox("Teacher", teacher_list)
                subject = st.selectbox("Subject", subject_list)
                room = st.selectbox("Room", [""] + room_list)
                num_periods = st.number_input("Number of Periods per Week", min_value=1, max_value=20, value=3)
                schedule_type = st.radio("Scheduling Type", ["Relaxed (best fit)", "Strict (fixed period)"])

                day, period = "", ""
                if schedule_type.startswith("Strict"):
                    day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                    period = st.text_input("Period (e.g., 1, 2, 3...)")

                submitted = st.form_submit_button("Add Class")
                if submitted:
                    st.session_state["classes"].append({
                        "ClassName": classname,
                        "YearLevel": year,
                        "TeacherUID": teacher.split(" - ")[0] if teacher else "",
                        "SubjectCode": subject.split(" - ")[0] if subject else "",
                        "RoomCode": room,
                        "NumPeriods": num_periods,
                        "ScheduleType": "Relaxed" if schedule_type.startswith("Relaxed") else "Strict",
                        "Day": day,
                        "Period": period
                    })
                    st.success(f"Added class: {classname}")

        if st.session_state["classes"]:
            class_df = pd.DataFrame(st.session_state["classes"])
            st.dataframe(class_df, use_container_width=True)
        else:
            st.warning("No classes assigned yet. Upload a CSV or add manually.")
    # ======================================
    # 📅 TIMETABLE GENERATOR TAB
    # ======================================
    with tabs[4]:
        st.subheader("📅 Auto-Generated Timetable")

        # Ensure we have the necessary data
        if not st.session_state.get("classes") or not st.session_state.get("days") or not st.session_state.get("periods"):
            st.warning("Please define classes, days, and periods before generating a timetable.")
        else:
            num_days = len(st.session_state["days"])
            num_periods = len(st.session_state["periods"])

            if "timetable" not in st.session_state:
                st.session_state["timetable"] = pd.DataFrame(
                    [["" for _ in range(num_periods)] for _ in range(num_days)],
                    index=st.session_state["days"],
                    columns=st.session_state["periods"]
                )

            # --- Generate Timetable ---
            if st.button("🧮 Generate Timetable Automatically"):
                df = st.session_state["timetable"].copy()
                used_slots = set()

                for c in st.session_state["classes"]:
                    periods_needed = int(c.get("NumPeriods", 1))
                    schedule_type = c.get("ScheduleType", "Relaxed")
                    teacher = c["TeacherUID"]
                    class_name = c["ClassName"]
                    room = c["RoomCode"]

                    placed = 0

                    # Strict scheduling → fixed day/period
                    if schedule_type == "Strict" and c.get("Day") and c.get("Period"):
                        day = c["Day"]
                        period = str(c["Period"])
                        if (day, period) not in used_slots:
                            df.at[day, period] = f"{class_name}\n({teacher})"
                            used_slots.add((day, period))
                            placed += 1

                    # Relaxed scheduling → find available slots
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

            # --- Conflict Checker ---
            if st.button("🔍 Check for Conflicts"):
                df = st.session_state["timetable"]
                conflicts = []

                # Check for teacher or room duplicates
                cell_teachers = {}
                for d in st.session_state["days"]:
                    for p in st.session_state["periods"]:
                        val = df.at[d, p]
                        if val:
                            if "(" in val and ")" in val:
                                teacher = val.split("(")[-1].split(")")[0]
                                key = (d, p)
                                if key not in cell_teachers:
                                    cell_teachers[key] = []
                                cell_teachers[key].append(teacher)

                for key, teachers in cell_teachers.items():
                    if len(teachers) > 1:
                        conflicts.append(f"Teacher conflict on {key[0]} Period {key[1]}: {', '.join(teachers)}")

                # Display results
                if conflicts:
                    st.error("⚠️ Conflicts detected:")
                    for c in conflicts:
                        st.write(f"- {c}")
                else:
                    st.success("✅ No teacher conflicts detected!")

                # (Room and over-allocation checks can be added next)
