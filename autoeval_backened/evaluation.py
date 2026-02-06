from sentence_transformers import SentenceTransformer, util
import re
from typing import List, Tuple

# Load model once at module import
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("SBERT model loaded successfully")
except Exception as e:
    print(f"Error loading SBERT model: {e}")
    model = None


def clean_text(text: str) -> str:
    """
    Clean and normalize text for evaluation while preserving semantic meaning.
    Also removes garbage patterns like "0 0 0 0" that might have slipped through OCR.
    """
    if not text:
        return ""
    
    # Remove garbage patterns like "0 0 0 0" that might have slipped through
    # Check if text is mostly repeated characters (garbage)
    text_no_spaces = text.replace(" ", "").replace("\n", "").replace("\t", "")
    if len(text_no_spaces) > 5:
        char_counts = {}
        for char in text_no_spaces:
            char_counts[char] = char_counts.get(char, 0) + 1
        if char_counts:
            most_common = max(char_counts, key=char_counts.get)
            if char_counts[most_common] / len(text_no_spaces) > 0.7:
                # This is garbage, return empty to trigger error
                return ""
    
    # Normalize whitespace (multiple spaces/tabs/newlines to single space)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    
    return text


def remove_non_answer_lines(text: str) -> str:
    """
    Remove lines that are metadata/formatting and not actual answer content.
    This improves evaluation by focusing only on the answer content itself.
    
    Removes lines starting with:
    - "Question:"
    - "Student Answer:"
    - "Answer Key:"
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        # Skip lines that are clearly metadata/formatting
        if line_stripped.lower().startswith('question:'):
            continue
        if line_stripped.lower().startswith('student answer:'):
            continue
        if line_stripped.lower().startswith('answer key:'):
            continue
        # Keep all other lines (actual answer content)
        if line_stripped:  # Only add non-empty lines
            filtered_lines.append(line_stripped)
    
    return ' '.join(filtered_lines)


def segment_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for sentence-level semantic matching.
    This allows us to match meaning even when sentence order differs,
    making evaluation more robust to formatting variations.
    
    Uses simple sentence splitting based on punctuation.
    Ignores empty or very short sentences (< 10 characters).
    """
    if not text:
        return []
    
    # Split on sentence-ending punctuation
    # This regex splits on . ! ? followed by space or end of string
    sentences = re.split(r'[.!?]+\s+|[.!?]+$', text)
    
    # Clean and filter sentences
    cleaned_sentences = []
    for sent in sentences:
        sent = sent.strip()
        # Ignore very short sentences (likely OCR noise or fragments)
        if len(sent) >= 10:
            cleaned_sentences.append(sent)
    
    return cleaned_sentences


def sentence_level_semantic_matching(student_sentences: List[str], key_sentences: List[str]) -> float:
    """
    Perform sentence-level semantic matching using SBERT.
    
    WHY THIS IMPROVES FAIRNESS:
    - Full-text comparison penalizes answers that cover the same content but in different order
    - Sentence-level matching finds the best semantic match for each student sentence
    - This rewards students who understand the concepts even if they express them differently
    - Averaging best matches gives a more accurate overall similarity score
    
    Algorithm:
    1. For each student sentence, find the best matching key sentence (highest cosine similarity)
    2. Average all best matches to get base similarity score
    3. This score reflects how well the student covered the key concepts
    """
    if not student_sentences or not key_sentences:
        return 0.0
    
    # If either side has no sentences, return 0
    if len(student_sentences) == 0 or len(key_sentences) == 0:
        return 0.0
    
    # Encode all sentences at once for efficiency
    student_embeddings = model.encode(student_sentences, convert_to_tensor=True, show_progress_bar=False)
    key_embeddings = model.encode(key_sentences, convert_to_tensor=True, show_progress_bar=False)
    
    # Compute similarity matrix: student_sentences x key_sentences
    similarity_matrix = util.cos_sim(student_embeddings, key_embeddings)
    
    # For each student sentence, find the best matching key sentence
    best_matches = []
    for i in range(len(student_sentences)):
        # Get similarities for this student sentence against all key sentences
        similarities = similarity_matrix[i]
        # Find the maximum similarity (best match)
        best_similarity = similarities.max().item()
        best_matches.append(best_similarity)
    
    # Average all best matches to get overall similarity
    if len(best_matches) > 0:
        base_similarity = sum(best_matches) / len(best_matches)
    else:
        base_similarity = 0.0
    
    # Ensure score is in [0, 1] range
    base_similarity = max(0.0, min(1.0, base_similarity))
    
    return base_similarity


