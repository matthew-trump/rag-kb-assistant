from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embeddings_model: str = "text-embedding-3-small"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    database_url: str

    chroma_dir: str = "/data/chroma"
    kb_dir: str = "/app/kb"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore
