from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import math

from src.database.config import supabase
from src.database.db import get_student_attendance
from src.pipelines.risk_predictor import compute_risk

router = APIRouter()

@router.get("/risk/{subject_id}")
def get_subject_risk_radar(subject_id: int):
    """Teacher view: Get ML dropout risk for all students in a specific subject."""
    try:
        # Get all attendance logs for this subject
        res = supabase.table("attendance_logs").select("*, students(name)").eq("subject_id", subject_id).execute()
        logs = res.data or []
        
        # Group by student
        student_data = {}
        for log in logs:
            sid = log["student_id"]
            if sid not in student_data:
                name = log.get("students", {}).get("name", f"Student {sid}")
                student_data[sid] = {"name": name, "logs": []}
            student_data[sid]["logs"].append(log)
        
        results = []
        for sid, data in student_data.items():
            # Sort logs by timestamp to maintain sequence for SMA slope
            sorted_logs = sorted(data["logs"], key=lambda x: x["timestamp"])
            risk_profile = compute_risk(sorted_logs)
            risk_profile["student_id"] = sid
            risk_profile["name"] = data["name"]
            results.append(risk_profile)
            
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student-radar/{student_id}")
def get_student_radar(student_id: int, subject_id: int = None):
    """Student view: Get personalized attendance insights, what-if, and streaks."""
    try:
        query = supabase.table("attendance_logs").select("*").eq("student_id", student_id)
        if subject_id:
            query = query.eq("subject_id", subject_id)
        
        res = query.execute()
        logs = res.data or []
        sorted_logs = sorted(logs, key=lambda x: x["timestamp"])
        
        # Calculate Risk Profile
        risk_profile = compute_risk(sorted_logs) if sorted_logs else None
        
        # Calculate Streak
        streak = 0
        for log in reversed(sorted_logs):
            if log["is_present"]:
                streak += 1
            else:
                break
                
        # Day of week habits
        days = {"Monday": [0,0], "Tuesday": [0,0], "Wednesday": [0,0], "Thursday": [0,0], "Friday": [0,0], "Saturday": [0,0], "Sunday": [0,0]}
        for log in logs:
            try:
                dt = datetime.fromisoformat(log["timestamp"])
                day_name = dt.strftime("%A")
                days[day_name][1] += 1
                if log["is_present"]:
                    days[day_name][0] += 1
            except:
                pass
                
        habits = []
        for day, (att, tot) in days.items():
            if tot > 0:
                habits.append({"day": day, "attended": att, "total": tot, "pct": round(att/tot*100, 1)})
                
        return {
            "success": True, 
            "streak": streak,
            "risk_profile": risk_profile,
            "habits": habits,
            "total_logs": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student-recovery/{student_id}")
def get_student_recovery_roadmap(student_id: int):
    """Student view: Attendance recovery calculator & subject-by-subject target roadmap."""
    try:
        res = supabase.table("attendance_logs").select("*, subjects(name, subject_code, section)").eq("student_id", student_id).execute()
        logs = res.data or []

        total_classes = len(logs)
        attended_classes = sum(1 for l in logs if l["is_present"])
        overall_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

        # Mathematical recovery formulas (AttendSmartly methodology):
        # To reach target T_pct (e.g. 75% = 0.75): (A + N) / (Tot + N) >= 0.75 => N >= (0.75*Tot - A) / 0.25
        needed_for_75 = 0
        needed_for_85 = 0
        safe_skips = 0

        if total_classes > 0:
            if overall_pct < 75.0:
                needed_for_75 = max(0, math.ceil((0.75 * total_classes - attended_classes) / 0.25))
            else:
                safe_skips = max(0, math.floor((attended_classes - 0.75 * total_classes) / 0.75))

            if overall_pct < 85.0:
                needed_for_85 = max(0, math.ceil((0.85 * total_classes - attended_classes) / 0.15))

        # Group by subject
        subject_breakdown = {}
        for l in logs:
            sub_id = l["subject_id"]
            if sub_id not in subject_breakdown:
                sub_info = l.get("subjects", {})
                subject_breakdown[sub_id] = {
                    "subject_id": sub_id,
                    "subject_name": sub_info.get("name", f"Course #{sub_id}"),
                    "subject_code": sub_info.get("subject_code", "GEN"),
                    "section": sub_info.get("section", "A"),
                    "total": 0,
                    "attended": 0
                }
            subject_breakdown[sub_id]["total"] += 1
            if l["is_present"]:
                subject_breakdown[sub_id]["attended"] += 1

        subject_cards = []
        for sid, sub in subject_breakdown.items():
            s_tot = sub["total"]
            s_att = sub["attended"]
            s_pct = round((s_att / s_tot * 100), 1) if s_tot > 0 else 100.0
            
            s_needed = 0
            s_skips = 0
            if s_pct < 75.0:
                s_needed = max(0, math.ceil((0.75 * s_tot - s_att) / 0.25))
            else:
                s_skips = max(0, math.floor((s_att - 0.75 * s_tot) / 0.75))

            subject_cards.append({
                "subject_id": sid,
                "subject_name": sub["subject_name"],
                "subject_code": sub["subject_code"],
                "section": sub["section"],
                "total_classes": s_tot,
                "attended_classes": s_att,
                "attendance_pct": s_pct,
                "classes_needed": s_needed,
                "safe_skips": s_skips,
                "status": "SAFE" if s_pct >= 85.0 else ("WARNING" if s_pct >= 75.0 else "DEBARRED")
            })

        # Recent 10 verification history logs
        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:10]
        recent_history = []
        for l in sorted_logs:
            sub_info = l.get("subjects", {})
            recent_history.append({
                "log_id": l.get("log_id"),
                "subject_name": sub_info.get("name", "Class Session"),
                "subject_code": sub_info.get("subject_code", "GEN"),
                "timestamp": l.get("timestamp"),
                "is_present": l.get("is_present", True),
                "method": "FaceID Scan"
            })

        return {
            "success": True,
            "overall_pct": overall_pct,
            "total_classes": total_classes,
            "attended_classes": attended_classes,
            "needed_for_75": needed_for_75,
            "needed_for_85": needed_for_85,
            "safe_skips": safe_skips,
            "subject_cards": subject_cards,
            "recent_history": recent_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
