from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    database_url: str = "postgresql+asyncpg://user:pass@localhost/bushop"
    database_url_sync: str = "postgresql+psycopg2://user:pass@localhost/bushop"
    internal_api_key: str
    debug: bool = True
    log_level: str = "INFO"
    alert_webhook_url: str | None = None


settings = Settings()
