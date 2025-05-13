FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for llama-cpp
ENV LLAMA_CUBLAS=0

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code after installing dependencies to prevent unnecessary reinstallation
COPY . .

# Add model download fallback
RUN mkdir -p /app/models && \
    if [ ! -f /app/models/tinyllama.gguf ]; then \
        echo "Downloading model..."; \
        curl -L -o /app/models/tinyllama.gguf \
        https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf; \
    else \
        echo "Model already present. Skipping download."; \
    fi

# Expose the port for Flask app
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
