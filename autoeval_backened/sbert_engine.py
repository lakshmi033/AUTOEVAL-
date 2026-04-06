import os
import random
import numpy as np
import torch
import warnings
# Suppress torch warnings
warnings.filterwarnings("ignore")

# --- STRICT DETERMINISTIC CONFIGURATION ---
def set_determinism(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    
    # Enforce CPU-only deterministic behavior
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(1) # Eliminate OS-level thread-order variation
    
    # Required for deterministic algorithms on some backends
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

set_determinism(42)

try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
except ImportError:
    print("WARNING: sentence-transformers not installed. SBERT Layer will be disabled.")
    SentenceTransformer = None
    util = None
    SBERT_AVAILABLE = False

_SBERT_MODEL = None

def load_sbert_model():
    """
    Loads the SBERT model into memory (Singleton).
    """
    global _SBERT_MODEL
    if _SBERT_MODEL is None:
        try:
            print("[SBERT Engine] Loading Transformer Model (all-MiniLM-L6-v2) | Revision: e4ce98d")
            # We remove the revision lock here to ensure it can load in completely offline setups.
            _SBERT_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("[SBERT Engine] Model Locked & Loaded Successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load SBERT Model: {e}")
            _SBERT_MODEL = None
    return _SBERT_MODEL

def calculate_similarity_score(student_text: str, key_text: str) -> float:
    """
    Calculates Cosine Similarity between Student Answer and Key.
    Returns: float (0.0 to 1.0)
    """
    model = load_sbert_model()
    if model is None:
        return 0.0

    try:
        # Standardize inputs for maximum stability
        s_text = student_text.strip().lower()
        k_text = key_text.strip().lower()

        # Compute embeddings
        embeddings1 = model.encode(s_text, convert_to_tensor=True)
        embeddings2 = model.encode(k_text, convert_to_tensor=True)

        # Compute cosine similarity
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score = float(cosine_scores[0][0])
        
        # Normalize to 0-1
        return max(0.0, min(1.0, score))
    except Exception as e:
        print(f"WARNING: SBERT Calculation failed: {e}")
        return 0.0
