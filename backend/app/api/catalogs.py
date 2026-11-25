import asyncio

from fastapi import APIRouter, HTTPException

from app.services.keitaro import (
    KeitaroClient,
    KeitaroNotConfigured
)

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.get("")
async def get_catalogs():
    try:
        client = KeitaroClient()

        offers, groups, domains, sources = await asyncio.gather(
            client.list_offers(),
            client.list_groups(),
            client.list_domains(),
            client.list_traffic_sources()
        )

        return {
            "offers": offers,
            "groups": groups,
            "domains": domains,
            "traffic_sources": sources
        }

    except KeitaroNotConfigured as exc:
        raise HTTPException(503, str(exc))

    except Exception as exc:
        raise HTTPException(502, f"Keitaro API error: {exc}")
