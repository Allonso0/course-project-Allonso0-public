from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.secrets import secrets_manager

database_url = secrets_manager.get("DATABASE_URL", "sqlite:///./reading_list.db")

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.domain.database_models import Base

    Base.metadata.create_all(bind=engine)
