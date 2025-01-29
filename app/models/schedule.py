from datetime import datetime

from app import db


class ScheduleModel(db.Model):
    __tablename__ = "scheduled_jobs"
    id = db.Column(db.Integer, primary_key=True)
    task_name: str = db.Column(db.String(128), nullable=False)
    schedule: str = db.Column(db.String(128), nullable=False)  # Exemplo: "*/5 * * * *"
    args: str = db.Column(db.Text, nullable=True, default="[]")  # JSON para argumentos
    kwargs: str = db.Column(db.Text, nullable=True, default="{}")  # JSON para kwargs
    last_run_at: datetime = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Schedule {self.task_name}>"
