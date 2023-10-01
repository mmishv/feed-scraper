from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CONFIG_LOGGER_PATH: str
    NEWS_TOPIC: str
    KAFKA_URL: str
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    NEWS_TOPIC: str
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
