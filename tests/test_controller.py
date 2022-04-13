from typing import Dict

import pytest
from mock import patch
from sqlalchemy.orm.exc import NoResultFound

from celery_sqlalchemy_scheduler.controller import (
    schedule_task,
    update_period_task,
    update_task_enable_status,
)
from celery_sqlalchemy_scheduler.data_models import ScheduledTask
from celery_sqlalchemy_scheduler.db.models import CrontabSchedule, PeriodicTask
from celery_sqlalchemy_scheduler.exceptions import PeriodicTaskNotFound


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

        schedule_task(mock_session, ScheduledTask.parse_obj(scheduled_task))

        actual_scheduled_task = mock_session.add.call_args[0][0]
        expected_scheduled_task = PeriodicTask(
            crontab=CrontabSchedule(
                minute=schedule["minute"],
                hour=schedule["hour"],
                day_of_week=schedule["day_of_week"],
                day_of_month=schedule["day_of_month"],
                month_of_year=schedule["month_of_year"],
                timezone=schedule["timezone"],
            ),
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )

        assert actual_scheduled_task.name == expected_scheduled_task.name
        assert actual_scheduled_task.task == expected_scheduled_task.task
        assert actual_scheduled_task.schedule == expected_scheduled_task.schedule


def test_update_task_enable_status():
    with patch("sqlalchemy.orm.Session") as mock_session:
        schedule: Dict = {
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
        schedule = CrontabSchedule(**schedule)

        mock_session.query(PeriodicTask).get.return_value = PeriodicTask(
            enabled=True,
            crontab=schedule,
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )
        periodic_task_id = 1

        updated_task = update_task_enable_status(mock_session, False, periodic_task_id)

        assert updated_task.enabled is False


def test_update_task_enabled_status_fail():

    with patch("sqlalchemy.orm.Session") as mock_session:
        with pytest.raises(PeriodicTaskNotFound):

            mock_session.query(PeriodicTask).get.side_effect = NoResultFound()
            periodic_task_id = 1
            update_task_enable_status(mock_session, False, periodic_task_id)


def test_update_periodic_task():
    with patch("sqlalchemy.orm.Session") as mock_session:
        schedule: Dict = {
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
        new_schedule: Dict = {
            "minute": "24",
            "hour": "01",
            "day_of_week": "3",
            "day_of_month": "24",
            "month_of_year": "11",
            "timezone": "UTC",
        }
        new_scheduled_task: Dict = {
            "name": "task_2",
            "task": "echo2",
            "schedule": new_schedule,
        }
        schedule = CrontabSchedule(**schedule)
        new_schedule = CrontabSchedule(**new_schedule)

        periodic_task = PeriodicTask(
            crontab=schedule,
            name=scheduled_task["name"],
            task=scheduled_task["task"],
        )
        updated_task = PeriodicTask(
            crontab=new_schedule,
            name=new_scheduled_task["name"],
            task=new_scheduled_task["task"],
        )

        mock_session.query(PeriodicTask).get.return_value = periodic_task
        periodic_task_id = 1

        updated_db_task = update_period_task(
            mock_session, ScheduledTask.parse_obj(new_scheduled_task), periodic_task_id)

        assert mock_session.query(PeriodicTask).get.call_count == 1
        assert updated_task.name == updated_db_task.name
