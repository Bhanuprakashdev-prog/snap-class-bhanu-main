# SnapClass — Final Presentation Script
## Seminar IV: PowerPoint Slide Outline (15–20 Slides)

> **Instructions:** This is a slide-by-slide outline with speaker notes for the `.pptx` presentation.  
> Copy slide titles + content into PowerPoint. Diagrams can be pasted as images from the workflow diagrams.

---

## Slide 1 — Title Slide

**Title:** SnapClass 🎓  
**Subtitle:** AI-Powered Student Attendance Management System

```
Group G5 | Semester 5 IT
[Member 1 Name]  [Enrollment No.]
[Member 2 Name]  [Enrollment No.]
[Member 3 Name]  [Enrollment No.]
[Member 4 Name]  [Enrollment No.]
Project Guide: [Guide Name]
Date: 21 October 2026
```

> 🎤 *Speaker Note:* "Good morning. Our project is SnapClass — an AI-powered attendance system that goes beyond face recognition to deliver prediction, recovery guidance, and anti-proxy infrastructure."

---

## Slide 2 — The Problem

**Title:** Why Attendance Management Is Broken

**Left column (Problems):**
- 📋 Manual roll-call wastes 10–15 min per session
- 🎭 Proxy attendance — friends marking absences as present
- 📉 Students hit 75% debarment threshold without warning
- 📦 Raw data — no insights, no action

**Right column (The Gap):**
```
Current systems can record attendance.
They cannot:
  → Verify who actually showed up
  → Predict who is about to be debarred
  → Tell students how to recover
```

> 🎤 *"The gap isn't recording attendance — it's making attendance intelligent."*

---

## Slide 3 — Literature Survey

**Title:** What Exists Already — And Why It's Not Enough

| Approach | Problem |
|----------|---------|
| Manual / Register | Slow, error-prone, proxy-vulnerable |
| Static QR Code | Screenshot → share → proxy done |
| RFID Cards | Hardware cost, card sharing |
| Basic Face Recognition | Photo spoofing, no liveness |
| Analytics Tools | Standalone — no attendance integration |

**Research Gap → SnapClass fills 4 missing pieces:**
1. Authenticity verification
2. Predictive intelligence
3. Recovery guidance
4. Multi-modal biometrics

> 🎤 *"Every group is building face recognition. We asked: what comes after the recognition?"*

---

## Slide 4 — Our Solution

**Title:** SnapClass — 4 Pillars

**Visual: 2×2 grid**

| 🔍 Biometric Identity | 🚫 Anti-Proxy |
|----------------------|--------------|
| Face + Voice recognition | 5-second rotating QR codes |
| **🤖 Predictive Intelligence** | **📈 Recovery Guidance** |
| ML risk radar — catch debarment risk early | Exact classes needed for 75% / 85% |

> 🎤 *"These four pillars together make SnapClass fundamentally different from any other attendance system."*

---

## Slide 5 — Architecture Evolution

**Title:** How We Got Here — From Prototype to Production

**Timeline visual:**

```
Seminar I (Aug)          Seminar II–III (Sep–Oct)       Seminar IV (Oct)
─────────────           ────────────────────────         ──────────────
Streamlit prototype  →  Realized limitations       →   FastAPI + HTML/JS
Single-file Python   →  Added proper backend       →   Full-stack REST API
No roles             →  Role-based portals         →   3 dedicated portals
```

**Why we migrated:**
- Streamlit: single-threaded, no routing, limited UI
- FastAPI: async, proper REST, mobile-compatible, modular

> 🎤 *"Choosing the right architecture made the project go from a demo to an actual product."*

---

## Slide 6 — System Architecture

**Title:** System Architecture

**Insert Mermaid diagram from `02-workflow-diagrams.md` — System Architecture diagram**

Three-layer architecture:
- **Client:** student.html, teacher.html, admin.html
- **API Gateway:** FastAPI with 6 route groups
- **Persistence:** Supabase PostgreSQL + local admin vault

