from fastapi import APIRouter, Depends, status, HTTPException, Query, Path, UploadFile, File
from crud import ConsultantProfile as consultant_profile_service
from db.database import db_dependency
from schema.ConsultantProfile import ConsultantProfileSchema
from core.security import get_current_user
from typing import Annotated
from PyPDF2 import PdfReader
from utility.file_reader_using_genai import extract_information
import logging
logger = logging.getLogger(__name__)

router = APIRouter()

# GET all consultant profiles
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_consultant_profiles(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching all consultant profiles.")
        consultant_profiles = consultant_profile_service.get_all_consultant_profiles(db)
        logger.info("Successfully fetched all consultant profiles.")
        return consultant_profiles
    except Exception as e:
        logger.error(f"Error occurred while fetching consultant profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching consultant profiles."
        )


# GET consultant profile by ID
@router.get("/{consultant_profile_id}", status_code=status.HTTP_200_OK)
async def read_consultant_profile_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, consultant_profile_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching consultant profile with ID: {consultant_profile_id}.")
        consultant_profile = consultant_profile_service.get_consultant_profile_by_id(db, consultant_profile_id)
        logger.info(f"Successfully fetched consultant profile with ID: {consultant_profile_id}.")
        return consultant_profile
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching consultant profile with ID {consultant_profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the consultant profile."
        )


# GET consultant profiles by skill
@router.get("/search", status_code=status.HTTP_200_OK)
async def read_consultant_profiles_by_skill(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, skill: str = Query(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching consultant profiles with skill: {skill}.")
        consultant_profiles = consultant_profile_service.get_consultant_profiles_by_skill(db, skill)
        logger.info(f"Successfully fetched consultant profiles with skill: {skill}.")
        return consultant_profiles
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching consultant profiles by skill {skill}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching consultant profiles by skill."
        )


# POST a new consultant profile
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_consultant_profile(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, consultant_profile_request: ConsultantProfileSchema):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Creating a new consultant profile.")
        consultant_profile = consultant_profile_service.add_consultant_profile(db, consultant_profile_request)
        logger.info("Successfully created a new consultant profile.")
        return consultant_profile
    except Exception as e:
        logger.error(f"Error occurred while creating a consultant profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the consultant profile."
        )

@router.post("/upload-pdfs/", status_code=status.HTTP_200_OK)
async def upload_multiple_pdfs(db: db_dependency,files: list[UploadFile] = File(...)):
    """
    Endpoint to upload multiple PDF files and process their content.
    """
    processed_results = []

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    try:
        logger.debug("Creating multiple new consultant profile.")
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
            processed_result = extract_information(pdf_content)
            consultant_profile_service.add_consultant_profile(db,processed_result)
            processed_results.append({file.filename: processed_result})

        return {"message": "PDF files processed successfully.", "results": processed_results}

    except Exception as e:
        logger.error(f"An error occurred while processing PDF files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the PDF files."
        )

# PUT to update consultant profile by ID
@router.put("/{consultant_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_consultant_profile(
    user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    consultant_profile_request: ConsultantProfileSchema,
    consultant_profile_id: int = Path(...),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating consultant profile with ID: {consultant_profile_id}.")
        consultant_profile_service.update_consultant_profile_by_id(db, consultant_profile_id, consultant_profile_request)
        logger.info(f"Successfully updated consultant profile with ID: {consultant_profile_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating consultant profile with ID {consultant_profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the consultant profile."
        )


# DELETE consultant profile by ID
@router.delete("/{consultant_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultant_profile(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, consultant_profile_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Deleting consultant profile with ID: {consultant_profile_id}.")
        consultant_profile_service.delete_consultant_profile_by_id(db, consultant_profile_id)
        logger.info(f"Successfully deleted consultant profile with ID: {consultant_profile_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting consultant profile with ID {consultant_profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the consultant profile."
        )


# PUT to update consultant availability
@router.put("/{consultant_profile_id}/availability", status_code=status.HTTP_200_OK)
async def update_consultant_availability(
    user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    consultant_profile_id: int = Path(...),
    availability: str = Query(...),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating availability of consultant profile with ID: {consultant_profile_id} to {availability}.")
        consultant_profile = consultant_profile_service.update_consultant_availability(db, consultant_profile_id, availability)
        logger.info(f"Successfully updated availability of consultant profile with ID: {consultant_profile_id} to {availability}.")
        return consultant_profile
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating availability of consultant profile with ID {consultant_profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the consultant profile availability."
        )
