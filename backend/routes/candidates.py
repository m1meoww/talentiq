from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import db, CandidateProfile, Application
from utils.auth import role_required

bp = Blueprint("candidates", __name__, url_prefix="/api/candidates")


@bp.get("")
@jwt_required()
def list_candidates():
    query = CandidateProfile.query

    search = request.args.get("search")
    if search:
        from sqlalchemy import or_
        from models import User
        query = query.join(User).filter(
            or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
        )

    min_experience = request.args.get("min_experience", type=float)
    if min_experience is not None:
        query = query.filter(CandidateProfile.experience_years >= min_experience)

    position_id = request.args.get("position_id", type=int)
    status = request.args.get("status")
    if position_id or status:
        app_query = Application.query
        if position_id:
            app_query = app_query.filter_by(position_id=position_id)
        if status:
            app_query = app_query.filter_by(status=status)
        candidate_ids = [a.candidate_id for a in app_query.all()]
        query = query.filter(CandidateProfile.id.in_(candidate_ids))

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "candidates": [c.to_dict() for c in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    })


@bp.get("/<int:candidate_id>")
@jwt_required()
def get_candidate(candidate_id):
    candidate = CandidateProfile.query.get_or_404(candidate_id)
    data = candidate.to_dict()
    data["applications"] = [a.to_dict() for a in candidate.applications.all()]
    return jsonify(data)


@bp.put("/<int:candidate_id>")
@role_required("Admin", "HR", "Candidate")
def update_candidate(candidate_id):
    candidate = CandidateProfile.query.get_or_404(candidate_id)
    data = request.get_json(force=True) or {}

    for field in ("phone", "location", "education", "experience_years", "skills", "summary"):
        if field in data:
            setattr(candidate, field, data[field])

    db.session.commit()
    return jsonify(candidate.to_dict())
