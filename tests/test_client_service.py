import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from api.config.db import Base
from api.models.db_user import UserDB
from api.models.client import ClientCreate
from api.services.client_service import add_client
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


def test_nip_uniqueness_scope(db_session):
    # two users in the database
    user1 = UserDB(username="u1", email="u1@test.local",
                   hashed_password="pwd1")
    user2 = UserDB(username="u2", email="u2@test.local",
                   hashed_password="pwd2")
    db_session.add_all([user1, user2])
    db_session.commit()

    client_data = make_client_data()

    # first client for user1 should be created successfully
    c1 = add_client(db_session, client_data, user_id=user1.id)
    assert c1.user_id == user1.id

    # trying to create the same NIP again for the same user should raise a conflict
    with pytest.raises(HTTPException) as excinfo:
        add_client(db_session, client_data, user_id=user1.id)
    assert excinfo.value.status_code == 409

    # but the identical NIP for a different user is allowed
    c2 = add_client(db_session, client_data, user_id=user2.id)
    assert c2.user_id == user2.id




