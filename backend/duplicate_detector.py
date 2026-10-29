"""Duplicate complaint detection module for Smart Complaint Router.

Uses TF-IDF vectorization and cosine similarity to detect textual resemblance
between an incoming civic complaint and a collection of existing complaints.

Note:
    This is an algorithmic prototype. High text similarity indicates strong
    textual resemblance, not definitive legal or empirical proof that two
    complaints describe the exact same real-world incident.
"""

from typing import Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_DUPLICATE_THRESHOLD = 0.65


def find_duplicate_complaint(
    new_complaint: str,
    existing_complaints: list[str],
    threshold: float = DEFAULT_DUPLICATE_THRESHOLD,
) -> dict[str, Any]:
    """Identify the most similar existing complaint if similarity meets or exceeds threshold.

    Args:
        new_complaint: The incoming complaint description to evaluate.
        existing_complaints: A list of existing complaint descriptions to compare against.
        threshold: Minimum cosine similarity score (between 0.0 and 1.0) to qualify as a duplicate.

    Returns:
        dict containing:
            - is_duplicate (bool): True if highest similarity >= threshold, else False.
            - most_similar_complaint (str or None): The matching complaint if duplicate, else None.
            - similarity_score (float): Cosine similarity score bounded in [0.0, 1.0].
            - threshold (float): The threshold evaluated against.
    """
    # 1. Safely handle empty, whitespace-only, or invalid new complaint
    if not isinstance(new_complaint, str) or not new_complaint.strip():
        return {
            "is_duplicate": False,
            "most_similar_complaint": None,
            "similarity_score": 0.0,
            "threshold": threshold,
        }

    # 2. Safely filter and handle empty existing complaints list
    if not existing_complaints or not isinstance(existing_complaints, list):
        return {
            "is_duplicate": False,
            "most_similar_complaint": None,
            "similarity_score": 0.0,
            "threshold": threshold,
        }

    valid_existing = [
        c.strip() for c in existing_complaints if isinstance(c, str) and c.strip()
    ]
    if not valid_existing:
        return {
            "is_duplicate": False,
            "most_similar_complaint": None,
            "similarity_score": 0.0,
            "threshold": threshold,
        }

    # 3. Fit TF-IDF on corpus of new complaint + valid existing complaints
    corpus = [new_complaint.strip()] + valid_existing
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 1), sublinear_tf=True)

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Handles cases where all tokens in the corpus are stop-words or non-word characters
        return {
            "is_duplicate": False,
            "most_similar_complaint": None,
            "similarity_score": 0.0,
            "threshold": threshold,
        }

    # 4. Compute cosine similarity between the new complaint and all existing complaints
    new_vector = tfidf_matrix[0:1]
    existing_vectors = tfidf_matrix[1:]

    similarity_scores = cosine_similarity(new_vector, existing_vectors)[0]

    # 5. Extract best match and clamp score to valid [0.0, 1.0] range
    best_index = int(similarity_scores.argmax())
    best_raw_score = float(similarity_scores[best_index])
    clamped_score = max(0.0, min(1.0, best_raw_score))
    rounded_score = round(clamped_score, 4)

    is_duplicate = bool(rounded_score >= threshold)
    matched_complaint = valid_existing[best_index] if is_duplicate else None

    return {
        "is_duplicate": is_duplicate,
        "most_similar_complaint": matched_complaint,
        "similarity_score": rounded_score,
        "threshold": threshold,
    }
