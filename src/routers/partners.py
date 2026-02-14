from fastapi import APIRouter
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import engine
from src.models.partner import Partner



router = APIRouter(prefix="/partners", tags=["partners"])

@router.get("/")
async def get_partners():
	async with AsyncSession(engine) as session:
		result = await session.exec(select(Partner))
		return result.all()

@router.get("/{partner_id}")
async def get_partner(partner_id: int):
	async with AsyncSession(engine) as session:
		partner = await session.get(Partner, partner_id)
		return partner
