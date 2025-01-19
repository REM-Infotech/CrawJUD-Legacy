import json

from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab


class DatabaseScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schedule = {}

    def get_schedule(self):
        """Carrega os agendamentos do banco de dados."""
        schedules = {}

        from app.models import ScheduleModel

        db_entries = ScheduleModel.query.all()
        for entry in db_entries:
            cron_args = self.parse_cron(entry.schedule)
            schedules[entry.task_name] = ScheduleEntry(
                name=entry.task_name,
                task=entry.task_name,
                schedule=crontab(**cron_args),
                args=json.loads(entry.args or "[]"),
                kwargs=json.loads(entry.kwargs or "{}"),
            )
        return schedules

    @staticmethod
    def parse_cron(cron_string):
        """Converte o formato crontab string em kwargs para crontab."""
        fields = ["minute", "hour", "day_of_month", "month_of_year", "day_of_week"]
        cron_parts = cron_string.split()
        return {field: value for field, value in zip(fields, cron_parts)}

    @property
    def schedule(self):
        self.sync()
        return self._schedule

    def sync(self):
        """Sincroniza os agendamentos com o banco de dados."""
        self._schedule = self.get_schedule()

    def tick(self):
        """Define como processar os schedules. Este método é chamado continuamente."""
        remaining_times = super().tick()
        self.sync()
        return remaining_times
