from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    APP_TITLE: str = "UK App"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ])
    FCM_SERVICE_ACCOUNT_FILE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FCM_SERVICE_ACCOUNT_FILE", "fcm_service_account_file"),
    )

    @property
    def DATABASE_URL(self) -> str:
        return URL.create(
            "postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
