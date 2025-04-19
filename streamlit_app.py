# === File: streamlit_app.py ===

import streamlit as st
from models import School
from data_utils import load_schools, save_schools
from sync import sync_from_humanity
import tempfile
import os

st.set_page_config(page_title="School Roster Web App", layout="wide")
st.title("📘 School Roster Dashboard")

# Load data
if "schools" not in st.session_state:
    st.session_state.schools = load_schools()

schools = st.session_state.schools

# Sidebar selection
school_names = [s.name for s in schools]
selected_school = st.sidebar.selectbox("Select a School", school_names) if school_names else None
selected_sport = None

if selected_school:
    school_obj = next(s for s in schools if s.name == selected_school)
    sport_names = list(school_obj.sub_schools.keys())
    selected_sport = st.sidebar.selectbox("Select Sport", sport_names) if sport_names else None

# Sync button
if st.sidebar.button("🔁 Sync from Humanity"):
    st.session_state.schools = sync_from_humanity(st.session_state.schools)
    save_schools(st.session_state.schools)
    st.success("Synced successfully!")
    st.experimental_rerun()

# Main section
if selected_school and selected_sport:
    st.header(f"{selected_school} – {selected_sport}")
    sub = school_obj.sub_schools[selected_sport]

    # Schedule
    st.subheader("📅 Schedule")
    if sub.schedule:
        for date, time in sorted(sub.schedule.items()):
            st.text(f"{date}: {time}")
    else:
        st.info("No schedule yet.")

    # Roster
    st.subheader("🧑‍🎓 Roster")
    if sub.roster.students:
        st.text_area("Student List", value=str(sub.roster), height=200)
    else:
        st.info("Roster is empty.")

    # Upload Roster Image
    st.subheader("📷 Upload Roster Image")
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        school_obj.load_roster_from_image(tmp_path, selected_sport)
        save_schools(schools)
        st.success("Roster updated successfully!")
        os.remove(tmp_path)
        st.experimental_rerun()

# No school selected fallback
elif not school_names:
    st.info("No schools found. Please sync or load data first.")
else:
    st.info("Select a school and sport from the sidebar to view details.")
