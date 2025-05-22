FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for llama-cpp
# ENV LLAMA_CUBLAS=0

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code after installing dependencies to prevent unnecessary reinstallation
COPY . .

# Expose the port for Flask app
EXPOSE 5000

# Run the app
#CMD ["python", "app.py"]
CMD ["gunicorn", "--workers=1", "--threads=4", "--preload", "--bind=0.0.0.0:5000", "app:app"]
