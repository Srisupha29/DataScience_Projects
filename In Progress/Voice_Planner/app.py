import streamlit as st

from services.transcription import transcribe_audio
from services.extraction import extract_checkin
from services.planner import generate_plan

st.set_page_config(
    page_title="Voice Daily Planner",
    page_icon="🎙️",
    layout="centered"
)


st.title("Voice Daily Check-In & Goal-Aware Planner")

st.write(
    "Speak your daily check-in and get a realistic plan for your day."
)


st.subheader("Daily Check-In")


audio = st.audio_input(
    "Record your check-in",
    sample_rate=16000
)


if audio is not None:
    st.audio(audio)

    with st.spinner("Transcribing..."):
        transcript = transcribe_audio(audio)

    st.subheader("Transcript")
    st.write(transcript)

    with st.spinner("Understanding your check-in..."):
        checkin = extract_checkin(transcript)

    st.subheader("Today's Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Sleep",
            f"{checkin.sleep_hours} hours"
            if checkin.sleep_hours is not None
            else "Not detected"
        )

    with col2:
        st.metric(
            "Energy",
            f"{checkin.energy_level}/5"
            if checkin.energy_level is not None
            else "Not detected"
        )

    if checkin.tasks:
        st.subheader("Tasks")

        for task in checkin.tasks:
            st.write(f"- {task}")

    if checkin.commitments:
        st.subheader("Commitments")

        for commitment in checkin.commitments:
            st.write(f" - {commitment}")

        
    st.subheader("Today's Plan")

    plan = generate_plan(checkin)

    for item in plan:
        st.write(
            f"**{item['time']}** — {item['activity']}"
        )