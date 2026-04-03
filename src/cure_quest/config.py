from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Cure-Quest"
    app_env: Literal["development", "test", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str = "sqlite:///./cure_quest.db"
    brain_gateway_mode: Literal["direct", "mcp"] = "direct"
    ocr_confidence_threshold: float = Field(default=0.85, ge=0, le=1)
    acute_condition_lookback_days: int = 180
    alloydb_project: str | None = None
    alloydb_region: str | None = None
    alloydb_cluster: str | None = None
    alloydb_instance: str | None = None
    alloydb_database: str = "cure_quest"
    alloydb_user: str | None = None
    alloydb_password: str | None = None
    google_api_key: str | None = None
    google_genai_use_vertexai: bool = False
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    adk_model: str = "gemini-2.5-pro"
    google_oauth_client_file: str = "credentials/google_oauth_client.json"
    google_drive_token_file: str = "credentials/google_drive_token.json"
    google_calendar_token_file: str = "credentials/google_calendar_token.json"
    google_drive_folder_id: str | None = None
    google_calendar_id: str = "primary"
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
