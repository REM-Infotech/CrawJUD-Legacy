"""Module for server-side operations in CrawJUD-Bots."""

import json
import re
from typing import Any, Union

from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab


class DatabaseScheduler(Scheduler):
    """Scheduler that loads task schedules from the database."""

    @classmethod
    def fix_unicode(cls, text: str) -> str:
        """Fix unicode characters in the text."""
        return re.sub(r"u00([0-9a-fA-F]{2})", r"\\u00\1", text).encode().decode("unicode_escape")

    def __init__(self, *args: tuple, **kwargs: dict[str, any]) -> None:
        """Initialize the DatabaseScheduler.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self._schedule = {}

    def get_schedule(self) -> dict:
        """Load schedules from the database.

        Retrieves all schedule entries from the ScheduleModel and constructs
        a dictionary of ScheduleEntry objects.

        Returns:
            dict: A dictionary where the key is the task name and the value is the ScheduleEntry.

        """
        schedules = {}

        from app.models import CrontabModel, ScheduleModel

        db_entries: list[ScheduleModel] = ScheduleModel.query.all()
        for entry in db_entries:
            cron_args = {}
            old_cron_args: CrontabModel = entry.schedule
            cron_args_items = list(old_cron_args.__dict__.items())
            for key, value in cron_args_items:
                if (not key.startswith("_")) and key != "schedule" and key != "id":
                    cron_args.update({key: value})

            name_custom = DatabaseScheduler.fix_unicode(entry.name)
            schedules[entry.task] = ScheduleEntry(
                name=name_custom,
                task=entry.task,
                schedule=crontab(**cron_args),
                args=json.loads(entry.args or "[]"),
                kwargs=json.loads(entry.kwargs or "{}"),
            )
        return schedules

    @staticmethod
    def parse_cron(cron_string: str) -> dict[str, any]:
        """Parse a cron string into its respective fields.

        Args:
            cron_string (str): A string representing the cron schedule.

        Returns:
            dict: A dictionary with keys "minute", "hour", "day_of_month",
                  "month_of_year", and "day_of_week" mapping to their respective values
                  from the cron string.

        """
        fields = ["minute", "hour", "day_of_month", "month_of_year", "day_of_week"]
        cron_parts = cron_string.split()
        return dict(zip(fields, cron_parts, strict=False))

    @property
    def schedule(self) -> dict:
        """Get the current schedule.

        Syncs the schedule with the database and returns the updated schedule.

        Returns:
            dict: The current schedule dictionary.

        """
        self.sync()
        return self._schedule

    def sync(self) -> None:
        """Synchronize the schedules with the database.

        Updates the internal schedule dictionary by fetching the latest schedules
        from the database.
        """
        self._schedule = self.get_schedule()

    def tick(self) -> Union[int, Any]:  # noqa: ANN401
        """Process the schedules.

        This method is called continuously to ensure that the scheduler stays
        up-to-date with any changes in the schedules.

        Returns:
            float: The remaining time until the next scheduled task.

        """
        remaining_times = super().tick()
        self.sync()
        return remaining_times
