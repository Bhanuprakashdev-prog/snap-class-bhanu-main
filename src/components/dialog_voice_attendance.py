import streamlit as st
import pandas as pd
from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog('🎙️ AI Voice Attendance', width="large")
def voice_attendance_dialog(selected_subject_id):
    st.markdown("""
        <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:1rem; padding:1rem 1.25rem; margin-bottom:1.25rem;">
            <p style="margin:0; color:#3730A3; font-size:0.92rem; font-weight:500;">
                🎙️ Record classroom audio of students answering roll call (e.g., <em>"I am present"</em>). The 128-d Librosa Acoustic AI pipeline will identify registered voices automatically.
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        audio_data = st.audio_input("Record Classroom Voice Roll-Call")

    if st.button('🚀 Analyze & Match Voices', use_container_width=True, type='primary'):
        if not audio_data:
            st.warning("Please record audio before analyzing.")
            return

        with st.spinner('Extracting 128-d acoustic embeddings & matching speakers...'):
            try:
                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data or []
            except Exception as e:
                st.error(f"Could not load enrolled students: {e}")
                return

            if not enrolled_students:
                st.warning('No students enrolled in this course.')
                return

            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding']
                for s in enrolled_students
                if s.get('students') and s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled students have voice biometric profiles registered yet.')
                return

            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student['name'],
                    "ID": f"#{student['student_id']}",
                    "Match Score": f"{score:.2f}" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
