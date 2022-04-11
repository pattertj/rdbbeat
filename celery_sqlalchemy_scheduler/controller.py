from typing import Union

from sqlalchemy.orm import Session

from .db.models import CrontabSchedule, PeriodicTask
from .data_models import ScheduledTask


def schedule_task(
    session: Session,
    scheduled_task: ScheduledTask,
) -> None:
    """
    Add
    """
    schedule = CrontabSchedule(
        minute=scheduled_task.schedule.minute,
        hour=scheduled_task.schedule.hour,
        day_of_week=scheduled_task.schedule.day_of_week,
        day_of_month=scheduled_task.schedule.day_of_month,
        month_of_year=scheduled_task.schedule.month_of_year,
    )
    task = PeriodicTask(
        crontab=schedule,
        name=scheduled_task.name,
        task=scheduled_task.task,
    )
    session.add(task)
