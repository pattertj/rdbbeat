import datetime as dt
from typing import Any, Dict, Union

import pytz
import sqlalchemy as sa
from celery import schedules
from celery.utils.log import get_logger
from sqlalchemy import MetaData, func
from sqlalchemy.engine import Engine
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, class_mapper, foreign, relationship, remote
from sqlalchemy.sql import insert, select, update

from celery_sqlalchemy_scheduler.tzcrontab import TzAwareCrontab

logger = get_logger("celery_sqlalchemy_scheduler.db.models")

Base: Any = declarative_base(metadata=MetaData(schema="scheduler"))


def cronexp(field: str) -> str:
    """Representation of cron expression."""
    return field and str(field).replace(" ", "") or "*"


class ModelMixin:
    @classmethod
    def create(cls, **kw: Dict) -> "ModelMixin":
        return cls(**kw)

    def update(self, **kw: Dict) -> "ModelMixin":
        for attr, value in kw.items():
            setattr(self, attr, value)
        return self


class IntervalSchedule(Base, ModelMixin):
    __tablename__ = "celery_interval_schedule"

    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    MICROSECONDS = "microseconds"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    every = sa.Column(sa.Integer, nullable=False)
    period = sa.Column(sa.String(24))

    def __repr__(self) -> str:
        if self.every == 1:
            return f"every {self.period_singular}"
        return f"every {self.every} {self.period}"

    @property
    def schedule(self) -> schedules.schedule:
        return schedules.schedule(
            dt.timedelta(**{self.period: self.every}),
            # nowfun=lambda: make_aware(now())
            # nowfun=dt.datetime.now
        )

    @classmethod
    def from_schedule(
        cls, session: Session, schedule: schedules.schedule, period: str = SECONDS
    ) -> "IntervalSchedule":
        every = max(schedule.run_every.total_seconds(), 0)
        model = session.query(IntervalSchedule).filter_by(every=every, period=period).first()
        if not model:
            model = cls(every=every, period=period)
            session.add(model)
            session.commit()
        return model

    @property
    def period_singular(self) -> str:
        return self.period[:-1]


class CrontabSchedule(Base, ModelMixin):
    __tablename__ = "celery_crontab_schedule"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    minute = sa.Column(sa.String(60 * 4), default="*")
    hour = sa.Column(sa.String(24 * 4), default="*")
    day_of_week = sa.Column(sa.String(64), default="*")
    day_of_month = sa.Column(sa.String(31 * 4), default="*")
    month_of_year = sa.Column(sa.String(64), default="*")
    timezone = sa.Column(sa.String(64), default="UTC")

    def __repr__(self) -> str:
        return (
            f"{cronexp(self.minute)} {cronexp(self.hour)} "
            f"{cronexp(self.day_of_week)} {cronexp(self.day_of_month)} "
            f"{cronexp(self.month_of_year)} (m/h/d/dM/MY) {str(self.timezone)}"
        )

    @property
    def schedule(self) -> TzAwareCrontab:
        return TzAwareCrontab(
            minute=self.minute,
            hour=self.hour,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year,
            tz=pytz.timezone(self.timezone),
        )

    @classmethod
    def from_schedule(cls, session: Session, schedule: schedules.crontab) -> "CrontabSchedule":
        spec = {
            "minute": schedule._orig_minute,
            "hour": schedule._orig_hour,
            "day_of_week": schedule._orig_day_of_week,
            "day_of_month": schedule._orig_day_of_month,
            "month_of_year": schedule._orig_month_of_year,
        }
        if schedule.tz:
            spec.update({"timezone": schedule.tz.zone})
        model = session.query(CrontabSchedule).filter_by(**spec).first()
        if not model:
            model = cls(**spec)
            session.add(model)
            session.commit()
        return model


class SolarSchedule(Base, ModelMixin):
    __tablename__ = "celery_solar_schedule"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    event = sa.Column(sa.String(24))
    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())

    @property
    def schedule(self) -> schedules.solar:
        return schedules.solar(self.event, self.latitude, self.longitude, nowfun=dt.datetime.now)

    @classmethod
    def from_schedule(cls, session: Session, schedule: schedules.solar) -> "SolarSchedule":
        spec = {"event": schedule.event, "latitude": schedule.lat, "longitude": schedule.lon}
        model = session.query(SolarSchedule).filter_by(**spec).first()
        if not model:
            model = cls(**spec)
            session.add(model)
            session.commit()
        return model

    def __repr__(self) -> str:
        return f"{self.event} ({self.latitude}, {self.longitude})"


