from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.routes import auth, attendance, subjects, insights, admin, exports

app = FastAPI(
    title="SnapClass API",
    description="FastAPI Backend for SnapClass Full-Fledged AI Attendance Platform",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development. In prod, restrict to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])

# Mount static files for the frontend if the directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
