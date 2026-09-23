"""
Feature representation: TF-IDF (unigrams + bigrams, sublinear TF) followed by
TruncatedSVD dimensionality reduction and L2 normalization, per spec.

If a persisted vectorizer/SVD pair exists in ml/saved_models it is loaded and
reused for consistent scoring across the app (production mode). If not, a
fresh pair is fit on-the-fly against whatever documents are supplied
("Demo ML mode") so scoring never crashes for lack of a trained model.
"""
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from .preprocessing import preprocess_for_vectorizer

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")
SVD_PATH = os.path.join(MODEL_DIR, "svd_reducer.joblib")


def build_vectorizer(max_features=4000):
    return TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=max_features,
        min_df=1,
    )


def load_saved_models():
    """Returns (vectorizer, svd) or (None, None) if not present on disk."""
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(SVD_PATH):
        try:
            return joblib.load(VECTORIZER_PATH), joblib.load(SVD_PATH)
        except Exception:  # noqa: BLE001
            return None, None
    return None, None


def save_models(vectorizer, svd):
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(svd, SVD_PATH)


def vectorize_documents(documents: list[str], n_components: int = 100):
    """
    Fits TF-IDF + TruncatedSVD on the given documents (Demo ML mode) and
    returns L2-normalized dense vectors, one row per document.
    """
    cleaned = [preprocess_for_vectorizer(d) for d in documents]
    vectorizer = build_vectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned)

    # SVD components can't exceed min(n_samples, n_features) - 1
    max_components = max(1, min(n_components, tfidf_matrix.shape[1] - 1, tfidf_matrix.shape[0] - 1))
    svd = TruncatedSVD(n_components=max_components, random_state=42)
    reduced = svd.fit_transform(tfidf_matrix)
    reduced = normalize(reduced, norm="l2")
    return reduced, vectorizer, svd


def transform_with_saved(documents: list[str], vectorizer, svd):
    cleaned = [preprocess_for_vectorizer(d) for d in documents]
    tfidf_matrix = vectorizer.transform(cleaned)
    reduced = svd.transform(tfidf_matrix)
    return normalize(reduced, norm="l2")
