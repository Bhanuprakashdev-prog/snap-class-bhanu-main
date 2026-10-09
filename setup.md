# SnapClass 🎓 Setup & Production Cloud Deployment Guide

This guide provides end-to-end setup instructions for **SnapClass**, covering local development, database configuration, containerization, and free cloud deployment options with HTTPS for mobile camera biometrics.

---

## 📌 Table of Contents
1. [Local Development Setup](#1-local-development-setup)
2. [Database Configuration (Supabase PostgreSQL)](#2-database-configuration-supabase-postgresql)
3. [Environment Variables](#3-environment-variables)
4. [Cloud Deployment Methods](#4-cloud-deployment-methods)
   - [Method A: Render.com (Recommended Free/Low-Cost)](#method-a-rendercom-recommended)
   - [Method B: Railway.app (Fastest 1-Click Git Deploy)](#method-b-railwayapp-fastest-1-click)
   - [Method C: Fly.io (Global Edge Docker)](#method-c-flyio-global-edge-docker)
   - [Method D: Self-Hosted VPS / Ubuntu / Docker](#method-d-self-hosted-vps--ubuntu--docker)
   - [Method E: Hugging Face Spaces (Docker SDK)](#method-e-hugging-face-spaces)
5. [Default Test Credentials & Access Points](#5-default-test-credentials--access-points)
6. [Mobile Camera & HTTPS Security Requirements](#6-mobile-camera--https-security-requirements)

---

## 1. Local Development Setup

### System Prerequisites
- **Python 3.11+**
- **CMake** & **C++ Build Tools** (required to compile `dlib` facial recognition bindings)
- **FFmpeg** & **libsndfile** (for Librosa voice biometric processing)

### Step 1: Clone Repository
```bash
git clone https://github.com/Bhanuprakashdev-prog/snapclass.git
cd snapclass
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows (PowerShell):
python -m venv venv
venv\Scripts\Activate.ps1

# Linux / macOS (Bash):
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Launch FastAPI Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
The server will start at `http://127.0.0.1:8000`.

---

## 2. Database Configuration (Supabase PostgreSQL)

SnapClass connects to **Supabase** via PostgreSQL REST API. 

### Required Tables Schema:
```sql
-- 1. Teachers Table
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    contact VARCHAR(50),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Students Table (with 128-d Face & Voice embeddings)
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    face_embedding JSONB,
    voice_embedding JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Subjects Table
CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    section VARCHAR(10) NOT NULL,
    teacher_id INT REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Subject Enrollments (Rosters)
CREATE TABLE subject_students (
    id SERIAL PRIMARY KEY,
    subject_id INT REFERENCES subjects(subject_id) ON DELETE CASCADE,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE(subject_id, student_id)
);

-- 5. Attendance Verification Logs
CREATE TABLE attendance_logs (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id INT REFERENCES subjects(subject_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_present BOOLEAN NOT NULL DEFAULT TRUE
);
```

### Seed Synthetic Benchmark Data (Optional)
To seed 20 benchmark students (with pre-computed 128-d face & voice vectors), 3 subjects, and 900+ attendance records:
```bash
python seed_db.py
```

---

## 3. Environment Variables

Configure the following environment variables in your deployment environment or locally in `.streamlit/secrets.toml`:

| Variable | Description | Example / Default |
|---|---|---|
| `SUPABASE_URL` | Supabase project API URL | `https://xyzcompany.supabase.co` |
| `SUPABASE_KEY` | Supabase `service_role` or `anon` key | `eyJhbGciOi...` |
| `ADMIN_KEY` | Master pass-key for Admin 2FA gate | `admin123` |
| `SESSION_SECRET` | Secret salt for stateless HMAC-SHA256 tokens | Any 32+ char random string |
| `PORT` | Listening port for web dynos | `8000` |

---

## 4. Cloud Deployment Methods

---

### Method A: Render.com (Recommended Free/Low-Cost)

Render offers automatic Docker container builds with free managed SSL certificates.

1. **Push your code to GitHub**.
2. Go to [dashboard.render.com](https://dashboard.render.com) and sign in.
3. Click **New +** ➔ **Blueprint** (or **Web Service**).
4. Select your `snapclass` repository.
5. In **Environment Variables**, provide:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ADMIN_KEY`
   - `SESSION_SECRET`
6. Click **Deploy**. Render will build the [`Dockerfile`](file:///d:/Subham/Project/snapclass/Dockerfile) and provide an active `https://snapclass.onrender.com` domain.

---

### Method B: Railway.app (Fastest 1-Click)

1. Go to [railway.app](https://railway.app) ➔ Click **New Project**.
2. Select **Deploy from GitHub repo** and choose `snapclass`.
3. Go to **Variables** tab and set:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-key
   ADMIN_KEY=admin123
   SESSION_SECRET=snapclass-super-secret-key-2026
   PORT=8000
   ```
4. In **Settings** ➔ **Networking**, click **Generate Domain** (e.g. `snapclass-production.up.railway.app`).

---

### Method C: Fly.io (Global Edge Docker)

1. Install Fly CLI:
   ```bash
   # Windows:
   pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
   # Linux/macOS:
   curl -L https://fly.io/install.sh | sh
   ```
2. Authenticate and launch:
   ```bash
   fly auth login
   fly launch --no-deploy
   ```
3. Set secrets:
   ```bash
   fly secrets set SUPABASE_URL="https://your-project.supabase.co" SUPABASE_KEY="your-key" ADMIN_KEY="admin123" SESSION_SECRET="your-secret"
   ```
4. Deploy:
   ```bash
   fly deploy
   ```

---

### Method D: Self-Hosted VPS / Ubuntu / Docker

For deployment on an Ubuntu VPS (AWS EC2, DigitalOcean Droplet, Oracle Cloud Free Tier):

1. **Install Docker on the VPS**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   ```
2. **Clone & Build**:
   ```bash
   git clone https://github.com/Bhanuprakashdev-prog/snapclass.git
   cd snapclass
   docker build -t snapclass .
   ```
3. **Run Container**:
   ```bash
   docker run -d \
     --name snapclass-prod \
     --restart always \
     -p 80:8000 \
     -e SUPABASE_URL="https://your-project.supabase.co" \
     -e SUPABASE_KEY="your-supabase-key" \
     -e ADMIN_KEY="admin123" \
     -e SESSION_SECRET="your-custom-hmac-secret" \
     snapclass
   ```

---

### Method E: Hugging Face Spaces

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces).
2. Choose **Docker** as the Space SDK.
3. Push your repository files to the Space.
4. Under Space **Settings** ➔ **Repository Secrets**, add `SUPABASE_URL`, `SUPABASE_KEY`, and `ADMIN_KEY`.
5. Hugging Face will build the Docker container and give you a free cloud-hosted instance.

---

## 5. Default Test Credentials & Access Points

| Portal | Route | Authentication Mechanism |
|---|---|---|
| 👨‍🎓 **Student Hub** | `/student.html` | Face Login or Selfie Self-Enrollment |
| 👨‍🏫 **Faculty Studio** | `/teacher.html` | Username: `prof_turing` / Pass: `teacher123` |
| 🏛️ **Dean & Admin Hub** | `/admin.html` | Passcode: `admin123` + Biometric 2FA Face Scan |
| 🚨 **Admin Face Setup** | `/admin-setup.html` | Passcode: `admin123` (Initial Master Vector Registration) |

---

## 6. Mobile Camera & HTTPS Security Requirements

> [!IMPORTANT]
> **HTTPS is strictly required for WebRTC Camera Access on mobile devices.**
> Modern mobile browsers (iOS Safari, Android Chrome) block camera and microphone access on non-localhost HTTP connections. 
> When deploying to **Render**, **Railway**, **Fly.io**, or using a custom domain with **Cloudflare/Let's Encrypt**, SSL is handled automatically.
