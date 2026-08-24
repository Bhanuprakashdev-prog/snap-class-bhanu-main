import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time
from datetime import datetime

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard, render_top_nav
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login,
    get_teacher_subjects, get_attendance_for_teacher
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_qr_attendance import qr_attendance_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.pipelines.risk_predictor import compute_risk
from src.database.config import supabase


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif st.session_state.get('teacher_login_type') == "register":
        teacher_screen_register()
    else:
        teacher_screen_login()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']

    # Dashboard Top Header
    c1, c2 = st.columns([3, 1.5], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        if st.button("🚪 Log Out", type='secondary', key='logout_teacher_btn', width="stretch"):
            st.session_state['is_logged_in'] = False
            st.session_state['login_type'] = None
            if 'teacher_data' in st.session_state:
                del st.session_state.teacher_data
            st.rerun()

    # Fetch stats for KPI ribbon
    try:
        teacher_subjects = get_teacher_subjects(teacher_id) or []
        teacher_attendance = get_attendance_for_teacher(teacher_id) or []
        total_students_set = set()
        for sub in teacher_subjects:
            total_students_set.update(range(sub.get('total_students', 0)))  # count estimate
        total_courses = len(teacher_subjects)
        total_sessions = len({log.get('timestamp', '')[:16] for log in teacher_attendance if log.get('timestamp')})
        avg_pct = (sum(1 for log in teacher_attendance if log.get('is_present')) / len(teacher_attendance) * 100) if teacher_attendance else 100.0
    except Exception:
        total_courses, total_sessions, avg_pct = 0, 0, 100.0

    st.markdown(f"""
        <div style="background:#FFFFFF; border-radius:1.25rem; padding:1.25rem 1.5rem; margin:1rem 0; border:1.5px solid #E2E8F0; box-shadow:0 4px 16px -4px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:1rem;">
                <div>
                    <h3 style="margin:0; color:#1E1B4B; font-size:1.35rem; font-family:'Outfit', sans-serif;">Welcome, Prof. {teacher_data['name']}! 👋</h3>
                    <p style="margin:0.2rem 0 0 0; color:#64748B; font-size:0.88rem;">Instructor Dashboard • #{teacher_id}</p>
                </div>
                <div style="display:inline-flex; align-items:center; gap:6px; background:#EEF2FF; color:#4F46E5; padding:6px 14px; border-radius:9999px; font-weight:700; font-size:0.82rem; border:1px solid #C7D2FE;">
                    ⚡ AI Live Mode Active
                </div>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:0.75rem;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.75rem 1rem;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:600;">Active Courses</div>
                    <div style="font-size:1.4rem; font-weight:800; color:#1E1B4B; font-family:'Outfit', sans-serif;">{total_courses}</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.75rem 1rem;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:600;">Total Logs</div>
                    <div style="font-size:1.4rem; font-weight:800; color:#1E1B4B; font-family:'Outfit', sans-serif;">{len(teacher_attendance)}</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.75rem 1rem;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:600;">Attendance Rate</div>
                    <div style="font-size:1.4rem; font-weight:800; color:#10B981; font-family:'Outfit', sans-serif;">{avg_pct:.0f}%</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.75rem 1rem;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:600;">Class Sessions</div>
                    <div style="font-size:1.4rem; font-weight:800; color:#4F46E5; font-family:'Outfit', sans-serif;">{total_sessions}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.columns(4)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('📸 Attendance', type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('📚 Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('📋 Records', type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    with tab4:
        type4 = "primary" if st.session_state.current_teacher_tab == 'ai_risk' else "tertiary"
        if st.button('🤖 AI Insights', type=type4, width='stretch', icon=':material/auto_graph:'):
            st.session_state.current_teacher_tab = 'ai_risk'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
    elif st.session_state.current_teacher_tab == "ai_risk":
        teacher_tab_ai_risk()

    # Chatbot widget
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )
    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.subheader('📸 Take Class Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception as e:
        st.error(f"Could not load subjects: {e}")
        return

    if not subjects:
        st.warning("You haven't created any subjects yet. Please go to **Subjects** tab to create one!")
        return

    subject_options = {f"{s['name']} ({s['subject_code']})": s['subject_id'] for s in subjects}
    subject_names = {s['subject_id']: s['name'] for s in subjects}

    col1, col2 = st.columns([3, 1.2], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Active Course', options=list(subject_options.keys()))
    with col2:
        if st.button('📷 Upload Photo', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.markdown("#### Captured Classroom Photos")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, use_container_width=True, caption=f'Photo {idx+1}')

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button('🗑️ Clear Photos', width='stretch', type='tertiary', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('🔍 Face Scan', width='stretch', type='primary', disabled=not has_photos):
            with st.spinner('AI analyzing classroom faces...'):
                try:
                    enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                    enrolled_students = enrolled_res.data or []
                except Exception as e:
                    st.error(f"Could not load enrolled students: {e}")
                    return

                enrolled_student_ids = [
                    int(node['students']['student_id'])
                    for node in enrolled_students
                    if node.get('students')
                ]

                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    try:
                        detected, _, _ = predict_attendance(
                            img_np,
                            allow_single_student=True,
                            candidate_student_ids=enrolled_student_ids
                        )
                    except Exception as e:
                        st.warning(f"Photo {idx+1} scan note: {e}")
                        continue

                    if detected:
                        for sid in detected.keys():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx+1}")

                if not enrolled_students:
                    st.warning('No students enrolled in this course.')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('🎙️ Voice Mode', type='secondary', width='stretch'):
            voice_attendance_dialog(selected_subject_id)

    with c4:
        if st.button('📱 Live QR Code', type='secondary', width='stretch'):
            qr_attendance_dialog(selected_subject_id, subject_names.get(selected_subject_id, ''))


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns([3, 1.5], vertical_alignment="center")
    with col1:
        st.subheader('📚 Subject Management')
    with col2:
        if st.button('➕ Create Subject', type="primary", width='stretch'):
            create_subject_dialog(teacher_id)

    st.divider()

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception as e:
        st.error(f"Error loading subjects: {e}")
        subjects = []

    if subjects:
        cols = st.columns(2)
        for i, sub in enumerate(subjects):
            stats = [
                ("👥", "Students", sub.get('total_students', 0)),
                ("📅", "Sessions", sub.get('total_classes', 0)),
            ]
            
            def make_share_callback(curr_name=sub['name'], curr_code=sub['subject_code']):
                def share_btn():
                    if st.button(f"Share Code: {curr_code}", key=f"share_{curr_code}", icon=":material/share:"):
                        share_subject_dialog(curr_name, curr_code)
                return share_btn

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub.get('section', '-'),
                    stats=stats,
                    footer_callback=make_share_callback()
                )
    else:
        st.info("No subjects found. Click **Create Subject** above to add your first course.")


def teacher_tab_attendance_records():
    st.subheader('📋 Class Attendance Records')
    teacher_id = st.session_state.teacher_data['teacher_id']

    try:
        records = get_attendance_for_teacher(teacher_id)
    except Exception as e:
        st.error(f"Could not load records: {e}")
        return

    if not records:
        st.info("No attendance records found yet. Start an attendance session to see results.")
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Date / Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False)),
            "students_name": r['students']['name']
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group', 'Date / Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count'),
            Students=('students_name', lambda x: ", ".join(x))
        )
        .reset_index()
    )
    summary['Attendance Status'] = (
        "✅ " + summary['Present_Count'].astype(str)
        + "/" + summary['Total_Count'].astype(str)
        + " Present"
    )
    st.dataframe(
        summary[['Date / Time', 'Subject', 'Subject Code', 'Students', 'Attendance Status']],
        use_container_width=True,
        hide_index=True
    )


def teacher_tab_ai_risk():
    """AI Risk Analytics tab — Money Shot dashboard."""
    st.subheader('🤖 AI Risk & Attendance Insights')
    teacher_id = st.session_state.teacher_data['teacher_id']

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception as e:
        st.error(f"Could not load subjects: {e}")
        return

    if not subjects:
        st.info("Create a subject first to view AI analytics.")
        return

    subject_options = {f"{s['name']} ({s['subject_code']})": s['subject_id'] for s in subjects}
    selected_label = st.selectbox('Select Subject for AI Analysis', list(subject_options.keys()), key='risk_subject')
    selected_id = subject_options[selected_label]

    try:
        enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_id).execute()
        enrolled = enrolled_res.data or []
        logs_res = supabase.table('attendance_logs').select('student_id, is_present').eq('subject_id', selected_id).execute()
        all_logs = logs_res.data or []
    except Exception as e:
        st.error(f"Could not load analytics data: {e}")
        return

    if not enrolled:
        st.info("No students enrolled in this course yet.")
        return

    st.divider()
    cols = st.columns(2)
    for i, node in enumerate(enrolled):
        student = node.get('students')
        if not student:
            continue
        sid = student['student_id']
        name = student['name']
        student_logs = [l for l in all_logs if l['student_id'] == sid]

        risk = compute_risk(student_logs)

        with cols[i % 2]:
            with st.container(border=True):
                c_n, c_t = st.columns([3, 1.5])
                with c_n:
                    st.markdown(f"**{name}**")
                with c_t:
                    st.markdown(f"<span style='color:{risk['color']}; font-weight:700;'>{risk['label']}</span>", unsafe_allow_html=True)
                
                st.progress(
                    int(risk['pct']),
                    text=f"{risk['pct']}% Attendance Score"
                )
                st.caption(f"💡 {risk['recommendation']}")
                if risk['lr_prob'] is not None:
                    st.caption(f"📊 Drop Probability: {risk['lr_prob']*100:.1f}%")


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    render_top_nav(back_label="Home", back_key="teacher_login_back_btn")

    st.markdown("""
        <div style="text-align:center; margin:1.25rem 0 1.5rem 0;">
            <h1 style="color:#1E1B4B; margin-bottom:0.25rem;">Teacher Login</h1>
            <p style="color:#64748B; font-size:1rem; margin:0;">Enter your instructor credentials to access the dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        teacher_username = st.text_input("Username", placeholder='e.g., ananyaroy')
        teacher_pass = st.text_input("Password", type='password', placeholder="Enter your password")

        st.write("")
        btnc1, btnc2 = st.columns(2)

        with btnc1:
            if st.button('🔐 Log In', type="primary", shortcut='control+enter', width='stretch'):
                if login_teacher(teacher_username, teacher_pass):
                    st.toast("Welcome back!", icon="👋")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password combination.")

        with btnc2:
            if st.button('Create Account', type="secondary", width='stretch'):
                st.session_state.teacher_login_type = 'register'
                st.rerun()

    # Chatbot widget
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )
    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username is already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Profile successfully registered! You can now log in."
    except Exception as e:
        return False, f"Registration error: {e}"


def teacher_screen_register():
    render_top_nav(back_label="Home", back_key="teacher_reg_back_btn")

    st.markdown("""
        <div style="text-align:center; margin:1.25rem 0 1.5rem 0;">
            <h1 style="color:#1E1B4B; margin-bottom:0.25rem;">Teacher Registration</h1>
            <p style="color:#64748B; font-size:1rem; margin:0;">Create a new instructor profile for SnapClass</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        teacher_username = st.text_input("Username", placeholder='e.g., ananyaroy')
        teacher_name = st.text_input("Full Name", placeholder='e.g., Prof. Ananya Roy')
        teacher_pass = st.text_input("Password", type='password', placeholder="Choose a password")
        teacher_pass_confirm = st.text_input("Confirm Password", type='password', placeholder="Repeat password")

        st.write("")
        btnc1, btnc2 = st.columns(2)

        with btnc1:
            if st.button('✨ Register Now', type="primary", width='stretch'):
                success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
                if success:
                    st.success(message)
                    time.sleep(1.5)
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
                else:
                    st.error(message)

        with btnc2:
            if st.button('Back to Login', type="secondary", width='stretch'):
                st.session_state.teacher_login_type = 'login'
                st.rerun()

    # Chatbot widget
    components.html(
        """<iframe src="https://www.noupe.com/embed/019ef88240ad7fcebbd43804d761b41a3257.js"
            sandbox="allow-scripts allow-same-origin allow-popups"
            style="border:none;width:60px;height:60px;position:fixed;bottom:20px;right:20px;">
        </iframe>""",
        height=0,
    )
    footer_dashboard()
