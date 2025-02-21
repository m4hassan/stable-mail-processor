import tempfile
from pathlib import Path

from fuzzywuzzy import process
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from logger import get_logger

from . import DriveService

logger = get_logger()


class GoogleDriveService(DriveService):
    DEFAULT_FOLDER_NAME = "Unmatched Court Documents"

    def __init__(self):
        ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        SCOPE = ["https://www.googleapis.com/auth/drive"]
        SERVICE_ACCOUNT_JSON_KEY = ROOT_DIR / "secrets.json"

        creds = service_account.Credentials.from_service_account_file(
            filename=SERVICE_ACCOUNT_JSON_KEY, scopes=SCOPE
        )
        self.service = build("drive", "v3", credentials=creds)
        self._ensure_default_folder_exists()

    def _ensure_default_folder_exists(self):
        """Ensures the default folder for unmatched documents exists"""
        folders = self.list_folders()
        for folder in folders:
            if folder["name"] == self.DEFAULT_FOLDER_NAME:
                self._default_folder_id = folder["id"]
                return

        # Create if doesn't exist
        self._default_folder_id = self.create_folder(self.DEFAULT_FOLDER_NAME)
        logger.info(f"Created default folder '{self.DEFAULT_FOLDER_NAME}'")

    def list_folders(self):
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        return results.get("files", [])

    def create_folder(self, folder_name):
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = self.service.files().create(body=file_metadata, fields="id").execute()
        return folder.get("id")

    def upload_file(self, file_name, file_content, folder_id):
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(file_content)
                temp_file.flush()

                file_metadata = {
                    "name": file_name,
                    "parents": [folder_id],
                }
                media = MediaFileUpload(
                    temp_file.name, mimetype="application/pdf", resumable=True
                )

                file = (
                    self.service.files()
                    .create(body=file_metadata, media_body=media, fields="id")
                    .execute()
                )
                return file.get("id")

        except Exception as error:
            logger.error(f"Error uploading file: {error}")
            return None

    def fuzzy_search(self, folder_name, threshold=80):
        folders = self.list_folders()
        folder_map = {folder["name"]: folder["id"] for folder in folders}

        if folder_map:
            best_match, score = process.extractOne(folder_name, list(folder_map.keys()))  # type: ignore
            if score >= threshold:
                logger.info(f"Found matching folder '{best_match}' with score {score}")
                return folder_map[best_match], True

        return self._default_folder_id, False

    def delete_all_folders(self):
        """
        Moves all folders in the user's Google Drive to the trash.
        """
        try:
            page_token = None
            while True:
                query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
                response = self.service.files().list(q=query,
                                                     spaces="drive",
                                                     fields="nextPageToken, files(id, name)",
                                                     pageToken=page_token,
                                                     ).execute()
                folders = response.get("files", [])
                for folder in folders:
                    try:
                        self.service.files().delete(fileId=folder["id"]).execute()
                        logger.info(f"Moved folder to trash: {folder['name']}")
                    except Exception as error:
                        logger.error(f"Error moving folder to trash: {folder['name']} - {error}")

                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
        except Exception as error:
            logger.error(f"An error occurred while listing folders: {error}")
            return None

        return True


