from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import get_session
from src.models.partner import Partner

router = APIRouter(prefix="/partners", tags=["partners"])

@router.get("/", response_model=list[Partner])
async def get_partners(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Partner))
    return result.all()

@router.get("/{partners}", response_model=Partner)
async def get_partner(partners: int, session: AsyncSession = Depends(get_session)):
    """Fetch a single partner by their Odoo ID."""
    statement = select(Partner).where(Partner.odoo_id == partners)
    result = await session.exec(statement)
    partner = result.first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner