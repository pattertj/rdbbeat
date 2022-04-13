from mock import patch

from celery_sqlalchemy_scheduler.controller import delete_task, schedule_task
from celery_sqlalchemy_scheduler.data_models import ScheduledTask
from celery_sqlalchemy_scheduler.db.models import CrontabSchedule, PeriodicTask


def test_schedule_task(scheduled_task):
    with patch("sqlalchemy.orm.Session") as mock_session:
        # Set up the mock_session
        mock_session.add.return_value = None

        actual_scheduled_task = schedule_task(mock_session, ScheduledTask.parse_obj(scheduled_task))

        expected_scheduled_task = PeriodicTask(
            crontab=CrontabSchedule(**scheduled_task["schedule"]),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )

        assert actual_scheduled_task.name == expected_scheduled_task.name
        assert actual_scheduled_task.task == expected_scheduled_task.task
        assert actual_scheduled_task.schedule == expected_scheduled_task.schedule


def test_delete_task(scheduled_task):
    with patch("sqlalchemy.orm.Session") as mock_session:
        # Set up the mock_session
        periodic_task_id = 1
        mock_session.query(PeriodicTask).get.return_value = PeriodicTask(
            crontab=CrontabSchedule(**scheduled_task["schedule"]),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )
        mock_session.delete.return_value = None
        # Delete task
        actual_deleted_task = delete_task(mock_session, periodic_task_id)

        expected_deleted_task = PeriodicTask(
            crontab=CrontabSchedule(**scheduled_task["schedule"]),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )

        assert actual_deleted_task.name == expected_deleted_task.name
        assert actual_deleted_task.task == expected_deleted_task.task
        assert actual_deleted_task.schedule == expected_deleted_task.schedule
