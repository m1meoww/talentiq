import datetime as dt
from .database import db

STATUSES = ("Applied", "Under Review", "Shortlisted", "Interview", "Selected", "Rejected")


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("candidate_id", "position_id", name="uq_candidate_position"),
    )

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate_profiles.id"), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey("job_positions.id"), nullable=False)

    match_score = db.Column(db.Float, default=0.0)          # overall cosine-similarity based %
    skill_score = db.Column(db.Float, default=0.0)
    experience_score = db.Column(db.Float, default=0.0)
    education_score = db.Column(db.Float, default=0.0)
    keyword_score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(db.Text)      # comma-separated
    missing_skills = db.Column(db.Text)      # comma-separated

    status = db.Column(db.String(20), default="Applied")
    applied_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    history = db.relationship(
        "ApplicationHistory", backref="application", cascade="all, delete-orphan",
        order_by="ApplicationHistory.changed_at",
    )

    def to_dict(self, include_related=True):
        data = {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "position_id": self.position_id,
            "match_score": round(self.match_score or 0, 1),
            "breakdown": {
                "skill": round(self.skill_score or 0, 1),
                "experience": round(self.experience_score or 0, 1),
                "education": round(self.education_score or 0, 1),
                "keyword": round(self.keyword_score or 0, 1),
            },
            "matched_skills": [s for s in (self.matched_skills or "").split(",") if s],
            "missing_skills": [s for s in (self.missing_skills or "").split(",") if s],
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_related:
            if self.candidate:
                data["candidate_name"] = self.candidate.user.name if self.candidate.user else None
                data["candidate_email"] = self.candidate.user.email if self.candidate.user else None
            if self.position:
                data["position_title"] = self.position.title
                data["department"] = self.position.department
        return data
