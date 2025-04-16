FROM python:3.11-slim

# Install system dependencies needed for dlib and face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libboost-all-dev \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Make sure Flask runs on 0.0.0.0 so it's accessible by Render
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["flask", "run", "--port=5000"]
