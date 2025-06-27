from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import JobDescription as job_description_service
from db.database import db_dependency
from schema.JobDescription import JobDescriptionRequest
from utility.logging_config import logger
from core.security import get_current_user
from typing import Annotated

router = APIRouter()


# GET all job descriptions
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_job_descriptions(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching all job descriptions.")
        job_descriptions = job_description_service.get_all_job_descriptions(db)
        logger.info("Successfully fetched all job descriptions.")
        return job_descriptions
    except Exception as e:
        logger.error(f"Error occurred while fetching job descriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching job descriptions."
        )


# GET job descriptions by title
@router.get("/searching_by_title/", status_code=status.HTTP_200_OK)
async def read_job_descriptions_by_title(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                         title: str = Query(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching job descriptions with title: {title}.")
        job_descriptions = job_description_service.get_job_description_by_title(db, title)
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


# GET job description by ID
@router.get("/{job_description_id}", status_code=status.HTTP_200_OK)
async def read_job_description_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                     job_description_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching job description with ID: {job_description_id}.")
        job_description = job_description_service.get_job_description_by_id(db, job_description_id)
        logger.info(f"Successfully fetched job description with ID: {job_description_id}.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching job description with ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the job description."
        )


# POST a new job description
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job_description(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                 job_description_request: JobDescriptionRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Creating a new job description.")
        job_description = job_description_service.add_job_description(db, job_description_request)
        logger.info("Successfully created a new job description.")
        return job_description
    except Exception as e:
        logger.error(f"Error occurred while creating a job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the job description."
        )


# PUT to update job description by ID
@router.put("/{job_description_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_job_description(
        user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
        job_description_request: JobDescriptionRequest,
        job_description_id: int = Path()
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating job description with ID: {job_description_id}.")
        job_description_service.update_job_description_by_id(db, job_description_id, job_description_request)
        logger.info(f"Successfully updated job description with ID: {job_description_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating job description with ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description."
        )


# DELETE job description by ID
@router.delete("/{job_description_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                 job_description_id: int = Path()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Deleting job description with ID: {job_description_id}.")
        job_description_service.delete_job_description_by_id(db, job_description_id)
        logger.info(f"Successfully deleted job description with ID: {job_description_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting job description with ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the job description."
        )


# PUT to update job description status
@router.put("/{job_description_id}/status", status_code=status.HTTP_200_OK)
async def update_job_description_status(
        user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
        job_description_id: int = Path(...),
        status: str = Query(...),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating status of job description with ID: {job_description_id} to {status}.")
        job_description = job_description_service.update_job_description_status(db, job_description_id, status)
        logger.info(f"Successfully updated status of job description with ID: {job_description_id} to {status}.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating status of job description with ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description status."
        )