> 🎤 *"Clean separation — the frontend has no direct database access. Everything goes through FastAPI."*

---

## Slide 7 — Technology Stack

**Title:** Technology Stack

| Layer | Technology |
|-------|-----------|
| 🌐 Frontend | Vanilla HTML5 + CSS3 + JavaScript |
| ⚡ Backend | Python 3.11 + FastAPI |
| 🧠 Face AI | dlib ResNet-34 (128-d) |
| 🎤 Voice AI | Librosa MFCC + Resemblyzer |
| 📊 Risk ML | Scikit-Learn Logistic Regression |
| 🗄️ Database | Supabase (PostgreSQL cloud) |
| 🔒 Security | bcrypt + HMAC-SHA256 JWT |
| 📱 QR | segno + html5-qrcode |

---

## Slide 8 — Database Design

**Title:** Database Schema

**Insert ER diagram from `02-workflow-diagrams.md`**

5 tables:
- `teachers` — faculty accounts (bcrypt password)
- `students` — student biometrics (face + voice embedding JSON)
- `subjects` — academic courses
- `subject_students` — enrollment junction
- `attendance_logs` — every attendance record with timestamp

> 🎤 *"No raw images are stored anywhere — only 128-dimensional floating-point descriptors."*

---

## Slide 9 — AI: Face Recognition

**Title:** How Face Recognition Works

**Flowchart:**
```
Webcam Capture
    ↓
dlib HOG Face Detection
    ↓
68-point Landmark Alignment
    ↓
ResNet-34 → 128-d Descriptor
    ↓
L2 Euclidean Distance vs Enrolled
    ↓
Distance ≤ 0.55 → Match ✅
Distance > 0.55 → Reject ❌
```

**Admin Tuning:** Threshold adjustable (0.45 Strict → 0.65 Lenient) from admin panel.

> 🎤 *"The threshold is configurable by the administrator — strict for high-security situations, lenient when lighting is poor."*

---

## Slide 10 — AI: Voice Biometrics

**Title:** Voice Speaker Identification

**Visual: embedding construction**

```
Audio Recording (3–5 seconds)
    ↓
Librosa: 16kHz mono
    ↓
MFCC Features:     80-d (mean, std, max, min × 20 coefficients)
Delta MFCC:        40-d (temporal changes)
Spectral Features:  8-d (centroid, bandwidth, ZCR, energy)
    ↓
Total: 128-d L2-normalized vector
    ↓
Cosine Similarity ≥ 0.60 → Identified ✅
```

> 🎤 *"Voice verification adds a second layer — even if someone brings a photo of a classmate, they can't replicate their voice."*

---

## Slide 11 — AI: Risk Predictor

**Title:** Predicting Debarment Before It Happens

**Visual: risk tier pyramid**

```
🚨 CRITICAL — pct < 75%, deteriorating trend
⚠️ AT RISK — borderline, declining slope
✅ SAFE — pct ≥ 85%, stable trend
```

**Two-signal hybrid model:**
- **SMA Slope:** Trend of last 5 sessions (always active)
- **Logistic Regression:** Probability model (activates at ≥10 records)
- **Combined:** `0.6 × LR + 0.4 × slope-risk`

> 🎤 *"Unlike simple percentage calculators, SnapClass catches a student who is still at 80% but dropping 5% every week — before they fall below 75%."*

---

## Slide 12 — Anti-Proxy QR System

**Title:** Defeating Proxy Attendance — Rotating QR Codes

**Visual: token rotation diagram**

```
Server Time (Unix epoch)
    ↓
bucket = int(time.time()) // 5
    ↓
token = SHA-256(subject_id:bucket:SECRET)[:12]
    ↓
QR displayed for 5 seconds
    ↓
Token rotates → old screenshot = invalid ❌
```

**Student check-in flow:**
1. Scan QR via phone camera
2. Token verified (bucket ± 1 tolerance)
3. Attendance marked immediately ✅

> 🎤 *"Even if a student forwards the QR screenshot to a friend, by the time they receive it — it's expired."*

---

