from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from crud import WorkflowStatus as workflow_status_service
from db.database import db_dependency
from schema.WorkflowStatus import WorkflowStatusSchema
from utility.logging_config import logger
from core.security import get_current_user
from typing import Annotated

router = APIRouter()


# GET all workflow statuses
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_workflow_statuses(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Fetching all workflow statuses.")
        workflow_statuses = workflow_status_service.get_all_workflow_statuses(db)
        logger.info("Successfully fetched all workflow statuses.")
        return workflow_statuses
    except Exception as e:
        logger.error(f"Error occurred while fetching workflow statuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching workflow statuses."
        )


# GET workflow status by ID
@router.get("/{workflow_status_id}", status_code=status.HTTP_200_OK)
async def read_workflow_status_by_id(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, workflow_status_id: str = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Fetching workflow status with ID: {workflow_status_id}.")
        workflow_status = workflow_status_service.get_workflow_status_by_id(db, workflow_status_id)
        logger.info(f"Successfully fetched workflow status with ID: {workflow_status_id}.")
        return workflow_status
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while fetching workflow status with ID {workflow_status_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the workflow status."
        )


# POST a new workflow status
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_workflow_status(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, workflow_status_request: WorkflowStatusSchema):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug("Creating a new workflow status.")
        workflow_status = workflow_status_service.add_workflow_status(db, workflow_status_request)
        logger.info("Successfully created a new workflow status.")
        return workflow_status
    except Exception as e:
        logger.error(f"Error occurred while creating a workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the workflow status."
        )


# PUT to update workflow status by ID
@router.put("/{workflow_status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_workflow_status(
    user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    workflow_status_request: WorkflowStatusSchema,
    workflow_status_id: str = Path(...),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating workflow status with ID: {workflow_status_id}.")
        workflow_status_service.update_workflow_status_by_id(db, workflow_status_id, workflow_status_request)
        logger.info(f"Successfully updated workflow status with ID: {workflow_status_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating workflow status with ID {workflow_status_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the workflow status."
        )


# DELETE workflow status by ID
@router.delete("/{workflow_status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_status(user: Annotated[dict, Depends(get_current_user)], db: db_dependency, workflow_status_id: str = Path(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Deleting workflow status with ID: {workflow_status_id}.")
        workflow_status_service.delete_workflow_status_by_id(db, workflow_status_id)
        logger.info(f"Successfully deleted workflow status with ID: {workflow_status_id}.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting workflow status with ID {workflow_status_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the workflow status."
        )


# PUT to update workflow progress
@router.put("/{workflow_status_id}/progress", status_code=status.HTTP_200_OK)
async def update_workflow_progress(
    user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    steps: dict,
    workflow_status_id: str = Path(...),
    progress: str = Query(..., regex="^(PENDING|PROCESSING|COMPLETED)$"),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        logger.debug(f"Updating progress of workflow status with ID: {workflow_status_id} to {progress}.")
        workflow_status = workflow_status_service.update_workflow_progress(db, workflow_status_id, progress, steps)
        logger.info(f"Successfully updated progress of workflow status with ID: {workflow_status_id}.")
        return workflow_status
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating progress of workflow status with ID {workflow_status_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the workflow progress."
        )
