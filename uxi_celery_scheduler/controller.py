from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from uxi_celery_scheduler.data_models import ScheduledTask
from uxi_celery_scheduler.db.models import CrontabSchedule, PeriodicTask


def schedule_task(
    session: Session,
    scheduled_task: ScheduledTask,
) -> PeriodicTask:
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
    return task


def delete_task(session: Session, periodic_task_id: int) -> PeriodicTask:
    try:
        task = session.query(PeriodicTask).get(periodic_task_id)
        session.delete(task)
        return task
    except NoResultFound:
        raise NoResultFound()
