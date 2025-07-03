from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import MatchResult as match_result_service
from db.database import db_dependency
from schema.MatchResult import MatchResultSchema
from core.security import get_current_user
from typing import Annotated
import logging
logger = logging.getLogger(__name__)
router = APIRouter()


# GET all match results
@router.get("/all-matches/{job_description_id}", status_code=status.HTTP_200_OK)
async def get_all_match_results(user: Annotated[dict, Depends(get_current_user)], job_description_id: int,
                                db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching all match results.")
        match_results = match_result_service.get_all_match_results(db, job_description_id)
        logger.info("Successfully fetched all match results.")
        return match_results
    except Exception as e:
        logger.error(f"Error occurred while fetching match results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching match results."
        )


@router.get("/top-3-matches/{job_description_id}", status_code=status.HTTP_200_OK)
async def top_3_match_results(user: Annotated[dict, Depends(get_current_user)], job_description_id: int,
                              db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching top 3 match results.")
        match_results = match_result_service.get_top_3_matches(db, job_description_id)
        logger.info("Successfully fetched top 3 match results.")
        return match_results
    except Exception as e:
        logger.error(f"Error occurred while fetching top 3 match results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching top 3 match results."
        )


# GET match result by ID
@router.get("/{match_result_id}", status_code=status.HTTP_200_OK)
async def read_match_result_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                  match_result_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching match result with ID: {match_result_id}.")
        match_result = match_result_service.get_match_result_by_id(db, match_result_id)
        logger.info(f"Successfully fetched match result with ID: {match_result_id}.")
        return match_result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching match result with ID {match_result_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the match result."
        )


# GET match results by job description ID
@router.get("/job/{job_description_id}", status_code=status.HTTP_200_OK)
async def read_match_results_by_job_description_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                                                   job_description_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching match results for job description ID: {job_description_id}.")
        match_results = match_result_service.get_match_results_by_job_description_id(db, job_description_id)
        logger.info(f"Successfully fetched match results for job description ID: {job_description_id}.")
        return match_results
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching match results for job description ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching match results for the job description ID."
        )


# GET top N match results by job description ID
@router.get("/job/{job_description_id}/top", status_code=status.HTTP_200_OK)
async def read_top_match_results_by_job_description_id(
        user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
        job_description_id: int = Path(...),
        top_n: int = Query(...)
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching top {top_n} match results for job description ID: {job_description_id}.")
        match_results = match_result_service.get_top_match_results_by_job_description_id(db, job_description_id, top_n)
        logger.info(f"Successfully fetched top {top_n} match results for job description ID: {job_description_id}.")
        return match_results
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error occurred while fetching top match results for job description ID {job_description_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching top match results for the job description ID."
        )


# POST a new match result
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_match_result(user: Annotated[dict, Depends(get_current_user)], db: db_dependency,
                              match_result_request: MatchResultSchema):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Creating a new match result.")
        match_result = match_result_service.add_match_result(db, match_result_request)
        logger.info("Successfully created a new match result.")
        return match_result
    except Exception as e:
        logger.error(f"Error occurred while creating a match result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the match result."
        )


# PUT to update match result by ID
@router.put("/{match_result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_match_result(
        user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
        match_result_request: MatchResultSchema,
        match_result_id: int = Path(...)
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating match result with ID: {match_result_id}.")
        match_result_service.update_match_result_by_id(db, match_result_id, match_result_request)
        logger.info(f"Successfully updated match result with ID: {match_result_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating match result with ID {match_result_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the match result."
        )


# DELETE match result by ID
@router.delete("/{match_result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match_result(db: db_dependency, user: Annotated[dict, Depends(get_current_user)],
                              match_result_id: int = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Deleting match result with ID: {match_result_id}.")
        match_result_service.delete_match_result_by_id(db, match_result_id)
        logger.info(f"Successfully deleted match result with ID: {match_result_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting match result with ID {match_result_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the match result."
        )
