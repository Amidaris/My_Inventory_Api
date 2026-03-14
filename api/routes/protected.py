
from fastapi import Depends, APIRouter
from api.models.user import User
from api.models.db_user import UserDB
from api.services.auth_service import get_current_active_user


router = APIRouter()


@router.get("/protected", response_model=User)
async def protected_route(current_user: UserDB = Depends(get_current_active_user)):
    return current_user
