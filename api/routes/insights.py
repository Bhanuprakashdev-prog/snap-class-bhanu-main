from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

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
