from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from celery_sqlalchemy_scheduler.exceptions import PeriodicTaskNotFound

from .data_models import ScheduledTask
from .db.models import CrontabSchedule, PeriodicTask


def create_or_update_task(
    session: Session,
    scheduled_task: ScheduledTask,
    periodic_task_id: int = None,
) -> PeriodicTask:
    """
    Try to update a task if it exists, otherwise create a new task.
    """
    if periodic_task_id is not None:
        return _update_period_task(session, periodic_task_id, scheduled_task)

    schedule = CrontabSchedule(**scheduled_task.schedule.dict())
    task = PeriodicTask(
        crontab=schedule,
        name=scheduled_task.name,
        task=scheduled_task.task,
    )
    session.add(task)


def update_task_enable_status(
    session: Session,
    enable_status: bool,
    periodic_task_id: int,
) -> None:
    """
    Update task enable status (if task is enabled or disabled).
    """
    try:
        task = session.query(PeriodicTask).get(periodic_task_id)
        task.enabled = enable_status
        session.flush()

    except NoResultFound as e:
        raise PeriodicTaskNotFound from e

    return task


def _update_period_task(
    session: Session,
    scheduled_task: ScheduledTask,
    periodic_task_id: int,
) -> PeriodicTask:
    """
    Update the details of a task including the crontab schedule
    """
    try:
        task = session.query(PeriodicTask).get(periodic_task_id)

        schedule = CrontabSchedule(**scheduled_task.schedule.dict())
        task.crontab = schedule
        task.name = (scheduled_task.name,)
        task.task = scheduled_task.task
        session.flush()

    except NoResultFound as e:
        raise PeriodicTaskNotFound from e

    return task
