"""Model evaluation script for Smart Complaint Router.

Performs dataset validation and 5-fold StratifiedKFold cross-validation
with a fresh TF-IDF + Logistic Regression pipeline fitted inside each fold
to ensure zero data leakage.
"""

import csv
import math
from pathlib import Path
import re
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline


DATA_PATH = Path(__file__).parent / "data" / "complaints.csv"
EXPECTED_CATEGORIES = {"Roads", "Water Supply", "Electricity", "Garbage", "Streetlights"}


def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, stripping punctuation, and collapsing whitespace."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join(cleaned.split())


def validate_dataset(filepath: Path):
    """Validate dataset for duplicates, empty values, invalid labels, and class balance."""
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at {filepath}")

    texts = []
    categories = []

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"].strip())
            categories.append(row["category"].strip())

    total = len(texts)
    print("=" * 75)
    print("DATASET INTEGRITY & VALIDATION REPORT")
    print("=" * 75)
    print(f"Dataset File: {filepath.name}")
    print(f"Total Records: {total}")

    # 1. Empty / whitespace check
    empty_indices = [i for i, t in enumerate(texts) if not t]
    print(f"• Empty or whitespace-only records: {len(empty_indices)}")
    if empty_indices:
        print(f"  WARNING: Empty rows found at indices: {empty_indices}")

    # 2. Exact duplicates
    exact_counts = Counter(texts)
    exact_duplicates = {t: c for t, c in exact_counts.items() if c > 1}
    print(f"• Exact duplicate texts: {len(exact_duplicates)}")
    if exact_duplicates:
        for text, count in exact_duplicates.items():
            print(f"  WARNING: Exact duplicate ({count}x): {text!r}")

    # 3. Normalized duplicates
    norm_to_original = {}
    normalized_duplicates = []
    for t in texts:
        n = normalize_text(t)
        if n in norm_to_original:
            normalized_duplicates.append((t, norm_to_original[n]))
        else:
            norm_to_original[n] = t

    print(f"• Normalized (near-exact) duplicates: {len(normalized_duplicates)}")
    if normalized_duplicates:
        for t1, t2 in normalized_duplicates:
            print(f"  WARNING: Normalized collision between: {t1!r} and {t2!r}")

    # 4. Valid category labels
    actual_categories = set(categories)
    invalid_categories = actual_categories - EXPECTED_CATEGORIES
    print(f"• Invalid category labels: {len(invalid_categories)}")
    if invalid_categories:
        print(f"  WARNING: Unexpected categories: {invalid_categories}")

    # 5. Class balance
    counts = Counter(categories)
    print("• Class distribution:")
    for cat in sorted(EXPECTED_CATEGORIES):
        print(f"    - {cat:<14}: {counts.get(cat, 0)} examples")

    counts_values = set(counts.values())
    is_balanced = len(counts_values) == 1 and len(counts) == len(EXPECTED_CATEGORIES)
    print(f"• Class balance verified: {'YES (perfectly balanced)' if is_balanced else 'NO (imbalanced)'}")
    print("=" * 75)

    return texts, categories


def run_cross_validation(texts, categories, n_splits=5, random_state=42):
    """Run 5-fold StratifiedKFold cross-validation with fresh pipeline per fold."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    classes = sorted(list(EXPECTED_CATEGORIES))

    fold_accuracies = []
    y_true_all = []
    y_pred_all = []

    print(f"\nRUNNING {n_splits}-FOLD STRATIFIED CROSS-VALIDATION")
    print("Note: A fresh TF-IDF + LogisticRegression pipeline is fitted inside each fold")
    print("to strictly isolate vocabulary extraction and model training from validation data.")
    print("-" * 75)

    for fold_idx, (train_indices, val_indices) in enumerate(skf.split(texts, categories), 1):
        # Extract train and validation folds
        X_train = [texts[i] for i in train_indices]
        y_train = [categories[i] for i in train_indices]
        X_val = [texts[i] for i in val_indices]
        y_val = [categories[i] for i in val_indices]

        # Fresh pipeline instance per fold (no leakage of vocabulary or IDF weights)
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("model", LogisticRegression(max_iter=1000, C=1.0)),
        ])
        pipeline.fit(X_train, y_train)

        # Predict strictly on unseen validation fold
        y_pred = pipeline.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        fold_accuracies.append(acc)

        y_true_all.extend(y_val)
        y_pred_all.extend(y_pred)

        print(f"Fold {fold_idx}: {len(X_train)} train samples | {len(X_val)} val samples | Accuracy: {acc * 100:.2f}%")

    # Aggregate statistics
    mean_acc = sum(fold_accuracies) / len(fold_accuracies)
    variance = sum((x - mean_acc) ** 2 for x in fold_accuracies) / (len(fold_accuracies) - 1)
    std_acc = math.sqrt(variance)

    print("-" * 75)
    print(f"MEAN ACCURACY:     {mean_acc * 100:.2f}%")
    print(f"STANDARD DEVIATION: ±{std_acc * 100:.2f}%")
    print(f"OVERALL POOLED:    {accuracy_score(y_true_all, y_pred_all) * 100:.2f}%")
    print("=" * 75)

    print("\nAGGREGATE CLASSIFICATION REPORT (Out-of-Fold Predictions):")
    print("-" * 75)
    report = classification_report(
        y_true_all,
        y_pred_all,
        labels=classes,
        target_names=classes,
        digits=3,
        zero_division=0,
    )
    print(report)

    print("AGGREGATE CONFUSION MATRIX (Out-of-Fold Predictions across all 125 samples):")
    print("-" * 75)
    cm = confusion_matrix(y_true_all, y_pred_all, labels=classes)

    col_width = 15
    header_labels = "".join([f"{c[:13]:>{col_width}}" for c in classes])
    header = f"{'Actual \\ Pred':<{col_width}}" + header_labels
    print(header)
    print("-" * len(header))

    for i, actual_cls in enumerate(classes):
        row_values = "".join([f"{cm[i][j]:>{col_width}}" for j in range(len(classes))])
        row_line = f"{actual_cls[:14]:<{col_width}}" + row_values
        print(row_line)

    print("-" * len(header))
    print("\nIMPORTANT INTERPRETATION NOTE:")
    print("These metrics represent 5-fold cross-validation on an author-curated prototype dataset.")
    print("While StratifiedKFold prevents data leakage across folds, cross-validation on curated")
    print("examples measures internal category separability rather than true out-of-domain performance.")
    print("Real-world citizen complaints will exhibit noisy formatting, unstandardized grammar,")
    print("spelling errors, and out-of-vocabulary terms that can lower operational accuracy.")
    print("=" * 75)


def main():
    texts, categories = validate_dataset(DATA_PATH)
    run_cross_validation(texts, categories, n_splits=5, random_state=42)


if __name__ == "__main__":
    main()
