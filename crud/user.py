from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from model.user import UserDetails
from schema.user import UserDetailsRequest
from core import security


db_dependency = Annotated[Session, Depends(get_db)]


def get_users(db: db_dependency):
    return db.query(UserDetails).all()


def get_user_by_id(id: int, db: db_dependency):
    return db.query(UserDetails).filter(UserDetails.id == id).first()


def delete_user_by_id(id: int, db: db_dependency):
    db.query(UserDetails).filter(UserDetails.id == id).delete()
    db.commit()


def add_user(user_request: UserDetailsRequest, db: db_dependency):
    user = UserDetails(**user_request.model_dump())
    password=user_request.password
    user.password = security.hashing_password(password)
    db.add(user)
    db.commit()


def update_user_by_id(id: int, user_details_request: UserDetailsRequest, db: db_dependency):
    user = get_user_by_id(id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.name = user_details_request.name
    user.password = security.hashing_password(user_details_request.password)
    user.role = user_details_request.role
    user.email = user_details_request.email
    db.add(user)
    db.commit()
