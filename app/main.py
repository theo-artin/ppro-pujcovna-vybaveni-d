from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.api_router import api_router

# Import všech modelů pro jistotu jejich registrace v Base.metadata
import app.db.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pro dev mód zajistíme vytvoření tabulek (v produkci spravuje Alembic)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Informační systém půjčovny sportovního vybavení (Zadání varianty D pro předmět PPRO na FIM UHK).",
    version="0.1.0-demo",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statické soubory pro webové rozhraní
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Frontend"])
def serve_frontend():
    """Servíruje webové rozhraní pro rezervace a správu půjčovny."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
    return {"message": "Frontend static file not found. Visit /docs for API."}


@app.get("/api/info", tags=["Info"])
def api_info():
    """Úvodní rozcestník API."""
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
    }

