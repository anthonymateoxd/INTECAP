from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.router import router as api_router
from app.core.config import settings
from app.database.dependencies import get_db


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


app.include_router(
    api_router,
    prefix="/api",
)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }