<div align="center">
  <img src="https://i.ibb.co/YTYGn5qV/logo.png" alt="SnapClass Logo" width="120" />
  <h1>SnapClass 📸</h1>
  <p><strong>AI-Powered Student Attendance & Engagement System</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=streamlit)](https://streamlit.io)
  [![Supabase](https://img.shields.io/badge/Supabase-3ECF8E.svg?style=for-the-badge&logo=supabase)](https://supabase.com)
  [![AI](https://img.shields.io/badge/AI_Powered-dlib_|_Resemblyzer-black.svg?style=for-the-badge&logo=openai)]()
</div>

---

## 🚀 Overview

**SnapClass** redefines how attendance is managed in modern classrooms. Moving beyond simple face recognition, it provides a comprehensive suite of tools designed to automate attendance tracking, prevent proxies, and deliver actionable AI-driven insights to educators.

Whether you're a teacher looking to save 15 minutes of class time or a student keeping track of your own metrics, SnapClass makes the experience frictionless.

### ✨ Key Features

- 👤 **FaceID Authentication:** Students log in seamlessly using their face.
- 📸 **Automated Attendance:** Teachers upload classroom photos, and the deep-learning pipeline instantly identifies enrolled students.
- 🎙️ **Voice Verification (Optional):** Dual-factor biometric attendance using voice embeddings (`resemblyzer`).
- 🛡️ **Anti-Proxy Infrastructure:** *[Upcoming]* Liveness detection to ensure physical presence.
- 📊 **Teacher Dashboard:** Create subjects, manage enrollments, and track live attendance metrics.
- 📉 **Predictive Analytics:** *[Upcoming]* AI risk scoring to identify students dropping below required attendance thresholds.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Teacher / Student] -->|Access via| B(Streamlit UI)
    B --> C{Biometric Auth}
    C -->|Face Embeddings| D[dlib / face_recognition]
    C -->|Voice Embeddings| E[Resemblyzer / librosa]
    D --> F[(Supabase)]
    E --> F
    F --> G[Attendance Engine]
    G --> H[Analytics Dashboard]
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

### 2. Install Dependencies
Make sure you have CMake installed (required for `dlib`), then run:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.streamlit/secrets.toml` file with your Supabase credentials:
```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📂 Project Structure

```text
snapclass/
├── .streamlit/             # Config and Secrets
├── src/
│   ├── components/         # Reusable UI Dialogs (Enroll, Share, etc.)
│   ├── database/           # Supabase Integration & Auth (bcrypt)
│   ├── pipelines/          # AI Models (Face & Voice Pipelines)
│   ├── screens/            # Main Views (Teacher, Student, Home)
│   └── ui/                 # Styling and Layout Settings
├── app.py                  # Application Entry Point
└── requirements.txt        # Python Dependencies
```

---

## 🔒 Security & Privacy (OWASP 2025 Aligned)
- **Zero Trust Biometrics:** Face and voice embeddings are stored as mathematical arrays, not as raw images or audio files.
- **Secure Authentication:** Teacher passwords are salted and hashed using `bcrypt`.
- **RBAC:** Strict separation of concerns between Teacher and Student routing.

---

<div align="center">
  <p>Built for GTU Minor Project.</p>
</div>