from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized, typed application configuration.

    All values are read once from the environment (via .env in development)
    and validated at startup instead of being fetched ad-hoc with os.getenv()
    scattered across the codebase.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str
    database_name: str = "pmng"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Comma-separated list of allowed browser origins, e.g.
    # "http://localhost:4200,https://your-site.netlify.app"
    allowed_origins: str = "http://localhost:4200"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
