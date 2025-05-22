from llama_cpp import Llama
import os

_llm_instance = None
_current_model_path = None

def load_model(model_path):
    global _llm_instance, _current_model_path
    if _current_model_path != model_path:
        print(f"[INFO] Loading model: {model_path}")
        _llm_instance = Llama(model_path=model_path, n_ctx=1024, n_threads=4, n_batch=32, n_gpu_layers=0)
        _current_model_path = model_path

def get_model():
    if _llm_instance is None:
        raise RuntimeError("Model not loaded yet")
    return _llm_instance

def available_models(models_dir="/app/models"):
    return [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
