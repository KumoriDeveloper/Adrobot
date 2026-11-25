from app.services.keitaro import KeitaroClient

async def create_two_flow_campaign(data: dict):
    client = KeitaroClient()
    # Intentionally not sending a guessed payload: stream schema and routing
    # semantics must be mapped from the installed Keitaro API documentation.
    payload = {
        "name": data["name"],
        "_adrobot": {
            "geo": data["geo"].upper(),
            "offer_id": data["offer_id"],
            "required_flows": [
                {"role": "geo_google", "country": data["geo"].upper(), "destination": "https://www.google.com"},
                {"role": "default_offer", "offer_id": data["offer_id"]},
            ],
        },
    }
    return await client.create_campaign(payload)
