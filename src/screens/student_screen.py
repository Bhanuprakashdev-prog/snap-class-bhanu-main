import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import numpy as np
import time

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
from src.components.radial_gauge import render_student_ai_insights
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier, load_dlib_models
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students, create_student, get_student_subjects,
    get_student_attendance, unenroll_student_to_subject, create_attendance
)


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button("Logout", type='secondary', key='logout_student_btn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            st.session_state['login_type'] = None
            if 'student_data' in st.session_state:
                del st.session_state.student_data
            st.rerun()

    st.write("")

    try:
        subjects = get_student_subjects(student_id) or []
        logs = get_student_attendance(student_id) or []
    except Exception as e:
        st.error(f"Could not load attendance data: {e}")
        subjects, logs = [], []

    # AI Attendance Radial Gauge & Tips
    render_student_ai_insights(logs, student_data['name'])

    col1, col2 = st.columns([3, 1], vertical_alignment='center')
    with col1:
        st.subheader('Enrolled Subjects')
    with col2:
        if st.button('Enroll', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    stats_map = {}
    for log in logs:
        sid = log.get('subject_id')
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.info("You haven't enrolled in any subjects yet. Click **Enroll** to join a course.")
    else:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node.get('subjects')
            if not sub:
                continue
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            total = stats['total']
            att = stats['attended']
            pct = (att / total * 100) if total > 0 else 100.0

            def make_unenroll_callback(curr_sid=sid, curr_name=sub['name']):
                def unenroll_button():
                    if st.button(f"Unenroll", key=f"unenroll_{curr_sid}", type='tertiary', width='stretch'):
                        try:
                            unenroll_student_to_subject(student_id, curr_sid)
                            st.toast(f'Unenrolled from {curr_name} successfully!')
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not unenroll: {e}")
                return unenroll_button

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub.get('section', '-'),
                    stats=[
                        ('📅', 'Sessions', total),
                        ('✅', 'Attended', att),
                        ('📊', 'Rate', f"{pct:.0f}%"),
                    ],
                    footer_callback=make_unenroll_callback()
                )

    # Chatbot widget
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )
    footer_dashboard()


# ─── QR Token Helpers ─────────────────────────────────────────────────────────

def _validate_qr_token(token: str, subject_id: str) -> bool:
    """Checks the last 2 time-buckets so network lag doesn't break the flow."""
    import hashlib
    key = st.secrets.get("SUPABASE_KEY", "fallback")
    now = int(time.time()) // 5
    for bucket in [now, now - 1, now + 1]:
        expected = hashlib.sha256(f"{subject_id}:{bucket}:{key}".encode()).hexdigest()[:12]
        if token == expected:
            return True
    return False


def _check_image_quality(img_np: np.ndarray, face_boxes) -> list:
    """Returns list of warning strings; empty = OK."""
    warnings = []
    h, w = img_np.shape[:2]

    # Lighting check
    gray = np.mean(img_np, axis=2)
    brightness = float(np.mean(gray))
    if brightness < 50:
        warnings.append("💡 Too dark — please face a light source.")
    elif brightness > 240:
        warnings.append("☀️ Overexposed — avoid strong backlight.")

    # Distance check
    if face_boxes:
        box = face_boxes[0]
        box_area = (box.right() - box.left()) * (box.bottom() - box.top())
        frame_area = h * w
        if box_area / frame_area < 0.05:
            warnings.append("📏 Please move closer to the camera.")

    return warnings


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    # QR Gate Validation
    qr_token = st.query_params.get("qr-token")
    qr_subject_id = st.query_params.get("subject-id")
    qr_valid = False

    if qr_token and qr_subject_id:
        qr_valid = _validate_qr_token(qr_token, qr_subject_id)
        if qr_valid:
            st.success("✅ QR Session Verified! Scan your face to log in & mark attendance.")
        else:
            st.error("❌ QR code expired or invalid. Please scan the latest code from your instructor.")
            footer_dashboard()
            return

    st.header('Login using FaceID', text_alignment='center')
    st.write("")

    # Mirroring is applied in CSS: div[data-testid="stCameraInput"] video { transform: scaleX(-1); }
    # So when you bend your head to the right, your face moves to the right on screen naturally!
    photo_source = st.camera_input("Position your face inside camera view")

    show_registration = False

    if photo_source:
        img = np.array(Image.open(photo_source))

        try:
            detector, _, _ = load_dlib_models()
            raw = np.ascontiguousarray(img[:, :, :3].astype(np.uint8))
            face_boxes = detector(raw, 1)
            quality_warnings = _check_image_quality(img, face_boxes)
            for w_msg in quality_warnings:
                st.warning(w_msg)
        except Exception:
            quality_warnings = []

        with st.spinner('Scanning face...'):
            try:
                detected, all_ids, num_faces = predict_attendance(img)
            except Exception as e:
                st.error(f"Face recognition error: {e}")
                detected, num_faces = {}, 0

            if num_faces == 0:
                st.warning('No face detected. Please face the camera directly with good lighting.')
            elif num_faces > 1:
                st.warning('Multiple faces detected. Ensure only one person is in frame.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    try:
                        all_students = get_all_students()
                    except Exception as e:
                        st.error(f"Could not load students: {e}")
                        all_students = []

                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student

                        if qr_valid and qr_subject_id:
                            from datetime import datetime
                            try:
                                create_attendance([{
                                    'student_id': student_id,
                                    'subject_id': qr_subject_id,
                                    'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                    'is_present': True,
                                }])
                                st.toast("Attendance marked via QR! 🎉")
                            except Exception as e:
                                st.warning(f"Attendance log note: {e}")

                        st.toast(f"Welcome back, {student['name']}!", icon="👋")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized in our database. Register your profile below:")
                    show_registration = True

    if show_registration:
        st.divider()
        st.subheader('Register as New Student')
        new_name = st.text_input("Enter your Full Name", placeholder='Alex Sharma')

        st.markdown("#### 🎙️ Voice Profile *(Optional)*")
        audio_data = None
        try:
            audio_data = st.audio_input('Speak clearly: "I am present for class today"')
        except Exception:
            pass

        if st.button('Register Face & Voice Profile', type='primary', width='stretch'):
            if not new_name.strip():
                st.warning('Please enter your full name.')
            else:
                with st.spinner('Creating biometric profile...'):
                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embeddings(img)

                    if encodings:
                        face_emb = encodings[0].tolist()
                        voice_emb = None

                        if audio_data:
                            try:
                                voice_emb = get_voice_embedding(audio_data.read())
                            except Exception as e:
                                st.caption(f"Voice embedding note: {e}")

                        try:
                            response_data = create_student(new_name.strip(), face_embedding=face_emb, voice_embedding=voice_emb)
                        except Exception as e:
                            st.error(f"Database error: {e}")
                            response_data = None

                        if response_data:
                            train_classifier()
                            st.cache_resource.clear()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f"Profile created! Welcome, {new_name}!", icon="🎉")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error('Could not detect face landmarks. Please retake photo with clearer lighting.')

    # Chatbot widget
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )
    footer_dashboard()