class PeriodicTaskChanged(Base, ModelMixin):
    """Helper table for tracking updates to periodic tasks."""

    __tablename__ = "celery_periodic_task_changed"

    id = sa.Column(sa.Integer, primary_key=True)
    last_update = sa.Column(sa.DateTime(timezone=True), nullable=False, default=dt.datetime.now)

    @classmethod
    def changed(
        cls, mapper: class_mapper, connection: Engine.connect, target: "PeriodicTask"
    ) -> None:
        """
        :param mapper: the Mapper which is the target of this event
        :param connection: the Connection being used
        :param target: the mapped instance being persisted
        """
        if not target.no_changes:
            cls.update_changed(mapper, connection, target)

    @classmethod
    def update_changed(
        cls, mapper: class_mapper, connection: Engine.connect, target: "PeriodicTask"
    ) -> None:
        """
        :param mapper: the Mapper which is the target of this event
        :param connection: the Connection being used
        :param target: the mapped instance being persisted
        """
        s = connection.execute(
            select([PeriodicTaskChanged]).where(PeriodicTaskChanged.id == 1).limit(1)
        )
        if not s:
            s = connection.execute(insert(PeriodicTaskChanged), last_update=dt.datetime.now())
        else:
            s = connection.execute(
                update(PeriodicTaskChanged)
                .where(PeriodicTaskChanged.id == 1)
                .values(last_update=dt.datetime.now())
            )

    @classmethod
    def last_change(cls, session: Session) -> Union[dt.datetime, None]:
        periodic_tasks = session.query(PeriodicTaskChanged).get(1)
        if periodic_tasks:
            return periodic_tasks.last_update
        return None


class PeriodicTask(Base, ModelMixin):
    __tablename__ = "celery_periodic_task"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    # name
    name = sa.Column(sa.String(255), unique=True)
    # task name
    task = sa.Column(sa.String(255))

    # not use ForeignKey
    interval_id = sa.Column(sa.Integer)
    interval = relationship(
        IntervalSchedule,
        uselist=False,
        primaryjoin=foreign(interval_id) == remote(IntervalSchedule.id),
    )

    crontab_id = sa.Column(sa.Integer)
    crontab = relationship(
        CrontabSchedule,
        uselist=False,
        primaryjoin=foreign(crontab_id) == remote(CrontabSchedule.id),
    )

    solar_id = sa.Column(sa.Integer)
    solar = relationship(
        SolarSchedule, uselist=False, primaryjoin=foreign(solar_id) == remote(SolarSchedule.id)
    )

    args = sa.Column(sa.Text(), default="[]")
    kwargs = sa.Column(sa.Text(), default="{}")
    # queue for celery
    queue = sa.Column(sa.String(255))
    # exchange for celery
    exchange = sa.Column(sa.String(255))
    # routing_key for celery
    routing_key = sa.Column(sa.String(255))
    priority = sa.Column(sa.Integer())
    expires = sa.Column(sa.DateTime(timezone=True))

    # 只执行一次
    one_off = sa.Column(sa.Boolean(), default=False)
    start_time = sa.Column(sa.DateTime(timezone=True))
    enabled = sa.Column(sa.Boolean(), default=True)
    last_run_at = sa.Column(sa.DateTime(timezone=True))
    total_run_count = sa.Column(sa.Integer(), nullable=False, default=0)
    # 修改时间
    date_changed = sa.Column(sa.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    description = sa.Column(sa.Text(), default="")

    no_changes = False

    def __repr__(self) -> str:
        fmt = "{self.name}: {{no schedule}}"
        if self.interval:
            fmt = "{self.name}: {self.interval}"
        elif self.crontab:
            fmt = "{self.name}: {self.crontab}"
        elif self.solar:
            fmt = "{self.name}: {self.solar}"
        return fmt

    @property
    def task_name(self) -> str:
        return self.task

    @task_name.setter
    def task_name(self, value: str) -> None:
        self.task = value

    @property
    def schedule(self) -> schedules.schedule:
        if self.interval:
            return self.interval.schedule
        elif self.crontab:
            return self.crontab.schedule
        elif self.solar:
            return self.solar.schedule
        raise ValueError(f"{self.name} schedule is None!")


listen(PeriodicTask, "after_insert", PeriodicTaskChanged.update_changed)
listen(PeriodicTask, "after_delete", PeriodicTaskChanged.update_changed)
listen(PeriodicTask, "after_update", PeriodicTaskChanged.changed)
listen(IntervalSchedule, "after_insert", PeriodicTaskChanged.update_changed)
listen(IntervalSchedule, "after_delete", PeriodicTaskChanged.update_changed)
listen(IntervalSchedule, "after_update", PeriodicTaskChanged.update_changed)
listen(CrontabSchedule, "after_insert", PeriodicTaskChanged.update_changed)
listen(CrontabSchedule, "after_delete", PeriodicTaskChanged.update_changed)
listen(CrontabSchedule, "after_update", PeriodicTaskChanged.update_changed)
listen(SolarSchedule, "after_insert", PeriodicTaskChanged.update_changed)
listen(SolarSchedule, "after_delete", PeriodicTaskChanged.update_changed)
listen(SolarSchedule, "after_update", PeriodicTaskChanged.update_changed)
