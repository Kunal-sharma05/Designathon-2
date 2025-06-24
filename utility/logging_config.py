import logging

# Configure the root logger
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filemode="a",
)

# Module-specific logger
logger = logging.getLogger(f"fastapi_project.{__name__}")
