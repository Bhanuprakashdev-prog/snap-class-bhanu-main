# SnapClass Enterprise AI Biometrics Platform Dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies required for dlib (cmake, build-essential) and audio/image processing (ffmpeg, libgl1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run Uvicorn production server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
