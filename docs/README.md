# SnapClass Documentation Index

> **Project:** G5 — AI-Powered Student Attendance Management System  
> **Seminar IV:** Final Demonstration — 21 October 2026

---

## 📁 Files in `docs/`

| File | Purpose | Use When |
|------|---------|----------|
| [`01-features-overview.md`](./01-features-overview.md) | Complete feature registry (38+ features, 3 roles) | GitHub README supplement, viva reference |
| [`02-workflow-diagrams.md`](./02-workflow-diagrams.md) | 10 Mermaid workflow diagrams for all major flows | GitHub docs, report diagrams |
| [`03-api-reference.md`](./03-api-reference.md) | Complete REST API reference (6 route groups) | GitHub docs, viva reference |
| [`04-final-report.md`](./04-final-report.md) | Full project report — all sections | Copy into Word for submission |
| [`05-presentation-outline.md`](./05-presentation-outline.md) | 19-slide PowerPoint outline with speaker notes | Build your `.pptx` from this |

---

## 🚀 Quick Actions

### To build the PowerPoint:
1. Open `05-presentation-outline.md`
2. Each `## Slide N —` block = one slide
3. For diagrams: render `02-workflow-diagrams.md` in any Mermaid viewer → screenshot → paste into PowerPoint

### To write the Word report:
1. Open `04-final-report.md`
2. Copy into Word, apply college formatting (font, margins, header/footer)
3. All Mermaid diagrams → paste as images

### Mermaid Rendering Tools:
- **Online:** https://mermaid.live — paste any code block, export PNG
- **VS Code:** Install "Markdown Preview Mermaid Support" extension
- **GitHub:** Renders automatically in any `.md` file

---

## 📋 Seminar IV Checklist

Based on the Minor Project Schedule requirements:

- [ ] Final presentation (PowerPoint) ready
- [ ] Final project report (Word/PDF) ready  
- [ ] Live working demo ready (all 7 demo scenarios)
- [ ] Supabase database seeded with test data (`python seed_db.py`)
- [ ] FastAPI server running (`uvicorn api.main:app --reload`)
- [ ] All 3 portals tested: student.html, teacher.html, admin.html
- [ ] Admin face vector enrolled (admin-setup.html)
- [ ] At least one faculty account created
- [ ] At least 2–3 students enrolled with face embeddings
- [ ] Group photo scan demo ready

---

## 📊 Project Summary Card

```
Project Title : SnapClass — AI-Powered Student Attendance Management System
Group         : G5
Semester      : 5 IT
Tech Stack    : FastAPI + Vanilla HTML/CSS/JS + Supabase PostgreSQL
AI Components : dlib ResNet-34 (face) + Librosa (voice) + Scikit-Learn (risk)
Portals       : 3 (Student, Faculty, Admin)
API Routes    : 6 groups, 28+ endpoints
Database      : 5 tables in Supabase PostgreSQL
Features      : 38+ across all roles
```

---

*SnapClass Documentation — Generated October 2026 for GTU Minor Project Seminar IV*
