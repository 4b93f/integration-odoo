from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import get_session
from src.db.models.invoices import Invoice


router = APIRouter(prefix="/invoices", tags=["invoices"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[Invoice])
async def get_invoices(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.exec(select(Invoice))
        return result.all()
    except Exception as e:
        logger.exception("Error fetching invoices")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Invoice).where(Invoice.id == invoice_id)
        result = await session.exec(statement)
        invoice = result.first()

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except Exception as e:
        logger.exception("Error fetching invoice")
        raise HTTPException(status_code=500, detail=str(e))
