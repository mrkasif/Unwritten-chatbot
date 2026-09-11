import os
from contextlib import contextmanager

from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine

from backend import models  # noqa: F401

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("CHAT_DB_PATH", os.path.join(BASE_DIR, "chat.db"))
SQLITE_URL = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False}

engine = create_engine(SQLITE_URL, echo=False, connect_args=connect_args)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@contextmanager
def db_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    finally:
        session.close()