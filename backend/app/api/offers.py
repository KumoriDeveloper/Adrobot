from fastapi import APIRouter, HTTPException, Query

from app.services.keitaro import KeitaroClient, KeitaroNotConfigured

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("")
async def search_offers(q: str = Query(default="", max_length=100)):
    try:
        offers = await KeitaroClient().list_offers()

        if not q.strip():
            return offers

        query = q.strip().casefold()
        return [
            offer for offer in offers
            if query in str(offer.get("name", "")).casefold()
            or query in str(offer.get("id", ""))
        ]

    except KeitaroNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}"
        )
