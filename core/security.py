import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from model.user import UserDetails as user_model
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, timezone, datetime
from dotenv import load_dotenv
from db.database import db_dependency

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

Oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/token")



async def authenticate_user(email: str, password: str, db: db_dependency):
    user = db.query(user_model).filter(user_model.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    else:
        return user


def hashing_password(password: str):
    password = bcrypt_context.hash(password)
    return password


async def create_access_token(email: str, user_id: int, expires_delta: timedelta, db: db_dependency):
    from crud.user import get_user_by_id
    user = get_user_by_id(user_id,db)
    encode = {'sub': email, 'id': user_id, 'role': user.role.value}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(Oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        role: str = payload.get('role')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        return {'email': email, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
