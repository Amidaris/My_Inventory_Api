
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from collections.abc import Generator
from api.config.settings import settings

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models so Alembic can detect them 
from api.models import db_user, db_client, db_product, db_product_category, db_document

