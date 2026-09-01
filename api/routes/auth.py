from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from pydantic import BaseModel
from typing import Optional
import numpy as np
from PIL import Image
import io

from src.database.db import teacher_login, create_teacher, create_student, check_teacher_exists
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings

router = APIRouter()

class TeacherLoginModel(BaseModel):
    username: str
    password: str

class TeacherRegisterModel(BaseModel):
    name: str
    username: str
    password: str

class TeacherProfileModel(BaseModel):
    name: str
    username: str
    password: Optional[str] = None
    department: Optional[str] = None
    contact: Optional[str] = None
    bio: Optional[str] = None

@router.post("/teacher/login")
async def login_teacher(req: Request):
    """Support both JSON payload and Form data for teacher login."""
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await req.json()
        username = body.get("username", "")
        password = body.get("password", "")
    else:
        form = await req.form()
        username = form.get("username", "")
        password = form.get("password", "")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    teacher = teacher_login(username, password)
    if teacher:
        return {"success": True, "teacher": teacher}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.post("/teacher/register")
async def register_teacher(req: Request):
    """Support both JSON payload and Form data for teacher registration."""
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await req.json()
        name = body.get("name", "")
        username = body.get("username", "")
        password = body.get("password", "")
    else:
        form = await req.form()
        name = form.get("name", "")
        username = form.get("username", "")
        password = form.get("password", "")

    if not name or not username or not password:
        raise HTTPException(status_code=400, detail="Name, username, and password are required.")

    if check_teacher_exists(username):
        raise HTTPException(status_code=400, detail="Username is already taken")
    try:
        teacher = create_teacher(username, password, name)
        return {"success": True, "message": "Registered successfully. You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/teacher/profile/{teacher_id}")
async def update_teacher_endpoint(teacher_id: int, req: Request):
    """Support both JSON payload and Form data for teacher profile updates."""
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await req.json()
        name = body.get("name")
        username = body.get("username")
        password = body.get("password")
        department = body.get("department")
        contact = body.get("contact")
        bio = body.get("bio")
    else:
        form = await req.form()
        name = form.get("name")
        username = form.get("username")
        password = form.get("password")
        department = form.get("department")
        contact = form.get("contact")
        bio = form.get("bio")

    if not name or not username:
        raise HTTPException(status_code=400, detail="Name and username are required.")

    try:
        from src.database.db import update_teacher_profile
        updated = update_teacher_profile(teacher_id, name, username, password, department, contact, bio)
        if not updated:
            raise HTTPException(status_code=404, detail="Teacher not found or update failed")
        return {"success": True, "teacher": updated[0], "message": "Profile updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/student/face-login")
async def student_face_login(image: UploadFile = File(...)):
    content = await image.read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img_np = np.array(img)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    detected, all_students, num_faces = predict_attendance(img_np, allow_single_student=True)
    
    if len(detected) == 1:
        student_id = list(detected.keys())[0]
        return {"success": True, "student_id": student_id}
    elif len(detected) > 1:
        raise HTTPException(status_code=400, detail="Multiple faces detected. Please show only one face.")
    else:
        raise HTTPException(status_code=404, detail="Face not recognized or not found.")

@router.post("/student/register")
async def student_register(name: str = Form(...), image: UploadFile = File(...)):
    content = await image.read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img_np = np.array(img)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    try:
        encodings = get_face_embeddings(img_np)
        if len(encodings) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the image.")
        if len(encodings) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Show only one.")
        
        face_embedding = encodings[0].tolist()
        student = create_student(name, face_embedding=face_embedding, voice_embedding=None)
        
        # After a new student is added, clear the cache to retrain
        from src.pipelines.face_pipeline import train_classifier
        train_classifier()
        
        return {"success": True, "student": student}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/student/voice-enroll")
async def student_voice_enroll(
    student_id: int = Form(...),
    audio: UploadFile = File(...)
):
    """Enroll student voice biometric profile (128-d acoustic embedding)."""
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio recording.")
    
    try:
        from src.pipelines.voice_pipeline import get_voice_embedding
        emb = get_voice_embedding(content)
        if not emb:
            raise HTTPException(status_code=400, detail="Could not extract voice embedding. Please speak clearly for at least 1-2 seconds.")
        
        from src.database.config import supabase
        supabase.table("students").update({"voice_embedding": emb}).eq("student_id", student_id).execute()
        return {"success": True, "student_id": student_id, "message": "Voice biometric vector enrolled successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
