from pydantic import BaseModel, ConfigDict


class CryptoProject(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    symbol: str
    name: str
    image: str | None = None
    market_cap: float
    fully_diluted_valuation: float
    total_volume: float
    total_value_locked: float
    max_supply: float
    total_supply: float
    preview_listing: bool


class CryptoListResponse(BaseModel):
    count: int
    items: list[CryptoProject]
