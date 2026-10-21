# SnapClass — Workflow Diagrams

> All major system workflows with Mermaid sequence and flow diagrams.

---

## 1. Student Registration & Face Enrollment

```mermaid
sequenceDiagram
    actor Student
    participant Browser as student.html
    participant API as FastAPI /api/auth
    participant FP as face_pipeline.py
    participant DB as Supabase

    Student->>Browser: Open student.html
    Browser->>Browser: Show "Register" form
    Student->>Browser: Enter name, allow webcam
    Browser->>Browser: Capture photo snapshot
    Browser->>API: POST /api/auth/student/register\n(multipart: name + image)
    API->>FP: get_face_embeddings(image_np)
    FP->>FP: dlib HOG → detect face
    FP->>FP: ResNet-34 → 128-d descriptor
    FP-->>API: [embedding vector]
    API->>DB: INSERT students(name, face_embedding)
    API->>FP: train_classifier() — clear cache
    API-->>Browser: {success, student_id, token}
    Browser->>Browser: Store JWT, show dashboard
```

---

## 2. Student Face Login

```mermaid
flowchart TD
    A([Student opens student.html]) --> B["Webcam opens\n1-second countdown"]
    B --> C["POST /api/auth/student/face-login\n(image)"]
    C --> D["dlib: detect + embed face"]
    D --> E{"How many faces?"}
    E -- "0 faces" --> F["❌ Face not detected\nRetry prompt"]
    E -- ">1 face" --> G["❌ Multiple faces\nShow one face only"]
    E -- "exactly 1" --> H["Compare to all enrolled\nL2 Euclidean distance"]
    H --> I{"Distance ≤ 0.55?"}
    I -- "No match" --> J["❌ 404 Not recognized"]
    I -- "Match found" --> K["Generate JWT (24h)\nReturn student_id"]
    K --> L["✅ Dashboard loads\nAttendance + Recovery data"]
```

---

## 3. Voice Biometric Enrollment

```mermaid
sequenceDiagram
    actor Student
    participant Browser as student.html
    participant API as /api/auth
    participant VP as voice_pipeline.py
    participant DB as Supabase

    Student->>Browser: Click "Enroll Voice"
    Browser->>Browser: Record 3–5 seconds audio (MediaRecorder API)
    Browser->>API: POST /api/auth/student/voice-enroll\n(student_id + audio bytes)
    API->>VP: get_voice_embedding(audio_bytes)
    VP->>VP: librosa.load (sr=16000)
    VP->>VP: Try Resemblyzer encoder
    alt Resemblyzer available
        VP->>VP: embed_utterance() → 256-d
    else Fallback
        VP->>VP: MFCC 80-d + Delta 40-d + Spectral 8-d = 128-d
        VP->>VP: L2 normalize
    end
    VP-->>API: [embedding list]
    API->>DB: UPDATE students SET voice_embedding=... WHERE student_id=...
    API-->>Browser: {success: "Voice profile enrolled"}
```

---

## 4. Faculty QR Attendance — Anti-Proxy Rotating Token

```mermaid
sequenceDiagram
    participant Teacher as Faculty Browser
    participant API as /api/attendance
    participant Timer as 5s Timer Loop
    participant Student as Student Browser

    Teacher->>API: GET /api/attendance/qr-token?subject_id=X
    API->>API: bucket = int(time.time()) // 5
    API->>API: SHA-256(subject_id:bucket:SECRET)[:12]
    API-->>Teacher: {token, bucket}
    Teacher->>Teacher: Render QR code + countdown
    Note over Timer: Every 5 seconds...
    Timer->>Teacher: Token refreshed → new QR displayed
    
    Student->>Student: Scan QR with html5-qrcode camera
    Student->>API: POST /api/attendance/qr-checkin\n(subject_id, token, student_id)
    API->>API: verify_qr_token: check bucket±1
    alt Token valid
        API->>API: Check enrollment; auto-enroll if missing
        API->>API: create_attendance(is_present=True)
        API-->>Student: ✅ Attendance recorded
    else Token expired/invalid
        API-->>Student: ❌ 400 Invalid or expired QR token
    end
```

---

## 5. Group Photo Face Scan (Classroom Roll-Call)

```mermaid
flowchart TD
    T(["Teacher clicks\n'Upload Classroom Photo'"]) --> U["POST /api/attendance/photo-scan\n(subject_id + image)"]
    U --> E1["Fetch enrolled students\nfor subject from Supabase"]
    E1 --> E2["candidate_ids = [enrolled student IDs]"]
    E2 --> F["face_pipeline.predict_attendance\n(image, candidate_ids)"]
    F --> D1["dlib: detect all faces in photo\n(DETECTOR_UPSAMPLE_TIMES=2)"]
    D1 --> D2["For each face:\ncompute 128-d descriptor"]
    D2 --> D3["Filter embedding DB to\ncandidate students only"]
    D3 --> D4["L2 Euclidean distance\nvs all candidate vectors"]
    D4 --> D5{"Distance ≤ 0.55\nfor any candidate?"}
    D5 -- "Match" --> M["Mark student_id as PRESENT"]
    D5 -- "No match" --> N["Student marked ABSENT"]
    M & N --> L["Batch INSERT into\nattendance_logs"]
    L --> R["Return:\nfaces_detected, matched_ids,\npresent_ids, absent_ids"]
```

---

## 6. Voice Roll-Call (Audio Speaker Identification)

