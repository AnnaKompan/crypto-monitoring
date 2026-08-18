import asyncio
import time
from typing import Any

import httpx

from config import settings
from schemas import CryptoProject


class CoinGeckoClient:
    def __init__(self) -> None:
        self.base_url = settings.coingecko_base_url.rstrip("/")
        self._cache: tuple[float, list[CryptoProject]] | None = None

    def _headers(self) -> dict[str, str]:
        if not settings.coingecko_api_key:
            return {}

        if "pro-api" in self.base_url:
            return {
                "x-cg-pro-api-key": settings.coingecko_api_key
            }

        return {
            "x-cg-demo-api-key": settings.coingecko_api_key
        }

    async def _get(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, Any],
    ) -> Any:
        for attempt in range(3):
            response = await client.get(
                path,
                params=params,
                headers=self._headers(),
            )

            if response.status_code == 429:
                if attempt == 2:
                    response.raise_for_status()

                await asyncio.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError("CoinGecko request failed")

    async def _get_market_pages(
    self,
    client: httpx.AsyncClient,
) -> list[dict[str, Any]]:
        all_coins: list[dict[str, Any]] = []

        for page in range(1, 3):
            data = await self._get(
                client,
                f"{self.base_url}/coins/markets",
                {
                    "vs_currency": "usd",
                    "order": "volume_desc",
                    "per_page": 250,
                    "page": page,
                    "sparkline": "false",
                },
            )

            if not data:
                break

            all_coins.extend(data)

            page_volumes = [
                coin.get("total_volume")
                for coin in data
                if coin.get("total_volume") is not None
            ]

            if len(data) < 250:
                break

            if page_volumes and page_volumes[-1] <= 50_000:
                break

        return all_coins

    @staticmethod
    def _passes_market_filters(
        coin: dict[str, Any],
    ) -> bool:
        mcap = coin.get("market_cap")
        fdv = coin.get("fully_diluted_valuation")
        volume = coin.get("total_volume")
        max_supply = coin.get("max_supply")
        total_supply = coin.get("total_supply")

        return (
            mcap is not None
            and mcap > 0
            and fdv is not None
            and fdv < 100_000_000
            and volume is not None
            and volume > 50_000
            and max_supply is not None
            and total_supply is not None
            and max_supply == total_supply
        )

    async def _get_coin_details(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        coin: dict[str, Any],
    ) -> CryptoProject | None:

        async with semaphore:
            try:
                details = await self._get(
                    client,
                    f"{self.base_url}/coins/{coin['id']}",
                    {
                        "localization": "false",
                        "tickers": "false",
                        "market_data": "true",
                        "community_data": "false",
                        "developer_data": "false",
                        "sparkline": "false",
                    },
                )

            except httpx.HTTPError:
                return None

            preview_listing = details.get("preview_listing") is True

        market_data = details.get("market_data") or {}

        tvl_data = market_data.get("total_value_locked") or {}

        tvl = (
            tvl_data.get("usd")
            if isinstance(tvl_data, dict)
            else None
        )

        if tvl is None or tvl <= 50_000:
            return None

        return CryptoProject(
            id=coin["id"],
            symbol=coin.get("symbol", "").upper(),
            name=coin.get("name", coin["id"]),
            image=coin.get("image"),
            market_cap=coin["market_cap"],
            fully_diluted_valuation=coin["fully_diluted_valuation"],
            total_volume=coin["total_volume"],
            total_value_locked=tvl,
            max_supply=coin["max_supply"],
            total_supply=coin["total_supply"],
            preview_listing=preview_listing,
        )

    async def get_filtered_projects(
        self,
    ) -> list[CryptoProject]:

        if self._cache:
            cached_at, cached_projects = self._cache

            if time.monotonic() - cached_at < settings.cache_ttl_seconds:
                return cached_projects

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            markets = await self._get_market_pages(client)

            candidates = [
                coin
                for coin in markets
                if self._passes_market_filters(coin)
            ]
            # candidates = candidates[:20]

            semaphore = asyncio.Semaphore(
                settings.max_detail_concurrency
            )

            tasks = [
                self._get_coin_details(
                    client,
                    semaphore,
                    coin,
                )
                for coin in candidates
            ]

            results = await asyncio.gather(*tasks)

        projects = [
            project
            for project in results
            if project is not None
        ]

        self._cache = (
            time.monotonic(),
            projects,
        )

        return projects


coingecko = CoinGeckoClient()