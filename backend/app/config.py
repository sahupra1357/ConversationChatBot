from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "arxiv_papers"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Qdrant settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "arxiv_ml_papers"
    VECTOR_DIM: int = 1024  # Default for BGE-Large embeddings

    # Embedding settings
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    OLLAMA_EMBED_MODEL: str = "bge-large"

    # ArXiv settings
    MAX_RESULTS: int = 5
    SHORT_SUMMARY_LENGTH: int = 100
    MAX_RETRIES: int = 3
    RETRY_DELAY_BASE: float = 2.0
    RETRY_JITTER: float = 0.5

    # LLM settings
    LLM_PROVIDER: str = "openai"  # Options: "openai" or "ollama"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    #OLLAMA_MODEL: str = "deepseek-coder:latest"
    OLLAMA_MODEL: str = "deepseek-r1:8b"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 512
    LLM_CONTEXT_WINDOW: int = 4096

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str


local_settings = Settings()