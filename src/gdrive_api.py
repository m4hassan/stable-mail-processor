import logging
import os
import sys
import tempfile
from pathlib import Path

import requests
from fuzzywuzzy import process
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

ROOT_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)

SCOPE = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_JSON_KEY = ROOT_DIR / "secrets.json"

creds = service_account.Credentials.from_service_account_file(
    filename=SERVICE_ACCOUNT_JSON_KEY, scopes=SCOPE
)

service = build("drive", "v3", credentials=creds)


def list_folders():
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return folders


def create_folder(recipient_folder_name):
    file_metadata = {
        "name": recipient_folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")


def fuzzy_search_or_create_folder(recipient_name, threshold=80):
    folders = list_folders()

    folder_map = {folder["name"]: folder["id"] for folder in folders}

    if folder_map:
        best_match, score = process.extractOne(recipient_name, list(folder_map.keys()))
        if score >= threshold:
            logger.info(
                f"Found matching folder '{folder_map[best_match]}' with score {score}."
            )
            return folder_map[best_match]

    logger.info(
        f"No matching folder found for '{recipient_name}' (threshold: {threshold}). Creating a new folder."
    )
    new_folder_id = create_folder(recipient_name)
    return new_folder_id


def upload_to_google_drive(mail_id, pdf_url, recipient_name, recipient_folder_id):
    file_name = f"{mail_id}.pdf"

    response = requests.get(pdf_url)
    if response.status_code != 200:
        logger.error(f"Error downloading file: {pdf_url}")
        return None

    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

            file_metadata = {
                "name": file_name,
                "parents": [recipient_folder_id],
            }
            media = MediaFileUpload(
                temp_file_path, mimetype="application/pdf", resumable=True
            )

            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            logger.info(f"Uploaded '{file_name}' to '{recipient_name}'.")

            return file.get("id")

    except Exception as error:
        logger.error(f"Error in Temp file : {error}")
        return None

    finally:
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
