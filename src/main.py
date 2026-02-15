from fastapi import FastAPI
from src.routers.partners import router as partners_router
from src.routers.invoices import router as invoices_router
from mangum import Mangum


app = FastAPI(title="Odoo Sync API")

app.include_router(partners_router)
app.include_router(invoices_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

handler = Mangum(app)