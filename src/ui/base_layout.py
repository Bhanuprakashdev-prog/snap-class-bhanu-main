import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
        .stApp {
            background-color: #5865F2 !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
        .stApp {
            background-color: #E0E3FF !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    # Inject font <link> tags — must use <link>, not @import, when injecting into <body>
    st.markdown("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>

        /* Hide Streamlit chrome */
        #MainMenu, footer, header {
            visibility: hidden;
            height: 0px;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2.5rem !important;
        }

        /* Typography — headings only, never span (Material Icons use span) */
        h1 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 3.2rem !important;
            line-height: 1.1 !important;
            margin-bottom: 0rem !important;
        }

        h2 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 2rem !important;
            line-height: 1 !important;
            margin-bottom: 0.5rem !important;
        }

        /* NOTE: 'span' intentionally excluded — Material Symbols icons live in <span> */
        h3, h4, p, div.stMarkdown, input, textarea, select, label {
            font-family: 'Outfit', sans-serif !important;
        }

        /* ── BUTTONS: scoped to Streamlit button wrappers ONLY ──
           Do NOT use button {} globally — it overrides the camera
           capture button, dialog close x, and other internal controls. */
        div[data-testid="stBaseButton-primary"] > button,
        div[data-testid="stBaseButton-secondary"] > button,
        div[data-testid="stBaseButton-tertiary"] > button {
            border-radius: 1.5rem !important;
            padding: 10px 24px !important;
            border: none !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            transition: transform 0.15s ease-in-out !important;
        }

        div[data-testid="stBaseButton-primary"] > button:hover,
        div[data-testid="stBaseButton-secondary"] > button:hover,
        div[data-testid="stBaseButton-tertiary"] > button:hover {
            transform: scale(1.03) !important;
        }

        div[data-testid="stBaseButton-primary"] > button {
            background-color: #5865F2 !important;
            color: #FFFFFF !important;
        }

        div[data-testid="stBaseButton-secondary"] > button {
            background-color: #EB459E !important;
            color: #FFFFFF !important;
        }

        div[data-testid="stBaseButton-tertiary"] > button {
            background-color: #1E1B4B !important;
            color: #FFFFFF !important;
        }

        /* ── CAMERA INPUT ──
           4:3 aspect ratio so mobile/desktop both show the same cropped frame.
           object-fit:cover ensures the visible frame matches what gets captured.
           NO scaleX(-1) — browser already mirrors front cameras by default.
           Adding it would double-flip the feed making it backwards. */
        div[data-testid="stCameraInput"] {
            border-radius: 1rem !important;
            overflow: hidden !important;
            width: 100% !important;
            aspect-ratio: 4 / 3 !important;
            background-color: #000 !important;
        }

        div[data-testid="stCameraInput"] video {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            border-radius: 0 !important;
        }

        div[data-testid="stCameraInput"] canvas {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            border-radius: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
