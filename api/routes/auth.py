from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import numpy as np
from PIL import Image
import io

from src.database.db import teacher_login, create_teacher, create_student, check_teacher_exists
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings

router = APIRouter()

@router.post("/teacher/login")
def login_teacher(username: str = Form(...), password: str = Form(...)):
    teacher = teacher_login(username, password)
    if teacher:
        return {"success": True, "teacher": teacher}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.post("/teacher/register")
def register_teacher(username: str = Form(...), password: str = Form(...), name: str = Form(...)):
    if check_teacher_exists(username):
        raise HTTPException(status_code=400, detail="Username is already taken")
    try:
        teacher = create_teacher(username, password, name)
        return {"success": True, "message": "Registered successfully. You can now log in."}
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
