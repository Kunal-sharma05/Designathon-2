from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import user as user_service
from sqlalchemy.orm import Session
from typing import Annotated
from db.database import sessionLocal, db_dependency
from core import security
from fastapi.security import OAuth2PasswordRequestForm
from schema.token import Token
from schema.user import UserDetailsRequest
from model.user import UserDetails
from utility.logging_config import logger

router = APIRouter()


# GET method
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    try:
        logger.debug("Fetching all users.")
        users = user_service.get_users(db)
        logger.info("Successfully fetched all users.")
        return users
    except Exception as e:
        logger.error(f"Error occurred while fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching users."
        )


# POST method
@router.post("/user_details", status_code=status.HTTP_201_CREATED)
async def create_user(user_details_request: UserDetailsRequest, db: db_dependency):
    try:
        logger.debug("Creating a new user.")
        user_service.add_user(user_details_request, db)
        logger.info("Successfully created a new user.")
    except Exception as e:
        logger.error(f"Error occurred while creating a user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user."
        )


# PUT method
@router.put("/user_details/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_details(db: db_dependency, user_details_request: UserDetailsRequest, user_id: int = Path(gt=0)):
    try:
        logger.debug(f"Updating user details for user ID: {user_id}.")
        user_service.update_user_by_id(user_id, user_details_request, db)
        logger.info(f"Successfully updated user details for user ID: {user_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating user details for user ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user details."
        )


# DELETE method
@router.delete("/user_details/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_details(db: db_dependency, user_id: str = Query()):
    try:
        logger.debug(f"Deleting user with ID: {user_id}.")
        user_details_model = user_service.get_user_by_id(user_id, db)
        if user_details_model is None:
            logger.warning(f"User with ID {user_id} not found for deletion.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        else:
            user_service.delete_user_by_id(user_id, db)
            logger.info(f"Successfully deleted user with ID: {user_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting user with ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user."
        )


# Login method
@router.put("/token", response_model=Token)
async def login_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    try:
        logger.debug(f"Authenticating user with username: {form_data.username}.")
        user = await security.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            logger.warning(f"Authentication failed for username: {form_data.username}.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        token = await security.create_access_token(user.email, user.id, timedelta(minutes=20), db)
        logger.info(f"Successfully authenticated user: {form_data.username}.")
        return {'access_token': token, 'token_type': 'bearer'}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred during user authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication."
        )


# Verify Email method
@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(email: str, db: db_dependency):
    try:
        logger.debug(f"Verifying email: {email}.")
        user = db.query(UserDetails).filter(UserDetails.email == email).first()
        if not user:
            logger.warning(f"Email {email} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
        logger.info(f"Successfully verified email: {email}.")
        return {"message": "Email verified. You can proceed to reset your password."}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while verifying email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying the email."
        )


# Reset Password method
@router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(email: str, new_password: str, db: db_dependency):
    try:
        logger.debug(f"Resetting password for email: {email}.")
        user = db.query(UserDetails).filter(UserDetails.email == email).first()
        if not user:
            logger.warning(f"Invalid email: {email}.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email")
        user.password = security.hashing_password(new_password)
        db.commit()
        logger.info(f"Successfully reset password for email: {email}.")
        return {"message": "Password has been reset successfully."}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while resetting password for email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting the password."
        )
