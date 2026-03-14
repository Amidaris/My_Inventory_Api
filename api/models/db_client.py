import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Index
from api.config.db import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    # NIP must be unique per owner; the global unique constraint is removed
    nip = Column(String, nullable=False, index=True)
    account_number = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    # composite unique constraint ensures every user can have their own set
    # of NIPs but prevents duplicates within the same account.
    __table_args__ = (
        Index('ix_client_user_active', 'user_id', 'active'),
        sa.UniqueConstraint('user_id', 'nip', name='uq_client_user_nip'),
    )
