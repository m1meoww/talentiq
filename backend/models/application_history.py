import datetime as dt
from .database import db


class ApplicationHistory(db.Model):
    """Append-only audit trail of status transitions for an application."""
    __tablename__ = "application_history"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.String(120))     # name/email of the acting user
    changed_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    remarks = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "remarks": self.remarks,
        }
