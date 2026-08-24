import streamlit as st
from streamlit_autorefresh import st_autorefresh
import segno
import io
import time
import hashlib
from datetime import datetime

from src.database.config import supabase
from src.database.db import create_attendance


def _get_app_url() -> str:
    """Auto-detect base URL: localhost → http, anything else → https."""
    try:
        host = st.context.headers.get("host", "")
        if not host:
            raise ValueError("no host header")
        scheme = "http" if host.startswith(("localhost", "127.0.0.1")) else "https"
        return f"{scheme}://{host}"
    except Exception:
        return st.secrets.get("APP_URL", "http://localhost:8501")


def _generate_token(subject_id: str) -> str:
    """Time-bucketed token that rotates every 5 seconds."""
    bucket = int(time.time()) // 5
    raw = f"{subject_id}:{bucket}:{st.secrets.get('SUPABASE_KEY', 'fallback')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _qr_png_bytes(data: str) -> bytes:
    buf = io.BytesIO()
    # High-res clean QR code
    segno.make_qr(data).save(buf, kind="png", scale=8, border=2, dark="#1E1B4B", light="#FFFFFF")
    return buf.getvalue()


@st.dialog("Live QR Attendance Studio", width="large")
def qr_attendance_dialog(subject_id: str, subject_name: str):
    st_autorefresh(interval=5000, key="qr_refresh")

    token = _generate_token(str(subject_id))
    base_url = _get_app_url()
    scan_url = f"{base_url}/?qr-token={token}&subject-id={subject_id}"
    qr_bytes = _qr_png_bytes(scan_url)

    st.markdown(f"""
        <div style="background:linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); padding:1.25rem 1.5rem; border-radius:1.25rem; color:white; margin-bottom:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <h3 style="margin:0; color:white; font-size:1.35rem; font-family:'Outfit', sans-serif;">{subject_name}</h3>
                    <p style="margin:0.25rem 0 0 0; color:rgba(255,255,255,0.85); font-size:0.88rem;">Live Self-Attendance Gateway</p>
                </div>
                <div style="background:rgba(255,255,255,0.2); backdrop-filter:blur(8px); padding:6px 14px; border-radius:9999px; font-weight:700; font-size:0.82rem; border:1px solid rgba(255,255,255,0.3);">
                    🔄 Rotates every 5s
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_qr, col_info = st.columns([1.1, 1.2], vertical_alignment="center")
    with col_qr:
        with st.container(border=True):
            st.image(qr_bytes, use_container_width=True)
            st.markdown(f"""
                <div style="text-align:center; padding:4px 0;">
                    <span style="font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase;">Current Passcode</span>
                    <div style="font-family:monospace; font-size:1.2rem; font-weight:800; color:#4F46E5; letter-spacing:0.1em;">{token}</div>
                </div>
            """, unsafe_allow_html=True)

    with col_info:
        st.markdown("""
            <div style="background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:1.25rem; padding:1.25rem; margin-bottom:0.75rem;">
                <h4 style="margin:0 0 0.5rem 0; color:#1E1B4B; font-size:1.05rem;">Student Instructions:</h4>
                <ol style="margin:0; padding-left:1.2rem; color:#475569; font-size:0.88rem; line-height:1.6;">
                    <li>Open <strong>SnapClass</strong> on your mobile device.</li>
                    <li>Scan this projected QR code or enter pass code.</li>
                    <li>Verify your FaceID to confirm attendance.</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)
        st.caption("🔒 Dynamic time-bucketing prevents link sharing or proxy attendance.")

    st.divider()
    _manual_override_section(subject_id)


def _manual_override_section(subject_id: str):
    """Teacher can toggle present/absent per enrolled student."""
    st.subheader("✏️ Manual Attendance Overrides")
    st.caption("Manually adjust attendance for students with camera or connectivity issues.")

    try:
        res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", subject_id).execute()
        enrolled = res.data or []
    except Exception as e:
        st.error(f"Could not load students: {e}")
        return

    if not enrolled:
        st.info("No students enrolled in this course.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    overrides = {}

    with st.container(border=True):
        for node in enrolled:
            student = node.get("students")
            if not student:
                continue
            sid = student["student_id"]
            name = student["name"]
            col1, col2 = st.columns([3, 1], vertical_alignment="center")
            with col1:
                st.markdown(f"**{name}** &nbsp; <span style='color:#64748B; font-size:0.8rem;'>#{sid}</span>", unsafe_allow_html=True)
            with col2:
                overrides[sid] = st.checkbox("Present", key=f"qr_override_{sid}", value=True)

    if st.button("💾 Save & Confirm Attendance", type="primary", use_container_width=True):
        logs = [
            {
                "student_id": sid,
                "subject_id": subject_id,
                "timestamp": timestamp,
                "is_present": is_present,
            }
            for sid, is_present in overrides.items()
        ]
        try:
            create_attendance(logs)
            st.toast("Attendance saved successfully! ✅")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save attendance: {e}")
