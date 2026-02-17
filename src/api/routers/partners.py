from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import get_session
from src.db.models.partner import Partner
from src.services.partner_service import PartnerService


router = APIRouter(prefix="/partners", tags=["partners"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[Partner])
async def get_partners(session: AsyncSession = Depends(get_session)): # Dependency injection of database session
    try:
        service = PartnerService(session)
        return await service.get_all_partners()
    except Exception as e:
        logger.exception("Error fetching partners")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{partner_odoo_id}", response_model=Partner)
async def get_partner(partner_odoo_id: int, session: AsyncSession = Depends(get_session)):
    try:
        service = PartnerService(session)
        partner = await service.get_partner_by_odoo_id(partner_odoo_id)

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        return partner
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching partner")
        raise HTTPException(status_code=500, detail=str(e))
