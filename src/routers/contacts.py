from fastapi import APIRouter
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import engine
from src.models.contact import Contact



router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/")
async def read_root():
	async with AsyncSession(engine) as session:
		result = await session.exec(select(Contact))
		return result.all()

@router.get("/{contact_id}")
async def read_item(contact_id: int, q: str | None = None):
	async with AsyncSession(engine) as session:
		result = await session.exec(select(Contact).where(Contact.id == contact_id))
		contact = result.first()
		if not contact:
			return {"error": "Contact not found"}
		return contact