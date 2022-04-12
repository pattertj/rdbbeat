import pytest
from pydantic import ValidationError

from celery_sqlalchemy_scheduler.data_models import Schedule


def test_schedule_pass():
    schedule = {
        "minute": "23",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    Schedule.parse_obj(schedule)


def test_schedule_invalid_minute_type():
    schedule = {
        "minute": "minute",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValueError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_minute():
    schedule = {
        "minute": "200",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValidationError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_hour_type():
    schedule = {
        "minute": "23",
        "hour": "h",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValueError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_hour():
    schedule = {
        "minute": "23",
        "hour": "0055",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValidationError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_day_of_week_type():
    schedule = {
        "minute": "23",
        "hour": "00",
        "day_of_week": "day",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValueError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_day_of_week():
    schedule = {
        "minute": "23",
        "hour": "0055",
        "day_of_week": "22",
        "day_of_month": "23",
        "month_of_year": "12",
    }
    with pytest.raises(ValidationError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_day_of_month_type():
    schedule = {
        "minute": "23",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "day",
        "month_of_year": "12",
    }
    with pytest.raises(ValueError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_day_of_month():
    schedule = {
        "minute": "23",
        "hour": "0055",
        "day_of_week": "2",
        "day_of_month": "32",
        "month_of_year": "12",
    }
    with pytest.raises(ValidationError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_month_type():
    schedule = {
        "minute": "23",
        "hour": "00",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "month",
    }
    with pytest.raises(ValueError):
        Schedule.parse_obj(schedule)


def test_schedule_invalid_month():
    schedule = {
        "minute": "23",
        "hour": "0055",
        "day_of_week": "2",
        "day_of_month": "23",
        "month_of_year": "0",
    }
    with pytest.raises(ValidationError):
        Schedule.parse_obj(schedule)
