import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home
import streamlit.components.v1 as components


def home_screen():
    # Style FIRST — before any content renders to avoid FOUC
    style_background_home()
    style_base_layout()

    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="
                background-color: #E0E3FF;
                border-radius: 2rem;
                padding: 2rem 1.5rem 1.5rem 1.5rem;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h2 style="color:#1E1B4B; margin:0 0 0.5rem 0;">I'm Student</h2>
                <img src="https://i.ibb.co/844D9Lrt/mascot-student.png" style="height:130px; width:auto;" />
            </div>
        """, unsafe_allow_html=True)
        if st.button('Student Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', use_container_width=True):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.markdown("""
            <div style="
                background-color: #E0E3FF;
                border-radius: 2rem;
                padding: 2rem 1.5rem 1.5rem 1.5rem;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <h2 style="color:#1E1B4B; margin:0 0 0.5rem 0;">I'm Teacher</h2>
                <img src="https://i.ibb.co/CsmQQV6X/mascot-prof.png" style="height:130px; width:auto;" />
            </div>
        """, unsafe_allow_html=True)
        if st.button('Teacher Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', use_container_width=True):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    # Sandboxed chatbot iframe
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )

    footer_home()