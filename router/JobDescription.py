from fastapi import APIRouter, Depends, status, HTTPException, Query, Path, UploadFile, File
from crud import JobDescription as job_description_service
from crud import MatchResult as match_result_service
from db.database import db_dependency
from schema.JobDescription import JobDescriptionRequest
from core.security import get_current_user
from typing import Annotated
from PyPDF2 import PdfReader
from utility.jobdescription_reader import extract_information
import logging
import requests
logger = logging.getLogger(__name__)

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
        match_results = match_result_service.get_all_match_results(db, job_description_id)
        logger.info(f"Successfully fetched job description with ID: {job_description_id}.")
        return {
            "job_description": job_description,
            "match_results": match_results
        }
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
        id = user.get("id")
        email = user.get("email")
        logger.debug("Creating a new job description.")
        job_description = job_description_service.add_job_description(db, job_description_request,id,email)
        logger.info("Successfully created a new job description.")
        return job_description
    except Exception as e:
        logger.error(f"Error occurred while creating a job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the job description."
        )


@router.post("/upload-job-descriptions/", status_code=status.HTTP_200_OK)
async def upload_job_descriptions(
        user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
        files: list[UploadFile] = File(...)
):
    """
    Endpoint to upload multiple job description PDF files and process their content.
    """
    processed_results = []

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized"
        )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    try:
        logger.debug("Uploading and processing multiple job description PDFs.")
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not a valid PDF."
                )

            logger.debug(f"Reading file: {file.filename}")
            pdf_reader = PdfReader(file.file)
            pdf_content = ""

            for page in pdf_reader.pages:
                pdf_content += page.extract_text()

            logger.info(f"Extracted content from {file.filename}")
            id = user.get("id")
            email = user.get("email")
            logger.debug("Creating a new job description.")
            processed_result = extract_information(pdf_content)  # Assuming a similar function exists
            job_description_service.add_job_description(db, processed_result, id, email)
            processed_results.append({file.filename: processed_result})

        logger.info("Successfully processed all job description PDFs.")
        return {"message": "Job description PDFs processed successfully.", "results": processed_results}

    except Exception as e:
        logger.error(f"Error occurred while processing job description PDFs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the job description PDFs."
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
        status_notification: str = Query(...),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating status of job description with ID: {job_description_id} to {status_notification}.")
        job_description = job_description_service.update_job_description_status(db, job_description_id, status_notification)
        logger.info(f"Successfully updated status of job description with ID: {job_description_id} to {status_notification}.")
        return job_description
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating status of job description with ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the job description status."
        )
