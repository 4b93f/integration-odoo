from fastapi import FastAPI
from src.routers.partners import router as partners_router

app = FastAPI(title="Odoo Sync API")

app.include_router(partners_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}
