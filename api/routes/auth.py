from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from api.services.token_service import create_access_token
from api.services.user_service import authenticate_user, create_user, get_user
from api.models.token import Token, RefreshTokenRequest, AccessTokenResponse
from api.models.user import RegisterRequest, RegisterResponse
from api.config.security import ALGORITHM
from api.config.settings import settings
from api.config.db import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id
            }
        )
    return Token(access_token=access_token)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(request.refresh_token,
                             settings.SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user = get_user(db, username=username)
    if user is None or user.disabled:
        raise HTTPException(status_code=401, detail="Invalid user")
    

    new_access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id
            }
        )
    return AccessTokenResponse(access_token=new_access_token)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = create_user(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )

    return RegisterResponse(
        id=user.id,
        email=user.email,
        role=user.role,
    )
