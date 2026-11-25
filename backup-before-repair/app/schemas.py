from pydantic import BaseModel, Field, ConfigDict

class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    geo: str = Field(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    offer_id: int = Field(gt=0)

class CampaignJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_name: str
    geo: str
    offer_id: int
    keitaro_campaign_id: int | None
    status: str

class OfferOut(BaseModel):
    id: int
    name: str

class CampaignOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(extra="allow")

class OfferMutation(BaseModel):
    offer_id: int = Field(gt=0)
