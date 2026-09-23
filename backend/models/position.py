import datetime as dt
from .database import db


class JobPosition(db.Model):
    __tablename__ = "job_positions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    department = db.Column(db.String(80))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    preferred_skills = db.Column(db.Text)   # comma-separated
    location = db.Column(db.String(120))
    employment_type = db.Column(db.String(40), default="Full-time")
    experience_level = db.Column(db.String(40), default="Mid")
    status = db.Column(db.String(20), default="Open")  # Open, Closed, On-Hold
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    applications = db.relationship(
        "Application", backref="position", cascade="all, delete-orphan", lazy="dynamic"
    )

    def full_text(self):
        """Concatenated text used as the ML pipeline's 'position document'."""
        parts = [self.title or "", self.description or "", self.requirements or "",
                 self.preferred_skills or ""]
        return " ".join(parts)

    def to_dict(self, applicant_count=None, avg_score=None):
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "description": self.description,
            "requirements": self.requirements,
            "preferred_skills": [s.strip() for s in (self.preferred_skills or "").split(",") if s.strip()],
            "location": self.location,
            "employment_type": self.employment_type,
            "experience_level": self.experience_level,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "applicant_count": applicant_count,
            "avg_score": avg_score,
        }
