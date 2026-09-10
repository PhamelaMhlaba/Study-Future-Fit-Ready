from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai

app = FastAPI(title="Future Study Fit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Future Study Fit API"}
