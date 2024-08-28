# Dockerfile

# Use the official Python image from the Docker Hub
FROM python:3.9
FROM nvidia/cuda:11.0.3-base-ubuntu20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York
# Install system dependencies for dlib and OpenCV
# Install system dependencies and Python
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libatlas-base-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    v4l-utils \
    python3 \
    python3-pip \
    tzdata && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip using Python 3's pip
RUN python3 -m pip install --upgrade pip

RUN mkdir -p /app/models
# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Expose the ports that the app runs on
EXPOSE 8000
EXPOSE 8501

# Command to run the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]