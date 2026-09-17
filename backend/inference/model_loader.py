import os
import sys
import threading

# Add project root to path so we can import model.src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from model.src.inference.predictor import Predictor
from backend.core.config import settings

_predictor_instance = None
_lock = threading.Lock()
_load_count = 0  # To track singleton loads in testing

def get_predictor() -> Predictor:
    """
    Singleton loader for the Predictor. Ensures the model is loaded exactly once
    at startup or first request, preventing per-request memory/loading overhead.
    """
    global _predictor_instance, _load_count
    if _predictor_instance is None:
        with _lock:
            # Double-checked locking
            if _predictor_instance is None:
                # Derive path dynamically from config version
                version_str = settings.MODEL_VERSION.strip()
                if version_str.startswith("model_"):
                    dir_name = version_str
                elif version_str.startswith("v"):
                    dir_name = f"model_{version_str}"
                else:
                    dir_name = f"model_v{version_str}"
                
                model_dir = os.path.join(project_root, "model", "exported", dir_name)
                
                if not os.path.exists(model_dir):
                    raise RuntimeError(f"Exported model directory not found: {model_dir}")
                
                _predictor_instance = Predictor(export_dir=model_dir)
                _load_count += 1
                
    return _predictor_instance
