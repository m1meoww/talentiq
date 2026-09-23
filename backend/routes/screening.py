from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, CandidateProfile, JobPosition
from utils.pdf_parser import PDFParseError
from services.resume_service import process_resume_upload
from ml.pipeline import analyze_resume
from ml.preprocessing import preprocess_for_vectorizer  # noqa: F401
from ml.similarity import score_resume_against_text

bp = Blueprint("screening", __name__, url_prefix="/api/screening")

STEPS = [
    "Extracting text from PDF...",
    "Cleaning and preprocessing text...",
    "Building TF-IDF representation...",
    "Reducing dimensions with SVD...",
    "Calculating cosine similarity...",
    "Generating final match score...",
]


@bp.get("/steps")
@jwt_required()
def get_steps():
    """Exposes the 6-step pipeline labels the frontend animates through."""
    return jsonify({"steps": STEPS})


@bp.post("/upload")
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    candidate = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not candidate:
        return jsonify({"error": "not_found", "message": "No candidate profile found for this account."}), 404

    if "resume" not in request.files:
        return jsonify({"error": "validation_error", "message": "No resume file was provided."}), 400

    file_storage = request.files["resume"]
    if not file_storage.filename.lower().endswith(".pdf"):
        return jsonify({"error": "validation_error", "message": "Only PDF resumes are supported."}), 400

    position_id = request.form.get("position_id", type=int)
    position = JobPosition.query.get(position_id) if position_id else None

    try:
        analysis = process_resume_upload(
            candidate, file_storage, current_app.config["UPLOAD_FOLDER"], position=position
        )
    except PDFParseError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), 422

    return jsonify({"analysis": analysis, "steps": STEPS})


@bp.post("/compare-text")
@jwt_required()
def compare_text():
    """Direct text-vs-text comparison, bypassing PDF upload (used for quick demos)."""
    data = request.get_json(force=True) or {}
    resume_text = data.get("resume_text", "")
    position_text = data.get("position_text", "")
    required_skills = data.get("required_skills", [])

    if not resume_text or not position_text:
        return jsonify({"error": "validation_error", "message": "resume_text and position_text are required."}), 400

    result = score_resume_against_text(resume_text, position_text, required_skills)
    category = analyze_resume(resume_text)
    return jsonify({**result, **category})
