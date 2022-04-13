from typing import Dict

from mock import patch

from celery_sqlalchemy_scheduler.controller import schedule_task, delete_task
from celery_sqlalchemy_scheduler.data_models import ScheduledTask
from celery_sqlalchemy_scheduler.db.models import CrontabSchedule, PeriodicTask


def test_schedule_task():
    with patch("sqlalchemy.orm.Session") as mock_session:
        # Set up the mock_session
        mock_session.add.return_value = None
        schedule = {
                "minute": "23",
                "hour": "00",
                "day_of_week": "2",
                "day_of_month": "23",
                "month_of_year": "12",
                "timezone": "UTC",
        }
        scheduled_task: Dict = {
            "name": "task_1",
            "task": "echo",
            "schedule": schedule,
        }

        actual_scheduled_task = schedule_task(mock_session, ScheduledTask.parse_obj(scheduled_task))

        expected_scheduled_task = PeriodicTask(
            crontab=CrontabSchedule(
                minute=schedule["minute"],
                hour=schedule["hour"],
                day_of_week=schedule["day_of_week"],
                day_of_month=schedule["day_of_month"],
                month_of_year=schedule["month_of_year"],
                timezone=schedule["timezone"]
            ),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )

        assert actual_scheduled_task.name == expected_scheduled_task.name
        assert actual_scheduled_task.task == expected_scheduled_task.task
        assert actual_scheduled_task.schedule == expected_scheduled_task.schedule

def test_delete_task():
    with patch("sqlalchemy.orm.Session") as mock_session:
        schedule = {
            "minute": "23",
            "hour": "00",
            "day_of_week": "2",
            "day_of_month": "23",
            "month_of_year": "12",
            "timezone": "UTC",
        }
        scheduled_task: Dict = {
            "name": "task_1",
            "task": "echo",
            "schedule": schedule,
        }
        # Set up the mock_session
        periodic_task_id = 1
        schedule = CrontabSchedule(**schedule)
        mock_session.query(PeriodicTask).get.return_value = PeriodicTask(
            crontab=schedule,
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )
        mock_session.delete.return_value = None
        # Delete task
        actual_deleted_task = delete_task(mock_session, periodic_task_id)

        expected_deleted_task = PeriodicTask(
            crontab=CrontabSchedule(
                minute=scheduled_task["schedule"]["minute"],
                hour=scheduled_task["schedule"]["hour"],
                day_of_week=scheduled_task["schedule"]["day_of_week"],
                day_of_month=scheduled_task["schedule"]["day_of_month"],
                month_of_year=scheduled_task["schedule"]["month_of_year"],
                timezone=scheduled_task["schedule"]["timezone"]
            ),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )

        assert actual_deleted_task.name == expected_deleted_task.name
        assert actual_deleted_task.task == expected_deleted_task.task
        assert actual_deleted_task.schedule == expected_deleted_task.schedule
