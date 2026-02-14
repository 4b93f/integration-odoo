from fastapi import FastAPI
from routers.partners import router as partners_router

app = FastAPI()
app.include_router(partners_router)