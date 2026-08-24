import streamlit as st
import time
from src.database.db import enroll_student_to_subject
from src.database.config import supabase


@st.dialog("📚 Enroll in Course")
def enroll_dialog():
    st.markdown("""
        <p style="color:#64748B; font-size:0.92rem; margin-bottom:1rem;">
            Enter the unique 6-character subject code provided by your instructor.
        </p>
    """, unsafe_allow_html=True)

    join_code = st.text_input('Course Code', placeholder='e.g., CS101').strip().upper()

    if st.button('✨ Join Course', type='primary', use_container_width=True):
        if join_code:
            try:
                res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
                if res.data:
                    subject = res.data[0]
                    student_id = st.session_state.student_data['student_id']

                    check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                    if check.data:
                        st.warning('You are already enrolled in this course.')
                    else:
                        enroll_student_to_subject(student_id, subject['subject_id'])
                        st.success(f"Enrolled in {subject['name']} successfully! 🎉")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error(f"No course found with code '{join_code}'. Please check with your teacher.")
            except Exception as e:
                st.error(f"Enrollment error: {e}")
        else:
            st.warning('Please enter a course code.')