```mermaid
flowchart TD
    T(["Teacher uploads\nclassroom audio"]) --> API["POST /api/attendance/voice-scan\n(subject_id + audio)"]
    API --> E["Fetch enrolled students\nwith voice_embedding from Supabase"]
    E --> V["voice_pipeline.process_bulk_audio\n(audio_bytes, candidates_dict)"]
    V --> L1["librosa.load → 16kHz mono"]
    L1 --> L2["librosa.effects.split\n(top_db=25) → non-silent segments"]
    L2 --> L3["For each segment > 300ms:\n_extract_acoustic_embedding()"]
    L3 --> C["identify_speaker:\ncosine similarity vs all candidates"]
    C --> T1{"Similarity ≥ 0.60?"}
    T1 -- "Yes" --> P["Add to detected_scores"]
    T1 -- "No" --> A["Student absent"]
    P & A --> Log["Batch log attendance\nfor ALL enrolled students"]
    Log --> R["Return: detected_students\n(with confidence %), absent_ids"]
```

---

## 7. AI Risk Predictor — Hybrid SMA + Logistic Regression

```mermaid
flowchart TD
    IN(["Input: student_logs\n(list of is_present bools)"]) --> CALC["Calculate:\ntotal, attended, pct"]
    CALC --> SMA["SMA Slope:\n_sma_slope(last 5 sessions)"]
    CALC --> ROWS["Build rolling DataFrame\n(1 row per session)"]
    ROWS --> LR{"len(df) >= 10?"}
    LR -- "No (< 10 rows)" --> SMAONLY["Use SMA only:\nat_risk = pct<80 OR\n(pct<85 AND slope<-0.2)"]
    LR -- "Yes (≥ 10 rows)" --> LRFIT["LogisticRegression.fit\nX=[total,attended,pct]\ny=[pct<75]"]
    LRFIT --> PROB["lr_prob = predict_proba"]
    PROB --> HYBRID["Hybrid Score:\n0.6×LR + 0.4×SMA-slope-risk"]
    HYBRID --> TIER["at_risk = combined > 0.5"]
    SMAONLY & TIER --> RESULT{"Assign Tier"}
    RESULT -- "pct≥85 & not at_risk" --> SAFE["✅ SAFE\nKeep it up!"]
    RESULT -- "pct≥75 or not at_risk" --> WARN["⚠️ AT RISK\nAttend next N sessions"]
    RESULT -- "else" --> CRIT["🚨 CRITICAL\nSee teacher immediately"]
```

---

## 8. Admin 2FA Biometric Security Gate

```mermaid
sequenceDiagram
    actor Admin
    participant Browser as admin.html
    participant API as /api/admin
    participant FP as face_pipeline.py
    participant Vault as admin_face_vector.json

    Admin->>Browser: Navigate to admin.html
    Browser->>Browser: Check if admin face enrolled
    alt Not enrolled
        Browser->>Browser: Redirect → admin-setup.html
        Admin->>Browser: Enter master passcode + webcam
        Browser->>API: POST /api/admin/register-admin-face
        API->>Vault: Save 128-d vector JSON
    end
    Admin->>Browser: Enter Master Key (admin123)
    Admin->>Browser: Allow webcam capture
    Browser->>API: POST /api/admin/login-2fa\n(passcode + image)
    API->>Vault: load_admin_face_vector()
    API->>FP: get_face_embeddings(image)
    API->>API: L2 distance vs vault vector
    alt Distance ≤ 0.48
        API->>API: generate_session_token(role=admin)
        API->>API: log_admin_attempt(status=SUCCESS)
        API-->>Browser: ✅ {token, expires_in}
        Browser->>Browser: Load Admin Intelligence Hub
    else Distance > 0.48 or key wrong
        API->>API: log_admin_attempt(status=FAIL)
        API-->>Browser: ❌ 401 Unauthorized
    end
```

---

## 9. AttendSmartly Recovery Calculator

```mermaid
flowchart TD
    IN(["GET /api/insights/student-recovery/{id}"]) --> DB["Fetch all attendance_logs\nfor student (all subjects)"]
    DB --> CALC["overall_pct = attended/total × 100"]
    CALC --> N75{"overall_pct < 75%?"}
    N75 -- "Yes" --> F75["needed_for_75 = ceil((0.75×T - A) / 0.25)"]
    N75 -- "No" --> S75["safe_skips = floor((A - 0.75×T) / 0.75)"]
    CALC --> N85{"overall_pct < 85%?"}
    N85 -- "Yes" --> F85["needed_for_85 = ceil((0.85×T - A) / 0.15)"]
    CALC --> SUBJ["Per-subject breakdown:\nstatus = SAFE/WARNING/DEBARRED"]
    F75 & S75 & F85 & SUBJ --> OUT["Return:\noverall_pct, needed_for_75,\nneeded_for_85, safe_skips,\nsubject_cards, recent_history"]
```

---

## 10. Complete Request-Response Architecture

```mermaid
graph LR
    subgraph Client["Browser (Vanilla JS fetch())"]
        UI["UI Event\n(button click / camera)"]
        JWT["localStorage: JWT token\nX-Auth-Token header"]
    end

    subgraph Server["FastAPI Server"]
        MW["CORS Middleware"]
        RT["Router Dispatch\n(prefix-based)"]
        EP["Endpoint Handler"]
        AUTH_MW["verify_session_token()\nHMAC-SHA256 stateless"]
    end

    subgraph ML["ML Pipelines"]
        FP["face_pipeline\n(dlib)"]
        VP["voice_pipeline\n(librosa)"]
        RP["risk_predictor\n(sklearn)"]
    end

    subgraph Data["Persistence"]
        SB["Supabase\nPostgreSQL"]
        LOCAL["admin_face_vector.json"]
    end

    UI --> JWT --> MW --> RT --> AUTH_MW --> EP
    EP --> FP & VP & RP
    EP --> SB & LOCAL
    SB --> EP --> UI
```

---

*All diagrams reflect the live production codebase — October 2026*
