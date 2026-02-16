from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import get_session
from src.db.models.partner import Partner


router = APIRouter(prefix="/partners", tags=["partners"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[Partner])
async def get_partners(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.exec(select(Partner))
        return result.all()
    except Exception as e:
        logger.exception("Error fetching partners")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{partners}", response_model=Partner)
async def get_partner(partners: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Partner).where(Partner.odoo_id == partners)
        result = await session.exec(statement)
        partner = result.first()

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        return partner
    except Exception as e:
        logger.exception("Error fetching partner")
        raise HTTPException(status_code=500, detail=str(e))
