FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV DEFAULT_MODEL=gemma-2.gguf
ENV N_GPU_LAYERS=0
ENV N_THREADS=16
ENV PYTHONUNBUFFERED=1

# Copy stuff
COPY pyproject.toml .
COPY README.md .
COPY llmgoat ./llmgoat

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Expose the port for LLMGoat
EXPOSE 5000

# Run the app
ENTRYPOINT [ "llmgoat" ]