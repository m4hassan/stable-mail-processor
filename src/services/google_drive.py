import tempfile
from pathlib import Path

from rapidfuzz import process, fuzz, utils
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from logger import get_logger

from . import DriveService

from config import DRAFT_LAWSUIT_PACKETS_ALL_ID

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

    def list_folders_recursively(self, parent_folder_id):
        """
        Recursively lists all folders under the given parent folder.
        """
        all_folders = []
        query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
        page_token = None

        while True:
            results = (
                self.service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )
            
            folders = results.get("files", [])
            all_folders.extend(folders)
            
            for folder in folders:
                subfolders = self.list_folders_recursively(folder["id"])
                all_folders.extend(subfolders)

            page_token = results.get("nextPageToken", None)
            if not page_token:
                break
        
        return all_folders

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

    def fuzzy_search(self, folders_list, folder_name, threshold=90):
        """
        Recursively searches in the DRAFT_LAWSUIT_PACKETS_ALL folder for a folder
        that fuzzy-matches the recipient's name. If a unique match is found, return its ID.
        If multiple valid matches are found (or none), return the default folder ID.
        """
        folder_map = {folder["name"]: folder["id"] for folder in folders_list}

        if not folder_map:
            logger.warning("No subfolders found in the DRAFT_LAWSUIT_PACKETS_ALL folder. defaulting to UNMATCHED_COURT_DOCUMENTS")
            return self.DEFAULT_FOLDER_NAME, False

        matches = process.extract(folder_name, 
                                  list(folder_map.keys()),
                                  processor=utils.default_process,
                                  scorer=fuzz.WRatio)
        
        valid_matches = [(name, score) for name, score, _ in matches if score >= threshold]

        if len(valid_matches) == 1:
            best_match, score = valid_matches[0]
            logger.info(f"Unique matching folder '{best_match}' found with score {score}")
            return folder_map[best_match], True
        
        else:
            if valid_matches:
                logger.warning(f"Multiple matching folders found for '{folder_name}': {[n for n, s in valid_matches]}. "
                               "Using default folder.")
            else:
                logger.warning(f"No matching folders found for '{folder_name}'. Using default folder.")
            
            return self.DEFAULT_FOLDER_NAME, False

    def delete_all_folders(self):
        """
        Moves all folders in the user's Google Drive to the trash.
        Warning: use it with caution as it will delete all the data from the drive.
        """
        try:
            page_token = None
            while True:
                query = f"mimeType='application/vnd.google-apps.folder' and '{DRAFT_LAWSUIT_PACKETS_ALL_ID}' in parents and trashed=false"
                response = (
                    self.service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )
                folders = response.get("files", [])
                for folder in folders:
                    try:
                        self.service.files().delete(fileId=folder["id"]).execute()
                        logger.info(f"Moved folder to trash: {folder['name']}")
                    except Exception as error:
                        logger.error(
                            f"Error moving folder to trash: {folder['name']} - {error}"
                        )

                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
        except Exception as error:
            logger.error(f"An error occurred while listing folders: {error}")
            return None

        return True
