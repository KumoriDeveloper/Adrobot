"""Keitaro API adapter.

Endpoint paths and payload schemas must be confirmed against the API docs
provided by the target Keitaro installation before production use.
"""
import httpx
from app.core.config import settings

class KeitaroNotConfigured(RuntimeError):
    pass

class KeitaroClient:
    def __init__(self):
        if not settings.keitaro_base_url or not settings.keitaro_api_key or settings.keitaro_api_key == "replace_me":
            raise KeitaroNotConfigured("Configure KEITARO_BASE_URL and KEITARO_API_KEY in .env")
        self.base_url = settings.keitaro_base_url.rstrip("/")
        self.headers = {"Api-Key": settings.keitaro_api_key, "Content-Type": "application/json"}

    async def request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30) as client:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None

    async def list_offers(self, search: str = ""):
        # TODO: Confirm exact endpoint, pagination and search params in local Keitaro API docs.
        return await self.request("GET", "/admin_api/v1/offers", params={"search": search})

    async def list_campaigns(self):
        # TODO: Confirm exact endpoint and response shape.
        return await self.request("GET", "/admin_api/v1/campaigns")

    async def create_campaign(self, payload: dict):
        # TODO: Map the domain model to the exact Keitaro campaign/stream API schema.
        return await self.request("POST", "/admin_api/v1/campaigns", json=payload)

    async def update_campaign(self, campaign_id: int, payload: dict):
        # TODO: Confirm whether Keitaro expects PUT or PATCH and the full payload schema.
        return await self.request("PATCH", f"/admin_api/v1/campaigns/{campaign_id}", json=payload)

    async def get_campaign(self, campaign_id: int):
        return await self.request("GET", f"/admin_api/v1/campaigns/{campaign_id}")
