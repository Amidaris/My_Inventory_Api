from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.models.db_client import Client
from api.models.client import ClientCreate, ClientUpdate
from api.models.db_location import LocationDB as LocationORM
from api.models.location import LocationCreate
from typing import List


def add_client(db: Session, client_data: ClientCreate, user_id: int) -> Client:
    # Check if client with this NIP already exists for this user
    existing = (
        db.query(Client)
        .filter(Client.nip == client_data.nip, Client.user_id == user_id)
        .first()
    )
    if existing:
        # caller (route) expects 409 on conflict; treat it as a business rule
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this NIP already exists"
        )

    client = Client(
        name=client_data.name,
        email=client_data.email,
        phone=client_data.phone,
        address=client_data.address,
        nip=client_data.nip,
        account_number=client_data.account_number,
        user_id=user_id
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


def list_clients(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0
):
    query = (
        db.query(Client)
        .filter(Client.user_id == user_id)
        .filter(Client.active == True)
        .order_by(Client.name.asc())
    )

    total = query.count()
    clients = query.offset(offset).limit(limit).all()

    return clients, total


def get_client(db: Session, client_id: int) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def soft_delete_client(db: Session, client: Client) -> None:
    try:
        client.active = False
        db.commit()
        db.refresh(client)
    except:
        db.rollback()
        raise


def get_client_by_id(db: Session, id: int) -> Client:
    return db.query(Client).filter(Client.id == id).first()


def is_nip_taken(
    db: Session,
    nip: str,
    user_id: int,
    exclude_id: int | None = None,
) -> bool:
    """Return True if *another* client belonging to the same user already
    uses the given NIP.

    ``exclude_id`` is used during updates so that the client being modified
    is not counted as a conflict.
    """

    query = db.query(Client).filter(
        Client.nip == nip,
        Client.user_id == user_id,
    )
    if exclude_id is not None:
        query = query.filter(Client.id != exclude_id)
    return query.first() is not None


def update_client_data(db: Session, db_client: Client, data: ClientUpdate) -> Client:
    db_client.name = data.name
    db_client.email = data.email
    db_client.phone = data.phone
    db_client.address = data.address
    db_client.nip = data.nip
    db_client.account_number = data.account_number

    db.commit()
    db.refresh(db_client)

    return db_client


def get_locations(db: Session, client_id: int) -> List[LocationORM]:
    return (
        db.query(LocationORM)
        .filter(LocationORM.client_id == client_id)
        .all()
    )


def add_location(db: Session, client: Client, location_data: LocationCreate) -> LocationORM:
    location = LocationORM(
        client_id=client.id,
        name=location_data.name,
        address=location_data.address,
        city=location_data.city,
        postal_code=location_data.postal_code,
        country=location_data.country,
        note=location_data.note,
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    return location


def get_location_by_id(db: Session, id: int) -> LocationORM | None:
    return db.query(LocationORM).filter(LocationORM.id == id).first()


def update_location(db: Session, location: LocationORM, data: LocationCreate) -> LocationORM:
    location.name = data.name
    location.address = data.address
    location.city = data.city
    location.postal_code = data.postal_code
    location.country = data.country
    location.note = data.note

    db.commit()
    db.refresh(location)

    return location


def delete_location(db: Session, location: LocationORM) -> None:
    try:
        db.delete(location)
        db.commit()
    except:
        db.rollback()
        raise
