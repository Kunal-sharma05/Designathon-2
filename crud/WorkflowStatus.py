from utility.logging_config import logger
from fastapi import HTTPException, status
from db.database import db_dependency
from model.WorkflowStatus import WorkflowStatus  # Assuming this is the ORM model
from schema.WorkflowStatus import WorkflowStatusSchema  # Assuming a Pydantic schema exists
from datetime import  datetime


def get_all_workflow_statuses(db: db_dependency) -> list[WorkflowStatusSchema]:
    try:
        logger.debug("Fetching all workflow statuses from the database.")
        result = db.query(WorkflowStatus).all()
        workflow_statuses = [WorkflowStatusSchema.model_validate(item) for item in result]
        logger.info("Successfully fetched all workflow statuses.")
        return workflow_statuses
    except Exception as e:
        logger.error(f"Error occurred while fetching workflow statuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching workflow statuses."
        )


def get_workflow_status_by_id(db: db_dependency, id: int) -> WorkflowStatusSchema:
    try:
        logger.debug(f"Fetching workflow status with ID: {id}.")
        result = db.query(WorkflowStatus).filter(WorkflowStatus.id == id).first()
        if not result:
            logger.warning(f"Workflow status with ID {id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow status not found."
            )
        workflow_status = WorkflowStatusSchema.model_validate(result)
        logger.info(f"Successfully fetched workflow status with ID: {id}.")
        return workflow_status
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching workflow status by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the workflow status."
        )


def add_workflow_status(db: db_dependency, workflow_status_request: WorkflowStatusSchema) -> WorkflowStatusSchema:
    try:
        logger.debug("Attempting to add a new workflow status.")
        new_workflow_status = WorkflowStatus(**workflow_status_request.model_dump())
        db.add(new_workflow_status)
        db.commit()
        logger.info("Successfully added a new workflow status.")
        return WorkflowStatusSchema.model_validate(new_workflow_status)
    except Exception as e:
        logger.error(f"Error occurred while adding a new workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the workflow status."
        )


def update_workflow_status_by_id(db: db_dependency, id: int, workflow_status_request: WorkflowStatusSchema) -> WorkflowStatusSchema:
    try:
        logger.debug(f"Attempting to update workflow status with ID: {id}.")
        result = db.query(WorkflowStatus).filter(WorkflowStatus.id == id).first()
        if not result:
            logger.warning(f"Workflow status with ID {id} not found for update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow status not found."
            )
        for key, value in workflow_status_request.model_dump().items():
            setattr(result, key, value)
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated workflow status with ID: {id}.")
        return WorkflowStatusSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating workflow status with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the workflow status."
        )


def delete_workflow_status_by_id(db: db_dependency, id: int) -> None:
    try:
        logger.debug(f"Attempting to delete workflow status with ID: {id}.")
        result = db.query(WorkflowStatus).filter(WorkflowStatus.id == id).first()
        if not result:
            logger.warning(f"Workflow status with ID {id} not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow status not found."
            )
        db.delete(result)
        db.commit()
        logger.info(f"Successfully deleted workflow status with ID: {id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting workflow status with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the workflow status."
        )


def update_workflow_progress(db: db_dependency, id: int, progress: str, steps: dict) -> WorkflowStatusSchema:
    try:
        logger.debug(f"Attempting to update progress of workflow status with ID: {id} to {progress}.")
        result = db.query(WorkflowStatus).filter(WorkflowStatus.id == id).first()
        if not result:
            logger.warning(f"Workflow status with ID {id} not found for progress update.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow status not found."
            )
        result.progress = progress
        result.steps = steps
        if progress == "COMPLETED":
            result.completed_at = datetime.now()
        db.add(result)
        db.commit()
        logger.info(f"Successfully updated progress of workflow status with ID: {id} to {progress}.")
        return WorkflowStatusSchema.model_validate(result)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating progress of workflow status with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the workflow progress."
        )
