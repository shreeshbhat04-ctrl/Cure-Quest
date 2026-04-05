import logging
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from cure_quest.config import get_settings
from cure_quest.services.google_workspace import get_google_credentials

logger = logging.getLogger(__name__)

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        # In-memory cache: (parent_id, folder_name) -> folder_id
        self._folder_cache: dict[tuple[str, str], str] = {}

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

    def get_or_create_subfolder(self, parent_folder_id: str, folder_name: str) -> str:
        """Return the Drive folder ID for *folder_name* under *parent_folder_id*.

        If the subfolder already exists it is reused; otherwise it is created.
        Results are cached for the lifetime of this adapter instance.
        """
        cache_key = (parent_folder_id, folder_name)
        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]

        service = self._service()

        # Search for an existing folder with this name under the parent.
        query = (
            f"name = '{folder_name}' "
            f"and '{parent_folder_id}' in parents "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )
        results = service.files().list(q=query, fields="files(id,name)", pageSize=1).execute()
        matches = results.get("files", [])

        if matches:
            folder_id = matches[0]["id"]
            logger.info("Found existing Drive subfolder '%s' (id=%s)", folder_name, folder_id)
        else:
            # Create the subfolder.
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id],
            }
            created = service.files().create(body=folder_metadata, fields="id,name").execute()
            folder_id = created["id"]
            logger.info("Created Drive subfolder '%s' (id=%s)", folder_name, folder_id)

        self._folder_cache[cache_key] = folder_id
        return folder_id

    def upload_file(
        self,
        file_path: str,
        mime_type: str = "application/octet-stream",
        folder_id: str | None = None,
    ) -> dict:
        """Upload a file to Google Drive.

        Parameters
        ----------
        folder_id:
            If provided, the file is uploaded into this specific folder.
            Otherwise falls back to the global ``GOOGLE_DRIVE_FOLDER_ID``.
        """
        service = self._service()
        path = Path(file_path)
        metadata: dict[str, object] = {"name": path.name}

        target_folder = folder_id or self.settings.google_drive_folder_id
        if target_folder:
            metadata["parents"] = [target_folder]

        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=False)
        created = (
            service.files()
            .create(body=metadata, media_body=media, fields="id,name,webViewLink,parents")
            .execute()
        )
        return created
