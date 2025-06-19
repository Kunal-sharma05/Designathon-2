from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import user as user_service
from sqlalchemy.orm import Session
from typing import Annotated
from db.database import sessionLocal
from core import security
from fastapi.security import OAuth2PasswordRequestForm
from schema.token import Token
from schema.user import UserDetailsRequest
from model.user import UserDetails

router = APIRouter()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


#get_method
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return user_service.get_users(db)


#post method
@router.post("/user_details", status_code=status.HTTP_201_CREATED)
async def create_user(user_details_request: UserDetailsRequest, db: db_dependency):
    user_service.add_user(user_details_request, db)


#put method
@router.put("/user_details/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_details(db: db_dependency, user_details_request: UserDetailsRequest, user_id: int = Path(gt=0)):
    user_service.update_user_by_id(user_id, user_details_request, db)


@router.delete("/user_details/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_details(db: db_dependency, user_id: int = Query(gt=0)):
    user_details_model = user_service.get_user_by_id(user_id, db)
    if user_details_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nor found")
    else:
        user_service.delete_user_by_id(user_id, db)


@router.put("/token", response_model=Token)
async def login_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = await security.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    print(user)
    token = await security.create_access_token(user.email, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(UserDetails).filter(UserDetails.email == email).first()  # Use UserDetails model
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    else:
        return {"message": "Email verified. You can proceed to reset your password."}


@router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(UserDetails).filter(UserDetails.email == email).first()  # Use UserDetails model
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email")

    # Update the user's password
    user.password = security.hashing_password(new_password)
    db.commit()

    return {"message": "Password has been reset successfully."}