## Slide 13 — Recovery Calculator (Student View)

**Title:** AttendSmartly — Knowing Your Target

**Visual: 3-panel student dashboard**

**Panel 1 — Standing Gauge:**
- SVG radial: 73% → 🚨 Debarred zone

**Panel 2 — Recovery Target:**
```
You need to attend the NEXT 8 consecutive classes
to reach 75% eligibility.

To reach 85% honors standing: 22 more classes needed.
```

**Panel 3 — What-If Simulator:**
- Slider: "If I skip 3 more classes → 68% → DEBARRED"

> 🎤 *"Students always know exactly what they need to do — no more surprises at exam time."*

---

## Slide 14 — Admin Intelligence Hub

**Title:** Dean & Admin Compliance Hub

**Screenshots / Feature list:**

- 📊 **Chart.js Analytics:** 7-day trend, donut (Safe/Risk/Debarred), cross-course comparison
- 🔒 **2FA Security:** Master key + biometric face verification (0.48 threshold)
- 🚨 **Defaulter Watchlist:** Configurable cutoff, 1-click exam CSV export
- 📡 **AI Summary Engine:** "34 students at critical risk — dispatch warnings?"
- 👨‍🏫 **Faculty Compliance:** Did faculty take attendance today?

> 🎤 *"The admin portal turns a passive registry into an active campus intelligence dashboard."*

---

## Slide 15 — Live Demo Summary

**Title:** What We Will Demonstrate

| Demo | Feature |
|------|---------|
| 1 | Teacher login → Create course → Generate QR |
| 2 | Student face enrollment → Face login |
| 3 | Student QR scan → Attendance marked |
| 4 | Faculty: upload group photo → batch recognition |
| 5 | Student: View recovery calculator |
| 6 | Admin: 2FA login → Analytics dashboard |
| 7 | Faculty: ML Risk Radar |

> 🎤 *"We will run through all 7 demos live. The Supabase database is live — all data is real."*

---

## Slide 16 — Testing Results

**Title:** Testing Summary

| Test Category | Tests Run | Pass Rate |
|---------------|-----------|-----------|
| Face Recognition (known faces) | 20 | 95% |
| Face Rejection (unknown persons) | 10 | 100% |
| QR Anti-Proxy (expired tokens) | 10 | 100% |
| QR Check-In (valid window) | 15 | 100% |
| Risk Predictor (various scenarios) | 8 | 100% |
| Voice Identification | 10 | 80% |
| Error Handling (bad inputs) | 12 | 100% |

---

## Slide 17 — Conclusion

**Title:** What SnapClass Achieves

**Four problems solved:**

| Problem | Solution |
|---------|---------|
| Proxy attendance | Rotating 5s QR + biometric verification |
| No early warning | ML risk predictor with trend analysis |
| No recovery guidance | AttendSmartly calculator |
| Manual roll-call | Group photo + voice scan automation |

**The project is:**
- ✅ Full-stack production system (not a prototype)
- ✅ 38+ features across 3 roles
- ✅ Real Supabase database
- ✅ Live API with Swagger docs at `/docs`

---

## Slide 18 — Future Scope

**Title:** What's Next for SnapClass

| Enhancement | Description |
|-------------|-------------|
| 🔴 Liveness Detection | Blink/head movement challenge to defeat photo spoofing |
| 📱 Mobile PWA | Progressive Web App for native-feel on phones |
| 📧 Alert System | Email/SMS for at-risk students |
| 🏛️ Exam Integration | Auto-send debarment list to exam office |

---

## Slide 19 — Thank You

**Title:** Thank You

```
SnapClass — G5, Semester 5 IT
AI-Powered Student Attendance Management System

GitHub: [repo URL]
Demo URL: http://localhost:8000

Questions?
```

**Team Members:**
```
[Name 1]  [Name 2]  [Name 3]  [Name 4]
```

**Guide:** [Guide Name]

---

*This outline is for PowerPoint creation. Diagrams → export as PNG from rendered Markdown or draw in PowerPoint.*
