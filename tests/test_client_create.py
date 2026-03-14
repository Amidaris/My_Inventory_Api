import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from api.config.db import Base
from api.models.db_user import UserDB
from api.models.client import ClientCreate
from fastapi import HTTPException


@pytest.fixture
def db_session():
    # in-memory SQLite avoids touching real database
    engine = sa.create_engine("sqlite:///:memory:", echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()
    yield session
    session.close()


def make_client_data(nip: str = "1234563218") -> ClientCreate:
    return ClientCreate(
        name="Test client",
        email="test@example.com",
        phone=None,
        address="Some address",
        nip=nip,
        accountNumber=None,
    )



