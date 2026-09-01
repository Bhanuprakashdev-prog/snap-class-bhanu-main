"""
SnapClass Database Seeding Script
Seeds benchmark courses, students with 128-d face and voice descriptors, and 30 days of attendance logs.
"""
import numpy as np
from datetime import datetime, timedelta
from src.database.config import supabase
from src.database.db import hash_pass

def generate_128d_vector():
    vec = np.random.randn(128)
    norm = np.linalg.norm(vec)
    return (vec / norm).tolist()

def seed():
    print("[*] Seeding SnapClass Benchmark Database...")

    # 1. Faculty
    teacher_res = supabase.table("teachers").select("*").eq("username", "prof_turing").execute()
    if not teacher_res.data:
        teacher = supabase.table("teachers").insert({
            "name": "Dr. Alan Turing",
            "username": "prof_turing",
            "password": hash_pass("teacher123"),
            "department": "Computer Science & Engineering",
            "contact": "turing@gtu.ac.in",
            "bio": "Founding Faculty & Machine Intelligence Lead"
        }).execute().data[0]
        teacher_id = teacher["teacher_id"]
    else:
        teacher_id = teacher_res.data[0]["teacher_id"]

    # 2. Subjects
    sub_res = supabase.table("subjects").select("*").eq("teacher_id", teacher_id).execute()
    if not sub_res.data:
        s1 = supabase.table("subjects").insert({
            "subject_code": "CS-501",
            "name": "Advanced Neural Networks",
            "section": "A",
            "teacher_id": teacher_id
        }).execute().data[0]
        s2 = supabase.table("subjects").insert({
            "subject_code": "CS-502",
            "name": "Computer Vision & Biometrics",
            "section": "B",
            "teacher_id": teacher_id
        }).execute().data[0]
        s3 = supabase.table("subjects").insert({
            "subject_code": "IT-503",
            "name": "Distributed Systems & Cloud",
            "section": "A",
            "teacher_id": teacher_id
        }).execute().data[0]
        subject_ids = [s1["subject_id"], s2["subject_id"], s3["subject_id"]]
    else:
        subject_ids = [s["subject_id"] for s in sub_res.data]

    # 3. Students
    student_names = [
        "Alex Rivera", "Sophia Chen", "Marcus Vance", "Elena Rostova", "Devon Miles",
        "Priya Sharma", "Liam O'Connor", "Aisha Khan", "Mateo Silva", "Zoe Bennett",
        "Jordan Lee", "Chloe Dubois", "Nikhil Patel", "Fatima Al-Sayed", "Lucas Meyer"
    ]

    stu_res = supabase.table("students").select("*").execute()
    existing_students = stu_res.data or []
    
    # Update existing students with voice embeddings if missing
    for st_rec in existing_students:
        if not st_rec.get("voice_embedding"):
            supabase.table("students").update({"voice_embedding": generate_128d_vector()}).eq("student_id", st_rec["student_id"]).execute()

    if len(existing_students) < len(student_names):
        for name in student_names[len(existing_students):]:
            supabase.table("students").insert({
                "name": name,
                "face_embedding": generate_128d_vector(),
                "voice_embedding": generate_128d_vector()
            }).execute()

    all_students = supabase.table("students").select("*").execute().data
    print(f"[+] Loaded {len(all_students)} student biometric profiles.")

    # 4. Enrollments
    for sub_id in subject_ids:
        for s in all_students:
            try:
                supabase.table("subject_students").insert({
                    "student_id": s["student_id"],
                    "subject_id": sub_id
                }).execute()
            except Exception:
                pass  # Ignore duplicate enrollments

    print("[+] Roster enrollments complete.")

    # 5. Historical Attendance (30 days)
    logs_res = supabase.table("attendance_logs").select("id").limit(5).execute()
    if not logs_res.data:
        print("[*] Generating 30-day realistic roll-call history...")
        logs = []
        now = datetime.now()
        for day in range(30, 0, -1):
            ts = (now - timedelta(days=day, hours=np.random.randint(9, 16))).strftime("%Y-%m-%dT%H:%M:%S")
            for sub_id in subject_ids:
                for idx, s in enumerate(all_students):
                    if idx < 8:
                        is_present = np.random.rand() < 0.92
                    elif idx < 12:
                        is_present = np.random.rand() < 0.78
                    else:
                        is_present = np.random.rand() < 0.55

                    logs.append({
                        "student_id": s["student_id"],
                        "subject_id": sub_id,
                        "timestamp": ts,
                        "is_present": is_present
                    })

        for i in range(0, len(logs), 100):
            supabase.table("attendance_logs").insert(logs[i:i+100]).execute()
        print(f"[+] Created {len(logs)} historical attendance logs.")

    print("[+] Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
