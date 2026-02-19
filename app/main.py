import os
import sys

from fastapi import FastAPI

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.middleware.cors import setup_cors
from app.api.v1.router import api_router

# Create FastAPI app
app = FastAPI(
    title="CEIT CMS API",
    version="1.0.0",
)

# Setup CORS middleware
setup_cors(app)

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