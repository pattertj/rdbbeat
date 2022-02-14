from contextlib import contextmanager
from typing import Any, Dict

from kombu.utils.compat import register_after_fork
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

ModelBase = declarative_base()


@contextmanager
def session_cleanup(session: Session) -> Any:
    try:
        yield
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _after_fork_cleanup_session(session: Session) -> None:
    session._after_fork()


class SessionManager(object):
    """Manage SQLAlchemy sessions."""

    def __init__(self) -> None:
        self._engines: Dict = {}
        self._sessions: Dict = {}
        self.forked: bool = False
        self.prepared: bool = False
        if register_after_fork is not None:
            register_after_fork(self, _after_fork_cleanup_session)

    def _after_fork(self) -> None:
        self.forked = True

    def get_engine(self, dburi: str, **kwargs: Any) -> Any:
        if self.forked:
            try:
                return self._engines[dburi]
            except KeyError:
                engine = self._engines[dburi] = create_engine(dburi, **kwargs)
                return engine
        else:
            return create_engine(dburi, poolclass=NullPool)

    def create_session(self, dburi: str, short_lived_sessions: bool = False, **kwargs: Any) -> Any:
        engine = self.get_engine(dburi, **kwargs)
        if self.forked:
            if short_lived_sessions or dburi not in self._sessions:
                self._sessions[dburi] = sessionmaker(bind=engine)
            return engine, self._sessions[dburi]
        else:
            return engine, sessionmaker(bind=engine)

    def prepare_models(self, engine: Any) -> None:
        if not self.prepared:
            ModelBase.metadata.create_all(engine)
            self.prepared = True

    def session_factory(self, dburi: str, **kwargs: Any) -> Session:
        engine, session = self.create_session(dburi, **kwargs)
        self.prepare_models(engine)
        return session()
