import os
import sys
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.middleware.cors import setup_cors
from app.api.v1.router import api_router
from app.core.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking database connection...", flush=True)
    try:
        async def _check_db() -> None:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))

        await asyncio.wait_for(_check_db(), timeout=8)
        print("Database connection successful", flush=True)
    except asyncio.TimeoutError:
        print("Database connection failed: timeout", flush=True)
    except Exception as exc:
        print(f"Database connection failed: {exc}", flush=True)
    yield

# Create FastAPI app
app = FastAPI(
    title="CEIT CMS API",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup CORS middleware
setup_cors(app)

# Serve static files (uploaded assets)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(api_router, prefix="/api")

# Root endpoints
@app.get("/")
async def root():
    return {"message": "API is running"}

# Migration commands:
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)