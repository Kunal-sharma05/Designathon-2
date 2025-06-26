from utility.logging_config import logger
from fastapi import HTTPException, status
from db.database import db_dependency
from model.Notification import Notification  # Assuming this is the ORM model
from schema.Notification import NotificationSchema, NotificationStatusEnum



def get_all_notifications(db: db_dependency) -> list[NotificationSchema]:
    try:
        logger.debug("Fetching all notifications from the database.")
        result = db.query(Notification).all()
        notifications = [NotificationSchema.model_validate(item) for item in result]
        logger.info("Successfully fetched all notifications.")
        return notifications
    except Exception as e:
        logger.error(f"Error occurred while fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching notifications."
        )


def get_notification_by_id(db: db_dependency, id: str) -> NotificationSchema:
    try:
        logger.debug(f"Fetching notification with ID: {id}.")
        result = db.query(Notification).filter(Notification.id == id).first()
        if not result:
            logger.warning(f"Notification with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found."
            )
        notification = NotificationSchema.model_validate(result)
        logger.info(f"Successfully fetched notification with ID: {id}.")
        return notification
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching notification by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the notification."
        )


def get_notifications_by_job_description_id(db: db_dependency, job_description_id: str) -> list[NotificationSchema]:
    try:
        logger.debug(f"Fetching notifications for job description ID: {job_description_id}.")
        result = db.query(Notification).filter(Notification.job_description_id == job_description_id).all()
        if not result:
            logger.warning(f"No notifications found for job description ID: {job_description_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No notifications found for the given job description ID."
            )
        notifications = [NotificationSchema.model_validate(item) for item in result]
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


def add_notification(db: db_dependency, notification_request: NotificationSchema) -> NotificationSchema:
    try:
        logger.debug("Attempting to add a new notification.")
        new_notification = Notification(**notification_request.model_dump())
        db.add(new_notification)
        db.commit()
        logger.info("Successfully added a new notification.")
        return NotificationSchema.model_validate(new_notification)
    except Exception as e:
        logger.error(f"Error occurred while adding a new notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the notification."
        )


def update_notification_status_by_id(db: db_dependency, id: str, status: NotificationStatusEnum) -> NotificationSchema:
    try:
        logger.debug(f"Attempting to update status of notification with ID: {id} to {status}.")
        result = db.query(Notification).filter(Notification.id == id).first()
        if not result:
            logger.warning(f"Notification with ID {id} not found for status update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found."
            )
        result.status = status
        if status == NotificationStatusEnum.sent:
            result.sent_at = datetime.now()
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated status of notification with ID: {id} to {status}.")
        return NotificationSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating status of notification with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the notification status."
        )


def delete_notification_by_id(db: db_dependency, id: str) -> None:
    try:
        logger.debug(f"Attempting to delete notification with ID: {id}.")
        result = db.query(Notification).filter(Notification.id == id).first()
        if not result:
            logger.warning(f"Notification with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found."
            )
        db.delete(result)
        db.commit()
        logger.info(f"Successfully deleted notification with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting notification with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the notification."
        )


def get_notifications_by_status(db: db_dependency, status: NotificationStatusEnum) -> list[NotificationSchema]:
    try:
        logger.debug(f"Fetching notifications with status: {status}.")
        result = db.query(Notification).filter(Notification.status == status).all()
        if not result:
            logger.warning(f"No notifications found with status: {status}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No notifications found with the given status."
            )
        notifications = [NotificationSchema.model_validate(item) for item in result]
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
