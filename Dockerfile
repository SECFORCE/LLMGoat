FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV DEFAULT_MODEL=gemma-2.gguf
ENV N_GPU_LAYERS=0
ENV N_THREADS=16

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code after installing dependencies to prevent unnecessary reinstallation
COPY . .

# Create models folder for mounting
RUN mkdir -p /app/models

# Expose the port for Flask app
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]