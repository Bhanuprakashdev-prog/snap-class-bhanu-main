import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    """Renders a sleek, elevated modern subject card with clean badge tags and stats."""
    
    stats_html = ""
    if stats:
        stats_html += '<div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:1rem; margin-bottom:0.75rem;">'
        for icon, label, value in stats:
            stats_html += f"""
            <div style="background:#F1F5F9; border:1px solid #E2E8F0; padding:6px 12px; border-radius:10px; font-size:0.85rem; color:#334155; display:inline-flex; align-items:center; gap:5px;">
                <span>{icon}</span> <strong>{value}</strong> <span style="color:#64748B;">{label}</span>
            </div>
            """
        stats_html += "</div>"

    card_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 1.25rem;
        padding: 1.4rem 1.5rem 1rem 1.5rem;
        box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.25rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
            <h3 style="margin:0; color:#1E1B4B; font-size:1.25rem; font-family:'Outfit', sans-serif; font-weight:700;">
                {name}
            </h3>
            <span style="
                background: #EEF2FF;
                color: #4F46E5;
                font-weight: 700;
                font-size: 0.78rem;
                padding: 4px 10px;
                border-radius: 9999px;
                border: 1px solid #C7D2FE;
                letter-spacing: 0.02em;
                white-space: nowrap;
            ">
                {code}
            </span>
        </div>
        <p style="color:#64748B; font-size:0.85rem; margin:0.35rem 0 0 0; font-weight:500;">
            Section: <strong style="color:#334155;">{section}</strong>
        </p>
        {stats_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
