import io
import logging

import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient import errors

from fuzzywuzzy import process

logger = logging.getLogger(__name__)

scope = ['https://www.googleapis.com/auth/drive']
service_account_json_key = "mail-scan-451215-6b685e65f439.json"

creds = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key,
    scopes=scope)

service = build('drive', 'v3', credentials=creds)

parent_folder_id="1SLCNgM6nWO8pRFIAqQdzr64MX4Er35Il"

def list_folders():
    """
    List folders in the specified parent folder.

    Returns:
        list: A list of folder dictionaries containing 'id' and 'name'.
    """
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return folders


def create_folder(recipient_folder_name):
    """
    Create a new folder in Google Drive.

    Args:
        recipient_folder_name (str): The name of the folder to create.

    Returns:
        str: The ID of the created folder.
    """
    file_metadata = {
        "name": recipient_folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        # "parents": [parent_folder_id],
    }
    folder = service.files().create(body=file_metadata,
                                    fields="id").execute()
    return folder.get("id")


def fuzzy_search_or_create_folder(recipient_name, threshold=80):
    """
    Searches for a folder in Google Drive that best matches the recipient_name.
    If no match above the threshold is found, creates a new folder with the recipient_name.

    Args:
        recipient_name (str): The recipient name to search for.
        threshold (int): The minimum score required for a match (default 80).

    Returns:
        str: The ID of the matching or newly created folder.
    """
    folders = list_folders()

    folder_map = {
        folder['name']: folder['id']
        for folder in folders
    }

    if folder_map:
        # perform fuzzy search to find best match
        best_match, score = process.extractOne(recipient_name, list(folder_map.keys()))
        if score >= threshold:
            logger.info(f"Found matching folder '{folder_map[best_match]}' with score {score}.")
            return folder_map[best_match]

    # No adequate match found; create a new folder
    logger.info(f"No matching folder found for '{recipient_name}' (threshold: {threshold}). Creating a new folder.")
    new_folder_id = create_folder(recipient_name)
    return new_folder_id


def upload_to_google_drive(mail_id, pdf_url, recipient_name, recipient_folder_id):
    """
    Uploads a PDF file to Google Drive under the specified folder.

    Args:
        mail_id (str): ID of the mail item
        pdf_url (str): Local path to the PDF file.
        recipient_name (str): The name of the folder to upload to.
        recipient_folder_id (str): The ID of the folder in Google Drive where the file should be uploaded.

    Returns:
        str: The ID of the uploaded file, or None if the upload fails.
    """
    file_name = f"{mail_id}.pdf"

    response = requests.get(pdf_url)
    if response.status_code != 200:
        logger.error(f"Error downloading file: {pdf_url}")
        return None

    # Create a file-like object from the downloaded content
    pdf_file = io.BytesIO(response.content)

    file_metadata = {
        "name": file_name,
        "parents": [recipient_folder_id],
    }
    media = MediaFileUpload(filename=pdf_file,
                            mimetype='application/pdf',
                            resumable=True)
    try:
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields="id").execute()
        logger.info(f"Uploaded '{file_name}' to '{recipient_name}'.")
        return file.get("id")

    except errors.HttpError as error:
        logger.error(f"Error uploading file: '{file_name}': {error}")
        return None