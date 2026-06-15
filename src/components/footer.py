import streamlit as st


def footer_home():
    st.markdown("""
    <div style="
        text-align:center;
        margin-top:30px;
        color:white;
        font-family:'Outfit', sans-serif;
        font-size:20px;
        font-weight:bold;
    ">
        Created with ❤️ by
        <b>
            <span style="color:black;">Bhanu</span>
            <span style="color:#D4A017;">Prakash</span>
        </b>
    </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
    <div style="
        text-align:center;
        margin-top:30px;
        color:black;
        font-family:'Outfit', sans-serif;
        font-size:20px;
        font-weight:bold;
    ">
        Created with ❤️ by
        <b>
            <span style="color:black;">Bhanu</span>
            <span style="color:#D4A017;">Prakash</span>
        </b>
    </div>
    """, unsafe_allow_html=True)