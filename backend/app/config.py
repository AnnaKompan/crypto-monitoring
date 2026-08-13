from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    coingecko_api_key: str | None = None
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    cache_ttl_seconds: int = 300
    max_detail_concurrency: int = 8

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
