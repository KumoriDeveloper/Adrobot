from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import campaigns, offers, catalogs

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router, prefix="/api")
app.include_router(offers.router, prefix="/api")
app.include_router(catalogs.router, prefix="/api")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name
    }
