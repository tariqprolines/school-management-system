from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "School Management System"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    API_ACCESS_TOKEN: str = "7f84d91d8c214fc9b12c6dfe3c4d4b1a"
    DATABASE_URL: str = "postgresql+asyncpg://sms_user:sms_password@localhost:5432/sms_db"
    DB_SCHEMA: str = "public"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://35.172.225.151:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
