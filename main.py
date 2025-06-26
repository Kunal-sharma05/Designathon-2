from fastapi import FastAPI
from db.database import engine
from db.database import base
from fastapi.middleware.cors import CORSMiddleware
from utility.logging_config import logger  # Import the logger from your logging configuration file

# Import all routers
from router.user import router as user_router
from router.JobDescription import router as job_description_router
from router.Notification import router as notification_router
from router.ConsultantProfile import router as consultant_profile_router
from router.WorkflowStatus import router as workflow_status_router
from router.MatchResult import router as match_result_router

app = FastAPI()

# Define allowed origins for CORS
origins = [
    "http://localhost:3000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Create database tables
base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")  # Log database initialization

# Include routers with prefixes
app.include_router(user_router, prefix="/api/user", tags=["User"])
logger.info("User router included successfully")  # Log router inclusion

app.include_router(job_description_router, prefix="/api/job-description", tags=["Job Description"])
logger.info("Job description router included successfully")  # Log router inclusion

app.include_router(notification_router, prefix="/api/notification", tags=["Notification"])
logger.info("Notification router included successfully")  # Log router inclusion

app.include_router(consultant_profile_router, prefix="/api/consultant-profile", tags=["Consultant Profile"])
logger.info("Consultant profile router included successfully")  # Log router inclusion

app.include_router(workflow_status_router, prefix="/api/workflow-status", tags=["Workflow Status"])
logger.info("Workflow status router included successfully")  # Log router inclusion

app.include_router(match_result_router, prefix="/api/match-result", tags=["Match Result"])
logger.info("Match result router included successfully")  # Log router inclusion
