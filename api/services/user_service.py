from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.models.db_user import UserDB
from api.utils.password import verify_password, get_password_hash


def get_user(db: Session, username: str) -> UserDB | None: 
    """ 
    Fetch user from the database by username. 
    """ 
    return db.query(UserDB).filter(UserDB.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> UserDB | None: 
    """ 
    Authenticate user using database credentials. 
    """ 
    user = get_user(db, username) 
    if not user: 
        return None 

    if not verify_password(password, user.hashed_password): 
        return None 
    
    return user

def create_user(db: Session, username: str, email: str, password: str) -> UserDB: 
    # Check email uniqueness 
    existing_email = db.query(UserDB).filter(UserDB.email == email).first() 
    if existing_email: 
        raise HTTPException ( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email is already registered" 
        ) 
    # Check username uniqueness
    existing_username = db.query(UserDB).filter(UserDB.username == username).first() 
    if existing_username: 
        raise HTTPException ( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username is already taken" 
        ) 
    
    # Hash the password
    hashed = get_password_hash(password) 
    
    # Create the user instance 
    new_user = UserDB( 
        username=username, 
        email=email, 
        hashed_password=hashed, 
        role="user",  
        disabled=False 
    ) 
    
    # Save to the database 
    db.add(new_user) 
    db.commit() 
    db.refresh(new_user)

    return new_user
