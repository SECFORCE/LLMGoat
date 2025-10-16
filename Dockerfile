FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
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