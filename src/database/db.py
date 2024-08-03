"""
This module contains the database connection and session management code.
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    The get_db function opens a new database connection if there is none yet
    for the current application context. It will also create the database
    tables we need for our models if they don't exist yet.

    :return: A database session
    """
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
