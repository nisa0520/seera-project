"""Background preset endpoints (API-IMG-05)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.services.background_service import BackgroundService

router = APIRouter(prefix="/backgrounds", tags=["backgrounds"])


@router.get("")
def list_backgrounds(db: DBSession = Depends(get_db)):
    service = BackgroundService(db)
    return {
        "backgrounds": [BackgroundService.serialize(preset) for preset in service.list_active()]
    }
