from fastapi import FastAPI
from db.database import engine
from router.user import router as user_router
from router.job_description import router as job_description_router
from db.database import base
from fastapi.middleware.cors import CORSMiddleware
from utility.logging_config import logger  # Import the logger from your logging configuration file

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

# Include the user router
app.include_router(user_router, tags=["User"])
logger.info("User router included successfully")  # Log router inclusion

app.include_router(job_description_router, tags=["Job Description"])
logger.info("Job description router included successfully")
