from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required

from models import JobPosition, CandidateProfile
from services.report_service import (
    generate_position_applicant_report,
    generate_candidate_screening_report,
    generate_analytics_report,
)
from routes.analytics import kpis as kpis_view

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _pdf_response(pdf_bytes, filename):
    return Response(
        pdf_bytes, mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@bp.get("/position/<int:position_id>")
@jwt_required()
def position_report(position_id):
    position = JobPosition.query.get_or_404(position_id)
    pdf_bytes = generate_position_applicant_report(position)
    return _pdf_response(pdf_bytes, f"position_{position_id}_applicants.pdf")


@bp.get("/candidate/<int:candidate_id>")
@jwt_required()
def candidate_report(candidate_id):
    candidate = CandidateProfile.query.get_or_404(candidate_id)
    pdf_bytes = generate_candidate_screening_report(candidate)
    return _pdf_response(pdf_bytes, f"candidate_{candidate_id}_screening.pdf")


@bp.get("/analytics")
@jwt_required()
def analytics_report():
    from models import db, Application
    from sqlalchemy import func

    stats = {
        "total_applicants": CandidateProfile.query.count(),
        "open_positions": JobPosition.query.filter_by(status="Open").count(),
        "avg_match_score": round(db.session.query(func.avg(Application.match_score)).scalar() or 0, 1),
        "shortlisted": Application.query.filter_by(status="Shortlisted").count(),
        "selected": Application.query.filter_by(status="Selected").count(),
    }
    pdf_bytes = generate_analytics_report(stats)
    return _pdf_response(pdf_bytes, "recruitment_analytics.pdf")
