import datetime as dt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from models import db, Application, JobPosition, CandidateProfile

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@bp.get("/kpis")
@jwt_required()
def kpis():
    total_applicants = CandidateProfile.query.count()
    resumes_screened = CandidateProfile.query.filter(
        CandidateProfile.extracted_resume_text.isnot(None)
    ).count()
    open_positions = JobPosition.query.filter_by(status="Open").count()
    shortlisted = Application.query.filter_by(status="Shortlisted").count()
    avg_score = db.session.query(func.avg(Application.match_score)).scalar() or 0

    return jsonify({
        "total_applicants": total_applicants,
        "resumes_screened": resumes_screened,
        "open_positions": open_positions,
        "shortlisted": shortlisted,
        "avg_match_score": round(avg_score, 1),
    })


@bp.get("/trends")
@jwt_required()
def trends():
    rows = (
        db.session.query(
            func.date(Application.applied_at).label("day"),
            func.count(Application.id),
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    return jsonify({"trends": [{"date": str(day), "count": count} for day, count in rows]})


@bp.get("/category-distribution")
@jwt_required()
def category_distribution():
    rows = (
        db.session.query(CandidateProfile.predicted_category, func.count(CandidateProfile.id))
        .group_by(CandidateProfile.predicted_category)
        .all()
    )
    return jsonify({"distribution": [{"category": cat or "Unclassified", "count": count} for cat, count in rows]})


@bp.get("/position-funnel")
@jwt_required()
def position_funnel():
    rows = (
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    return jsonify({"funnel": [{"status": s, "count": c} for s, c in rows]})


@bp.get("/score-histogram")
@jwt_required()
def score_histogram():
    buckets = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    scores = [row[0] for row in db.session.query(Application.match_score).all()]
    for s in scores:
        s = s or 0
        if s < 20:
            buckets["0-20"] += 1
        elif s < 40:
            buckets["20-40"] += 1
        elif s < 60:
            buckets["40-60"] += 1
        elif s < 80:
            buckets["60-80"] += 1
        else:
            buckets["80-100"] += 1
    return jsonify({"histogram": [{"bucket": k, "count": v} for k, v in buckets.items()]})


@bp.get("/position-wise")
@jwt_required()
def position_wise():
    rows = (
        db.session.query(JobPosition.title, func.count(Application.id), func.avg(Application.match_score))
        .join(Application, Application.position_id == JobPosition.id)
        .group_by(JobPosition.id)
        .all()
    )
    return jsonify({"positions": [
        {"title": t, "applicants": c, "avg_score": round(a or 0, 1)} for t, c, a in rows
    ]})


@bp.get("/export")
@jwt_required()
def export_data():
    from services.report_service import generate_csv_export
    from flask import Response

    apps = Application.query.all()
    rows = [{
        "candidate": a.candidate.user.name if a.candidate.user else "",
        "position": a.position.title if a.position else "",
        "match_score": a.match_score,
        "status": a.status,
        "applied_at": a.applied_at.isoformat() if a.applied_at else "",
    } for a in apps]

    csv_bytes = generate_csv_export(rows)
    return Response(
        csv_bytes, mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=recruitment_export.csv"},
    )
