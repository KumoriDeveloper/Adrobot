from app.services.keitaro import KeitaroClient


async def create_two_flow_campaign(data: dict):
    client = KeitaroClient()

    campaign = await client.create_campaign({
        "name": data["name"],
        "domain_id": data["domain_id"],
        "group_id": data["group_id"],
        "traffic_source_id": data["traffic_source_id"],
    })

    campaign_id = campaign.get("id")

    if not campaign_id:
        raise RuntimeError("Keitaro не вернул ID кампании")

    try:
        await client.create_stream({
            "campaign_id": campaign_id,
            "name": "Geo → Google",
            "type": "regular",
            "schema": "redirect",
            "action_type": "http",
            "action_payload": "https://google.com",
            "filters": [
                {
                    "name": "country",
                    "mode": "accept",
                    "payload": [data["geo"].upper()]
                }
            ]
        })

        await client.create_stream({
            "campaign_id": campaign_id,
            "name": "Offers",
            "type": "default",
            "schema": "landings",
            "offers": [
                {
                    "offer_id": data["offer_id"],
                    "share": 100,
                    "state": "active"
                }
            ]
        })

    except Exception:
        try:
            await client.delete_campaign(campaign_id)
        except Exception:
            pass
        raise

    return {
        "id": campaign_id,
        "streams_created": 2
    }
