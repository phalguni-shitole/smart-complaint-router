import csv
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

EXPECTED_CATEGORIES = {"Roads", "Water Supply", "Electricity", "Garbage", "Streetlights"}
DATA_PATH = Path(__file__).parent / "data" / "complaints.csv"


def load_training_data(filepath: Path):
    """Load text and category columns from CSV and validate expected categories."""
    if not filepath.exists():
        raise FileNotFoundError(f"Training dataset not found at {filepath}")

    complaints = []
    categories = []

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("text", "").strip()
            cat = row.get("category", "").strip()
            if text and cat:
                complaints.append(text)
                categories.append(cat)

    loaded_categories = set(categories)
    if loaded_categories != EXPECTED_CATEGORIES:
        unexpected = loaded_categories - EXPECTED_CATEGORIES
        missing = EXPECTED_CATEGORIES - loaded_categories
        raise ValueError(
            f"Dataset categories mismatch. Unexpected: {unexpected}, Missing: {missing}"
        )

    return complaints, categories


# Load dataset and fit pipeline on all examples
training_complaints, training_categories = load_training_data(DATA_PATH)

classifier = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")),
    ("model", LogisticRegression(max_iter=1000, C=1.0)),
])

classifier.fit(training_complaints, training_categories)


# Heuristic decision threshold for the top predicted class score.
# Note: Uncalibrated logistic regression scores on a small training dataset
# represent empirical decision margins rather than statistical probabilities.
UNCERTAINTY_THRESHOLD = 0.28


def predict_category(description: str) -> str:
    """Predict civic category with three-tier uncertainty handling.

    Returns:
        The predicted category string, or "Uncertain" if the input is empty,
        contains no recognized TF-IDF features, or falls below the decision threshold.
    """
    # 1. Reject empty or whitespace-only input
    if not description or not description.strip():
        return "Uncertain"

    # 2. Reject inputs with zero features recognized by the TF-IDF vocabulary
    tfidf_step = classifier.named_steps["tfidf"]
    feature_matrix = tfidf_step.transform([description])

    if feature_matrix.nnz == 0:
        return "Uncertain"

    # 3. Evaluate highest class decision score via predict_proba
    probabilities = classifier.predict_proba([description])[0]
    best_index = probabilities.argmax()
    best_score = probabilities[best_index]

    if best_score < UNCERTAINTY_THRESHOLD:
        return "Uncertain"

    return str(classifier.classes_[best_index])


if __name__ == "__main__":
    while True:
        description = input(
            "\nEnter a complaint (or type 'exit' to stop): "
        ).strip()

        if description.lower() == "exit":
            break

        if not description:
            print("Please enter a complaint.")
            continue

        category = predict_category(description)
        print("Predicted category:", category)
