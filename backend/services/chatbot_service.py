"""
"Talia" - the TalentIQ AI recruitment assistant.

Lightweight rule/intent-based NLU (no external LLM dependency) that resolves
a handful of high-value recruiter intents against live database data:
  - application status lookup by candidate name
  - candidate eligibility for a position
  - position info / open roles
  - top-ranked candidate for a position
  - general navigation help
  - respectful fallback for anything else
"""
import re
from sqlalchemy import func

from models import db, CandidateProfile, JobPosition, Application, User
from services.ranking_service import get_live_rankings

GREETINGS = ("hi", "hello", "hey", "good morning", "good afternoon")


def _find_candidate_by_name(name_fragment: str):
    name_fragment = name_fragment.strip().lower()
    return (
        CandidateProfile.query.join(User)
        .filter(func.lower(User.name).contains(name_fragment))
        .first()
    )


def _find_position_by_title(title_fragment: str):
    title_fragment = title_fragment.strip().lower()
    return JobPosition.query.filter(func.lower(JobPosition.title).contains(title_fragment)).first()


def _status_intent(message: str):
    match = re.search(r"status of ([a-zA-Z .]+)", message, re.IGNORECASE)
    if not match:
        return None
    candidate = _find_candidate_by_name(match.group(1))
    if not candidate:
        return f"I couldn't find a candidate matching '{match.group(1).strip()}'."
    apps = candidate.applications.all()
    if not apps:
        return f"{candidate.user.name} hasn't applied to any open positions yet."
    lines = [f"- {a.position.title}: {a.status} ({round(a.match_score,1)}% match)" for a in apps]
    return f"Application status for {candidate.user.name}:\n" + "\n".join(lines)


def _top_applicant_intent(message: str):
    match = re.search(r"top applicant for (?:the )?([a-zA-Z0-9 /\-]+)", message, re.IGNORECASE)
    if not match:
        return None
    position = _find_position_by_title(match.group(1))
    if not position:
        return f"I couldn't find an open position matching '{match.group(1).strip()}'."
    rankings = get_live_rankings(position, only_applicants=True)
    if not rankings:
        return f"No applicants yet for {position.title}."
    top = rankings[0]
    return (
        f"The top applicant for {position.title} is {top['candidate_name']} "
        f"with a {top['overall_match']}% match score."
    )


def _open_positions_intent(message: str):
    if "open position" not in message.lower() and "positions" not in message.lower():
        return None
    positions = JobPosition.query.filter_by(status="Open").all()
    if not positions:
        return "There are currently no open positions."
    lines = [f"- {p.title} ({p.department})" for p in positions]
    return "Current open positions:\n" + "\n".join(lines)


def _skill_search_intent(message: str):
    match = re.search(r"candidates? with ([a-zA-Z0-9,+.# ]+)", message, re.IGNORECASE)
    if not match:
        return None
    skills = [s.strip().lower() for s in re.split(r"and|,", match.group(1)) if s.strip()]
    if not skills:
        return None
    candidates = CandidateProfile.query.all()
    hits = []
    for c in candidates:
        cand_skills = [s.lower() for s in c.skills_list()]
        if all(any(sk in cs for cs in cand_skills) for sk in skills):
            hits.append(c)
    if not hits:
        return f"No candidates found with skills: {', '.join(skills)}."
    names = ", ".join(c.user.name for c in hits[:8] if c.user)
    return f"Candidates matching {', '.join(skills)}: {names}"


def _eligibility_intent(message: str):
    match = re.search(r"is ([a-zA-Z .]+) eligible for (?:the )?([a-zA-Z0-9 /\-]+)", message, re.IGNORECASE)
    if not match:
        return None
    candidate = _find_candidate_by_name(match.group(1))
    position = _find_position_by_title(match.group(2))
    if not candidate or not position:
        return "I couldn't find that candidate or position — could you double-check the names?"
    from ml.similarity import score_resume_against_text
    result = score_resume_against_text(
        resume_text=candidate.extracted_resume_text or candidate.summary or "",
        position_text=position.full_text(),
        required_skills=(position.preferred_skills or "").split(","),
        resume_experience_years=candidate.experience_years,
    )
    verdict = "a strong fit" if result["overall_match"] >= 70 else (
        "a moderate fit" if result["overall_match"] >= 45 else "not currently a strong fit"
    )
    return (
        f"{candidate.user.name} is {verdict} for {position.title} "
        f"({result['overall_match']}% match)."
    )


INTENT_HANDLERS = [
    _status_intent,
    _top_applicant_intent,
    _eligibility_intent,
    _skill_search_intent,
    _open_positions_intent,
]


def get_reply(message: str) -> dict:
    stripped = message.strip()
    lowered = stripped.lower()

    if any(lowered.startswith(g) for g in GREETINGS):
        return {"reply": "Hi! I'm Talia, your recruitment assistant. Ask me about "
                          "application status, candidate eligibility, open positions, "
                          "or top applicants for a role.", "intent": "greeting"}

    for handler in INTENT_HANDLERS:
        try:
            result = handler(stripped)
        except Exception:  # noqa: BLE001
            result = None
        if result:
            return {"reply": result, "intent": handler.__name__.strip("_")}

    return {
        "reply": (
            "I'm not sure I understood that. You can ask me things like "
            "\"Show status of Aarav Sharma\", \"Who is the top applicant for "
            "AI/ML Engineer?\", or \"Find candidates with Python and PyTorch\"."
        ),
        "intent": "fallback",
    }
