from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import get_session
from src.db.models.invoices import Invoice
from src.services.invoice_service import InvoiceService


router = APIRouter(prefix="/invoices", tags=["invoices"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[Invoice])
async def get_invoices(session: AsyncSession = Depends(get_session)):
    try:
        service = InvoiceService(session)
        return await service.get_all_invoices()
    except Exception as e:
        logger.exception("Error fetching invoices")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int, session: AsyncSession = Depends(get_session)):
    try:
        service = InvoiceService(session)
        invoice = await service.get_invoice_by_id(invoice_id)

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching invoice")
        raise HTTPException(status_code=500, detail=str(e))
