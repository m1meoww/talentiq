from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models import db, Application, ApplicationHistory, User
from models.application import STATUSES
from utils.auth import role_required

bp = Blueprint("applications", __name__, url_prefix="/api/applications")


@bp.get("")
@jwt_required()
def list_applications():
    query = Application.query
    position_id = request.args.get("position_id", type=int)
    candidate_id = request.args.get("candidate_id", type=int)
    status = request.args.get("status")

    if position_id:
        query = query.filter_by(position_id=position_id)
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)
    if status:
        query = query.filter_by(status=status)

    apps = query.order_by(Application.applied_at.desc()).all()
    return jsonify({"applications": [a.to_dict() for a in apps]})


@bp.get("/<int:application_id>")
@jwt_required()
def get_application(application_id):
    app_ = Application.query.get_or_404(application_id)
    return jsonify(app_.to_dict())


@bp.get("/<int:application_id>/history")
@jwt_required()
def get_history(application_id):
    app_ = Application.query.get_or_404(application_id)
    return jsonify({"history": [h.to_dict() for h in app_.history]})


@bp.put("/<int:application_id>/status")
@role_required("Admin", "HR")
def update_status(application_id):
    app_ = Application.query.get_or_404(application_id)
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    remarks = data.get("remarks", "")

    if new_status not in STATUSES:
        return jsonify({"error": "validation_error",
                         "message": f"status must be one of {', '.join(STATUSES)}."}), 400

    user_id = get_jwt_identity()
    actor = User.query.get(user_id)

    history_entry = ApplicationHistory(
        application_id=app_.id,
        old_status=app_.status,
        new_status=new_status,
        changed_by=actor.name if actor else "system",
        remarks=remarks,
    )
    app_.status = new_status
    db.session.add(history_entry)
    db.session.commit()

    return jsonify(app_.to_dict())


@bp.post("")
@role_required("Admin", "HR", "Candidate")
def create_application():
    data = request.get_json(force=True) or {}
    candidate_id, position_id = data.get("candidate_id"), data.get("position_id")
    if not candidate_id or not position_id:
        return jsonify({"error": "validation_error", "message": "candidate_id and position_id are required."}), 400

    existing = Application.query.filter_by(candidate_id=candidate_id, position_id=position_id).first()
    if existing:
        return jsonify({"error": "duplicate", "message": "This candidate has already applied to this position."}), 409

    from models import CandidateProfile, JobPosition
    from ml.similarity import score_resume_against_text

    candidate = CandidateProfile.query.get_or_404(candidate_id)
    position = JobPosition.query.get_or_404(position_id)

    scoring = score_resume_against_text(
        resume_text=candidate.extracted_resume_text or candidate.summary or "",
        position_text=position.full_text(),
        required_skills=(position.preferred_skills or "").split(","),
        resume_experience_years=candidate.experience_years,
    )

    application = Application(
        candidate_id=candidate_id,
        position_id=position_id,
        match_score=scoring["overall_match"],
        skill_score=scoring["skill_score"],
        experience_score=scoring["experience_score"],
        education_score=scoring["education_score"],
        keyword_score=scoring["keyword_score"],
        matched_skills=",".join(scoring["matched_skills"]),
        missing_skills=",".join(scoring["missing_skills"]),
        status="Applied",
    )
    db.session.add(application)
    db.session.flush()
    db.session.add(ApplicationHistory(
        application_id=application.id, old_status=None, new_status="Applied",
        changed_by=candidate.user.name if candidate.user else "candidate",
        remarks="Application submitted.",
    ))
    db.session.commit()

    return jsonify(application.to_dict()), 201
