from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
from core.security import get_current_user
from crud import job_description as job_description_service
from schema.job_description import JobDescriptionRequest
from db.database import get_db
from utility.logging_config import logger

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/job-descriptions", response_model=List[JobDescriptionRequest], status_code=status.HTTP_200_OK)
async def read_all_job_descriptions(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    try:
        if user is None:
            logger.warning("Unauthorized access attempt to read all job descriptions.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        logger.debug("Fetching all job descriptions.")
        job_descriptions = job_description_service.get_job_description(db)
        logger.info("Successfully fetched all job descriptions.")
        return job_descriptions
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job descriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching job descriptions."
        )


@router.get("/job-descriptions/{job_id}", response_model=JobDescriptionRequest, status_code=status.HTTP_200_OK)
async def read_job_description_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                     job_id: int = Path(gt=0)):
    try:
        if user is None:
            logger.warning(f"Unauthorized access attempt to read job description with ID: {job_id}.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        logger.debug(f"Fetching job description with ID: {job_id}.")
        job_description = job_description_service.get_job_description_by_id(db, job_id)
        logger.info(f"Successfully fetched job description with ID: {job_id}.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job description with ID {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the job description."
        )


@router.post("/job-descriptions", response_model=JobDescriptionRequest, status_code=status.HTTP_201_CREATED)
async def create_job_description(job_description_request: JobDescriptionRequest,
                                 user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    try:
        if user is None:
            logger.warning("Unauthorized access attempt to create a job description.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        logger.debug("Creating a new job description.")
        job_description = job_description_service.add_job_description(db, job_description_request)
        logger.info("Successfully created a new job description.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while creating a job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the job description."
        )


@router.put("/job-descriptions/{job_id}", response_model=JobDescriptionRequest, status_code=status.HTTP_200_OK)
async def update_job_description(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                 job_description_request: JobDescriptionRequest, job_id: int = Path(gt=0)):
    try:
        if user is None:
            logger.warning(f"Unauthorized access attempt to update job description with ID: {job_id}.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        logger.debug(f"Updating job description with ID: {job_id}.")
        updated_job_description = job_description_service.update_job_description_by_id(db, job_id,
                                                                                       job_description_request)
        logger.info(f"Successfully updated job description with ID: {job_id}.")
        return updated_job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating job description with ID {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description."
        )


@router.delete("/job-descriptions/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                 job_id: int = Path(gt=0)):
    try:
        if user is None:
            logger.warning(f"Unauthorized access attempt to delete job description with ID: {job_id}.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        logger.debug(f"Deleting job description with ID: {job_id}.")
        job_description_service.delete_job_description_by_id(db, job_id)
        logger.info(f"Successfully deleted job description with ID: {job_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting job description with ID {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the job description."
        )
