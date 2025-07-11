#!/bin/bash
set -e

MODEL_DIR="models"
mkdir -p "$MODEL_DIR"

declare -A MODELS
MODELS=(
  #["tinyllama.gguf"]="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
  #["mistral.gguf"]="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
  ["zephyr.gguf"]="https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_M.gguf"
  ["phi-2.gguf"]="https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
  ["gemma-2.gguf"]="https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf"
  
)

for FILE in "${!MODELS[@]}"; do
  if [ ! -f "$MODEL_DIR/$FILE" ]; then
    echo "Downloading $FILE..."
    curl -L -o "$MODEL_DIR/$FILE" "${MODELS[$FILE]}"
  else
    echo "$FILE already exists. Skipping."
  fi
done

echo "Building Docker image..."
docker build -t llmgoat .
