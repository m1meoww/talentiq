from models import CandidateProfile, JobPosition, Application
from ml.pipeline import rank_candidates_for_position


def get_live_rankings(position: JobPosition, only_applicants: bool = True):
    """
    Computes fresh cosine-similarity rankings for a position.
    If only_applicants=True, ranks only candidates who have applied;
    otherwise ranks the entire candidate pool (useful for sourcing).
    """
    if only_applicants:
        candidate_ids = [a.candidate_id for a in position.applications]
        candidates = CandidateProfile.query.filter(CandidateProfile.id.in_(candidate_ids)).all()
    else:
        candidates = CandidateProfile.query.all()

    ranked = rank_candidates_for_position(position, candidates)

    by_id = {c.id: c for c in candidates}
    enriched = []
    for row in ranked:
        cand = by_id.get(row["candidate_id"])
        if not cand:
            continue
        enriched.append({
            **row,
            "candidate_name": cand.user.name if cand.user else None,
            "candidate_email": cand.user.email if cand.user else None,
            "predicted_category": cand.predicted_category,
        })
    return enriched
