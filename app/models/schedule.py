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
    email: str = db.Column(db.String(128), nullable=True)

    schedule_id = db.Column(db.Integer, db.ForeignKey("crontab_model.id"), nullable=False)
    schedule = db.relationship("CrontabModel", backref="schedule", lazy=True)

    args: str = db.Column(db.Text, nullable=True, default="[]")  # JSON para argumentos

    kwargs: str = db.Column(db.Text, nullable=True, default="{}")  # JSON para kwargs
    last_run_at: datetime = db.Column(db.DateTime, nullable=True)

    license_id = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship("LicensesUsers", backref=db.backref("scheduled_execution", lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        """Return a string representation of the scheduled job.

        Returns:
            str: The task name of the scheduled job.

        """
        return f"<Schedule {self.name}>"


class CrontabModel(db.Model):
    """Represents a crontab schedule with its execution details."""

    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.String(64), default="*")
    minute = db.Column(db.String(64), default="*")
    day_of_week = db.Column(db.String(64), default="*")
    day_of_month = db.Column(db.String(64), default="*")
    month_of_year = db.Column(db.String(64), default="*")

    def __init__(
        self,
        minute: str = "*",
        hour: str = "*",
        day_of_week: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*",
    ) -> None:
        """Initialize a new crontab schedule.

        Args:
            minute (str): The minute to run the task.
            hour (str): The hour to run the task.
            day_of_week (str): The day of the week to run the task.
            day_of_month (str): The day of the month to run the task.
            month_of_year (str): The month of the year to run the task.

        """
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.month_of_year = month_of_year
