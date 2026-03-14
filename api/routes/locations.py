from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session

from api.config.db import get_db
from api.models.db_user import UserDB
from api.services.auth_service import get_current_active_user
from api.services.client_service import get_location_by_id, get_client_by_id, update_location, delete_location
from api.models.location import LocationCreate, LocationRead


router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


@router.put("/{id}",
            response_model=LocationRead,
            status_code=status.HTTP_200_OK,
            summary="Update location",
            description="""
        Update location data.

            - Requires authentication (JWT).
            - Location must belong to a client owned by the authenticated user.
            - Returns 200 with the updated location.
            - Raises 404 if the location is not found.
            - Raises 403 if the location belongs to another user.
        """,
            )
async def update_location_endpoint(
    id: int,
    data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    loc = get_location_by_id(db, id)

    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    client = get_client_by_id(db, loc.clientId)

    if not client or client.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = update_location(db, loc, data)
    return updated


@router.delete("/{id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete location",
               description="""
        Delete a client location.

            - Requires authentication (JWT).
            - Location must belong to a client owned by the authenticated user.
            - Returns 204 on success.
            - Raises 404 if the location is not found.
            - Raises 403 if the location belongs to another user.
        """,
               )
async def delete_location_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    loc = get_location_by_id(db, id)

    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    client = get_client_by_id(db, loc.clientId)

    if not client or client.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    delete_location(db, loc)
    return None
