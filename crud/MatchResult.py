from fastapi import HTTPException, status
from db.database import db_dependency
from model.MatchResult import MatchResult as MatchResultModel
from model.MatchResult import MatchResult  # Assuming this is the ORM model
from schema.MatchResult import MatchResultSchema
from model.JobDescription import JobDescription
from model.ConsultantProfile import ConsultantProfile, ConsultantEnum
from utility.agentic_flow import run_agent_matching
import logging

logger = logging.getLogger(__name__)


def get_all_match_results(db: db_dependency, jobDescription_id: int):
    try:
        logger.debug("Fetching all match results from the database.")
        jd = db.query(JobDescription).filter(JobDescription.id == jobDescription_id).first()
        profiles = db.query(ConsultantProfile).filter(
            ConsultantProfile.availability != ConsultantEnum.unavailable).all()
        if not jd or not profiles:
            print(f"Job Descriptions or Profiles not found for Job ID: {jobDescription_id}")
        logger.debug("Invoking run_agent_matching function.")
        result = run_agent_matching(db, jd, profiles)
        all_matches = result.get("all_matches", [])

        if not all_matches:
            print(f"No matches found for job_id: {jobDescription_id}")

        db.query(MatchResultModel).filter(MatchResultModel.job_description_id == jobDescription_id).delete()
        db.commit()

        for idx, match in enumerate(all_matches):
            matched_profile = MatchResultModel(
                rank=idx + 1,
                job_description_id=jobDescription_id,
                consultant_id=match["profile"].id,
                similarity_score=match["similarity_score"]

            )
            db.add(matched_profile)
        db.commit()
        serialized_matches = [
            {
                "profile": {
                    "id": match["profile"].id,
                    "name": match["profile"].name,
                    "skills": match["profile"].skills,
                    "experience": match["profile"].experience,
                    "location": match["profile"].location,
                    "availability": match["profile"].availability,
                },
                "similarity_score": match["similarity_score"],
                "rank": idx + 1,
            }
            for idx, match in enumerate(all_matches)
        ]

        logger.info("Successfully fetched all match results.")
        return serialized_matches

    except Exception as e:
        logger.error(f"Error occurred while fetching match results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching match results."
        )


def get_top_3_matches(db: db_dependency, jd_id: int):
    """
    Fetch the top 3 ranked profiles for a given Job Description ID.
    """
    # Query the RankedProfile table for the top 3 results
    try:
        logger.debug("Fetching top 3 results")
        top_3_profiles = (
            db.query(MatchResult)
            .filter(MatchResult.job_description_id == jd_id)
            .order_by(MatchResult.rank.asc())
            .limit(3)
            .all()
        )

        # Serialize the response
        serialized_results = [
            {
                "profile_id": profile.consultant_id,
                "rank": profile.rank,
                "similarity_score": profile.similarity_score,
                "ranked_at": profile.matched_at.isoformat() if profile.matched_at else None,
            }
            for profile in top_3_profiles
        ]

        return serialized_results
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching match result by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the match result."
        )


def get_match_result_by_id(db: db_dependency, id: int) -> MatchResultSchema:
    try:
        logger.debug(f"Fetching match result with ID: {id}.")
        result = db.query(MatchResult).filter(MatchResult.id == id).first()
        if not result:
            logger.warning(f"Match result with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match result not found."
            )
        match_result = MatchResultSchema.model_validate(result)
        logger.info(f"Successfully fetched match result with ID: {id}.")
        return match_result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching match result by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the match result."
        )


def get_match_results_by_job_description_id(db: db_dependency, job_description_id: int) -> list[MatchResultSchema]:
    try:
        logger.debug(f"Fetching match results for job description ID: {job_description_id}.")
        result = db.query(MatchResult).filter(MatchResult.job_description_id == job_description_id).all()
        if not result:
            logger.warning(f"No match results found for job description ID: {job_description_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No match results found for the given job description ID."
            )
        match_results = [MatchResultSchema.model_validate(item) for item in result]
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


def add_match_result(db: db_dependency, match_result_request: MatchResultSchema) -> MatchResultSchema:
    try:
        logger.debug("Attempting to add a new match result.")
        new_match_result = MatchResult(**match_result_request.model_dump())
        db.add(new_match_result)
        db.commit()
        logger.info("Successfully added a new match result.")
        return MatchResultSchema.model_validate(new_match_result)
    except Exception as e:
        logger.error(f"Error occurred while adding a new match result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the match result."
        )


def update_match_result_by_id(db: db_dependency, id: int, match_result_request: MatchResultSchema) -> MatchResultSchema:
    try:
        logger.debug(f"Attempting to update match result with ID: {id}.")
        result = db.query(MatchResult).filter(MatchResult.id == id).first()
        if not result:
            logger.warning(f"Match result with ID {id} not found for update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match result not found."
            )
        for key, value in match_result_request.model_dump().items():
            setattr(result, key, value)
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated match result with ID: {id}.")
        return MatchResultSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating match result with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the match result."
        )


def delete_match_result_by_id(db: db_dependency, id: int) -> None:
    try:
        logger.debug(f"Attempting to delete match result with ID: {id}.")
        result = db.query(MatchResult).filter(MatchResult.id == id).first()
        if not result:
            logger.warning(f"Match result with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match result not found."
            )
        db.delete(result)
        db.commit()
        logger.info(f"Successfully deleted match result with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting match result with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the match result."
        )


def get_top_match_results_by_job_description_id(db: db_dependency, job_description_id: int, top_n: int) -> list[
    MatchResultSchema]:
    try:
        logger.debug(f"Fetching top {top_n} match results for job description ID: {job_description_id}.")
        result = db.query(MatchResult).filter(MatchResult.job_description_id == job_description_id).order_by(
            MatchResult.rank.asc()).limit(top_n).all()
        if not result:
            logger.warning(f"No match results found for job description ID: {job_description_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No match results found for the given job description ID."
            )
        match_results = [MatchResultSchema.model_validate(item) for item in result]
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
