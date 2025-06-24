from utility.logging_config import logger
from fastapi import HTTPException, status
from db.database import db_dependency
from model.job_description import JobDescription
from schema.job_description import JobDescriptionRequest


def get_job_description(db: db_dependency) -> JobDescriptionRequest:
    try:
        logger.debug("Fetching all job descriptions from the database.")
        result = db.query(JobDescription).all()
        job_description_result = JobDescriptionRequest.model_validate(result)
        logger.info("Successfully fetched all job descriptions.")
        return job_description_result
    except Exception as e:
        logger.error(f"Error occurred while fetching job descriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching job descriptions."
        )


def get_job_description_by_id(db: db_dependency, id: int) -> JobDescriptionRequest:
    try:
        logger.debug(f"Fetching job description with ID: {id}.")
        result = db.query(JobDescription).filter(JobDescription.id == id).first()
        if not result:
            logger.warning(f"Job description with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found."
            )
        job_description_result = JobDescriptionRequest.model_validate(result)
        logger.info(f"Successfully fetched job description with ID: {id}.")
        return job_description_result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job description by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the job description."
        )


def delete_job_description_by_id(db: db_dependency, id: int) -> None:
    try:
        logger.debug(f"Attempting to delete job description with ID: {id}.")
        result = db.query(JobDescription).filter(JobDescription.id == id).first()
        if not result:
            logger.warning(f"Job description with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found."
            )
        db.query(JobDescription).filter(JobDescription.id == id).delete()
        db.commit()
        logger.info(f"Successfully deleted job description with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting job description with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the job description."
        )


def update_job_description_by_id(db: db_dependency, id: int,
                                 job_description_request: JobDescriptionRequest) -> JobDescriptionRequest:
    try:
        logger.debug(f"Attempting to update job description with ID: {id}.")
        result = db.query(JobDescription).filter(JobDescription.id == id).first()
        if result is None:
            logger.warning(f"Job description with ID {id} not found for update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found."
            )
        for key, value in job_description_request.model_dump().items():
            setattr(result, key, value)
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated job description with ID: {id}.")
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating job description with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description."
        )


def add_job_description(db: db_dependency, job_description_request: JobDescriptionRequest) -> JobDescriptionRequest:
    try:
        logger.debug("Attempting to add a new job description.")
        result = JobDescription(**job_description_request.model_dump())
        db.add(result)
        db.commit()
        logger.info("Successfully added a new job description.")
        return result
    except Exception as e:
        logger.error(f"Error occurred while adding a new job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the job description."
        )
