from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from models import db, JobPosition, Application
from services.ranking_service import get_live_rankings
from utils.auth import role_required

bp = Blueprint("positions", __name__, url_prefix="/api/positions")


def _with_stats(position):
    apps = position.applications.all()
    count = len(apps)
    avg = round(sum(a.match_score or 0 for a in apps) / count, 1) if count else 0
    return position.to_dict(applicant_count=count, avg_score=avg)


@bp.get("")
@jwt_required()
def list_positions():
    department = request.args.get("department")
    status = request.args.get("status")
    query = JobPosition.query
    if department:
        query = query.filter_by(department=department)
    if status:
        query = query.filter_by(status=status)
    positions = query.order_by(JobPosition.created_at.desc()).all()
    return jsonify({"positions": [_with_stats(p) for p in positions]})


@bp.get("/departments")
@jwt_required()
def list_departments():
    rows = db.session.query(JobPosition.department).distinct().all()
    return jsonify({"departments": [r[0] for r in rows if r[0]]})


@bp.get("/<int:position_id>")
@jwt_required()
def get_position(position_id):
    position = JobPosition.query.get_or_404(position_id)
    data = _with_stats(position)
    data["rankings"] = get_live_rankings(position, only_applicants=True)
    return jsonify(data)


@bp.post("")
@role_required("Admin", "HR")
def create_position():
    data = request.get_json(force=True) or {}
    if not data.get("title"):
        return jsonify({"error": "validation_error", "message": "title is required."}), 400

    position = JobPosition(
        title=data["title"],
        department=data.get("department"),
        description=data.get("description"),
        requirements=data.get("requirements"),
        preferred_skills=",".join(data.get("preferred_skills", [])) if isinstance(data.get("preferred_skills"), list) else data.get("preferred_skills"),
        location=data.get("location"),
        employment_type=data.get("employment_type", "Full-time"),
        experience_level=data.get("experience_level", "Mid"),
        status=data.get("status", "Open"),
    )
    db.session.add(position)
    db.session.commit()
    return jsonify(_with_stats(position)), 201


@bp.put("/<int:position_id>")
@role_required("Admin", "HR")
def update_position(position_id):
    position = JobPosition.query.get_or_404(position_id)
    data = request.get_json(force=True) or {}

    for field in ("title", "department", "description", "requirements", "location",
                  "employment_type", "experience_level", "status"):
        if field in data:
            setattr(position, field, data[field])

    if "preferred_skills" in data:
        val = data["preferred_skills"]
        position.preferred_skills = ",".join(val) if isinstance(val, list) else val

    db.session.commit()
    return jsonify(_with_stats(position))


@bp.delete("/<int:position_id>")
@role_required("Admin")
def delete_position(position_id):
    position = JobPosition.query.get_or_404(position_id)
    db.session.delete(position)
    db.session.commit()
    return jsonify({"message": "Position deleted."})
