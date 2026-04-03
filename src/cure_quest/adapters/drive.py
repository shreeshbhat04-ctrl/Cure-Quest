from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from cure_quest.config import get_settings
from cure_quest.services.google_workspace import get_google_credentials

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _service(self):
        creds = get_google_credentials(DRIVE_SCOPES, self.settings.google_drive_token_file)
        return build("drive", "v3", credentials=creds)

    def list_accessible_files(self, page_size: int = 10) -> list[dict]:
        service = self._service()
        response = (
            service.files()
            .list(pageSize=page_size, fields="files(id,name,mimeType,modifiedTime)")
            .execute()
        )
        return response.get("files", [])

    def upload_file(self, file_path: str, mime_type: str = "application/octet-stream") -> dict:
        service = self._service()
        path = Path(file_path)
        metadata: dict[str, object] = {"name": path.name}
        if self.settings.google_drive_folder_id:
            metadata["parents"] = [self.settings.google_drive_folder_id]

        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=False)
        created = (
            service.files()
            .create(body=metadata, media_body=media, fields="id,name,webViewLink,parents")
            .execute()
        )
        return created
