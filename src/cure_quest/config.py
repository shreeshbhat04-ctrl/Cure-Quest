from functools import lru_cache
from typing import Literal
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Cure-Quest"
    app_env: Literal["development", "test", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    app_api_key: str | None = None
    database_url: str = "sqlite:///./cure_quest.db"
    brain_gateway_mode: Literal["direct", "mcp"] = "direct"
    ocr_confidence_threshold: float = Field(default=0.85, ge=0, le=1)
    acute_condition_lookback_days: int = 180
    integration_max_retries: int = 2
    integration_retry_delay_ms: int = 300
    alloydb_project: str | None = None
    alloydb_region: str | None = None
    alloydb_cluster: str | None = None
    alloydb_instance: str | None = None
    alloydb_use_auth_proxy: bool = False
    alloydb_auth_proxy_host: str = "127.0.0.1"
    alloydb_auth_proxy_port: int = 5432
    alloydb_database: str = "cure_quest"
    alloydb_user: str | None = None
    alloydb_password: str | None = None
    google_api_key: str | None = None
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    google_genai_use_vertexai: bool = False
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    adk_model: str = "gemini-2.5-pro"
    google_oauth_client_file: str = "credentials/google_oauth_client.json"
    google_drive_token_file: str = "credentials/google_drive_token.json"
    google_calendar_token_file: str = "credentials/google_calendar_token.json"
    google_drive_folder_id: str | None = None
    google_drive_classification_enabled: bool = True
    google_calendar_id: str = "primary"
    bigquery_project_id: str | None = None
    bigquery_dataset_id: str = "cure_quest"
    bigquery_table_id: str = "integration_events"
    openfda_api_key: str | None = None
    google_maps_api_key: str | None = None
    medical_model_backend: Literal["placeholder", "huggingface", "vertex"] = "placeholder"
    huggingface_hub_token: str | None = None
    medgemma_model_id: str = "google/medgemma-1.5-4b-it"
    medsiglip_model_id: str = "google/medsiglip-448"
    medical_embedding_dimensions: int = 768
    medical_vector_table_name: str = "medical_memories_vector"
    gemini_fast_model_id: str = "gemini-3.1-flash-lite-preview"
    asana_access_token: str | None = None
    asana_project_gid: str | None = None
    asana_assignee_gid: str | None = None
    asana_workspace_gid: str | None = None
    asana_task_due_on: str | None = None
    mcp_server_command: str = "python"
    mcp_server_args: str = "-m cure_quest.mcp.server"

    @property
    def mcp_server_arg_list(self) -> list[str]:
        return [part for part in self.mcp_server_args.split(" ") if part]

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def alloydb_instance_uri(self) -> str | None:
        if not all([self.alloydb_project, self.alloydb_region, self.alloydb_cluster, self.alloydb_instance]):
            return None
        return (
            f"projects/{self.alloydb_project}/locations/{self.alloydb_region}/"
            f"clusters/{self.alloydb_cluster}/instances/{self.alloydb_instance}"
        )

    @property
    def resolved_database_url(self) -> str:
        if (
            self.alloydb_use_auth_proxy
            and self.alloydb_user
            and self.alloydb_password is not None
            and self.alloydb_database
        ):
            quoted_user = quote(self.alloydb_user, safe="")
            quoted_password = quote(self.alloydb_password, safe="")
            return (
                f"postgresql+psycopg://{quoted_user}:{quoted_password}"
                f"@{self.alloydb_auth_proxy_host}:{self.alloydb_auth_proxy_port}/{self.alloydb_database}"
            )
        return self.database_url

    @property
    def database_backend_hint(self) -> str:
        return self.resolved_database_url.split("://", 1)[0]


@lru_cache
def get_settings() -> Settings:
    return Settings()
