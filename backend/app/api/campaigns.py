from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign_job import CampaignJob
from app.schemas import CampaignCreate, CampaignJobOut
from app.services.campaign_creator import create_two_flow_campaign
from app.services.keitaro import KeitaroClient, KeitaroNotConfigured
from app.services.campaign_editor import (
    get_campaign,
    add_offer,
    remove_offer,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/create", response_model=CampaignJobOut)
async def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
):
    job = CampaignJob(
        campaign_name=payload.name,
        geo=payload.geo.upper(),
        offer_id=payload.offer_id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        result = await create_two_flow_campaign(payload.model_dump())

        if isinstance(result, dict):
            job.keitaro_campaign_id = result.get("id")

        job.status = "created"

    except KeitaroNotConfigured as exc:
        job.status = "needs_keitaro_config"
        db.commit()
        raise HTTPException(status_code=503, detail=str(exc))

    except Exception as exc:
        job.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}",
        )

    db.commit()
    db.refresh(job)

    return job


@router.get("/{campaign_id}")
async def read_campaign(
    campaign_id: int = Path(gt=0),
):
    try:
        return await get_campaign(campaign_id)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except KeitaroNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}",
        )


@router.post("/{campaign_id}/offers/{offer_id}")
async def add_campaign_offer(
    campaign_id: int = Path(gt=0),
    offer_id: int = Path(gt=0),
):
    try:
        return await add_offer(campaign_id, offer_id)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except KeitaroNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}",
        )


@router.delete("/{campaign_id}/offers/{offer_id}")
async def delete_campaign_offer(
    campaign_id: int = Path(gt=0),
    offer_id: int = Path(gt=0),
):
    try:
        return await remove_offer(campaign_id, offer_id)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except KeitaroNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}",
        )

@router.get("/")
async def list_campaigns(
    offset: int = 0,
    limit: int = 100,
):
    if offset < 0 or limit < 1 or limit > 500:
        raise HTTPException(
            status_code=422,
            detail="Некорректные параметры offset или limit",
        )

    try:
        campaigns = await KeitaroClient().list_campaigns(
            offset=offset,
            limit=limit,
        )

        if not isinstance(campaigns, list):
            raise HTTPException(
                status_code=502,
                detail="Некорректный ответ Keitaro: ожидался список кампаний",
            )

        return [
            {
                "id": campaign.get("id"),
                "name": campaign.get("name"),
                "state": campaign.get("state"),
            }
            for campaign in campaigns
        ]

    except KeitaroNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keitaro API error: {exc}",
        )

