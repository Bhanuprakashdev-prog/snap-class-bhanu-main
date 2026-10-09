from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
import csv
from datetime import datetime

from src.database.config import supabase

router = APIRouter()

@router.get("/attendance/{subject_id}")
@router.get("/export/{subject_id}")
def export_attendance_csv(subject_id: int):
    """Teacher view: Export 1-click CSV of attendance records."""
    try:
        # Fetch all attendance logs for subject
        res = supabase.table("attendance_logs").select("*, students(name)").eq("subject_id", subject_id).execute()
        logs = res.data or []
        
        # Group by student
        student_data = {}
        for log in logs:
            sid = log["student_id"]
            if sid not in student_data:
                name = log.get("students", {}).get("name", f"Student {sid}")
                student_data[sid] = {"name": name, "total": 0, "attended": 0}
            
            student_data[sid]["total"] += 1
            if log["is_present"]:
                student_data[sid]["attended"] += 1
                
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student ID", "Student Name", "Total Classes", "Attended Classes", "Attendance %", "Status"])
        
        for sid, data in student_data.items():
            pct = (data["attended"] / data["total"] * 100) if data["total"] > 0 else 0
            status = "DEBARRED" if pct < 75.0 else ("WARNING" if pct < 80.0 else "SAFE")
            
            writer.writerow([
                sid,
                data["name"],
                data["total"],
                data["attended"],
                f"{pct:.1f}%",
                status
            ])
            
        output.seek(0)
        
        filename = f"Attendance_Subject_{subject_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
