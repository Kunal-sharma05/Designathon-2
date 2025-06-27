from utility.logging_config import logger
from fastapi import HTTPException, status
from db.database import db_dependency
from model.ConsultantProfile import ConsultantProfile  # Assuming this is the ORM model
from schema.ConsultantProfile import ConsultantProfileSchema


def get_all_consultant_profiles(db: db_dependency) -> list[ConsultantProfileSchema]:
    try:
        logger.debug("Fetching all consultant profiles from the database.")
        result = db.query(ConsultantProfile).all()
        consultant_profiles = [ConsultantProfileSchema.model_validate(item) for item in result]
        logger.info("Successfully fetched all consultant profiles.")
        return consultant_profiles
    except Exception as e:
        logger.error(f"Error occurred while fetching consultant profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching consultant profiles."
        )


def get_consultant_profile_by_id(db: db_dependency, id: int) -> ConsultantProfileSchema:
    try:
        logger.debug(f"Fetching consultant profile with ID: {id}.")
        result = db.query(ConsultantProfile).filter(ConsultantProfile.id == id).first()
        if not result:
            logger.warning(f"Consultant profile with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultant profile not found."
            )
        consultant_profile = ConsultantProfileSchema.model_validate(result)
        logger.info(f"Successfully fetched consultant profile with ID: {id}.")
        return consultant_profile
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching consultant profile by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the consultant profile."
        )


def get_consultant_profiles_by_skill(db: db_dependency, skill: str) -> list[ConsultantProfileSchema]:
    try:
        logger.debug(f"Fetching consultant profiles with skill: {skill}.")
        result = db.query(ConsultantProfile).filter(ConsultantProfile.skills.contains([skill])).all()
        if not result:
            logger.warning(f"No consultant profiles found with skill: {skill}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No consultant profiles found with the given skill."
            )
        consultant_profiles = [ConsultantProfileSchema.model_validate(item) for item in result]
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


def add_consultant_profile(db: db_dependency, consultant_profile_request: ConsultantProfileSchema) -> ConsultantProfileSchema:
    try:
        logger.debug("Attempting to add a new consultant profile.")
        new_consultant_profile = ConsultantProfile(**consultant_profile_request.model_dump())
        db.add(new_consultant_profile)
        db.commit()
        logger.info("Successfully added a new consultant profile.")
        return ConsultantProfileSchema.model_validate(new_consultant_profile)
    except Exception as e:
        logger.error(f"Error occurred while adding a new consultant profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the consultant profile."
        )


def update_consultant_profile_by_id(db: db_dependency, id: int, consultant_profile_request: ConsultantProfileSchema) -> ConsultantProfileSchema:
    try:
        logger.debug(f"Attempting to update consultant profile with ID: {id}.")
        result = db.query(ConsultantProfile).filter(ConsultantProfile.id == id).first()
        if not result:
            logger.warning(f"Consultant profile with ID {id} not found for update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultant profile not found."
            )
        for key, value in consultant_profile_request.model_dump().items():
            setattr(result, key, value)
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated consultant profile with ID: {id}.")
        return ConsultantProfileSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating consultant profile with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the consultant profile."
        )


def delete_consultant_profile_by_id(db: db_dependency, id: int) -> None:
    try:
        logger.debug(f"Attempting to delete consultant profile with ID: {id}.")
        result = db.query(ConsultantProfile).filter(ConsultantProfile.id == id).first()
        if not result:
            logger.warning(f"Consultant profile with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultant profile not found."
            )
        db.delete(result)
        db.commit()
        logger.info(f"Successfully deleted consultant profile with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting consultant profile with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the consultant profile."
        )


def update_consultant_availability(db: db_dependency, id: int, availability: str) -> ConsultantProfileSchema:
    try:
        logger.debug(f"Attempting to update availability of consultant profile with ID: {id} to {availability}.")
        result = db.query(ConsultantProfile).filter(ConsultantProfile.id == id).first()
        if not result:
            logger.warning(f"Consultant profile with ID {id} not found for availability update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultant profile not found."
            )
        result.availability = availability
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated availability of consultant profile with ID: {id} to {availability}.")
        return ConsultantProfileSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating availability of consultant profile with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the consultant profile availability."
        )
