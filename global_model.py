from llama_cpp import Llama
import os
import gc

_llm_instance = None
_current_model_path = None

def free_llm_instance():
    global _llm_instance

    if _llm_instance is not None:
        try:
            _llm_instance.__del__()
        except Exception:
            pass

        _llm_instance = None

        gc.collect()
        print("[INFO] Previous model instance freed from memory.")

def load_model(model_path):
    print("[INFO] Model check")

    global _llm_instance, _current_model_path
    if _current_model_path != model_path:
        print(f"[INFO] Loading model: {model_path}")
        
        # get number of CPU cores + GPU layers
        n_threads = min(os.cpu_count(), int(os.environ.get("N_THREADS", os.cpu_count())))
        n_gpu_layers = int(os.environ.get("N_GPU_LAYERS", 0))
        
        # explicitly free the memory taken by the current model
        free_llm_instance()
        
        # load the LLM
        _llm_instance = Llama(model_path=model_path, n_ctx=1024, n_threads=n_threads, n_batch=32, n_gpu_layers=n_gpu_layers)
        
        print(f"[INFO] Hardware config: {n_threads} CPU cores, n_gpu_layers: {n_gpu_layers}")
        
        _current_model_path = model_path

def get_model():
    if _llm_instance is None:
        raise RuntimeError("Model not loaded yet")
    return _llm_instance

def available_models(models_dir="/app/models"):
    return [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
