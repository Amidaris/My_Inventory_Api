from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.config.security import ALGORITHM, oauth2_scheme
from api.config.settings import settings
from api.config.db import get_db
from api.services.user_service import get_user
from api.models.db_user import UserDB
from api.models.token import TokenData

SECRET_KEY = settings.SECRET_KEY.get_secret_value()


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"
                                                   })
    try:
        payload = jwt.decode(token, SECRET_KEY,
                             algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int | None = payload.get("user_id")

        if username is None:
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            user_id=user_id    
        )

    except JWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
        current_user: UserDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user
