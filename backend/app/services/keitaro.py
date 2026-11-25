import httpx
from app.core.config import settings


class KeitaroNotConfigured(RuntimeError):
    pass


class KeitaroClient:
    def __init__(self):
        base = settings.keitaro_base_url.rstrip("/")
        key = settings.keitaro_api_key

        if not base or not key or key == "replace_me":
            raise KeitaroNotConfigured(
                "Настройте KEITARO_BASE_URL и KEITARO_API_KEY в .env"
            )

        self.base_url = base
        self.headers = {
            "Api-Key": key,
            "Content-Type": "application/json",
        }

    async def request(self, method, path, **kwargs):
        async with httpx.AsyncClient(
            timeout=30,
            headers=self.headers
        ) as client:
            response = await client.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else None

    async def list_campaigns(self, offset=0, limit=100):
        return await self.request(
            "GET", "/campaigns",
            params={"offset": offset, "limit": limit}
        )

    async def get_campaign(self, campaign_id):
        return await self.request("GET", f"/campaigns/{campaign_id}")

    async def create_campaign(self, payload):
        return await self.request("POST", "/campaigns", json=payload)

    async def update_campaign(self, campaign_id, payload):
        return await self.request(
            "PUT", f"/campaigns/{campaign_id}", json=payload
        )

    async def delete_campaign(self, campaign_id):
        return await self.request("DELETE", f"/campaigns/{campaign_id}")

    async def list_streams(self, campaign_id):
        return await self.request(
            "GET", f"/campaigns/{campaign_id}/streams"
        )

    async def get_stream(self, stream_id):
        return await self.request("GET", f"/streams/{stream_id}")

    async def create_stream(self, payload):
        return await self.request("POST", "/streams", json=payload)

    async def update_stream(self, stream_id, payload):
        return await self.request(
            "PUT", f"/streams/{stream_id}", json=payload
        )

    async def delete_stream(self, stream_id):
        return await self.request("DELETE", f"/streams/{stream_id}")

    async def list_offers(self):
        return await self.request("GET", "/offers")

    async def get_offer(self, offer_id):
        return await self.request("GET", f"/offers/{offer_id}")

    async def list_groups(self):
        return await self.request(
            "GET", "/groups", params={"type": "campaigns"}
        )

    async def list_domains(self):
        return await self.request("GET", "/domains")

    async def list_traffic_sources(self):
        return await self.request("GET", "/traffic_sources")