def calculate_concept_coverage_bonus(student_text: str, key_text: str) -> float:
    """
    Calculate bonus score based on matching core concepts/keywords.
    
    WHY THIS IMPROVES ACADEMIC EVALUATION:
    - Academic answers should cover specific concepts/keywords
    - Even if phrasing differs, presence of key concepts indicates understanding
    - This bonus rewards students who mention important terms/concepts
    - Maximum bonus of +0.05 prevents over-rewarding while still being meaningful
    
    Algorithm:
    1. Define core concepts (domain-specific keywords)
    2. Check if both student and key text contain each concept
    3. Add +0.01 per matched concept
    4. Cap bonus at +0.05 (5 concepts max)
    """
    # Core concepts that indicate understanding of the topic
    # These are example concepts - in practice, these could be extracted from the answer key
    core_concepts = [
        "artificial intelligence",
        "learn from data",
        "prediction",
        "classification",
        "recommendation"
    ]
    
    student_lower = student_text.lower()
    key_lower = key_text.lower()
    
    matched_concepts = 0
    for concept in core_concepts:
        # Check if concept appears in both texts
        if concept in student_lower and concept in key_lower:
            matched_concepts += 1
    
    # Add +0.01 per matched concept, maximum +0.05
    bonus = min(matched_concepts * 0.01, 0.05)
    
    return bonus


def evaluate_answer(student_text: str, key_text: str):
    """
    Evaluate student answer against answer key using sentence-level semantic matching.
    
    This improved evaluation method:
    1. Removes non-answer lines (Question:, Student Answer:, etc.)
    2. Segments both texts into sentences
    3. Performs sentence-level semantic matching using SBERT
    4. Adds concept coverage bonus for matching keywords
    5. Returns a fair, academically appropriate score
    
    Args:
        student_text: The student's answer text
        key_text: The answer key text
        
    Returns:
        dict with:
            - score: Final score (0.0-1.0)
            - feedback: Textual feedback
            - raw_similarity: Base similarity from sentence matching
            - keyword_bonus: Bonus from concept coverage
    """
    if not model:
        raise Exception("SBERT model not loaded. Please restart the server.")
    
    # Step 1: Clean input texts (remove garbage, normalize whitespace)
    student_cleaned = clean_text(student_text)
    key_cleaned = clean_text(key_text)
    
    print(f"DEBUG: Student text length: {len(student_cleaned)}, Key text length: {len(key_cleaned)}")
    print(f"DEBUG: Student preview: {student_cleaned[:150]}...")
    print(f"DEBUG: Key preview: {key_cleaned[:150]}...")
    
    if not student_cleaned:
        raise ValueError("Student answer text is empty after cleaning.")
    if not key_cleaned:
        raise ValueError("Answer key text is empty after cleaning.")
    
    try:
        # Step 2: Remove non-answer lines (Question:, Student Answer:, Answer Key:)
        student_content = remove_non_answer_lines(student_cleaned)
        key_content = remove_non_answer_lines(key_cleaned)
        
        print(f"DEBUG: After removing non-answer lines - Student: {len(student_content)} chars, Key: {len(key_content)} chars")
        
        if not student_content:
            raise ValueError("Student answer has no content after removing metadata lines.")
        if not key_content:
            raise ValueError("Answer key has no content after removing metadata lines.")
        
        # Step 3: Segment into sentences
        student_sentences = segment_into_sentences(student_content)
        key_sentences = segment_into_sentences(key_content)
        
        print(f"DEBUG: Student sentences: {len(student_sentences)}, Key sentences: {len(key_sentences)}")
        
        if len(student_sentences) == 0:
            raise ValueError("Student answer has no valid sentences after segmentation.")
        if len(key_sentences) == 0:
            raise ValueError("Answer key has no valid sentences after segmentation.")
        
        # Step 4: Perform sentence-level semantic matching
        raw_similarity = sentence_level_semantic_matching(student_sentences, key_sentences)
        print(f"DEBUG: Raw similarity (sentence-level): {raw_similarity:.4f}")
        
        # Step 5: Calculate concept coverage bonus
        keyword_bonus = calculate_concept_coverage_bonus(student_content, key_content)
        print(f"DEBUG: Concept coverage bonus: {keyword_bonus:.4f}")
        
        # Step 6: Combine scores with bonus
        final_score = raw_similarity + keyword_bonus
        
        # Step 7: Score safety - clip between 0 and 1
        final_score = max(0.0, min(1.0, final_score))
        
        print(f"DEBUG: Final score: {final_score:.4f} (raw: {raw_similarity:.4f}, bonus: {keyword_bonus:.4f})")
        
        # Step 8: Generate feedback based on final score
        if final_score >= 0.85:
            feedback = "Excellent answer"
        elif final_score >= 0.65:
            feedback = "Good answer with minor gaps"
        elif final_score >= 0.45:
            feedback = "Fair answer, needs improvement"
        else:
            feedback = "Poor answer"
        
        print(f"DEBUG: Feedback: {feedback}")
        
        return {
            "score": round(final_score, 3),
            "feedback": feedback,
            "raw_similarity": round(raw_similarity, 4),
            "keyword_bonus": round(keyword_bonus, 4)
        }
    
    except Exception as e:
        print(f"ERROR in evaluate_answer: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error during evaluation: {str(e)}")
