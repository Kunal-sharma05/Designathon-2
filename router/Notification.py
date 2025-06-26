from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import Notification as notification_service
from db.database import db_dependency
from schema.Notification import NotificationSchema, NotificationStatusEnum
from utility.logging_config import logger
from core.security import get_current_user
from typing import Annotated

router = APIRouter()

# GET all notifications
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_notifications(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching all notifications.")
        notifications = notification_service.get_all_notifications(db)
        logger.info("Successfully fetched all notifications.")
        return notifications
    except Exception as e:
        logger.error(f"Error occurred while fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching notifications."
        )


# GET notification by ID
@router.get("/{notification_id}", status_code=status.HTTP_200_OK)
async def read_notification_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, notification_id: str = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching notification with ID: {notification_id}.")
        notification = notification_service.get_notification_by_id(db, notification_id)
        logger.info(f"Successfully fetched notification with ID: {notification_id}.")
        return notification
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching notification with ID {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the notification."
        )


# GET notifications by job description ID
@router.get("/job/{job_description_id}", status_code=status.HTTP_200_OK)
async def read_notifications_by_job_description_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, job_description_id: str = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching notifications for job description ID: {job_description_id}.")
        notifications = notification_service.get_notifications_by_job_description_id(db, job_description_id)
        logger.info(f"Successfully fetched notifications for job description ID: {job_description_id}.")
        return notifications
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching notifications for job description ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching notifications for the job description ID."
        )


# GET notifications by status
@router.get("/status/{status}", status_code=status.HTTP_200_OK)
async def read_notifications_by_status(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, status: NotificationStatusEnum = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching notifications with status: {status}.")
        notifications = notification_service.get_notifications_by_status(db, status)
        logger.info(f"Successfully fetched notifications with status: {status}.")
        return notifications
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching notifications with status {status}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching notifications with the given status."
        )


# POST a new notification
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notification(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, notification_request: NotificationSchema):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Creating a new notification.")
        notification = notification_service.add_notification(db, notification_request)
        logger.info("Successfully created a new notification.")
        return notification
    except Exception as e:
        logger.error(f"Error occurred while creating a notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the notification."
        )


# PUT to update notification status by ID
@router.put("/{notification_id}/status", status_code=status.HTTP_200_OK)
async def update_notification_status(
    user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    notification_id: str = Path(...),
    status: NotificationStatusEnum = Query(...)
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating status of notification with ID: {notification_id} to {status}.")
        notification = notification_service.update_notification_status_by_id(db, notification_id, status)
        logger.info(f"Successfully updated status of notification with ID: {notification_id} to {status}.")
        return notification
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating status of notification with ID {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the notification status."
        )


# DELETE notification by ID
@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(user: Annotated[dict, Depends(get_current_user)],db: db_dependency, notification_id: str = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Deleting notification with ID: {notification_id}.")
        notification_service.delete_notification_by_id(db, notification_id)
        logger.info(f"Successfully deleted notification with ID: {notification_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting notification with ID {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the notification."
        )
