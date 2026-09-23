"""
Core scoring logic: score_resume_against_text().

Combines:
  1. Mathematical cosine similarity over TF-IDF+SVD vectors (semantic overlap)
  2. Weighted category sub-scores (skills, experience, education, keywords)
into a single overall match percentage, plus matched/missing skill chips.
"""
import re
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import clean_text
from .vectorizer import vectorize_documents, transform_with_saved, load_saved_models

# Weights for the composite score (must sum to 1.0)
WEIGHTS = {
    "semantic": 0.40,
    "skill": 0.30,
    "experience": 0.15,
    "education": 0.10,
    "keyword": 0.05,
}

EDUCATION_LEVELS = [
    ("phd", 5), ("doctorate", 5),
    ("master", 4), ("m.tech", 4), ("mtech", 4), ("msc", 4), ("mba", 4),
    ("bachelor", 3), ("b.tech", 3), ("btech", 3), ("bsc", 3), ("be ", 3),
    ("diploma", 2),
    ("high school", 1),
]

_EXPERIENCE_RE = re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)")


def _extract_experience_years(text: str) -> float:
    matches = _EXPERIENCE_RE.findall(text.lower())
    if not matches:
        return 0.0
    return max(float(m) for m in matches)


def _extract_education_level(text: str) -> int:
    lowered = text.lower()
    for keyword, level in EDUCATION_LEVELS:
        if keyword in lowered:
            return level
    return 0


def _extract_skill_set(text: str, vocabulary: set[str]) -> set[str]:
    cleaned = clean_text(text)
    tokens = set(cleaned.split(" "))
    # also catch bigram skills like "machine learning"
    found = set()
    for skill in vocabulary:
        skill_clean = clean_text(skill)
        if skill_clean and skill_clean in cleaned:
            found.add(skill.strip())
    return found or (tokens & vocabulary)


def score_resume_against_text(
    resume_text: str,
    position_text: str,
    required_skills: list[str] | None = None,
    resume_experience_years: float | None = None,
) -> dict:
    """
    Returns a dict with overall match %, category breakdown, matched/missing
    skills, using exact cosine similarity + rule-based sub-scores. Never
    raises: falls back to 0-scores on degenerate input rather than crashing.
    """
    resume_text = resume_text or ""
    position_text = position_text or ""
    required_skills = required_skills or []

    # ---- 1. Semantic similarity (TF-IDF + SVD + cosine) ----
    vectorizer, svd = load_saved_models()
    try:
        if vectorizer is not None and svd is not None:
            vectors = transform_with_saved([resume_text, position_text], vectorizer, svd)
        else:
            vectors, _, _ = vectorize_documents([resume_text, position_text])
        semantic_sim = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
        semantic_sim = max(0.0, min(1.0, semantic_sim))
    except Exception:  # noqa: BLE001
        semantic_sim = 0.0

    # ---- 2. Skill overlap ----
    skill_vocab = set(s.strip() for s in required_skills if s.strip())
    if not skill_vocab:
        # fall back to naive noun-ish tokens from the position text
        skill_vocab = set(clean_text(position_text).split(" ")[:40])

    resume_skills = _extract_skill_set(resume_text, skill_vocab)
    matched = sorted(skill_vocab & resume_skills) if skill_vocab else []
    missing = sorted(skill_vocab - resume_skills) if skill_vocab else []
    skill_score = (len(matched) / len(skill_vocab)) if skill_vocab else semantic_sim

    # ---- 3. Experience ----
    required_years = _extract_experience_years(position_text)
    candidate_years = (
        resume_experience_years
        if resume_experience_years is not None
        else _extract_experience_years(resume_text)
    )
    if required_years <= 0:
        experience_score = 1.0 if candidate_years > 0 else 0.5
    else:
        experience_score = min(1.0, candidate_years / required_years)

    # ---- 4. Education ----
    required_level = _extract_education_level(position_text)
    candidate_level = _extract_education_level(resume_text)
    if required_level == 0:
        education_score = 1.0 if candidate_level > 0 else 0.6
    else:
        education_score = min(1.0, candidate_level / required_level)

    # ---- 5. Keyword density (non-skill overlap) ----
    resume_tokens = set(clean_text(resume_text).split(" "))
    position_tokens = set(clean_text(position_text).split(" "))
    if position_tokens:
        keyword_score = len(resume_tokens & position_tokens) / len(position_tokens)
        keyword_score = min(1.0, keyword_score)
    else:
        keyword_score = 0.0

    overall = (
        WEIGHTS["semantic"] * semantic_sim
        + WEIGHTS["skill"] * skill_score
        + WEIGHTS["experience"] * experience_score
        + WEIGHTS["education"] * education_score
        + WEIGHTS["keyword"] * keyword_score
    )

    return {
        "overall_match": round(overall * 100, 1),
        "semantic_similarity": round(semantic_sim * 100, 1),
        "skill_score": round(skill_score * 100, 1),
        "experience_score": round(experience_score * 100, 1),
        "education_score": round(education_score * 100, 1),
        "keyword_score": round(keyword_score * 100, 1),
        "matched_skills": matched,
        "missing_skills": missing,
        "candidate_experience_years": candidate_years,
    }
