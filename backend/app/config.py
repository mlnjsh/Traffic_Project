from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    environment: str = "development"
    log_level: str = "info"
    demo_mode: bool = True
    cors_origins: str = "http://localhost:3000,https://*.vercel.app"

    # Database
    database_url: str = "sqlite+aiosqlite:///./traffic.db"

    # Redis
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""

    # TomTom
    tomtom_api_key: str = ""

    # ASTraM
    astram_api_url: str = ""
    astram_api_key: str = ""

    # Google Maps
    google_maps_api_key: str = ""

    # Bangalore bounding box
    bangalore_bbox: str = "12.85,77.45,13.15,77.80"

    # Polling
    poll_interval_seconds: int = 120

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def bbox_tuple(self) -> tuple[float, float, float, float]:
        parts = self.bangalore_bbox.split(",")
        return float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])


settings = Settings()
