from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import time
import hashlib
import os
import numpy as np
from PIL import Image
import io
from datetime import datetime

from src.database.db import create_attendance, get_attendance_for_teacher, get_student_attendance
from src.database.config import supabase
from src.pipelines.face_pipeline import predict_attendance

router = APIRouter()

def get_secret() -> str:
    return os.environ.get("SUPABASE_KEY", "fallback-secret-12345")

@router.get("/qr-token")
def get_qr_token(subject_id: str):
    """Generate a time-bucketed QR token rotating every 5 seconds."""
    bucket = int(time.time()) // 5
    raw = f"{subject_id}:{bucket}:{get_secret()}"
    token = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return {"token": token, "bucket": bucket}

def verify_qr_token(subject_id: str, token: str) -> bool:
    """Verify the token is valid for the current bucket, or previous/next to account for slight latency."""
    current_bucket = int(time.time()) // 5
    for b in [current_bucket, current_bucket - 1, current_bucket + 1]:
        raw = f"{subject_id}:{b}:{get_secret()}"
        expected = hashlib.sha256(raw.encode()).hexdigest()[:12]
        if expected == token:
            return True
    return False

class AttendanceLog(BaseModel):
    student_id: int
    subject_id: int
    is_present: bool

class MarkBatchRequest(BaseModel):
    logs: List[AttendanceLog]
    timestamp: Optional[str] = None

@router.post("/mark-batch")
def mark_attendance_batch(request: MarkBatchRequest):
    timestamp = request.timestamp or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    db_logs = [
        {
            "student_id": log.student_id,
            "subject_id": log.subject_id,
            "timestamp": timestamp,
            "is_present": log.is_present,
        }
        for log in request.logs
    ]
    try:
        data = create_attendance(db_logs)
        return {"success": True, "count": len(db_logs), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/photo-scan")
async def photo_scan(
    subject_id: int = Form(...),
    image: UploadFile = File(...)
):
    """Process a classroom photo and mark attendance for detected faces."""
    content = await image.read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img_np = np.array(img)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Get enrolled students for this subject
    res = supabase.table("subject_students").select("student_id").eq("subject_id", subject_id).execute()
    candidate_ids = [row["student_id"] for row in res.data] if res.data else []
    
    detected, all_candidate_students, num_faces = predict_attendance(
        img_np, allow_single_student=True, candidate_student_ids=candidate_ids
    )
    
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logs = [
        {
            "student_id": sid,
            "subject_id": subject_id,
            "timestamp": timestamp,
            "is_present": sid in detected,
        }
        for sid in all_candidate_students
    ]
    
    if logs:
        create_attendance(logs)
    
    return {
        "success": True, 
        "faces_detected": num_faces, 
        "students_matched": len(detected),
        "present_ids": list(detected.keys()),
        "absent_ids": [s for s in all_candidate_students if s not in detected]
    }

@router.post("/qr-checkin")
def qr_checkin(
    subject_id: int = Form(...),
    token: str = Form(...),
    student_id: int = Form(...)
):
    """Direct live QR scan check-in for enrolled student."""
    if not verify_qr_token(str(subject_id), token):
        raise HTTPException(status_code=400, detail="Invalid or expired QR token. Please scan the current rotating code.")
    
    # Check if student is enrolled
    enrollment = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject_id).execute()
    if not enrollment.data:
        # Auto-enroll on verified QR scan
        supabase.table("subject_students").insert({"student_id": student_id, "subject_id": subject_id}).execute()
        
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    create_attendance([{
        "student_id": student_id,
        "subject_id": subject_id,
        "timestamp": timestamp,
        "is_present": True
    }])
    
    return {"success": True, "message": "Attendance successfully verified and recorded!", "student_id": student_id}

@router.post("/qr-submit")
async def qr_submit(
    subject_id: int = Form(...),
    token: str = Form(...),
    image: UploadFile = File(...)
):
    """Student submits FaceID + QR token from their own device."""
    if not verify_qr_token(str(subject_id), token):
        raise HTTPException(status_code=400, detail="Invalid or expired QR token")
    
    content = await image.read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img_np = np.array(img)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    detected, _, num_faces = predict_attendance(img_np, allow_single_student=True)
    
    if len(detected) != 1:
        raise HTTPException(status_code=400, detail="Must show exactly one face.")
    
    student_id = list(detected.keys())[0]
    
    # Log attendance
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    create_attendance([{
        "student_id": student_id,
        "subject_id": subject_id,
        "timestamp": timestamp,
        "is_present": True
    }])
    
    return {"success": True, "message": "Attendance marked securely.", "student_id": student_id}

@router.post("/voice-scan")
@router.post("/recognize-voice")
async def voice_scan(
    subject_id: int = Form(...),
    audio: UploadFile = File(...)
):
    """Classroom voice roll-call speaker identification using 128-d Librosa Acoustic Embeddings."""
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="No audio data received.")
    
    try:
        from src.pipelines.voice_pipeline import process_bulk_audio
        
        # 1. Fetch enrolled students for this course
        enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", subject_id).execute()
        enrolled_students = enrolled_res.data or []
        
        if not enrolled_students:
            raise HTTPException(status_code=404, detail="No students enrolled in this course.")
            
        candidates_dict = {
            s["students"]["student_id"]: s["students"]["voice_embedding"]
            for s in enrolled_students
            if s.get("students") and s["students"].get("voice_embedding")
        }
        
        if not candidates_dict:
            raise HTTPException(status_code=400, detail="Enrolled students do not have registered voice biometric profiles yet.")
            
        # 2. Process audio & identify speakers
        detected_scores = process_bulk_audio(content, candidates_dict)
        
        # 3. Log attendance
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logs_to_create = []
        detected_info = []
        absent_ids = []
        
        for node in enrolled_students:
            student = node["students"]
            sid = student["student_id"]
            score = detected_scores.get(sid, 0.0)
            is_present = bool(score > 0)
            
            if is_present:
                detected_info.append({
                    "student_id": sid,
                    "name": student.get("name", f"Student #{sid}"),
                    "confidence": round(score * 100, 1)
                })
            else:
                absent_ids.append(sid)
                
            logs_to_create.append({
                "student_id": sid,
                "subject_id": subject_id,
                "timestamp": timestamp,
                "is_present": is_present
            })
            
        create_attendance(logs_to_create)
        
        return {
            "success": True,
            "subject_id": subject_id,
            "total_enrolled": len(enrolled_students),
            "detected_students": detected_info,
            "absent_ids": absent_ids,
            "timestamp": timestamp,
            "message": f"Voice roll-call verified: {len(detected_info)} present, {len(absent_ids)} absent."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")
