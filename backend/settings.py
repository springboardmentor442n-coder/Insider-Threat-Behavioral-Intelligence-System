"""Centralized application settings.

This module provides the single source of truth for runtime configuration.
Settings are loaded from environment variables and `.env`, while preserving
safe defaults so the prototype continues to run locally without extra setup.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # Application Settings
    # =========================================================================

    app_name: str = Field(
        default="Insider Threat Behavioral Intelligence System",
        alias="APP_NAME",
    )
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_description: str = Field(
        default="Enterprise Behavioral Intelligence REST API",
        alias="APP_DESCRIPTION",
    )
    app_env: Literal["development", "testing", "production"] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_debug: bool = Field(default=False, alias="APP_DEBUG")

    # =========================================================================
    # Security / JWT Settings
    # =========================================================================

    secret_key: str = Field(
        default="insider-threat-secret-key",
        alias="SECRET_KEY",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
    )

# Token valid for 24 hours during development
    access_token_expire_minutes: int = Field(
            default=1440,
            alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        )

    oauth2_token_url: str = Field(
            default="/auth/login",
            alias="OAUTH2_TOKEN_URL",
        )

    # =========================================================================
    # CORS Settings
    # =========================================================================

    cors_allow_credentials: bool = Field(
        default=True,
        alias="CORS_ALLOW_CREDENTIALS",
    )
    cors_allow_methods: str = Field(default="*", alias="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="*", alias="CORS_ALLOW_HEADERS")
    cors_allow_all_origins: bool = Field(
        default=True,
        alias="CORS_ALLOW_ALL_ORIGINS",
    )
    cors_allowed_origins_raw: str = Field(
        default="",
        alias="CORS_ALLOWED_ORIGINS",
    )

    # =========================================================================
    # Logging Settings
    # =========================================================================

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s | %(levelname)s | %(message)s",
        alias="LOG_FORMAT",
    )

    # =========================================================================
    # Future Integration Placeholders
    # =========================================================================

    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/insider_threat",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )
    object_storage_url: str = Field(
        default="http://localhost:9000",
        alias="OBJECT_STORAGE_URL",
    )

    # =========================================================================
    # Path Settings
    # =========================================================================

    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1],
        alias="PROJECT_ROOT",
    )
    backend_dir_name: str = Field(default="backend", alias="BACKEND_DIR_NAME")
    reports_dir_name: str = Field(default="reports", alias="REPORTS_DIR_NAME")
    models_dir_name: str = Field(default="models", alias="MODELS_DIR_NAME")
    plots_dir_name: str = Field(default="plots", alias="PLOTS_DIR_NAME")
    datasets_dir_name: str = Field(default="datasets", alias="DATASETS_DIR_NAME")
    backend_data_dir_name: str = Field(default="data", alias="BACKEND_DATA_DIR_NAME")
    backend_models_dir_name: str = Field(
        default="models",
        alias="BACKEND_MODELS_DIR_NAME",
    )
    users_file_name: str = Field(default="users.json", alias="USERS_FILE_NAME")

    @property
    def backend_dir(self) -> Path:
        """Absolute path to the backend source directory."""
        return self.project_root / self.backend_dir_name

    @property
    def reports_dir(self) -> Path:
        """Absolute path to generated report artifacts."""
        return self.project_root / self.reports_dir_name

    @property
    def models_dir(self) -> Path:
        """Absolute path to trained model artifacts."""
        return self.project_root / self.models_dir_name

    @property
    def plots_dir(self) -> Path:
        """Absolute path to generated plot artifacts."""
        return self.project_root / self.plots_dir_name

    @property
    def datasets_dir(self) -> Path:
        """Absolute path to the datasets directory."""
        return self.project_root / self.datasets_dir_name

    @property
    def backend_data_dir(self) -> Path:
        """Absolute path to backend runtime CSV data."""
        return self.backend_dir / self.backend_data_dir_name

    @property
    def users_file(self) -> Path:
        """Absolute path to the local prototype user store."""
        return self.backend_dir / self.backend_models_dir_name / self.users_file_name

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Return effective CORS origins for the active environment."""
        if self.cors_allow_all_origins:
            return ["*"]

        origins = [
            origin.strip()
            for origin in self.cors_allowed_origins_raw.split(",")
            if origin.strip()
        ]

        return origins

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Return effective allowed HTTP methods."""
        if self.cors_allow_methods.strip() == "*":
            return ["*"]

        return [
            method.strip()
            for method in self.cors_allow_methods.split(",")
            if method.strip()
        ]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Return effective allowed HTTP headers."""
        if self.cors_allow_headers.strip() == "*":
            return ["*"]

        return [
            header.strip()
            for header in self.cors_allow_headers.split(",")
            if header.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    return Settings()


settings = get_settings()
