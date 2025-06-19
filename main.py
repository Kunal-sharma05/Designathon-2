from fastapi import FastAPI
from db.database import engine
from router.user import router as user_router
from db.database import base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

base.metadata.create_all(bind=engine)

app.include_router(user_router, tags=["User"])

