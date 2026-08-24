from fastapi import APIRouter, HTTPException
from src.database.config import supabase
from src.pipelines.risk_predictor import compute_risk

router = APIRouter()

@router.get("/overview")
def get_admin_overview():
    """Admin view: Campus-wide KPIs."""
    try:
        students_res = supabase.table("students").select("student_id", count="exact").execute()
        teachers_res = supabase.table("teachers").select("teacher_id", count="exact").execute()
        subjects_res = supabase.table("subjects").select("subject_id", count="exact").execute()
        
        return {
            "success": True,
            "total_students": students_res.count if students_res else 0,
            "total_teachers": teachers_res.count if teachers_res else 0,
            "total_subjects": subjects_res.count if subjects_res else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defaulters")
def get_defaulters():
    """Admin view: List of all students with <75% attendance across subjects."""
    try:
        # Fetch all attendance logs
        res = supabase.table("attendance_logs").select("*, students(name), subjects(name)").execute()
        logs = res.data or []
        
        # Group by student and subject
        student_course_map = {}
        for log in logs:
            key = f"{log['student_id']}_{log['subject_id']}"
            if key not in student_course_map:
                student_course_map[key] = {
                    "student_id": log["student_id"],
                    "student_name": log.get("students", {}).get("name", "Unknown"),
                    "subject_name": log.get("subjects", {}).get("name", "Unknown"),
                    "logs": []
                }
            student_course_map[key]["logs"].append(log)
            
        defaulters = []
        for key, data in student_course_map.items():
            total = len(data["logs"])
            attended = sum(1 for l in data["logs"] if l["is_present"])
            pct = (attended / total * 100) if total > 0 else 0
            
            if pct < 75.0:
                defaulters.append({
                    "student_id": data["student_id"],
                    "student_name": data["student_name"],
                    "subject": data["subject_name"],
                    "attendance_pct": round(pct, 1),
                    "total_classes": total,
                    "attended_classes": attended
                })
                
        # Sort by lowest attendance
        defaulters = sorted(defaulters, key=lambda x: x["attendance_pct"])
        
        return {"success": True, "defaulters": defaulters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
