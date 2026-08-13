from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.coingecko import coingecko
from app.schemas import CryptoListResponse


class SortBy(str, Enum):
    market_cap = "market_cap"
    volume_24h = "volume_24h"


app = FastAPI(title="Crypto Screener API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/crypto", response_model=CryptoListResponse)
async def get_crypto_projects(
    sort_by: SortBy = Query(SortBy.market_cap),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    fdv_max: float | None = Query(None, gt=0),
) -> CryptoListResponse:
    try:
        projects = await coingecko.get_filtered_projects()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CoinGecko request failed: {exc}") from exc

    if fdv_max is not None:
        projects = [p for p in projects if p.fully_diluted_valuation < fdv_max]

    key = (
        (lambda p: p.market_cap)
        if sort_by == SortBy.market_cap
        else (lambda p: p.total_volume)
    )
    projects = sorted(projects, key=key, reverse=order == "desc")

    return CryptoListResponse(count=len(projects), items=projects)
