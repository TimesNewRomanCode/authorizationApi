from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):

    DB_DRIVER: str
    DB_PROTOCOL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.DB_PROTOCOL}+{self.DB_DRIVER}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @computed_field
    @property
    def REFRESH_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60

    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()