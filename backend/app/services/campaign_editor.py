from app.services.keitaro import KeitaroClient


def _normalize_offers(offers: list[dict]) -> list[dict]:
    """
    Равномерно распределяет 100% между офферами.
    Сохраняет offer_id и state.
    """
    if not offers:
        return []

    count = len(offers)
    base_share, remainder = divmod(100, count)

    normalized = []

    for index, offer in enumerate(offers):
        normalized.append({
            "offer_id": int(offer["offer_id"]),
            "share": base_share + (1 if index < remainder else 0),
            "state": offer.get("state", "active"),
        })

    return normalized


async def get_campaign(campaign_id):
    client = KeitaroClient()

    campaign = await client.get_campaign(campaign_id)
    streams = await client.list_streams(campaign_id)

    return {
        "campaign": campaign,
        "streams": streams
    }


async def _get_offer_stream(client, campaign_id):
    streams = await client.list_streams(campaign_id)

    if isinstance(streams, dict):
        streams = streams.get("data", streams.get("items", []))

    stream = next(
        (s for s in streams if s.get("type") == "default"),
        None
    )

    if not stream:
        raise ValueError("Поток офферов не найден")

    return await client.get_stream(stream["id"])


async def add_offer(campaign_id, offer_id):
    if offer_id <= 0:
        raise ValueError("ID оффера должен быть положительным")

    client = KeitaroClient()

    stream = await _get_offer_stream(client, campaign_id)
    offers = list(stream.get("offers", []))

    if any(int(o["offer_id"]) == offer_id for o in offers):
        return {
            "message": "Оффер уже существует",
            "offers": _normalize_offers(offers)
        }

    offers.append({
        "offer_id": offer_id,
        "state": "active"
    })

    updated = _normalize_offers(offers)

    await client.update_stream(
        stream["id"],
        {"offers": updated}
    )

    return {
        "message": "Оффер добавлен",
        "offers": updated,
        "total_share": sum(o["share"] for o in updated)
    }


async def remove_offer(campaign_id, offer_id):
    if offer_id <= 0:
        raise ValueError("ID оффера должен быть положительным")

    client = KeitaroClient()

    stream = await _get_offer_stream(client, campaign_id)
    offers = list(stream.get("offers", []))

    updated = [
        o for o in offers
        if int(o["offer_id"]) != offer_id
    ]

    if len(updated) == len(offers):
        return {
            "message": "Оффер не найден",
            "offers": _normalize_offers(offers)
        }

    normalized = _normalize_offers(updated)

    await client.update_stream(
        stream["id"],
        {"offers": normalized}
    )

    return {
        "message": "Оффер удалён",
        "offers": normalized,
        "total_share": sum(o["share"] for o in normalized)
    }
