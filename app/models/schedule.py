"""Database model for scheduled jobs in CrawJUD-Bots."""

from datetime import datetime

from app import db

# from sqlalchemy.orm.relationships import RelationshipProperty


class ScheduleModel(db.Model):
    """Represents a scheduled job with its execution details."""

    __tablename__ = "scheduled_jobs"
    id = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(128), nullable=False)
    task: str = db.Column(db.String(128), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey("crontab_model.id"), nullable=False)
    schedule = db.relationship("CrontabModel", backref="schedule", lazy=True)
    args: str = db.Column(db.Text, nullable=True, default="[]")  # JSON para argumentos
    kwargs: str = db.Column(db.Text, nullable=True, default="{}")  # JSON para kwargs
    last_run_at: datetime = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        """Return a string representation of the scheduled job.

        Returns:
            str: The task name of the scheduled job.

        """
        return f"<Schedule {self.name}>"


class CrontabModel(db.Model):
    """Represents a crontab schedule with its execution details."""

    id = db.Column(db.Integer, primary_key=True)
    minute = db.Column(db.String(64), default="*")
    hour = db.Column(db.String(64), default="*")
    day_of_week = db.Column(db.String(64), default="*")
    day_of_month = db.Column(db.String(64), default="*")
    month_of_year = db.Column(db.String(64), default="*")
