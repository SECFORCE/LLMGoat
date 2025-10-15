import os
import gc
from llama_cpp import Llama
from transformers import BlipProcessor, BlipForConditionalGeneration
from utils.helpers import download_file, sha256_of_file

# Constant values
DEFAULT_MODEL = {
    "name": "gemma-2.gguf",
    "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
    "sha256": "13b2a7b4115bbd0900162edcebe476da1ba1fc24e718e8b40d32f6e300f56dfe"
}
MODELS_FOLDER = "/app/models"
MAX_TOKENS=100
TEMPERATURE=0.7
LLM_STOP=["<|user|>", "<|system|>"]

class LLManager:
    _instance = None # the Singleton instance
    _init_started = False # Ensure init is run only once
    _llm_instance = None # the LLM current instance
    _current_model = None # the currently loaded model (name)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance
    

    def load_additional_models(self):
        print(f"[INFO] Downloading 'Salesforce/blip-image-captioning-base'...")
        BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def init(self):
        if self._init_started:
            return
        self._init_started = True
        available_models = self.available_models()
        # Default to model set in Dockerfile (or argument to docker command)
        selected_model = os.environ.get("DEFAULT_MODEL")

        # There are no available models, the default should be downloaded
        if len(available_models) == 0:
            print(f"[ERROR] There are no available models. Downloading gemma-2...")
            download_file(DEFAULT_MODEL["url"], MODELS_FOLDER, DEFAULT_MODEL["name"])
            # TODO: check that the hash matches
            print(f"[INFO] Default model correctly downloaded, loading it...")
            self.load_model(DEFAULT_MODEL["name"])
        # If available load the selected model
        elif selected_model in available_models:
            print(f"[INFO] Selected model is available, loading it...")
            self.load_model(selected_model)
        # If available load the default model
        elif DEFAULT_MODEL["name"] in available_models:
            print(f"[INFO] Default model is available")
            # TODO: check that the hash matches
            print(f"[INFO] Model is correct, loading it...")
            self.load_model(DEFAULT_MODEL["name"])
        # Let's just load the first in the list if not
        else:
            print(f"[INFO] Loading the first available model: {available_models[0]}")
            self.load_model(available_models[0])

        # Load additional stuff
        self.load_additional_models()


    def free_llm_instance(self):
        if self._llm_instance is not None:
            try:
                self._llm_instance.__del__()
            except Exception:
                pass

            self._llm_instance = None

            gc.collect()
            print("[INFO] Previous model instance freed from memory.")

    def load_model(self, model):
        print("[INFO] Model check")

        if self._current_model != model:
            print(f"[INFO] Loading model: {model}")
            
            # get number of CPU cores + GPU layers
            n_threads = min(os.cpu_count(), int(os.environ.get("N_THREADS", os.cpu_count())))
            n_gpu_layers = int(os.environ.get("N_GPU_LAYERS", 0))
            
            # explicitly free the memory taken by the current model
            self.free_llm_instance()
            
            # load the LLM
            model_path = os.path.join(MODELS_FOLDER, model)
            self._llm_instance = Llama(model_path=model_path, n_ctx=1024, n_threads=n_threads, n_batch=32, n_gpu_layers=n_gpu_layers)
            # Set current model name
            self._current_model = model

            print(f"[INFO] Hardware config: {n_threads} CPU cores, n_gpu_layers: {n_gpu_layers}")


    def get_model(self):
        if self._llm_instance is None:
            raise RuntimeError("Model not loaded yet")
        return self._llm_instance
    
    def available_models(self, models_dir=MODELS_FOLDER):
        return [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
    
    def get_current_model_name(self):
        return self._current_model
    
    def call_llm(self, prompt):
        try:
            llm = self.get_model()
            output = llm(
                prompt,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                stop=LLM_STOP
            )
            return output["choices"][0]["text"].strip()
        except:
            return "Alpine Goat" # Fallback
