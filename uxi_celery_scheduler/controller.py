from sqlalchemy.orm import Session

from uxi_celery_scheduler.data_models import ScheduledTask
from uxi_celery_scheduler.db.models import CrontabSchedule, PeriodicTask


def schedule_task(
    session: Session,
    scheduled_task: ScheduledTask,
) -> None:
    """
    Schedule a task by adding a periodic task entry.
    """
    schedule = CrontabSchedule(**scheduled_task.schedule.dict())
    task = PeriodicTask(
        crontab=schedule,
        name=scheduled_task.name,
        task=scheduled_task.task,
    )
    session.add(task)
