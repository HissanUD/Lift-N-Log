import sqlalchemy as sqa
from app.config import DATABASE_URL
from sqlalchemy.orm import declarative_base, sessionmaker



engine = sqa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
