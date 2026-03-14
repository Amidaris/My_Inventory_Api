from fastapi import Depends, APIRouter, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Annotated

from api.config.db import get_db
from api.models.db_user import UserDB
from api.services.auth_service import get_current_active_user
from api.services.client_service import add_client, list_clients, get_client, soft_delete_client, get_client_by_id, update_client_data, is_nip_taken, get_locations, add_location
from api.models.client import ClientCreate, ClientRead, ClientNIPRequest, ClientListResponse, ClientUpdate
from api.models.location import LocationListResponse, LocationCreate, LocationRead


import httpx
import datetime


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=ClientRead,
             summary="Create a new client",
             description="""
Create a new client.

    - Requires authentication.
    - Email and phone are empty by default and can be filled later.
    - Returns 201 with the created client.
    - Raises 409 if client with the same NIP already exists for the authenticated user.
""")
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    # add_client now raises HTTPException(409) when the nip is duplicated for
    # the authenticated user, so we can simply propagate that.
    db_client = add_client(db, client, user_id=current_user.id)
    return db_client


@router.post("/by-nip",
             status_code=status.HTTP_201_CREATED,
             response_model=ClientRead,
             summary="Create a new client by NIP",
             description="""
Create a new client by providing only the NIP number.  

    - Requires authentication.
    - Fetches client data from the external API (MF.gov.pl).
    - Email and phone are empty by default and can be filled later.
    - Returns 201 with the created client.
    - Raises 404 if the client is not found in the external API.
    - Raises 409 if a client with the same NIP already exists for the authenticated user.

""")
async def create_client_by_nip(
    request_data: ClientNIPRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    nip = request_data.nip.replace("-", "").strip()
    date = datetime.date.today().strftime("%Y-%m-%d")

    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={date}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Unable to fetch data for NIP {nip}"
        )

    api_data = resp.json().get("result", {}).get("subject", {})
    if not api_data:
        raise HTTPException(
            status_code=404, detail="Client not found in external API")

    accounts = api_data.get("accountNumbers") or []
    account_number = accounts[0] if accounts else None

    client_create = ClientCreate(
        name=api_data.get("name", ""),
        email=None,  # fill later
        phone=None,  # fill later
        account_number=account_number,
        address=api_data.get("residenceAddress", ""),
        nip=api_data.get("nip", nip)
    )

    # add_client already returns 409 if the nip exists for this user; let
    # that bubble up. We don't expect any other exceptions here.
    db_client = add_client(db, client_create, owner_id=current_user.id)
    return db_client


@router.get(
    "/",
    response_model=ClientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List clients of the current user",
    description="""
Returns a paginated list of clients belonging to the authenticated user.

- Requires JWT authentication.
- Sorted by name ascending.
- Supports pagination: limit (default 20), offset (default 0).
- Returns only active clients.
"""
)
def get_clients(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    clients, total = list_clients(
        db=db,
        owner_id=current_user.id,
        limit=limit,
        offset=offset
    )

    return ClientListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=clients
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete client",
    description="""
Soft delete client by setting active = false.

- Requires authentication.
- Returns 204 on success.
- Raises 404 if client does not exist.
- Raises 403 if client is inactive or belongs to another user.
"""
)
def delete_client(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    client = get_client(db, id)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if client.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not client.active:
        raise HTTPException(
            status_code=403,
            detail="Client is already inactive"
        )

    soft_delete_client(db, client)
    return None


@router.put("/{id}",
            response_model=ClientRead,
            status_code=status.HTTP_200_OK,
            summary="Update client",
            description="""
Update client data.

    - Requires authentication.
    - Returns 200 with the updated client.
    - Raises 404 if the client is not found.
    - Raises 403 if the client is inactive.
    - Raises 409 if the client with the same NIP already exists for that user.
    - Raises 403 if the user is not the owner of the client.
    """,
            )
async def update_client(
    id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    db_client = get_client_by_id(db, id)
    # 404 – client not exist
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    # 403 – forbidden
    if db_client.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # block inactive client
    if not db_client.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive client cannot be edited"
        )
    # 409 – client with this NIP already exists for the same user
    if is_nip_taken(db, data.nip, current_user.id, exclude_id=db_client.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this NIP already exists"
        )

    db_client = update_client_data(db, db_client, data)
    return db_client


@router.get("/{id}/locations",
            response_model=LocationListResponse,
            status_code=status.HTTP_200_OK,
            summary="Get client locations",
            description="""
Get client locations.

    - Requires authentication.
    - Returns 200 with the client locations.
    - Raises 404 if the client is not found.
    - Raises 403 if the user is not the owner of the client..
    """,
            )
async def get_client_locations(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    client = get_client_by_id(db, id)

    # 404 – client not exist
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # 403 – Forbidden
    if client.owner_id != current_user.id:
        raise HTTPException(status_code=403)

    client_locations = get_locations(db, client.id)
    return LocationListResponse(
        items=client_locations
    )


@router.post(
    "/{client_id}/locations",
    status_code=status.HTTP_201_CREATED,
    response_model=LocationRead,
    summary="Create a new client location",
    description="""
    Create a new client location.

        - Requires authentication.
        - Returns 201 with the created location.
        - Raises 404 if the client is not found.
        - Raises 403 if the user is not the owner of the client.
        """,
)
async def add_client_location(
    client_id: int,
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    client = get_client_by_id(db, client_id)

    # 404 – client not exist
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # 403 – Forbidden
    if client.owner_id != current_user.id:
        raise HTTPException(status_code=403)
    new_location = add_location(db, client, location_data)
    return new_location
