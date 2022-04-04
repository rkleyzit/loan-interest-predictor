import importlib
import os
from pathlib import Path
from typing import Optional, Iterable
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session

Model = declarative_base(name='Model')
session: Optional[Session] = None


def get_cnx_str_uri() -> str:
    """Returns the connection string for the app database"""
    """TODO: Sqlite is not a production db. Switch to a better solution"""
    db_path = Path.joinpath(Path(__file__).parent.parent, 'app.db')
    return f'sqlite:///{db_path}'


def import_models():
    """Dynamically import all models under the 'models' directory"""
    path = Path('utils').joinpath('models')
    here = Path(__file__).parent.parent.joinpath(path)
    models = os.listdir(here)
    for model in models:
        importlib.import_module(f"{'.'.join(path.parts)}.{model.split('.')[0]}")


def init_db():
    """Initialize Sqlalchemy tables"""
    global Model, session

    cnx_uri = get_cnx_str_uri()

    connect_args = {'check_same_thread': False}  # this is only needed for sqlite
    engine = create_engine(cnx_uri, connect_args=connect_args)

    import_models()

    Model.metadata.create_all(bind=engine)
    session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def attempt_commit():
    """Commit pending updates to db"""
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise Exception('Failed to commit')


def insert(obj):
    """Insert new row(s) to the db session"""
    if not isinstance(obj, Iterable):
        obj = [obj]

    for o in obj:
        session.add(o)

    session.flush()
