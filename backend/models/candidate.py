import datetime as dt
from .database import db


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    phone = db.Column(db.String(30))
    location = db.Column(db.String(120))
    education = db.Column(db.Text)          # JSON-encoded list of education entries
    experience_years = db.Column(db.Float, default=0)
    skills = db.Column(db.Text)             # comma-separated skill tags
    resume_path = db.Column(db.String(255))
    extracted_resume_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    predicted_category = db.Column(db.String(80))

    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    applications = db.relationship(
        "Application", backref="candidate", cascade="all, delete-orphan", lazy="dynamic"
    )

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def to_dict(self, include_user=True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "phone": self.phone,
            "location": self.location,
            "education": self.education,
            "experience_years": self.experience_years,
            "skills": self.skills_list(),
            "resume_path": self.resume_path,
            "summary": self.summary,
            "predicted_category": self.predicted_category,
        }
        if include_user and self.user:
            data["name"] = self.user.name
            data["email"] = self.user.email
        return data
