# SnapClass — REST API Reference

> **Base URL:** `http://localhost:8000`  
> **Auth:** Most protected endpoints require `X-Auth-Token: <JWT>` header  
> **Content-Type:** `application/json` or `multipart/form-data` (for file uploads)

---

## Authentication (`/api/auth`)

### POST `/api/auth/teacher/login`
Authenticate a faculty account.

| Field | Type | Required |
|-------|------|----------|
| `username` | string | ✅ |
| `password` | string | ✅ |

**Response:** `{ success, teacher, token, expires_in: 28800 }`

---

### POST `/api/auth/teacher/register`
Register a new faculty account.

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |
| `username` | string | ✅ |
| `password` | string | ✅ |

**Response:** `{ success, message }`

---

### PUT `/api/auth/teacher/profile/{teacher_id}`
Update faculty profile details.

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |
| `username` | string | ✅ |
| `password` | string | ❌ |
| `department`, `contact`, `bio` | string | ❌ |

**Response:** `{ success, teacher, message }`

---

### POST `/api/auth/student/register`
Enroll a new student with face biometrics. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |
| `image` | file (JPEG/PNG) | ✅ |

**Response:** `{ success, student, student_id, token, expires_in: 86400 }`  
**Errors:** 400 if no face or multiple faces detected

---

### POST `/api/auth/student/face-login`
Passwordless student login via webcam. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `image` | file (JPEG/PNG) | ✅ |

**Response:** `{ success, student_id, token, expires_in: 86400 }`  
**Errors:** 404 if unrecognized, 400 if multiple faces

---

### POST `/api/auth/student/voice-enroll`
Enroll student 128-d voice biometric profile. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `student_id` | int | ✅ |
| `audio` | file (WAV/MP3/M4A) | ✅ |

**Response:** `{ success, student_id, message }`

---

### GET `/api/auth/verify-session`
Validate a JWT session token.

| Header | Value |
|--------|-------|
| `Authorization` | `Bearer <token>` or `X-Auth-Token: <token>` |

**Response:** `{ success, claims: { id, role, exp } }`

---

## Attendance & Roll-Call (`/api/attendance`)

### GET `/api/attendance/qr-token`
Generate a time-bucketed 12-char QR token (rotates every 5 seconds).

| Query Param | Type | Required |
|-------------|------|----------|
| `subject_id` | int | ✅ |

**Response:** `{ token, bucket }`

---

### POST `/api/attendance/qr-checkin`
Direct QR check-in for a verified student.

| Field | Type | Required |
|-------|------|----------|
| `subject_id` | int | ✅ |
| `token` | string | ✅ |
| `student_id` | int | ✅ |

**Response:** `{ success, message, student_id }`  
**Errors:** 400 if token expired/invalid

---

### POST `/api/attendance/photo-scan`
Batch classroom group photo recognition. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `subject_id` | int | ✅ |
| `image` | file (JPEG/PNG) | ✅ |

**Response:** `{ success, faces_detected, students_matched, present_ids, absent_ids }`

---

### POST `/api/attendance/voice-scan` *(alias: `/recognize-voice`)*
Classroom audio roll-call via speaker identification. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `subject_id` | int | ✅ |
| `audio` | file (WAV/MP3/M4A) | ✅ |

**Response:** `{ success, total_enrolled, detected_students: [{student_id, name, confidence}], absent_ids, timestamp, message }`

---

### POST `/api/attendance/qr-submit`
Dual FaceID + QR token check-in from student's own device. (`multipart/form-data`)

| Field | Type | Required |
|-------|------|----------|
| `subject_id` | int | ✅ |
| `token` | string | ✅ |
| `image` | file (JPEG/PNG) | ✅ |

**Response:** `{ success, message, student_id }`

---

### POST `/api/attendance/mark-batch`
Manual batch attendance marking (teacher override). (`application/json`)

```json
{
  "logs": [
    { "student_id": 1, "subject_id": 2, "is_present": true }
  ],
  "timestamp": "2026-10-21T10:00:00"
}
```

**Response:** `{ success, count, data }`

---

## Subjects & Rosters (`/api/subjects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/subjects/teacher/{teacher_id}` | List courses taught by faculty |
| `POST` | `/api/subjects/create` | Create new course (name, subject_code, section, teacher_id) |
| `GET` | `/api/subjects/student/{student_id}` | List courses student is enrolled in |
| `POST` | `/api/subjects/enroll` | Enroll student: `{ student_id, subject_id }` |
| `DELETE` | `/api/subjects/{subject_id}` | Delete a course |
| `DELETE` | `/api/subjects/unenroll` | Unenroll student: query `student_id + subject_id` |

---

## AI Insights & Analytics (`/api/insights`)

### GET `/api/insights/student-radar/{student_id}`
Cumulative attendance gauge, streak, and day-of-week habits.

| Query Param | Type | Required |
|-------------|------|----------|
| `subject_id` | int | ❌ (optional filter) |

**Response:** `{ success, streak, risk_profile, habits, total_logs }`

---

### GET `/api/insights/student-recovery/{student_id}`
Recovery target roadmap — exact classes needed for 75%/85%.

**Response:** `{ overall_pct, total_classes, attended_classes, needed_for_75, needed_for_85, safe_skips, subject_cards, recent_history }`

---

### GET `/api/insights/risk/{subject_id}`
ML dropout risk radar for all students in a course.

**Response:** `{ success, data: [{ student_id, name, pct, tier, label, color, recommendation, slope, lr_prob }] }`

---

## Dean & Admin Hub (`/api/admin`)

All admin endpoints (except login) require header: `X-Admin-Token: <token>` or `X-Admin-Key: <token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/login-2fa` | Master Key + facial biometric 2FA |
| `POST` | `/api/admin/register-admin-face` | Emergency face vector enrollment |
| `GET` | `/api/admin/overview` | Campus KPI metrics ribbon |
| `GET` | `/api/admin/analytics` | Chart.js datasets (trend, donut, bar) |
| `GET` | `/api/admin/face-gallery` | Student vector directory |
| `POST` | `/api/admin/tuning` | Set Euclidean threshold: `{ threshold: 0.55 }` |
| `GET` | `/api/admin/faculty-compliance` | Faculty daily roll-call status |
| `GET` | `/api/admin/defaulters?threshold={pct}` | Defaulter list with configurable cutoff |
| `POST` | `/api/admin/trigger-action` | 1-click actions: `{ action_type: "dispatch_warnings" }` |

---

## Exports (`/api/exports`)

### GET `/api/exports/attendance/{subject_id}`
Download university-compliant CSV for a course.

**Response:** CSV file download  
**Columns:** `Student ID, Student Name, Total Classes, Attended Classes, Attendance %, Status`  
**Status values:** `SAFE` (≥80%) · `WARNING` (75–79%) · `DEBARRED` (<75%)

---

## Health Check

### GET `/api/health`
Server liveness probe.

**Response:** `{ status: "healthy" }`

---

*SnapClass REST API — October 2026*
