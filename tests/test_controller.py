from typing import Dict

from mock import patch

from celery_sqlalchemy_scheduler.controller import schedule_task
from celery_sqlalchemy_scheduler.data_models import ScheduledTask
from celery_sqlalchemy_scheduler.db.models import CrontabSchedule, PeriodicTask


def test_schedule_task():
    with patch("sqlalchemy.orm.Session") as mock_session:
        # Set up the mock_session
        mock_session.add.return_value = None
        scheduled_task: Dict = {
            "name": "task_1",
            "task": "echo",
            "schedule": {
                "minute": "23",
                "hour": "00",
                "day_of_week": "2",
                "day_of_month": "23",
                "month_of_year": "12",
                "timezone": "UTC",
            },
        }

        schedule_task(mock_session, ScheduledTask.parse_obj(scheduled_task))

        actual_scheduled_task = mock_session.add.call_args[0][0]
        expected_scheduled_task = PeriodicTask(
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

        assert actual_scheduled_task.name == expected_scheduled_task.name
        assert actual_scheduled_task.task == expected_scheduled_task.task
        assert actual_scheduled_task.schedule == expected_scheduled_task.schedule
