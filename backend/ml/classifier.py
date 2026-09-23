"""
Job-category classifier: Logistic Regression over TF-IDF+SVD features,
predicting the candidate's best-fit category (Software Engineering,
Data Science, AI/ML, Cybersecurity, Cloud/DevOps, Product, Operations).

Falls back to a lightweight keyword-voting classifier ("Demo ML mode")
whenever no trained model is present on disk, so the pipeline never crashes.
"""
import os
import joblib

from .preprocessing import clean_text

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "category_classifier.joblib")

CATEGORIES = [
    "Software Engineering",
    "Data Science",
    "AI/ML",
    "Cybersecurity",
    "Cloud/DevOps",
    "Product",
    "Operations",
]

# Keyword lexicon used both to synthesize training data and as the
# rule-based fallback when no persisted model exists.
CATEGORY_KEYWORDS = {
    "Software Engineering": [
        "java", "python", "c++", "spring", "microservices", "api", "backend",
        "frontend", "react", "node", "software engineer", "git", "rest",
    ],
    "Data Science": [
        "pandas", "numpy", "statistics", "data analysis", "sql", "tableau",
        "power bi", "data scientist", "regression", "visualization",
    ],
    "AI/ML": [
        "machine learning", "deep learning", "pytorch", "tensorflow", "nlp",
        "computer vision", "neural network", "llm", "scikit-learn", "ai engineer",
    ],
    "Cybersecurity": [
        "penetration testing", "siem", "firewall", "vulnerability", "soc",
        "security engineer", "encryption", "iso 27001", "incident response",
    ],
    "Cloud/DevOps": [
        "aws", "azure", "gcp", "kubernetes", "docker", "terraform", "ci/cd",
        "devops", "jenkins", "cloud engineer", "ansible",
    ],
    "Product": [
        "product manager", "roadmap", "stakeholder", "user research",
        "product strategy", "agile", "backlog", "go-to-market",
    ],
    "Operations": [
        "operations", "supply chain", "logistics", "vendor management",
        "process improvement", "sop", "recruitment operations",
    ],
}


def _keyword_vote(text: str) -> tuple[str, float]:
    cleaned = clean_text(text)
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if clean_text(kw) in cleaned:
                scores[cat] += 1
    best_cat = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = scores[best_cat] / total if scores[best_cat] else (1 / len(CATEGORIES))
    return best_cat, round(confidence * 100, 1)


def load_classifier():
    if os.path.exists(CLASSIFIER_PATH):
        try:
            return joblib.load(CLASSIFIER_PATH)
        except Exception:  # noqa: BLE001
            return None
    return None


def save_classifier(bundle):
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(bundle, CLASSIFIER_PATH)


def predict_category(text: str) -> dict:
    """
    Returns {"category": str, "confidence": float}. Uses the trained
    LogisticRegression bundle if present, otherwise the keyword fallback.
    """
    bundle = load_classifier()
    if bundle is not None:
        try:
            vectorizer = bundle["vectorizer"]
            svd = bundle["svd"]
            model = bundle["model"]
            from .preprocessing import preprocess_for_vectorizer
            cleaned = [preprocess_for_vectorizer(text)]
            vec = svd.transform(vectorizer.transform(cleaned))
            proba = model.predict_proba(vec)[0]
            idx = proba.argmax()
            return {
                "category": model.classes_[idx],
                "confidence": round(float(proba[idx]) * 100, 1),
                "mode": "trained",
            }
        except Exception:  # noqa: BLE001
            pass

    category, confidence = _keyword_vote(text)
    return {"category": category, "confidence": confidence, "mode": "demo"}
