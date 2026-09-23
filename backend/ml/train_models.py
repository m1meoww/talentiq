"""
Self-contained trainer that generates synthetic labeled training data (job
descriptions per category) and serializes a baseline TF-IDF vectorizer, SVD
reducer, and LogisticRegression classifier to ml/saved_models/.

Run standalone:
    python -m ml.train_models
If this script has never been run, the app operates in "Demo ML mode" using
on-the-fly TF-IDF + exact cosine similarity instead -- it will not crash.
"""
import random
from sklearn.linear_model import LogisticRegression

from .classifier import CATEGORY_KEYWORDS, save_classifier
from .vectorizer import build_vectorizer, TruncatedSVD, save_models
from .preprocessing import preprocess_for_vectorizer
from sklearn.preprocessing import normalize

random.seed(42)

TEMPLATES = [
    "Looking for a {role} with strong experience in {kw1}, {kw2} and {kw3}. "
    "Responsibilities include building solutions using {kw4} and collaborating "
    "with cross-functional teams. {years}+ years of experience preferred.",
    "We are hiring a {role}. Must have hands-on skills in {kw1}, {kw2}, {kw3} "
    "and familiarity with {kw4}. Bachelor's degree required, {years}+ years experience.",
    "Seeking a {role} to join our growing team, working daily with {kw1} and {kw2}. "
    "Bonus points for {kw3} and {kw4} exposure. {years} years of relevant background.",
]


def _synthesize_dataset(samples_per_category=25):
    texts, labels = [], []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for _ in range(samples_per_category):
            kws = random.sample(keywords, k=min(4, len(keywords)))
            while len(kws) < 4:
                kws.append(random.choice(keywords))
            template = random.choice(TEMPLATES)
            text = template.format(
                role=category, kw1=kws[0], kw2=kws[1], kw3=kws[2], kw4=kws[3],
                years=random.choice([1, 2, 3, 4, 5, 6]),
            )
            texts.append(text)
            labels.append(category)
    return texts, labels


def train_and_save():
    texts, labels = _synthesize_dataset()
    cleaned = [preprocess_for_vectorizer(t) for t in texts]

    vectorizer = build_vectorizer(max_features=2000)
    tfidf = vectorizer.fit_transform(cleaned)

    n_components = max(2, min(50, tfidf.shape[1] - 1, tfidf.shape[0] - 1))
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    reduced = normalize(svd.fit_transform(tfidf), norm="l2")

    model = LogisticRegression(max_iter=1000)
    model.fit(reduced, labels)

    save_models(vectorizer, svd)
    save_classifier({"vectorizer": vectorizer, "svd": svd, "model": model})

    train_acc = model.score(reduced, labels)
    print(f"[TalentIQ] Trained classifier on {len(texts)} synthetic samples "
          f"({len(set(labels))} categories). Train accuracy: {train_acc:.2%}")
    print("[TalentIQ] Models saved to ml/saved_models/. ML pipeline is now in production mode.")


if __name__ == "__main__":
    train_and_save()
