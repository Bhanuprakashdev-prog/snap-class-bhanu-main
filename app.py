
# v2 - force reload
import streamlit as st
from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
import streamlit.components.v1 as components

from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon= "https://i.ibb.co/YTYGn5qV/logo.png"
    )
    # Chatbot widget — sandboxed iframe (T11)
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()
        
        case None:
            home_screen()


    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)
main()