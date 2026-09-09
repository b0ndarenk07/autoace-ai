import logging

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.batches import router as batches_router
from app.api.results import router as results_router
from app.api.single import router as single_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


app = FastAPI(
    title="AutoAce AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "AutoAce AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
    }


app.include_router(auth_router)
app.include_router(batches_router)
app.include_router(results_router)
app.include_router(single_router)