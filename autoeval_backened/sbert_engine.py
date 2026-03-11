import warnings
# Suppress torch warnings if any
warnings.filterwarnings("ignore")

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
            print("[SBERT Engine] Loading Transformer Model (all-MiniLM-L6-v2)...")
            _SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            print("[SBERT Engine] Model Loaded Successfully.")
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
