from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from src.database.db import (
    create_subject,
    get_teacher_subjects,
    enroll_student_to_subject,
    unenroll_student_to_subject,
    get_student_subjects
)

router = APIRouter()

class SubjectCreate(BaseModel):
    subject_code: str
    name: str
    section: str
    teacher_id: int

class EnrollRequest(BaseModel):
    student_id: int
    subject_id: int

@router.get("/teacher/{teacher_id}")
def read_teacher_subjects(teacher_id: int):
    try:
        subjects = get_teacher_subjects(teacher_id)
        return {"success": True, "data": subjects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
def create_new_subject(req: SubjectCreate):
    try:
        data = create_subject(req.subject_code, req.name, req.section, req.teacher_id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}")
def read_student_subjects(student_id: int):
    try:
        subjects = get_student_subjects(student_id)
        return {"success": True, "data": subjects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enroll")
def enroll_student(req: EnrollRequest):
    try:
        data = enroll_student_to_subject(req.student_id, req.subject_id)
        return {"success": True, "data": data}
    except Exception as e:
        # Check if already enrolled (unique constraint violation)
        if "duplicate key value" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Already enrolled in this subject.")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/unenroll")
def unenroll_student(student_id: int, subject_id: int):
    try:
        data = unenroll_student_to_subject(student_id, subject_id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
