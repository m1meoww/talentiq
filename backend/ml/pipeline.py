"""
Unified pipeline coordinating text extraction -> preprocessing -> scoring ->
classification, used by both the API (services/resume_service.py) and the
CLI demo tool (cli/resume_demo.py).
"""
from .similarity import score_resume_against_text
from .classifier import predict_category
from .preprocessing import clean_text


def analyze_resume(resume_text: str, position=None, required_skills=None):
    """
    position: a JobPosition ORM instance or None (category prediction only).
    Returns a fully-assembled analysis dict ready to persist / serialize.
    """
    category = predict_category(resume_text)

    result = {
        "predicted_category": category["category"],
        "category_confidence": category["confidence"],
        "category_mode": category["mode"],
    }

    if position is not None:
        scoring = score_resume_against_text(
            resume_text=resume_text,
            position_text=position.full_text(),
            required_skills=required_skills or (position.preferred_skills or "").split(","),
        )
        result.update(scoring)

    return result


def rank_candidates_for_position(position, candidates):
    """
    candidates: iterable of CandidateProfile.
    Returns a list of dicts sorted by overall_match descending.
    """
    required_skills = (position.preferred_skills or "").split(",")
    ranked = []
    for cand in candidates:
        scoring = score_resume_against_text(
            resume_text=cand.extracted_resume_text or cand.summary or "",
            position_text=position.full_text(),
            required_skills=required_skills,
            resume_experience_years=cand.experience_years,
        )
        ranked.append({"candidate_id": cand.id, **scoring})
    ranked.sort(key=lambda r: r["overall_match"], reverse=True)
    return ranked
