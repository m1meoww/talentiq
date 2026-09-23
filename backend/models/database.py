from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TimestampMixin:
    """Shared created_at/updated_at columns."""
    pass
