from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    serpapi_key: str
    imgbb_key: str
    replicate_api_token: str | None = None
    pinterest_client_id: str | None = None
    pinterest_client_secret: str | None = None
    pinterest_redirect_uri: str = "http://127.0.0.1:8000/api/auth/pinterest/callback"
    cache_ttl_seconds: int = 86400  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
