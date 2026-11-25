from app.services.keitaro import KeitaroClient

async def get_campaign(campaign_id: int):
    return await KeitaroClient().get_campaign(campaign_id)

async def add_offer(campaign_id: int, offer_id: int):
    # TODO: Load campaign, preserve existing settings/streams, append offer
    # using the exact stream schema from Keitaro docs, then persist via API.
    raise NotImplementedError("Waiting for the installed Keitaro stream schema")

async def remove_offer(campaign_id: int, offer_id: int):
    # TODO: Remove only the selected offer and preserve all other campaign data.
    raise NotImplementedError("Waiting for the installed Keitaro stream schema")
