
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
    # Chatbot widget — inject into parent page DOM to bypass iframe limitation
    components.html("""
        <script>
        (function() {
            if (window.parent && window.parent.document) {
                var existing = window.parent.document.getElementById('noupe-chatbot-script');
                if (!existing) {
                    var script = window.parent.document.createElement('script');
                    script.id = 'noupe-chatbot-script';
                    script.src = 'https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js';
                    window.parent.document.body.appendChild(script);
                }
            }
        })();
        </script>
    """, height=0)

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