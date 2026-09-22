"""Configuration module for ParkinDraw AI Backend Service.

Provides centralized application settings loaded from environment variables
using Pydantic Settings v2.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema and default configurations."""

    # Project Metadata
    PROJECT_NAME: str = "ParkinDraw AI Backend API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level threshold")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        description="Allowed CORS origin URLs for browser clients",
    )

    # Model & Storage Paths
    # Resolves default to '../ml/artifacts/models' relative to this backend package
    MODELS_DIR: Path = Field(
        default=(
            Path(__file__).resolve().parent.parent.parent.parent
            / "ml"
            / "artifacts"
            / "models"
        ),
        description="Directory containing canonical trained PyTorch model checkpoints",
    )

    # Inference & Clinical Screening Parameters
    CLASSIFICATION_THRESHOLD: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Probability threshold for positive Parkinson classification",
    )
    DEVICE: str = Field(
        default="auto",
        description="Inference execution device ('auto', 'cuda', or 'cpu')",
    )

    # Input Validation Limits
    MAX_UPLOAD_SIZE_BYTES: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum allowable uploaded image payload size in bytes",
    )
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = Field(
        default={".png", ".jpg", ".jpeg", ".webp"},
        description="Permissible file extensions for uploaded drawing images",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached application settings instance.

    Returns:
        Settings: Singleton application configuration instance.
    """
    return Settings()
