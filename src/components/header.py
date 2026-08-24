import streamlit as st


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:20px;">
            <img src='{logo_url}' style='height:100px;' />
            <h1 style='text-align:center; color:#E0E3FF; font-family:"Climate Crisis", sans-serif; font-size:3.5rem; line-height:1.1; margin:0;'>
                SNAP<br/>CLASS
            </h1>
        </div>   
    """, unsafe_allow_html=True)


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:12px;">
            <img src='{logo_url}' style='height:75px;' />
            <h2 style='text-align:left; color:#5865F2; font-family:"Climate Crisis", sans-serif; font-size:2rem; line-height:0.9; margin:0;'>
                SNAP<br/>CLASS
            </h2>
        </div>   
    """, unsafe_allow_html=True)


def render_top_nav(back_label="Go back to Home", back_key="btn_back_nav"):
    """Renders the dashboard top header with back button."""
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button(back_label, type='secondary', key=back_key, shortcut="control+backspace"):
            st.session_state['login_type'] = None
            # Clear teacher login flow state so returning always lands on login screen
            st.session_state.pop('teacher_login_type', None)
            st.rerun()

