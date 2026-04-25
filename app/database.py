import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)

# A factory for database sections
# A section is a unit of work, a connection to the database that you open, do things with, and close
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# fastAPI dependency that opens a session for each request and closes it when the request finishes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()