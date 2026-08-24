# Architectural Plan: SnapClass Complete UI & Dashboard Overhaul

## 1. Executive Summary & UI Framework Strategy
The goal is to transform SnapClass from a basic Python layout into a modern, aesthetic web application.

### UI Languages & Technologies in the Streamlit Ecosystem
Streamlit supports 3 primary tiers for modern UI engineering:

| Tier | UI Stack / Languages | How It Works in Streamlit | Best For |
|---|---|---|---|
| **Tier 1: Advanced Design System (Recommended)** | **HTML5 + CSS3 + Vanilla JS + CSS Variables** | Injected via `st.markdown` & `components.html`. Custom component cards, responsive flex/grid layouts, micro-animations, glassmorphism. | **Fastest, no build step, production-ready, highly aesthetic.** |
| **Tier 2: Bidirectional Custom Components** | **React + TypeScript + TailwindCSS / Lucide** | Streamlit Component API (`streamlit-component-lib`). Renders custom React widgets inside Streamlit frames and passes state back to Python. | Complex interactive widgets (custom audio visualizers, interactive charts). |
| **Tier 3: Decoupled Full-Stack Architecture** | **FastAPI (Python Backend) + Next.js / Vite React (Frontend)** | Python serves REST/WebSocket AI endpoints; Next.js renders the full SPA. | Complete departure from Streamlit if full native mobile/SPA app is required. |

---

## 2. Redesign Architecture Plan (Tier 1 & 2 Execution)

### Phase 1: Core Design System & Theme Engine (`src/ui/`)
- **Modern Color Palette (Tailwind-inspired)**:
  - Primary Indigo/Violet: `#4F46E5` / `#6366F1`
  - Background Neutral: `#F8FAFC` (Slate 50)
  - Surface Cards: Pure White `#FFFFFF` with border `#E2E8F0` and `backdrop-filter: blur(12px)`
  - Status Colors: Emerald `#10B981` (Safe), Amber `#F59E0B` (At-Risk), Rose `#F43F5E` (Critical)
- **Typography Hierarchy**:
  - Headings: **Outfit** (Weights 600, 700, 800)
  - Body & Numbers: **Plus Jakarta Sans** / **Inter** (Weights 400, 500, 600)
- **Responsive Layout Tokens**:
  - Unified mobile navbar with sticky back chip and branding.
  - Interactive hover states and active button feedback.

### Phase 2: Teacher Portal Dashboard Overhaul (`src/screens/teacher_screen.py`)
- **Metric Highlights Row**:
  - Total Enrolled Students, Active Courses, Average Attendance Rate, Students At Risk badge counter.
- **Modern Tab Switcher**:
  - Segmented control styling for `[📸 Live Attendance | 📚 Course Manager | 📋 History Records | 🤖 AI Risk Radar]`.
- **Live QR Studio**:
  - High-resolution SVG/PNG rendering, animated pulsing countdown timer (5s circle ring), and quick manual override drawer.
- **AI Attendance Analysis Results Dialog**:
  - High-contrast badges (Present/Absent), confidence scores, and instant export to CSV.

### Phase 3: Student Portal Dashboard Overhaul (`src/screens/student_screen.py`)
- **Hero FaceID Check-in Card**:
  - Camera view with natural unmirrored feed, centering guide, and instant feedback status.
- **Student Stats Card**:
  - Attendance rate radial progress gauge (e.g., `85% - Good Standing`).
- **Enrolled Course Grid**:
  - Rich interactive course cards with progress bars and session history breakdown.

### Phase 4: AI & Pipeline Hardening
- **Dual Voice Pipeline**:
  - Librosa 128-d acoustic feature engine with silence trimming.
- **Hybrid Risk Predictor**:
  - SMA slope + Logistic Regression trend warning.

---

## 3. Tasks Breakdown

- [ ] **Task 1: Design Tokens & CSS Framework** → Implement complete CSS design system in `src/ui/base_layout.py`.
- [ ] **Task 2: Component Architecture** → Build reusable card, badge, metric, and header components in `src/components/`.
- [ ] **Task 3: Teacher Portal Redesign** → Rebuild teacher dashboard with stats grid, tab bar, and QR session studio.
- [ ] **Task 4: Student Portal Redesign** → Rebuild student dashboard with course grid, stats gauges, and FaceID check-in.
- [ ] **Task 5: Mobile & Cross-Device Audit** → Verify layout responsiveness on both mobile screens (e.g. 375px) and desktop.
