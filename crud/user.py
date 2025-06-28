from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from model.user import UserDetails
from schema.user import UserDetailsRequest
from core import security
import logging
logger = logging.getLogger(__name__)

db_dependency = Annotated[Session, Depends(get_db)]


def get_users(db: db_dependency):
    try:
        logger.debug("Fetching all users from the database.")
        users = db.query(UserDetails).all()
        logger.info("Successfully fetched all users.")
        return users
    except Exception as e:
        logger.error(f"Error occurred while fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching users."
        )


def get_user_by_id(id: int, db: db_dependency):
    try:
        logger.debug(f"Fetching user with ID: {id}.")
        user = db.query(UserDetails).filter(UserDetails.id == id).first()
        if not user:
            logger.warning(f"User with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        logger.info(f"Successfully fetched user with ID: {id}.")
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching user by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the user."
        )


def delete_user_by_id(id: int, db: db_dependency):
    try:
        logger.debug(f"Attempting to delete user with ID: {id}.")
        user = db.query(UserDetails).filter(UserDetails.id == id).first()
        if not user:
            logger.warning(f"User with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        db.query(UserDetails).filter(UserDetails.id == id).delete()
        db.commit()
        logger.info(f"Successfully deleted user with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting user with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user."
        )


def add_user(user_request: UserDetailsRequest, db: db_dependency):
    try:
        logger.debug("Attempting to add a new user.")
        user = UserDetails(**user_request.model_dump())
        password = user_request.password
        user.password = security.hashing_password(password)
        db.add(user)
        db.commit()
        logger.info("Successfully added a new user.")
        return user
    except Exception as e:
        logger.error(f"Error occurred while adding a new user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the user."
        )


def update_user_by_id(id: int, user_details_request: UserDetailsRequest, db: db_dependency):
    try:
        logger.debug(f"Attempting to update user with ID: {id}.")
        user = get_user_by_id(id, db)
        if user is None:
            logger.warning(f"User with ID {id} not found for update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        user.name = user_details_request.name
        user.password = security.hashing_password(user_details_request.password)
        user.role = user_details_request.role
        user.email = user_details_request.email
        db.add(user)
        db.commit()
        logger.info(f"Successfully updated user with ID: {id}.")
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating user with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user."
        )
