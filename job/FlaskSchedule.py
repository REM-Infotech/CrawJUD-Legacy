"""
Module for server-side operations in CrawJUD-Bots.
"""

import json

from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab


class DatabaseScheduler(Scheduler):
    """
    Scheduler that loads task schedules from the database.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the DatabaseScheduler.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self._schedule = {}

    def get_schedule(self):
        """
        Load schedules from the database.

        Retrieves all schedule entries from the ScheduleModel and constructs
        a dictionary of ScheduleEntry objects.

        Returns:
            dict: A dictionary where the key is the task name and the value is the ScheduleEntry.
        """
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
        """
        Parse a cron string into its respective fields.

        Args:
            cron_string (str): A string representing the cron schedule.

        Returns:
            dict: A dictionary with keys "minute", "hour", "day_of_month",
                  "month_of_year", and "day_of_week" mapping to their respective values
                  from the cron string.
        """
        fields = ["minute", "hour", "day_of_month", "month_of_year", "day_of_week"]
        cron_parts = cron_string.split()
        return {field: value for field, value in zip(fields, cron_parts)}

    @property
    def schedule(self):
        """
        Get the current schedule.

        Syncs the schedule with the database and returns the updated schedule.

        Returns:
            dict: The current schedule dictionary.
        """
        self.sync()
        return self._schedule

    def sync(self):
        """
        Synchronize the schedules with the database.

        Updates the internal schedule dictionary by fetching the latest schedules
        from the database.
        """
        self._schedule = self.get_schedule()

    def tick(self):
        """
        Process the schedules.

        This method is called continuously to ensure that the scheduler stays
        up-to-date with any changes in the schedules.

        Returns:
            float: The remaining time until the next scheduled task.
        """
        remaining_times = super().tick()
        self.sync()
        return remaining_times
