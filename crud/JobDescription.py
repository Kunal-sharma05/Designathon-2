from utility.logging_config import logger
from fastapi import HTTPException, status
from db.database import db_dependency
from model.JobDescription import JobDescription
from schema.JobDescription import JobDescriptionRequest


def get_all_job_descriptions(db: db_dependency) -> list[JobDescriptionRequest]:
    try:
        logger.debug("Fetching all job descriptions from the database.")
        result = db.query(JobDescription).all()
        job_descriptions = [JobDescriptionRequest.model_validate(item) for item in result]
        logger.info("Successfully fetched all job descriptions.")
        return job_descriptions
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
        job_description = JobDescriptionRequest.model_validate(result)
        logger.info(f"Successfully fetched job description with ID: {id}.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job description by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the job description."
        )


def get_job_description_by_title(db: db_dependency, title: str) -> list[JobDescriptionRequest]:
    try:
        logger.debug(f"Fetching job descriptions with title: {title}.")
        result = db.query(JobDescription).filter(JobDescription.title.ilike(f"%{title}%")).all()
        if not result:
            logger.warning(f"No job descriptions found with title: {title}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No job descriptions found with the given title."
            )
        job_descriptions = [JobDescriptionRequest.model_validate(item) for item in result]
        logger.info(f"Successfully fetched job descriptions with title: {title}.")
        return job_descriptions
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job descriptions by title {title}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching job descriptions by title."
        )


def add_job_description(db: db_dependency, job_description_request: JobDescriptionRequest, id: int,
                        email: str) -> JobDescriptionRequest:
    try:
        logger.debug("Attempting to add a new job description.")
        new_job_description = JobDescription(
            title=job_description_request.title,
            department=job_description_request.department,
            location=job_description_request.location,
            experience=job_description_request.experience,
            description=job_description_request.description,
            skills=job_description_request.skills,  # Stored as JSON array
            requestor_email=email,
            user_id=id, )

        db.add(new_job_description)
        db.commit()
        logger.info("Successfully added a new job description.")
        return JobDescriptionRequest.model_validate(new_job_description)
    except Exception as e:
        logger.error(f"Error occurred while adding a new job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the job description."
        )


def update_job_description_by_id(db: db_dependency, id: int,
                                 job_description_request: JobDescriptionRequest) -> JobDescriptionRequest:
    try:
        logger.debug(f"Attempting to update job description with ID: {id}.")
        result = db.query(JobDescription).filter(JobDescription.id == id).first()
        if not result:
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
        return JobDescriptionRequest.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating job description with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description."
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
        db.delete(result)
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


def update_job_description_status(db: db_dependency, id: int, status: str) -> JobDescriptionRequest:
    try:
        logger.debug(f"Attempting to update status of job description with ID: {id} to {status}.")
        result = db.query(JobDescription).filter(JobDescription.id == id).first()
        if not result:
            logger.warning(f"Job description with ID {id} not found for status update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found."
            )
        result.status = status
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated status of job description with ID: {id} to {status}.")
        return JobDescriptionRequest.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating status of job description with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description status."
        )
