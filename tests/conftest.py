import pytest


@pytest.fixture
def scheduled_task():
    schedule = {
        "minute": "23",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
        "timezone": "UTC",
    }
    scheduled_task = {
        "name": "task_1",
        "task": "echo",
        "schedule": schedule,
    }
    return scheduled_task
